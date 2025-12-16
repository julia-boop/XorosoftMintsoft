import os
from dotenv import load_dotenv
load_dotenv()

def map_xoro_item_to_mintsoft(item):
    return {
        "SKU": item.get("ItemNumber") or "",
        "Name": item.get("Title") or item.get("Description") or "",
        "Description": item.get("Description") or "",
        "UPC": item.get("ItemUpc", ""),
        "Weight": item.get("Weight") or 0,
        "Price": item.get("StandardUnitPrice") or 0,
        "CostPrice": item.get("StandardUnitCost") or 0,
        "ImageURL": item.get("ImagePath") or "",
        "ClientId": int(os.getenv("MINTSOFT_CLIENT_ID"))
    }
