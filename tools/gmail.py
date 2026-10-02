import os
import base64
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

CREDENTIALS_FILE = os.path.join(
    BASE_DIR,
    "credentials.json"
)

TOKEN_FILE = os.path.join(
    BASE_DIR,
    "token.json"
)


def get_gmail_service():

    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES
            )

            creds = flow.run_local_server(
                port=0
            )

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build(
        "gmail",
        "v1",
        credentials=creds
    )


def send_email(to, subject, body):

    if not to:
        return {
            "success": False,
            "error": "Recipient email is required."
        }

    if not subject:
        return {
            "success": False,
            "error": "Email subject is required."
        }

    if not body:
        return {
            "success": False,
            "error": "Email body is required."
        }

    try:

        service = get_gmail_service()

        message = MIMEText(body)

        message["to"] = to
        message["subject"] = subject

        encoded_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()

        result = service.users().messages().send(
            userId="me",
            body={
                "raw": encoded_message
            }
        ).execute()

        return {
            "success": True,
            "message": "Email sent successfully.",
            "message_id": result.get("id")
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }