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
# Tool 1: Recent Alert Snapshot
# =========================
class AlertQueryArgs(BaseModel):
    appName: str
    incidentTime: datetime

@tool(args_schema=AlertQueryArgs)
@log_entry
def get_recent_alerts(appName: str, incidentTime: datetime) -> str:
    """
    Identifies recent Azure Monitor alerts triggered around a specified incident time.

    Args:
        appName (str): Name of the application.
        incidentTime (datetime): Time the incident was detected.

    Returns:
        str: Summary of triggered alerts (if any) with severity and timestamps.
    """
    workspace_id = config["application"][appName]["log_analytics_workspace_id"]
    start_time = incidentTime - timedelta(minutes=30)
    end_time = incidentTime + timedelta(minutes=5)

    query = f"""
    AlertsManagementAlerts
    | where TimeGenerated between (datetime({start_time.isoformat()}) .. datetime({end_time.isoformat()}))
    | where MonitorCondition == "Fired"
    | summarize count() by AlertRule, Severity, Description, TimeGenerated
    """

    response = client.query_workspace(workspace_id, query, timespan=(start_time, end_time))
    if response.status != LogsQueryStatus.SUCCESS or not response.tables:
        return "No recent alert data found."

    df = pd.DataFrame(response.tables[0].rows, columns=response.tables[0].columns)
    if df.empty:
        return "No triggered alerts found in the selected time window."

    return df.to_string(index=False)
