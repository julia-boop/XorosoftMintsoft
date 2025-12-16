import sys
import os
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from services.product_service import ProductSyncService

service = ProductSyncService()

cursor_max = datetime(2025, 8, 8, 7, 59, 59)

window = timedelta(hours=1)

cutoff_date = datetime(2024, 2, 3, 0, 0, 0)

fmt = "%m/%d/%Y %I:%M:%S %p"

while cursor_max > cutoff_date:

    cursor_min = cursor_max - window

    updated_at_max = cursor_max.strftime(fmt)
    updated_at_min = cursor_min.strftime(fmt)

    print("\n=== SYNC WINDOW ===")
    print(f"From (min): {updated_at_min}")
    print(f"To   (max): {updated_at_max}")

    result = service.sync_all_products_create_only(
        updated_at_min=updated_at_min,
        updated_at_max=updated_at_max
    )

    print("Window result:", result)

    cursor_max = cursor_min
