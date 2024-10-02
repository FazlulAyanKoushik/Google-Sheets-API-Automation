# Google Spreadsheets API

This is a simple example of how to use the Google Spreadsheets API.

## Setup

1. Go to the [Google Developers Console](https://console.developers.google.com/).
2. Create a new project.
3. Enable the Google Drive API.
4. Create credentials for a service account.
5. Download the JSON file.
6. Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of the JSON file.
7. Share the Google Sheet with the service account email address.
8. Install the required libraries:

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

or 

```bash
pip install -r requirements.txt
```

## Required file
add you credentials file in the root directory of the project and rename it to `credentials.json`

## Usage

```bash
python google_sheet_api_automation.py
```