import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from services.product_service import ProductSyncService

service = ProductSyncService()

print("Fetching products from Mintsoft...")
products = service.mint.get_all_products()   # <--- we call the CLIENT here

print(f"Total Mintsoft products fetched: {len(products)}")

print("\nBuilding index...")
index = service._build_mintsoft_index(products)

print("\nIndex sizes:")
print(" by_sku:", len(index["by_sku"]))
print(" by_barcode:", len(index["by_barcode"]))
print(" by_id:", len(index["by_id"]))

# Test lookup
TEST_SKU = "SKU-123"  # change to a real SKU that exists in Mintsoft
print(f"\nTesting lookup for SKU '{TEST_SKU}'...")

if TEST_SKU in index["by_sku"]:
    print("FOUND! Product:")
    print(index["by_sku"][TEST_SKU])
else:
    print("NOT FOUND.")
