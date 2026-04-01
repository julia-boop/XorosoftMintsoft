import os
from dotenv import load_dotenv
import sys 
from datetime import datetime, timezone, timedelta

load_dotenv()

#Cambiar SKU, CHANNEL, CLIENT



def map_xoro_order_to_mintsoft(order_data, wave_data):      
    
    name = order_data.get("ShipToName", "") or ""
    
    first, last = (name.split(" ", 1) + [""])[:2]
    
    line_items = []
   # print(order_data["OrderNumber"][:2])
    if order_data["OrderNumber"][:2] == "DS": #Distinguir también para el warehouse 
        courrierId = 2543
        warehouseId = 5
    else:
        courrierId = 2547
        warehouseId = 3


    allocations = wave_data.get("WaveDetailAllocationArr", [])
    for alloc in allocations:
        
        line_items.append({
            "SKU": alloc.get("ItemNumber"),
            "Quantity": int(alloc.get("QtyAllocated")),
            "WarehouseId": warehouseId,

        })

    #Ver cual es el externalReferenceId: Traer external reference Id? ThirdPartyRefNo o otro
    #Chequear si el price se actualiza con el sku o es aparte, UnitPrice y Details en line_items
    #usa wholesale, ds ecommerce 
    
    despatch_date_vieja = order_data["DateToBeShipped"]
    dt = datetime.strptime(despatch_date_vieja, "%m/%d/%Y")
    despatch_date = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "Z"
    print(despatch_date_vieja, despatch_date)

    mintsoft_order = {
        "OrderNumber": order_data["OrderNumber"],
        "RequiredDespatchDate": despatch_date,
        "ChannelId": 55, #cambiar a 55
        "FirstName": first,
        "LastName": last,
        "Email": order_data.get("ShipToEmail", ""),
        "Phone": order_data.get("ShipToPhoneNumber", ""),
        "Address1": order_data.get("ShipToAddr", ""),
        "Town": order_data.get("ShipToCity", ""),
        "County": order_data.get("ShipToState", ""),
        "PostCode": order_data.get("ShipToZpCode", ""),
        "Country": order_data.get("ShipToCountryISO2", "US"),
        "WarehouseId": warehouseId,
        "ClientId": 4, #os.getenv("MINTSOFT_CLIENT_ID"),
        "CourierServiceId": courrierId,
        "OrderItems": line_items
    }

    return mintsoft_order
