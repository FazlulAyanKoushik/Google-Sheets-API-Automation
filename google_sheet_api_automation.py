from google.oauth2 import service_account
from googleapiclient.discovery import build
from featch_excel_id import extract_id_from_link
from datetime import datetime, timezone
import pytz

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


# Helper function to retrieve all data from the sheet
def get_all_products_of_actual_inventory(service, spreadsheet_id, sheet_name='Actual Inventory'):
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A:G"
    ).execute()
    return result.get('values', [])


def get_list_of_transaction_registry(service, spreadsheet_id, sheet_name='Transaction Registry'):
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A:G"
    ).execute()
    return result.get('values', [])


# Function to get a product by code or name
def get_product_by_code_or_name(service, spreadsheet_id, search_value, sheet_name='Sheet1'):
    products = get_all_products_of_actual_inventory(service, spreadsheet_id, sheet_name)
    for row in products:
        product_code, product_name = row[0], row[1]
        if search_value == product_code or search_value == product_name:
            return row
    return None


# Function to update product details
def update_product_by_code(
        service,
        spreadsheet_id,
        product_code,
        type_of_transaction,
        quantity,
        payment_method,
        main_sheet='Actual Inventory',
        registry_sheet='Transaction Registry'
):
    # Step 1: Check if the product exists in the "Actual Inventory" sheet.
    product = get_product_by_code_or_name(service, spreadsheet_id, product_code, main_sheet)
    if not product:
        return f"Product {product_code} not found in {main_sheet}."

    # Step 2: Get the current list of transactions in the "Transaction Registry" sheet.
    products = get_list_of_transaction_registry(service, spreadsheet_id, registry_sheet)

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


# Function to delete the last occurrence of a product by product code
def delete_product_by_code(service, spreadsheet_id, product_code, registry_sheet='Transaction Registry'):
    # Step 1: Get the list of transactions in the "Transaction Registry" sheet.
    transactions = get_list_of_transaction_registry(service, spreadsheet_id, registry_sheet)

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
                "sheetId": get_sheet_id_by_name(service, spreadsheet_id, registry_sheet),  # Get the sheet ID
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
def get_sheet_id_by_name(service, spreadsheet_id, sheet_name):
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get('sheets', [])
    for sheet in sheets:
        if sheet['properties']['title'] == sheet_name:
            return sheet['properties']['sheetId']
    return None


# Helper function to clear a sheet
def clear_sheet(service, spreadsheet_id, sheet_name):
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=f'{sheet_name}!A1:Z1000'
    ).execute()


def get_sheet_names(service, spreadsheet_id):
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get('sheets', '')
    sheet_names = [sheet['properties']['title'] for sheet in sheets]
    return sheet_names


if __name__ == '__main__':
    # Extract the spreadsheet ID from the provided URL
    spreadsheet_id = extract_id_from_link(excel_url)

    # Create the Sheets API service
    service = build('sheets', 'v4', credentials=credentials)

    # Get sheet names
    sheet_names = get_sheet_names(service, spreadsheet_id)
    main_inventory_sheet_name = sheet_names[0]
    transaction_registry_sheet_name = sheet_names[1]

    # Get the list of products in the "Actual Inventory" sheet
    # all_products = get_all_products_of_actual_inventory(service, spreadsheet_id, main_inventory_sheet_name)
    # print("All Products:", all_products)

    # Get the list of transactions in the "Transaction Registry" sheet
    # all_transactions = get_list_of_transaction_registry(service, spreadsheet_id, transaction_registry_sheet_name)
    # print("All Transactions:", all_transactions)

    # # Get a specific product by code from the "Actual Inventory" sheet
    # product = get_product_by_code_or_name(
    #     service,
    #     spreadsheet_id,
    #     "1111",
    #     main_inventory_sheet_name
    # )
    # print("Product:", product)

    # ====================================================
    # Update a product by code section
    # ====================================================
    update_message = update_product_by_code(
        service=service,
        spreadsheet_id=spreadsheet_id,
        product_code="1111",
        type_of_transaction="Sale",
        quantity=5,
        payment_method="Cash",
        main_sheet=main_inventory_sheet_name,
        registry_sheet=transaction_registry_sheet_name
    )
    print(update_message)
    #
    # # Delete a product by code
    # delete_message = delete_product_by_code(
    #     service,
    #     spreadsheet_id,
    #     "2222",
    #     registry_sheet="Transaction Registry"
    # )

    # print(delete_message)
