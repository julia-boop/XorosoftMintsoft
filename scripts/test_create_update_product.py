import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from services.product_service import ProductSyncService
from mappers.product_mapper import map_xoro_item_to_mintsoft

service = ProductSyncService()

ITEM_CREATE = {
    "ItemNumber": "TEST-SKU-9999",
    "Title": "Test Product Created From Script",
    "Description": "This is a test product generated automatically.",
    "ItemUpc": "12345678999999",    # SAME BARCODE FOR BOTH TESTS
    "StandardUnitPrice": 10.0,
    "StandardUnitCost": 4.0,
    "Weight": 100,
    "HSCode": "1234.56",
    "CooCodeIso2": "US",
    "ImagePath": "",
    "ClientId": 4
}

print("\n=== STEP 1: CREATE PRODUCT ===")

payload_create = map_xoro_item_to_mintsoft(ITEM_CREATE)

create_result = service.mint.create_product(payload_create)
print("CREATE RESULT:", create_result)

product_id = create_result.get("ProductId")


ITEM_UPDATE = {
    "ItemNumber": "TEST-SKU-UPDATED",   # <-- DIFFERENT SKU
    "Title": "Updated Product Name",
    "Description": "Updated description goes here.",
    "ItemUpc": "12345678999999",         # <-- SAME BARCODE
    "StandardUnitPrice": 12.0,
    "StandardUnitCost": 5.0,
    "Weight": 110,
    "HSCode": "1234.56",
    "CooCodeIso2": "US",
    "ImagePath": "",
    "ClientId": 4
}

print("\n=== STEP 2: UPDATE PRODUCT USING SAME BARCODE BUT NEW SKU ===")

# Build update payload
payload_update = map_xoro_item_to_mintsoft(ITEM_UPDATE)

# Update using product_id returned from creation step
update_result = service.mint.update_product(product_id, payload_update)

print("\nUPDATE RESULT:", update_result)
