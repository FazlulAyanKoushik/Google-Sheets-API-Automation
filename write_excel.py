from google.oauth2 import service_account
from googleapiclient.discovery import build

from featch_excel_id import extract_id_from_link

# Set up credentials
credentials = service_account.Credentials.from_service_account_file(
    'trip-care-413400-f6b3ee3249da.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)


def upload_data_in_excel(excel_url, location_name, cleaning_list):
    # Extract the spreadsheet ID from the provided URL
    spreadsheet_id = extract_id_from_link(excel_url)

    # Create the Sheets API service
    service = build('sheets', 'v4', credentials=credentials)

    another_list = [i for i in cleaning_list if "edited" not in i]
    range_location = f"A1:B{len(another_list) + 2}"
    values_location = [[location_name], ["Cleaning Dates & Checkouts", "House"]]
    values_location.extend(another_list)

    # Define the range to clear
    clear_range = "A1:Z1000"  # Adjust the range as necessary to cover all possible data

    try:
        # Clear the specified range
        clear_request = service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=clear_range,
            body={}
        )
        clear_response = clear_request.execute()
        print("Cleared existing data")

        # Build the request to update values
        update_request = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_location,
            body={'values': values_location},
            valueInputOption='RAW'  # Use 'RAW' for plain text, 'USER_ENTERED' for formulas and formatting
        )
        update_response = update_request.execute()
        print("Data uploaded successfully")
        return "okay"

    except Exception as e:
        print(f"Problem uploading: {e}")
        return "problem"


def clear_sheet(service, spreadsheet_id, sheet_name):
    clear_range = f'{sheet_name}'
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=clear_range,
        body={}
    ).execute()


# Example usage
# upload_data_in_excel('your_excel_url_here', 'Sample Location', [['2023-01-01', 'House A'], ['2023-01-02', 'House B']])
def upload_data_in_excel_checkInOut(excel_url, data):
    try:
        # Extract the spreadsheet ID from the provided URL
        spreadsheet_id = extract_id_from_link(excel_url)

        # Create the Sheets API service
        service = build('sheets', 'v4', credentials=credentials)

        # The ID of the sheet where you want to append data
        sheet_id = 0  # Assuming the first sheet; adjust if needed

        clear_sheet(service, spreadsheet_id, "Sheet1")

        # Prepare the body for appending data
        body = {
            'values': data
        }

        # Append data to the sheet
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range='Sheet1',  # Adjust the range if needed
            valueInputOption='RAW',
            body=body
        ).execute()

        print(f"{result.get('updates').get('updatedCells')} cells appended.")
        # Now apply formatting to location names
        apply_formatting_to_location_names(service, spreadsheet_id, data)
        return "okay"

    except:
        print("Problem problem")
        return "wrong"


def apply_formatting_to_location_names(service, spreadsheet_id, data):
    requests = []

    for i, row in enumerate(data):
        if len(row) == 1:
            if row[0].startswith("Location"):
                requests.append({
                    "repeatCell": {
                        "range": {
                            "sheetId": 0,  # Assuming the first sheet; adjust if needed
                            "startRowIndex": i,
                            "endRowIndex": i + 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": 1
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "textFormat": {
                                    "fontSize": 14,
                                    "bold": True
                                }
                            }
                        },
                        "fields": "userEnteredFormat.textFormat"
                    }
                })
            elif row[0].startswith("House"):
                requests.append({
                    "repeatCell": {
                        "range": {
                            "sheetId": 0,  # Assuming the first sheet; adjust if needed
                            "startRowIndex": i,
                            "endRowIndex": i + 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": 1
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "textFormat": {
                                    "fontSize": 12,
                                    "bold": True
                                }
                            }
                        },
                        "fields": "userEnteredFormat.textFormat"
                    }
                })

    body = {
        'requests': requests
    }

    if requests:
        response = service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()
        print(f"{response.get('totalUpdatedCells')} cells updated with formatting.")
