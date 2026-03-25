import sys
import os
import json
from datetime import datetime, timezone
from clients.xorosoft_order_client import XorosoftOrderClient
from clients.mintsoft_order_client import MintsoftOrderClient
from clients.mintsoft_product_client import MintsoftProductClient
from mappers.order_mapper import map_xoro_order_to_mintsoft
from loggers.order_logger import order_logger
from utils.datetime_util import iso_to_xorosoft, xorosoft_to_iso

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

FMT = "%m/%d/%Y %I:%M:%S %p"

STATE_DIR = os.path.join(ROOT, "state")
STATE_FILE = os.path.join(STATE_DIR, "sync_state.json")
os.makedirs(STATE_DIR, exist_ok=True)


class AsnSyncService:

    def __init__(self):
        self.xoro = XorosoftOrderClient()
        self.mint_o = MintsoftOrderClient()
        self.mint_p = MintsoftProductClient()

    def _load_asn_sync_state(self):
        if not os.path.exists(STATE_FILE):
            return {
                "orders": {
                    "created_at": None,
                    "updated_at": None
                }
            }

        with open(STATE_FILE, "r") as f:
            return json.load(f)

    def _save_asn_sync_state(self, created_at=None, updated_at=None):
        state = self._load_order_sync_state()
        state.setdefault("orders", {})

        if created_at:
            state["orders"]["created_at"] = created_at
        if updated_at:
            state["orders"]["updated_at"] = updated_at

        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=4)

    def check_missing_mint_asns(self):
        # Traigo ASNs de Mint y guardo el POReference
        mintsoft_asns = self.mint_o.get_asns()
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

        print("Estos son los ASNs pendientes de migrar de XoroSoft a Mintsoft")
        print(missing_asns)

        # Almaceno la info de los ASNs a crear en Mintsoft, es el Data de Xorosoft pero para los ASNs que importan
        asns_to_sync = [
            asn for asn in xoro_asns 
            if asn.get("AsnHeaderData", {}).get("AsnNumber") in missing_asns
        ]

        return asns_to_sync
    
    def sync_asns(self, data: list):
        asns_to_sync = data

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
        
    

try:
    client = AsnSyncService()
    asns_to_sync = client.check_missing_mint_asns()

    print("Sincronizando ASNs")
    print(asns_to_sync)
    response = client.sync_asns(asns_to_sync)
    print(response.text)


    

except Exception as e:
    print (e)


   