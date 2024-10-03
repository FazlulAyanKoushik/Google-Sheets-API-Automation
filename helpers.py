from google_sheet_api_automation import (
    get_product_by_code,
    add_new_transaction,
    delete_product_by_code
)

functions = [
    {
        "name": "get_product_by_code",
        "description": "Retrieve product details using the product code from the main inventory sheet.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_code": {"type": "string", "description": "The product code to search for in the inventory."}
            },
            "required": ["product_code"]
        }
    },
    {
        "name": "add_new_transaction",
        "description": "Add a new transaction to the transaction registry for a product.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_code": {"type": "string", "description": "The product code for which the transaction is being recorded."},
                "type_of_transaction": {"type": "string", "description": "Type of transaction, e.g., 'Income' or 'Sale'."},
                "quantity": {"type": "number", "description": "The quantity of the product involved in the transaction."},
                "payment_method": {"type": "string", "description": "The payment method used for the transaction, e.g., 'Cash', 'Card'."}
            },
            "required": ["product_code", "type_of_transaction", "quantity", "payment_method"]
        }
    },
    {
        "name": "delete_product_by_code",
        "description": "Delete the last occurrence of a product by product code from the transaction registry sheet.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_code": {"type": "string", "description": "The product code to delete from the transaction registry."}
            },
            "required": ["product_code"]
        }
    }
]

available_functions = {
    "get_product_by_code": get_product_by_code,
    "add_new_transaction": add_new_transaction,
    "delete_product_by_code": delete_product_by_code
}
