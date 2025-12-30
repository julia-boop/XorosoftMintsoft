import requests
import os
from dotenv import load_dotenv
load_dotenv()

class MintsoftOrderClient:

    BASE_URL = "https://api.mintsoft.co.uk"

    def __init__(self):
        self.base_url = "https://api.mintsoft.co.uk/api"
        self.username = os.getenv("MINTSOFT_USERNAME")
        self.password = os.getenv("MINTSOFT_PASSWORD")
        self.api_key = self.authenticate()

    def authenticate(self):
        url = f"{self.base_url}/Auth"
        payload = {
            "Username": self.username,
            "Password": self.password
        }

        response = requests.post(url, json=payload)

        if response.status_code != 200:
            raise Exception(f"Mintsoft Auth Failed: {response.status_code} - {response.text}")

        data = response.json()
        print("Mintsoft Auth Successful — API Key Acquired")
        return data

    def _headers(self):
        return {
            "ms-apikey": self.api_key,
            "Content-Type": "application/json"
        }

    def create_order(self, order_payload):
        url = f"{self.BASE_URL}/api/Order"
        headers = self._headers()
        r = requests.put(url, json=order_payload, headers=headers)
        r.raise_for_status()
        return r.json()
    
    def get_orders(self):
        url = f"{self.BASE_URL}/api/Order/List"
        params = {
            "ClientId": int(os.getenv("MINTSOFT_CLIENT_ID"))
        }
        response = requests.get(url, headers=self._headers(), params=params)
        print(response.json())
        response.raise_for_status()

        return response.json()
    
    
