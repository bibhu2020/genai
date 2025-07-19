import os
import pandas as pd
from datetime import datetime, timedelta
from pandas import Timedelta
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain.tools import tool
from azure.identity import AzureCliCredential, ManagedIdentityCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from logger.decorators import log_entry
from prompt_library.prompt import SYSTEM_PROMPT  # Optional, adjust use if needed
from utils.config_loader import load_config


# Load environment variables
load_dotenv()

# Azure credentials
client_id = os.getenv("AZURE_MANAGED_IDENTITY_CLIENT_ID")
credential = None
if client_id and len(client_id) > 1: 
    credential = ManagedIdentityCredential(client_id=client_id)
else:
    credential = AzureCliCredential()
client = LogsQueryClient(credential)

# Workspace mapping
WORKSPACE_IDS = {
    "msonecloudapi-prod": "edf08e1f-916f-48c3-bc52-273492d63c8f",
    "msonecloudtool": "edf08e1f-916f-48c3-bc52-273492d63c8f",
    "blogging": "5938c293-3317-4e63-9b33-a248eb20cc81",
    # Add more as needed
}

class ConfigLoader:
    def __init__(self):
        print("Loading config...")
        self.config = load_config()

    def __getitem__(self, key):
        return self.config[key]

# Tool input schema
class LogQueryArgs(BaseModel):
    appName: str
    incidentTime: datetime

class LogQueryTool:
    def __init__(self):
        self.log_query_tool_list = self._setup_tools()
        self.config = ConfigLoader()

    def _setup_tools(self) -> List:
        @tool(args_schema=LogQueryArgs)
        @log_entry
        def azure_log_analytics_query(appName: str, incidentTime: datetime) -> str:
            """
            Query Azure Log Analytics for error, exception, trace, and dependency logs 
            around a specified incident time for a given application.

            Args:
                appName (str): application name.
                incidentTime (str): time when the incident occured in the application.

            Returns:
                str: query result.
            """

            # workspace_id = WORKSPACE_IDS.get(appName)
            workspace_id = self.config["application"][appName]["log_analytics_workspace_id"]
            app_role_name = self.config["application"][appName]["app_role_name"]
            if not workspace_id:
                return f"Error: Unknown appName '{appName}'. Please check your application name."

            start_time = incidentTime - timedelta(minutes=5)
            end_time = incidentTime + timedelta(minutes=5)
            timespan = (start_time, end_time)

            tables = {
                "AppRequests": f"""
                    AppRequests
                    | where TimeGenerated between (datetime({start_time.isoformat()}) .. datetime({end_time.isoformat()}))
                    and AppRoleName contains "{app_role_name}"
                    and Success == false
                    and toint(ResultCode) >= 500
                    | project TimeGenerated, type="request", Url, OperationName, Name, ResultCode, Duration = DurationMs, Success, AppRoleName
                """,
                "AppExceptions": f"""
                    AppExceptions
                    | where TimeGenerated between (datetime({start_time.isoformat()}) .. datetime({end_time.isoformat()}))
                    and AppRoleName contains "{app_role_name}"
                    and ProblemId != "Microsoft.IdentityModel.S2S.S2SAuthenticationException"
                    | project TimeGenerated, type="exception", OperationName, ProblemId, Message = OuterMessage, AppRoleName
                """,
                "AppTraces": f"""
                    AppTraces
                    | where TimeGenerated between (datetime({start_time.isoformat()}) .. datetime({end_time.isoformat()}))
                    and AppRoleName contains "{app_role_name}"
                    and SeverityLevel >= 2
                    | project TimeGenerated, type="trace", Message, SeverityLevel, AppRoleName
                """,
                "AppDependencies": f"""
                    AppDependencies
                    | where TimeGenerated between (datetime({start_time.isoformat()}) .. datetime({end_time.isoformat()}))
                    and AppRoleName contains "{app_role_name}"
                    and Success == false
                    | project TimeGenerated, type="dependency", Name, Target = Data, ResultCode, Success, Duration = DurationMs, AppRoleName, Server = AppRoleName
                """
            }

            log_dict = {}
            for table_name, query in tables.items():
                response = client.query_workspace(workspace_id, query, timespan=timespan)
                if response.status == LogsQueryStatus.SUCCESS and response.tables:
                    table = response.tables[0]
                    df = pd.DataFrame(table.rows, columns=table.columns)
                    df["type"] = table_name
                    log_dict[table_name] = df

            def merge_with_role_and_time(base_df, other_df, tolerance="2s"):
                if base_df.empty or other_df.empty:
                    return base_df
                base_df["TimeGenerated"] = pd.to_datetime(base_df["TimeGenerated"])
                other_df["TimeGenerated"] = pd.to_datetime(other_df["TimeGenerated"])
                base_df.sort_values(["AppRoleName", "TimeGenerated"], inplace=True)
                other_df.sort_values(["AppRoleName", "TimeGenerated"], inplace=True)
                merged_chunks = []
                for role, base_group in base_df.groupby("AppRoleName"):
                    other_group = other_df[other_df["AppRoleName"] == role]
                    if other_group.empty:
                        merged_chunks.append(base_group)
                        continue
                    overlapping = set(base_group.columns) & set(other_group.columns) - {"TimeGenerated", "AppRoleName"}
                    other_group = other_group.drop(columns=overlapping)
                    merged = pd.merge_asof(
                        base_group,
                        other_group,
                        on="TimeGenerated",
                        by="AppRoleName",
                        direction="nearest",
                        tolerance=Timedelta(tolerance)
                    )
                    merged_chunks.append(merged)
                return pd.concat(merged_chunks).sort_values("TimeGenerated")

            merged_logs = log_dict.get("AppRequests", pd.DataFrame())
            for table in ["AppExceptions", "AppTraces", "AppDependencies"]:
                merged_logs = merge_with_role_and_time(merged_logs, log_dict.get(table, pd.DataFrame()))

            if merged_logs.empty:
                return f"No logs found for app '{appName}' between {start_time} and {end_time}."

            if merged_logs.shape[0] > 30:
                merged_logs = merged_logs.sample(30)
                merged_logs.sort_values(["AppRoleName", "TimeGenerated"], inplace=True)

            lines = []
            for _, row in merged_logs.iterrows():
                summary = f"[{row['TimeGenerated']}] [{row['type']}] " + " | ".join(
                    f"{k}={row[k]}" for k in row.index if k not in ['TimeGenerated', 'type']
                )
                lines.append(summary)

            query_result = "\n".join(lines[:20] + lines[-20:])

            return f"Query result for '{appName}' between {start_time} and {end_time}:\n\n{query_result}"

        return [azure_log_analytics_query]
