import os
import base64
import requests
import json
from dotenv import load_dotenv

load_dotenv() 


class XoroOneClient:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://res.xorosoft.io"

    def _headers(self):
        token = f"{self.api_key}:{self.api_secret}"
        encoded = base64.b64encode(token.encode()).decode()

        return {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def get_all_sales_orders(self):
        all_items = []
        status = "released"
        page = 1

        while True:
            url = f"{self.base_url}/api/xerp/wave/getwave"
            params = {"page": page}

            print(f"Requesting page {page}...")

            response = requests.get(url, headers=self._headers(), params=params)

            response.raise_for_status()

            data = response.json()

            payload = data.get("Data", {})

            order_list = payload.get("OrderData", [])
            wave_list = payload.get("WaveData", [])

            # The lists match by index → zip to combine them
            for order, wave in zip(order_list, wave_list):
                all_items.append({
                    "OrderData": order,
                    "WaveData": wave
                })

            total_pages = data.get("TotalPages", 1)
            if page >= total_pages:
                break

            page += 1

        return all_items


if __name__ == "__main__":
    API_KEY = os.getenv("XORO_API_KEY")
    API_SECRET = os.getenv("XORO_API_SECRET")

    client = XoroOneClient(API_KEY, API_SECRET)
    waves = client.get_all_sales_orders()

    with open("wave_orders.json", "w", encoding="utf-8") as f:
        json.dump(waves, f, indent=4, ensure_ascii=False, default=str)


        print("\nSaved JSON to wave_orders.json")

