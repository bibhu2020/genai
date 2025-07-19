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
# Tool 3: Infrastructure Metrics (CPU, Memory, Disk)
# =========================
class InfraMetricArgs(BaseModel):
    appName: str
    incidentTime: datetime
    metric: Literal['cpu', 'memory', 'disk']

@tool(args_schema=InfraMetricArgs)
@log_entry
def get_infra_metrics(appName: str, incidentTime: datetime, metric: str) -> str:
    """
    Returns infrastructure metrics like CPU, Memory, or Disk usage around incident time.

    Args:
        appName (str): Application name.
        incidentTime (datetime): Incident time window.
        metric (str): One of 'cpu', 'memory', or 'disk'.

    Returns:
        str: Average values per 5-minute window.
    """
    workspace_id = config["application"][appName]["log_analytics_workspace_id"]
    start_time = incidentTime - timedelta(minutes=10)
    end_time = incidentTime + timedelta(minutes=10)

    metric_map = {
        "cpu": ("Processor", "% Processor Time"),
        "memory": ("Memory", "Available MBytes"),
        "disk": ("LogicalDisk", "% Free Space")
    }

    if metric not in metric_map:
        return f"Unsupported metric type: {metric}"

    object_name, counter_name = metric_map[metric]

    query = f"""
    Perf
    | where ObjectName == "{object_name}" and CounterName == "{counter_name}"
    | where TimeGenerated between (datetime({start_time.isoformat()}) .. datetime({end_time.isoformat()}))
    | summarize avg_value = avg(CounterValue) by bin(TimeGenerated, 5m)
    """

    response = client.query_workspace(workspace_id, query, timespan=(start_time, end_time))
    if response.status != LogsQueryStatus.SUCCESS or not response.tables:
        return f"No {metric} metric data available."

    df = pd.DataFrame(response.tables[0].rows, columns=response.tables[0].columns)
    if df.empty:
        return f"No data found for {metric} in the incident window."

    return df.to_string(index=False)