import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from clients.mintsoft_product_client import MintsoftProductClient
from db.product_db import ProductDB

mint = MintsoftProductClient()
db = ProductDB()

products = mint.get_all_products()

for p in products:
    db.upsert(p)



print("Full Mintsoft refresh completed")
