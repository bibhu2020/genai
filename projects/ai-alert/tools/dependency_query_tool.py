from datetime import datetime, timedelta
from typing import List, Literal
import pandas as pd
from pandas import Timedelta
from pydantic import BaseModel
from langchain.tools import tool
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.identity import AzureCliCredential
from logger.decorators import log_entry
from utils.config_loader import load_config

# Initialize credentials and Log Analytics client
credential = AzureCliCredential()
client = LogsQueryClient(credential)
config = load_config()

# =========================
# Tool 2: Dependency Failures
# =========================
class DependencyQueryArgs(BaseModel):
    appName: str
    incidentTime: datetime

@tool(args_schema=DependencyQueryArgs)
@log_entry
def get_dependency_failures(appName: str, incidentTime: datetime) -> str:
    """
    Detects dependency call failures (e.g., external APIs, databases) around incident time.

    Args:
        appName (str): Application name.
        incidentTime (datetime): Time of the incident.

    Returns:
        str: Summary of failing dependencies.
    """
    workspace_id = config["application"][appName]["log_analytics_workspace_id"]
    app_role_name = config["application"][appName]["app_role_name"]
    start_time = incidentTime - timedelta(minutes=10)
    end_time = incidentTime + timedelta(minutes=10)

    query = f"""
    AppDependencies
    | where TimeGenerated between (datetime({start_time.isoformat()}) .. datetime({end_time.isoformat()}))
    and AppRoleName contains "{app_role_name}"
    and Success == false
    | summarize failure_count = count() by Name, Target, ResultCode, AppRoleName
    """

    response = client.query_workspace(workspace_id, query, timespan=(start_time, end_time))
    if response.status != LogsQueryStatus.SUCCESS or not response.tables:
        return "No dependency failure data found."

    df = pd.DataFrame(response.tables[0].rows, columns=response.tables[0].columns)
    if df.empty:
        return "No failing dependencies detected."

    return df.to_string(index=False)