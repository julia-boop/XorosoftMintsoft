import sys
import os
import json
import csv
from datetime import datetime, timezone, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from clients.xorosoft_product_client import XoroSoftProductClient
from clients.mintsoft_product_client import MintsoftProductClient
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
    
    def extract_xorosoft_catalog(self):
        # Extraer catalogo de Xorosoft
        xorosoft_items = []
        current_page = 1

        while True:
            print(f"Consultando pagina {current_page}")

            params = {
                "PageNo": current_page,
                "UpdatedAtMin": "2026-03-30 7:00:00PM"
            }

            data = self.xoro.get_products(params)

            products_in_page = data.get("Data")

            if not products_in_page:
                print("Empty Page")
                break

            for product in products_in_page:
                product_data = {
                    "SKU": product.get("ItemNumber"),
                    "Name": product.get("Title"),
                    "Description": product.get("Description"),
                    "Upc": product.get("ItemUpc"),
                    "ImageURL": product.get("ImagePath"),
                    "Price": product.get("StandardUnitPrice"),
                    "CountryCode":product.get("CooCodeIso2"),
                    "CommodityCode": product.get("HSCode")
                }
                xorosoft_items.append(product_data)

            if len(products_in_page) != 100:
                print("Last Page Reached")
                break

            current_page += 1

        return xorosoft_items
    
    def create_missing_mintsoft_products(self, item_data):

        product_json = {
            "SKU": item_data.get("SKU"),
            "Name": item_data.get("Name"),
            "EAN": item_data.get("Upc"),
            "Description": item_data.get("Description"),
            "ClientId": 4, # Holiday Company
            "ImageURL": item_data.get("ImageURL"),
            "Price": item_data.get("Price"),
            "LowStockAlertLevel": 1,
            "HandlingTime": 1,
            "BestBeforeDateWarningPeriodDays": 365,
            "CountryOfManufacture": {
                "Code":item_data.get("CountryCode"), # CooCodeIso2, ver tema de los ID
            }, 
            "CommodityCode": {
                "Code": item_data.get("CommodityCode")
            }
        }

        response = self.mint.create_product(product_json)
        print(response)
    
        return None
    
    def update_missing_mintsoft_products(self, item_data):

        product_json = {
            "ClientId": self.mint.get_product_id(item_data.get("SKU")),
            "SKU": item_data.get("SKU"),
            "Name": item_data.get("Name"),
            "EAN": item_data.get("Upc"),
            "Description": item_data.get("Description"),
            "ImageURL": item_data.get("ImageURL"),
            "Price": item_data.get("Price"),
        }

        response = self.mint.create_product(product_json)
        print(response)
    
        return None


