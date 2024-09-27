import os.path
from google.oauth2 import service_account

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "1voO7KrKWfHLRz9kT38h4VxQ277ClMu7C3fwEQX11UAE"
SAMPLE_RANGE_NAME = "Class Data!A:G"


def main():
    credentials = None
    if os.path.exists("token.json"):
        print("Found token.json")
        credentials = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    if not credentials or not credentials.valid:
        print("No valid credentials found.")
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            print("Fetching new credentials")
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )
            print("=" * 30)
            print(flow)
            print("=" * 30)
            credentials = flow.run_local_server(port=0)
            print("=" * 30)
            print(credentials)
            print("=" * 30)

        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    try:
        service = build("sheets", "v4", credentials=credentials)
        sheets = service.spreadsheets()

        result = sheets.values().get(spreadsheetId=SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()
        print("=" * 30)
        print(result)
        print("=" * 30)
        values = result.get("values", [])
        print("=" * 30)
        print(values)
        print("=" * 30)
    except:
        pass


if __name__ == "__main__":
    main()
