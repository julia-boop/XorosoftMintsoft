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

    
    


