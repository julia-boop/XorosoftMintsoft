import requests
import base64
import json

class XorosoftOrderClient:

    BASE_URL = "https://res.xorosoft.io"

    def __init__(self, api_key, api_secret):
        token = f"{api_key}:{api_secret}"
        self.auth_header = {
            "Authorization": f"Basic {base64.b64encode(token.encode()).decode()}"
        }

    def get_orders(self, status="released"):
        url = f"{self.BASE_URL}/api/xerp/wave/getwave?page=1"
        params = {"status": status}

        response = requests.get(url, headers=self.auth_header, params=params)
        response.raise_for_status()

        return response.json()
    

