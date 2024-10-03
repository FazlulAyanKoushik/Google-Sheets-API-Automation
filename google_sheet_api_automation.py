import json
from datetime import datetime

import pytz

from google.oauth2 import service_account
from googleapiclient.discovery import build

from featch_excel_id import extract_id_from_link

excel_url = "https://docs.google.com/spreadsheets/d/1voO7KrKWfHLRz9kT38h4VxQ277ClMu7C3fwEQX11UAE/edit?gid=1293238047#gid=1293238047"

# Set up credentials
credentials = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)

# Get the current time in UTC
utc_time = datetime.now(pytz.utc)

# Convert the UTC time to Bangladesh timezone (Asia/Dhaka)
bd_timezone = pytz.timezone('Asia/Dhaka')
current_date_time = utc_time.astimezone(bd_timezone).strftime("%Y-%m-%d %H:%M:%S")

spreadsheet_id = extract_id_from_link(excel_url)

service = build('sheets', 'v4', credentials=credentials)


def get_sheet_names():
    """
    Retrieves the names of all sheets in the Google Sheets document associated with the given spreadsheet ID.

    :return:
        A list of sheet names.
    """
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get('sheets', '')
    sheet_names_ = [sheet['properties']['title'] for sheet in sheets]
    return sheet_names_


sheet_names = get_sheet_names()
main_inventory_sheet_name = sheet_names[0]
transaction_registry_sheet_name = sheet_names[1]


# Helper function to retrieve all data from the sheet
def get_all_products_of_actual_inventory(sheet_name='Actual Inventory'):
    """
    Retrieves all products from the Actual Inventory in the Google Sheets document.

    :param sheet_name:
    :return:
        A list of lists representing the products and their details.
    """
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A:G"
    ).execute()
    return result.get('values', [])


def get_list_of_transaction_registry(sheet_name='Transaction Registry'):
    """
        Retrieves all products from the Transaction Registry in the Google Sheets document.

        :param sheet_name:
        :return:
            A list of lists representing the products and their details.
        """
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A:G"
    ).execute()
    return result.get('values', [])


def get_product_by_code(product_code):
    sheet_name = main_inventory_sheet_name
    products = get_all_products_of_actual_inventory(sheet_name)

    for row in products:
        product_code_ = row[0]
        if product_code == product_code_:
            product_details = {
                "product_code": row[0],
                "stock_quantity": row[1],
                "unitary_price": row[2],
                "actual_amount_in_dollars": row[3]
            }
            return json.dumps(product_details, indent=4)  # Return as a JSON string

    return json.dumps({"error": "Product not found"}, indent=4)


def add_new_transaction(
        product_code,
        type_of_transaction,
        quantity,
        payment_method,
):
    main_sheet = main_inventory_sheet_name
    registry_sheet = transaction_registry_sheet_name
    # Step 1: Check if the product exists in the "Actual Inventory" sheet.
    product_json = get_product_by_code(product_code)
    product_data = json.loads(product_json)

    if "error" in product_data:
        return f"Product {product_code} not found in {main_sheet}."

    # Step 2: Get the current list of transactions in the "Transaction Registry" sheet.
    products = get_list_of_transaction_registry(registry_sheet)

    # Extract product name from the product details if needed (assuming product[1] holds the product name).
    product_name = None
    if not product_name:
        for row in products:
            if row[1] == product_code:  # Assuming product_code is in the 2nd column of the Transaction Registry
                product_name = row[2]  # Assuming product_name is in the 3rd column
                break

    # Create a new row with the updated details, leaving quantity blank for now
    new_row = [
        current_date_time,  # Date and Time (blank)
        product_code,  # Product Code
        product_name,  # Product Name
        type_of_transaction,  # Type of Transaction (Income/Sale)
        quantity,  # Quantity
        "",  # Adjusted Quantity (blank)
        payment_method  # Payment Method
    ]

    # Step 4: Append the new row to the sheet.
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f'{registry_sheet}!A:G',  # The sheet range where the new row should be added
        body={'values': [new_row]},
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS'  # Automatically inserts the new row
    ).execute()

    return f"New transaction for product {product_code} added successfully with quantity updated."


def delete_product_by_code(product_code):
    registry_sheet = transaction_registry_sheet_name
    # Step 1: Get the list of transactions in the "Transaction Registry" sheet.
    transactions = get_list_of_transaction_registry(registry_sheet)

    # Step 2: Find the last occurrence of the product by product code
    last_row_to_delete = None
    for i, row in enumerate(transactions):
        if row[1] == product_code:  # Assuming the product code is in the second column
            last_row_to_delete = i  # Keep updating this index to track the last occurrence

    if last_row_to_delete is None:
        return f"Product {product_code} not found in {registry_sheet}."

    # Step 3: Prepare the batch update request to delete the last row
    requests = [{
        "deleteDimension": {
            "range": {
                "sheetId": get_sheet_id_by_name(registry_sheet),  # Get the sheet ID
                "dimension": "ROWS",
                "startIndex": last_row_to_delete,  # 0-based index of the row to delete
                "endIndex": last_row_to_delete + 1  # End index is non-inclusive, so +1
            }
        }
    }]

    # Step 4: Execute the batch update to remove the row
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": requests}
    ).execute()

    return f"Last occurrence of product {product_code} deleted successfully from {registry_sheet}."


# Function to get sheet ID by sheet name
def get_sheet_id_by_name(sheet_name):
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get('sheets', [])
    for sheet in sheets:
        if sheet['properties']['title'] == sheet_name:
            return sheet['properties']['sheetId']
    return None


# Helper function to clear a sheet
def clear_sheet(sheet_name):
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=f'{sheet_name}!A1:Z1000'
    ).execute()
