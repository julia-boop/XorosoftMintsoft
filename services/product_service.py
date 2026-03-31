import sys
import os
import json
import csv
from datetime import datetime, timezone, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from clients.xorosoft_product_client import XoroSoftProductClient
from clients.mintsoft_product_client import MintsoftProductClient
from mappers.product_mapper import map_xoro_item_to_mintsoft
from loggers.product_logger import product_logger
# from db.product_db import ProductDB
from utils.datetime_util import iso_to_xorosoft, xorosoft_to_iso

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

FMT = "%m/%d/%Y %I:%M:%S %p"

STATE_DIR = os.path.join(ROOT, "state")
STATE_FILE = os.path.join(STATE_DIR, "sync_state.json")
os.makedirs(STATE_DIR, exist_ok=True)


class ProductSyncService:

    def __init__(self):
        self.xoro = XoroSoftProductClient()
        self.mint = MintsoftProductClient()

    def _load_product_sync_state(self):
        if not os.path.exists(STATE_FILE):
            return {
                "products": {
                    "created_at": None,
                    "updated_at": None
                }
            }

        with open(STATE_FILE, "r") as f:
            return json.load(f)

    def _save_product_sync_state(self, created_at=None, updated_at=None):
        state = self._load_product_sync_state()

        if created_at:
            state["products"]["created_at"] = created_at
        if updated_at:
            state["products"]["updated_at"] = updated_at

        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=4)
    
    def extract_mintsoft_catalog(self):
        # Extraer catalogo de Mintsoft

        mintsoft_skus = []
        current_page = 1
        
        while True:
            print(f"Consultando pagina {current_page}")

            params = {
                "PageNo": current_page,
                "ClientId": 4,
                "SinceLastUpdated": "2026-03-20T00:00:00.000Z"
            }

            products_in_page = self.mint.get_products(params)

            if not products_in_page:
                print("Empty Page")
                break

            for product in products_in_page:
                mintsoft_skus.append(product.get("SKU"))

            print(len(mintsoft_skus))

            if len(products_in_page) != 100:
                print("Last Page Reached")
                break
            
            current_page += 1

        return mintsoft_skus
    
    def extract_xorosoft_catalog(self):
        # Extraer catalogo de Xorosoft
        xorosoft_skus = []
        current_page = 1

        while True:
            print(f"Consultando pagina {current_page}")

            params = {
                "PageNo": current_page,
                "UpdatedAtMin": "2026-03-30 00:00:00AM"
            }

            data = self.xoro.get_products(params)

            products_in_page = data.get("Data")

            if not products_in_page:
                print("Empty Page")
                break

            for product in products_in_page:
                xorosoft_skus.append(product.get("ItemNumber"))
            
            print(len(products_in_page))

            if len(products_in_page) != 100:
                print("Last Page Reached")
                break

            current_page += 1

        return xorosoft_skus
    
    def fetch_missing_mintsoft_products(self, missing_products):
        missing_product_list = list(missing_products)
        missing_product_data = []
        batch_size = 110

        for i in range(0, len(missing_product_list), batch_size):
            batch = missing_product_list[i:i + batch_size]
            batch_string = ",".join(batch)

            print(batch_string)

            params = {
                "MissingSKUs": batch_string,
                "PageNo": 1
            }

            data = self.xoro.get_products(params)
            products_in_page = data.get("Data")

            if not products_in_page:
                print("Empty Page")
                break

            missing_product_data.extend(products_in_page)

        return missing_product_data
    
    def create_missing_mintsoft_products(self, missing_product_data):

        print(missing_product_data)

        for product in missing_product_data:

            product_json = {
                "SKU": product.get("ItemNumber"),
                "Name": product.get("Description"),
                "EAN": product.get("ItemUpc"),
                "ClientId": 4, # Holiday Company
                "ImageURL": product.get("ImagePath"),
                "Price": product.get("StandardUnitPrice"),
                "LowStockAlertLevel": 1,
                "HandlingTime": 1,
                "BestBeforeDateWarningPeriodDays": 365,
                "CountryOfManufacture": {
                    "Code":product.get("CooCodeIso2"), # CooCodeIso2, ver tema de los ID
                }, 
                "CommodityCode": {
                    "Code": product.get("HSCode")
                }
            }

            response = self.mint.create_product(product_json)
            print(response)
        
        return None
    
    def export_missing_products_to_csv(self, missing_product_data, filename="missing_products.csv"):
        fields_to_extract = ["ItemNumber", "Description", "ItemUpc", "StandardUnitPrice", "HSCode", "CooCodeIso2", "ImagePath"]
    
        with open(filename, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fields_to_extract, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(missing_product_data)


try:

    client = ProductSyncService()

    print("Extracting Mintsoft Catalog")
    mintsoft_skus = client.extract_mintsoft_catalog()

    print("Extracting Xorosoft Catalog")
    xorosoft_skus = client.extract_xorosoft_catalog() 

    missing_products = set(xorosoft_skus) - set(mintsoft_skus)
    
    if missing_products == set():
        print("There are no missing items in Mintsoft")

    else: 
        print(f"There are currently {len(missing_products)} items missing in Mintsoft")
    
        print("Fetching missing item info")
        missing_product_data = client.fetch_missing_mintsoft_products(missing_products)

    print("Exporting to CSV")
    client.export_missing_products_to_csv(missing_product_data)

    # print("Creating missing Mintsoft products")
    # client.create_missing_mintsoft_products(missing_product_data)

except Exception as e:
    print(e)

    
            

