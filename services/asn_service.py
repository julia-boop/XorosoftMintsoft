import sys
import os
import json
from datetime import datetime, timezone
from clients.xorosoft_order_client import XorosoftOrderClient
from clients.mintsoft_order_client import MintsoftOrderClient
from clients.mintsoft_product_client import MintsoftProductClient

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

FMT = "%m/%d/%Y %I:%M:%S %p"

class AsnSyncService:

    def __init__(self):
        self.xoro = XorosoftOrderClient()
        self.mint_o = MintsoftOrderClient()
        self.mint_p = MintsoftProductClient()

    def check_missing_mint_asns(self):
        # Traigo ASNs de Mint y guardo el POReference
        
        params = {
            "ClientId": 4
        }

        mintsoft_asns = self.mint_o.get_asns(params)
        current_mint_asns = []
        for asn in mintsoft_asns:
            POReference = asn.get("POReference")
            current_mint_asns.append(POReference)

        # Traigo ASNs de Xoro y guardo el listado a recorrer
        current_xoro_asns = []
        xoro_asn_data = self.xoro.get_asns()
        xoro_asns = xoro_asn_data["Data"]

        # Recorro array y almaceno los POReference
        for asn in xoro_asns:
            asninfo = asn.get("AsnHeaderData")
            POReference = asninfo.get("AsnNumber")

            current_xoro_asns.append(POReference)
        
        # Comparo listado para ver faltantes en Mintsoft
        missing_asns = set(current_xoro_asns) - set(current_mint_asns)

        # Almaceno la info de los ASNs a crear en Mintsoft, es el Data de Xorosoft pero para los ASNs que importan
        asns_to_sync = [
            asn for asn in xoro_asns 
            if asn.get("AsnHeaderData", {}).get("AsnNumber") in missing_asns
        ]

        return asns_to_sync
    
    def create_mint_asns(self, asns_to_sync: list):
        for asn in asns_to_sync:
            asn_info = asn.get("AsnHeaderData") # Info del ASN

            strip_date = asn_info.get("DeliveryDate").strip()
            parsed_date = datetime.strptime(strip_date, "%m/%d/%Y")
            delivery_date = parsed_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")

            asn_items = asn.get("AsnDetailData") # Info de items
            asn_item_details = []

            for item in asn_items:
                qty_to_int = int(item.get("BaseQtyToReceive"))

                asn_item_details.append({
                    "ProductId": self.mint_p.get_product_id(item.get("ItemNumber")),
                    # "SKU": item.get("ItemNumber"),
                    "Quantity": qty_to_int,
                })

            asn_upload_details = {
                "WarehouseId": 3, # Siempre 3 porque va a General Wholesale
                "POReference": "TEST-Xoro-ASN", #AsnNumber
                "Supplier": "XoroSoft Migration",
                "EstimatedDelivery": delivery_date, # DeliveryDate
                "GoodsInType": "Carton", # Carton
                "Quantity": 1, # Cantidad total de items, cantidad de items distintos o 1?
                "ClientId": 4, # 4 para Holiday Company
                "Items": asn_item_details
            }

            print(asn_upload_details)

            response = self.mint_o.create_asn(asn_upload_details)
            response.raise_for_status()
            
            return response
    
    def update_xoro_asn_status(self):
        
        # Consultamos ordenes de Mintsoft en Status COMPLETED
        params_mint = {
            "ClientId": 4,
            "StatusId": 6 # Status Completed
        }

        mintsoft_completed_asns = self.mint_o.get_asns(params_mint)
        current_mint_asns = []

        for asn in mintsoft_completed_asns:
            POReference = asn.get("POReference")
            current_mint_asns.append(POReference)

        # Consultamos ordenes de Xorosoft en Status COMPLETED
        params_xoro = {
            "CreatedAtMin": "03/30/2026 07:47:27 PM",
            "StatusId": "Closed"
        }

        current_xoro_asns = []
        xoro_asn_data = self.xoro.get_asns(params_xoro)
        xoro_asns = xoro_asn_data["Data"]

        for asn in xoro_asns:
            asn_header_data = asn.get("AsnHeaderData")

            asn_info = {
                "POReference": asn_header_data.get("AsnNumber"),
                "Status": asn_header_data.get("StatusName")
            }

            current_xoro_asns.append(asn_info)
        
        xoro_asns_to_update = set(current_mint_asns) - set(current_xoro_asns)

        # Recibir esos ASNs
            # Body {
                # "AsnHeaderData":{
                    # "AsnNumber":"MAIN-A000330",
                    # "CloseASN":false
                    # },
                    # "AsnDetailLocationData":[
                    # {
                    # "ItemNumber":"BC",
                    # "PONumber":"MAIN-P000538",
                    # "ReceiveLocationName":"MAIN WAREHOUSE - LOCATION-3PL",
                    # "QtyReceived":10
                    # }
                    # ]}

        # Cerrar esos ASNs
            # Body {
                # "AsnHeaderData":{
                #     "AsnNumber":"MAIN-A000330"
                #     }
                # }




        

        
        
    

# try:
#     client = AsnSyncService()
#     asns_to_sync = client.check_missing_mint_asns()

#     print("Sincronizando ASNs")
#     print(asns_to_sync)
#     response = client.create_mint_asns(asns_to_sync)
#     print(response.text)

# except Exception as e:
#     print (e)


   