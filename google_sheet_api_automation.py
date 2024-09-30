from google.oauth2 import service_account
from googleapiclient.discovery import build
from featch_excel_id import extract_id_from_link
from datetime import datetime, timezone

excel_url = "https://docs.google.com/spreadsheets/d/1voO7KrKWfHLRz9kT38h4VxQ277ClMu7C3fwEQX11UAE/edit?gid=1293238047#gid=1293238047"

# Set up credentials
credentials = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)


current_time = str(datetime.now(timezone.utc))


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
        current_time,  # Date and Time (blank)
        product_code,  # Product Code
        product_name,  # Product Name
        type_of_transaction,  # Type of Transaction (Income/Sale)
        quantity,  # Quantity (Initially blank)
        "",  # Adjusted Quantity (blank)
        payment_method  # Payment Method
    ]

    # Step 4: Append the new row to the sheet (with blank quantity).
    products.append(new_row)

    # Step 5: Write the updated products list back to the sheet (initially without quantity).
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f'{registry_sheet}!A1:G{len(products)}',  # Adjust range to include all rows
        body={'values': products},
        valueInputOption='RAW'
    ).execute()

    # Step 6: Get the row index of the newly added row (which is the last row in the sheet).
    new_row_index = len(products)

    # Step 7: Now update the quantity in the newly added row.
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f'{registry_sheet}!E{new_row_index}',  # Update only the quantity field in the new row (Column E)
        body={'values': [[quantity]]},  # Add the actual quantity
        valueInputOption='RAW'
    ).execute()

    return f"New transaction for product {product_code} added successfully with quantity updated."


# Function to delete a product by product code
# def delete_product_by_code(service, spreadsheet_id, product_code, sheet_name='Sheet1'):
#     products = get_all_products(service, spreadsheet_id, sheet_name)
#     for i, row in enumerate(products):
#         if row[0] == product_code:
#             del products[i]
#
#             # Clear the sheet and write back the remaining products
#             clear_sheet(service, spreadsheet_id, sheet_name)
#             service.spreadsheets().values().update(
#                 spreadsheetId=spreadsheet_id,
#                 range=f'{sheet_name}!A1:F{len(products)}',
#                 body={'values': products},
#                 valueInputOption='RAW'
#             ).execute()
#             return f"Product {product_code} deleted successfully."
#     return f"Product {product_code} not found."


# Helper function to clear a sheet
def clear_sheet(service, spreadsheet_id, sheet_name='Sheet1'):
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

    # Get the list of products
    # all_products = get_all_products(service, spreadsheet_id, main_inventory_sheet_name)
    # print("All Products:", all_products)

    # # Get a specific product by code or name
    # product = get_product_by_code_or_name(service, spreadsheet_id, "1111", main_inventory_sheet_name)

    # ====================================================
    # Update a product by code section
    # ====================================================
    update_message = update_product_by_code(
        service=service,
        spreadsheet_id=spreadsheet_id,
        product_code="1111",
        type_of_transaction="Sale",
        quantity=10,
        payment_method="Cash",
        main_sheet=main_inventory_sheet_name,
        registry_sheet=transaction_registry_sheet_name
    )
    print(update_message)
    #
    # # Delete a product by code
    # delete_message = delete_product_by_code(service, spreadsheet_id, "P001")
    # print(delete_message)
