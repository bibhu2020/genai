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
# Tool 4: Deployment History
# =========================
class DeploymentQueryArgs(BaseModel):
    appName: str
    incidentTime: datetime

@tool(args_schema=DeploymentQueryArgs)
@log_entry
def check_recent_deployments(appName: str, incidentTime: datetime) -> str:
    """
    Checks deployment activity in Azure within a time window.

    Args:
        appName (str): Application name.
        incidentTime (datetime): Time of the incident.

    Returns:
        str: Summary of deployment actions.
    """
    workspace_id = config["application"][appName]["log_analytics_workspace_id"]
    resource_group = config["application"][appName]["resource_group"]
    start_time = incidentTime - timedelta(minutes=10)
    end_time = incidentTime + timedelta(minutes=5)

    query = f"""
    AzureActivity
    | where ResourceGroup == "{resource_group}"
    | where OperationName contains "Deploy"
    | where TimeGenerated between (datetime({start_time.isoformat()}) .. datetime({end_time.isoformat()}))
    | project TimeGenerated, OperationName, Status, Caller
    """

    response = client.query_workspace(workspace_id, query, timespan=(start_time, end_time))
    if response.status != LogsQueryStatus.SUCCESS or not response.tables:
        return "No deployment history available."

    df = pd.DataFrame(response.tables[0].rows, columns=response.tables[0].columns)
    if df.empty:
        return "No deployments found around incident time."

    return df.to_string(index=False)