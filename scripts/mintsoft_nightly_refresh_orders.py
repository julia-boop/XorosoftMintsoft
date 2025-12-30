import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from clients.mintsoft_order_client import MintsoftOrderClient
from db.order_db import OrderDB

mint = MintsoftOrderClient()
db = OrderDB()

orders = mint.get_orders()


print("Full Mintsoft order refresh completed")
