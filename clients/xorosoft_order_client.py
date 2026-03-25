import requests
import base64
import json
import pandas as ps

class XorosoftOrderClient:

    BASE_URL = "https://res.xorosoft.io"

    def __init__(self):
        api_key="d6e83420252b44e5a8d6c28cf8a1a74e"
        api_secret="5bce652dafc9404cb268de320904308e"

        token = f"{api_key}:{api_secret}"
        self.auth_header = {
            "Authorization": f"Basic {base64.b64encode(token.encode()).decode()}"
        }

    def get_waves(self, wave_id):
        url = f"{self.BASE_URL}/api/xerp/wave/getwave?wave_number={wave_id}&page=1"

        response = requests.get(url, headers=self.auth_header)
        response.raise_for_status()

        return response.json()
    
    def get_order_details(self, order_number):
        url = f"{self.BASE_URL}/api/xerp/salesorder/getsalesorder?order_number={order_number}"

        response = requests.get(url, headers=self.auth_header)
        response.raise_for_status()

        return response.json()
    
    # Cada item de la orden esta dentro de SoEstimateItemLineArr, array de {},
    # en el campo ItemNumber. Cantidad esta en el campo Qty 
    
    def get_asns(self):
        url = f'{self.BASE_URL}/api/xerp/asn/getasn?created_at_min=03/16/2026 12:44:27 PM&created_at_max=03/16/2026 12:44:29 PM'

        response = requests.get(url, headers=self.auth_header)
        response.raise_for_status()

        return response.json()
    
    # Array de Data [] -> AsnDetailData [] -> Detalle de cada item del ASN {}
    # Array de Data [] -> AsnHeaderData {} -> Detalle del ASN en si

    # SKU esta en el campo ItemNumber, Qty esta en BaseQtyToReceive

    
    

# try:
#     client = XorosoftOrderClient()

#     asns = client.get_asns()

#     # waves = client.get_waves("USA-W007006")
#     # order_data = waves["Data"]["OrderData"][0]
#     # order_number = order_data.get("OrderNumber")

#     # order = client.get_order_details(order_number)
#     # order_details = order["Data"][0]
#     # order_items = order_details["SoEstimateItemLineArr"]

#     # array = []

#     # for item in order_items:
#     #     item_sku = item.get("ItemNumber")
#     #     quantity = item.get("Qty")

#     #     array.append({
#     #         "Sku": item_sku,
#     #         "Quantity": quantity
#     #     })

#     # data = asns["Data"][0]
#     # asnitems = data.get("AsnDetailData")
#     # asninfo = data.get("AsnHeaderData")
#     # array = []

#     # for item in asnitems:
#     #     array.append({
#     #         "sku": item.get("ItemNumber"),
#     #         "quantity": item.get("BaseQtyToReceive")
#     #     })
    
#     # print(asninfo.get("AsnNumber"))
#     # print(asninfo.get("DeliveryDate"))
#     # print(array)
    
# except Exception as e:
#     print(e)


