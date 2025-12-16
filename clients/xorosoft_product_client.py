import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

class XoroSoftProductClient:
    def __init__(self):
        self.api_key = os.getenv("XORO_API_KEY")
        self.api_secret = os.getenv("XORO_API_SECRET")
        self.base_url = "https://res.xorosoft.io"

    def _headers(self):
        token = f"{self.api_key}:{self.api_secret}"
        encoded = base64.b64encode(token.encode()).decode()

        return {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json"
        }

    def get_all_items( self, created_at_min=None, created_at_max=None, updated_at_min=None, updated_at_max=None):
        params = {}

        if created_at_min:
            params["created_at_min"] = created_at_min
        if created_at_max:
            params["created_at_max"] = created_at_max
        if updated_at_min:
            params["updated_at_min"] = updated_at_min
        if updated_at_max:
            params["updated_at_max"] = updated_at_max

        url = f"{self.base_url}/api/xerp/product/item/getitem"
        response = requests.get(url, headers=self._headers(), params=params)

        if response.status_code != 200:
            raise Exception(f"Error fetching items: {response.text}")

        data = response.json().get("Data", [])
        return data