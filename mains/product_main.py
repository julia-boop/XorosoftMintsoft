import sys
import os
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from services.product_service import ProductSyncService

if __name__ == "__main__":
    service = ProductSyncService()
    service.sync_all_products()
