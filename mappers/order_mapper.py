import os
from dotenv import load_dotenv

load_dotenv()


def map_xoro_order_to_mintsoft(order):
    order_data = order["OrderData"]    
    wave_data = order["WaveData"]      

    name = order_data.get("CustomerName", "") or ""
    first, last = (name.split(" ", 1) + [""])[:2]

    line_items = []

    allocations = wave_data.get("WaveDetailAllocationArr", [])
    for alloc in allocations:

        line_items.append({
            "SKU": alloc.get("ItemNumber"),
            "Quantity": alloc.get("QtyAllocated", 1),
            "WarehouseId": 3,
        })

    mintsoft_order = {
        "OrderNumber": order_data["OrderNumber"],
        "FirstName": first,
        "LastName": last,
        "Email": order_data.get("ShipToEmail", ""),
        "Phone": order_data.get("ShipToPhoneNumber", ""),
        "Address1": order_data.get("ShipToAddr", ""),
        "Town": order_data.get("ShipToCity", ""),
        "PostCode": order_data.get("ShipToZpCode", ""),
        "Country": order_data.get("ShipToCountryISO2", "US"),
        "WarehouseId": 3,
        "ClientId": os.getenv("MINTSOFT_CLIENT_ID"),
        "CourierServiceId":
            1036 if order_data.get("ShipServiceCode") == "UPS Ground"
            else 1006,

        "OrderItems": line_items
    }

    return mintsoft_order
