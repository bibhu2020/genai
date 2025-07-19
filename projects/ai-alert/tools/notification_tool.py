import requests
import os
from typing import List
from langchain.tools import tool
from logger.decorators import log_entry
from pydantic import BaseModel
from utils.config_loader import load_config
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ConfigLoader:
    def __init__(self):
        print("Loading config...")
        self.config = load_config()

    def __getitem__(self, key):
        return self.config[key]
    
class NotificationArgs(BaseModel):
    appName: str
    incidentTime: str  # consider datetime if ISO format is used
    severity: str
    result: str


class NotificationTool:
    """
    A tool for notifying the SRE team with the incident analysis report.
    This tool is used to email and create incident in the IcM incident management system.

    Args:
        appName (str): application name.
        incidentTime (str): time when the incident occured in the application.
        severity (str): severity of the incident.
        result (str): result of the incident analysis.

    Returns:
        str: confirmation of the notification.
    """
    def __init__(self):
        self.notification_tool_list = self._setup_tools()
        self.config = ConfigLoader()

    def _setup_tools(self) -> List:
        """Setup all tools for the notification tool"""
        @tool(args_schema=NotificationArgs)
        @log_entry
        def notify_by_email(appName: str, incidentTime: str, severity: str, result: str) -> str:
            """
                Notifying the SRE team by emailing the incident analysis report.

                Args:
                    appName (str): application name.
                    incidentTime (str): time when the incident occured in the application.
                    severity (str): severity of the incident.
                    result (str): result of the incident analysis.

                Returns:
                    str: confirmation of the notification.
            """
            EMAIL_API_URL = "https://gdcwebopsemail.azurewebsites.net/key/api/emailhtml"
            EMAIL_SERVICE_API_KEY = os.getenv("EMAIL_SERVICE_API_KEY")
            email_to_list = self.config["application"][appName]["email_to"]
            email_from = "DoNotReply@gdcwebopsservice.microsoft.com"
            email_subject = f"Incident Analysis Report for {appName} at {incidentTime}"
            email_body = f"""
                <h2>Incident Analysis from LLM</h2>
                <p><b>Incident Time:</b> {incidentTime}</p>
                <p><b>Severity:</b> {severity}</p>
                <pre>{result}</pre>
            """
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"ApiKey {EMAIL_SERVICE_API_KEY}"
            }

            # Split recipients by semicolon and trim
            recipients = [email.strip() for email in email_to_list.split(';') if email.strip()]
            success_count = 0
            failure_list = []

            for recipient in recipients:
                payload = {
                    "emailTo": recipient,
                    "emailFrom": email_from,
                    "emailSubject": email_subject,
                    "emailBody": email_body
                }
                try:
                    resp = requests.post(EMAIL_API_URL, json=payload, headers=headers)
                    if resp.ok:
                        print(f"Notification sent to {recipient}")
                        success_count += 1
                    else:
                        print(f"Failed to send to {recipient}: {resp.status_code} - {resp.text}")
                        failure_list.append(recipient)
                except Exception as e:
                    print(f"Exception while sending to {recipient}: {e}")
                    failure_list.append(recipient)

            return f"Notification sent to {success_count} recipients. Failed for: {', '.join(failure_list)}" if failure_list else f"All notifications sent successfully for {appName}."

        return [notify_by_email]