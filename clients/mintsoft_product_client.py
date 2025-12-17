import os
import requests
from dotenv import load_dotenv

load_dotenv()

class MintsoftProductClient:
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
    
    def get_products_updated_since(self, since, page=1, limit=100):
        url = f"{self.base_url}/Product/List"
        params = {
            "PageNo": page,
            "Limit": limit,
            "ClientId": os.getenv("MINTSOFT_CLIENT_ID"),
            "SinceLastUpdated": since
        }
        response = requests.get(url, headers=self._headers(), params=params)

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    def create_product(self, product_json):
        url = f"{self.base_url}/Product"
        response = requests.put(url, headers=self._headers(), json=product_json)

        if response.status_code not in (200, 201):
            raise Exception(f"Error creating product: {response.status_code} - {response.text}")


        return response.json()

    def get_all_products(self):
        all_products = []
        page = 1
        limit = 100

        while True:
            url = f"{self.base_url}/Product/List"
            params = {
                "PageNo": page,
                "Limit": limit,
                "ClientId": os.getenv("MINTSOFT_CLIENT_ID")
            }

            response = requests.get(url, headers=self._headers(), params=params)

            if response.status_code != 200:
                print("STATUS:", response.status_code)
                print("RESPONSE:", response.text)
                raise Exception("Error fetching products from Mintsoft")

            batch = response.json()

            if not batch:
                break

            all_products.extend(batch)
            print(f"Fetched page {page}: {len(batch)} products")
            page += 1

        print(f"Total Mintsoft products fetched: {len(all_products)}")
        return all_products

    def update_product(self, product_id, payload):
        payload = dict(payload)  
        payload["ID"] = product_id

        url = f"{self.base_url}/Product"
        response = requests.post(url, headers=self._headers(), json=payload)

        if response.status_code not in (200, 201):
            raise Exception(
                f"Error updating Mintsoft product {product_id}: "
                f"{response.status_code} — {response.text}"
            )

        return response.json() if response.text else {}
