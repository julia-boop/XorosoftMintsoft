import sys 
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from clients.mintsoft_product_client import MintsoftProductClient
from db.product_db import ProductDB
from datetime import datetime, timezone
import json
from pathlib import Path

STATE_FILE = Path("state/product_sync_state.json")

mint = MintsoftProductClient()
db = ProductDB()

state = json.loads(STATE_FILE.read_text())
since = state["products"]["updated_at"]

page = 1
max_seen = since

while True:
    products = mint.get_products_updated_since(since, page)
    if not products:
        break

    for p in products:
        db.upsert(p)
        if p.get("LastUpdated") > max_seen:
            max_seen = p["LastUpdated"]

    page += 1

state["products"]["updated_at"] = max_seen
STATE_FILE.write_text(json.dumps(state, indent=4))
