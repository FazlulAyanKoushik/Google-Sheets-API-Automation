from google.oauth2 import service_account
from googleapiclient.discovery import build
from featch_excel_id import extract_id_from_link

excel_url = "https://docs.google.com/spreadsheets/d/1voO7KrKWfHLRz9kT38h4VxQ277ClMu7C3fwEQX11UAE/edit?gid=1293238047#gid=1293238047"

# Set up credentials
credentials = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)

print(credentials)


# Helper function to retrieve all data from the sheet
def get_all_products(a_service, a_spreadsheet_id, sheet_name='Sheet1'):
    result = a_service.spreadsheets().values().get(
        spreadsheetId=a_spreadsheet_id,
        range="Class Data!A:G"
    ).execute()
    return result.get('values', [])


# Function to get a product by code or name
def get_product_by_code_or_name(service, spreadsheet_id, search_value, sheet_name='Sheet1'):
    products = get_all_products(service, spreadsheet_id, sheet_name)
    for row in products:
        product_code, product_name = row[0], row[1]
        if search_value == product_code or search_value == product_name:
            return row
    return None


# Function to update product details
def update_product_by_code(service, spreadsheet_id, product_code, updated_details, sheet_name='Sheet1'):
    products = get_all_products(service, spreadsheet_id, sheet_name)
    for i, row in enumerate(products):
        if row[0] == product_code:
            # Assuming updated_details contains [transaction_type, quantity, payment_method]
            products[i][2] = updated_details[0]  # Type of transaction
            products[i][3] = updated_details[1]  # Quantity
            products[i][4] = updated_details[2]  # Payment method

            # Write back the updated products list to the sheet
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f'{sheet_name}!A1:F{len(products)}',
                body={'values': products},
                valueInputOption='RAW'
            ).execute()
            return f"Product {product_code} updated successfully."
    return f"Product {product_code} not found."


# Function to delete a product by product code
def delete_product_by_code(service, spreadsheet_id, product_code, sheet_name='Sheet1'):
    products = get_all_products(service, spreadsheet_id, sheet_name)
    for i, row in enumerate(products):
        if row[0] == product_code:
            del products[i]

            # Clear the sheet and write back the remaining products
            clear_sheet(service, spreadsheet_id, sheet_name)
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f'{sheet_name}!A1:F{len(products)}',
                body={'values': products},
                valueInputOption='RAW'
            ).execute()
            return f"Product {product_code} deleted successfully."
    return f"Product {product_code} not found."


# Helper function to clear a sheet
def clear_sheet(service, spreadsheet_id, sheet_name='Sheet1'):
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=f'{sheet_name}!A1:Z1000'
    ).execute()


# Example usage
if __name__ == '__main__':
    # Extract the spreadsheet ID from the provided URL
    spreadsheet_id = extract_id_from_link(excel_url)

    print(spreadsheet_id)
    # return true if both string is same
    if spreadsheet_id == "1voO7KrKWfHLRz9kT38h4VxQ277ClMu7C3fwEQX11UAE":
        print("True")

    # Create the Sheets API service
    service = build('sheets', 'v4', credentials=credentials)

    # Get the list of products
    all_products = get_all_products(service, spreadsheet_id)
    print("All Products:", all_products)

    # # Get a specific product by code or name
    # product = get_product_by_code_or_name(service, spreadsheet_id, "P001")
    # print("Product Found:", product)
    #
    # # Update a product by code
    # update_message = update_product_by_code(service, spreadsheet_id, "P001", ["Sale", "100", "Credit Card"])
    # print(update_message)
    #
    # # Delete a product by code
    # delete_message = delete_product_by_code(service, spreadsheet_id, "P001")
    # print(delete_message)
