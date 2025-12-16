import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from clients.mintsoft_product_client import MintsoftProductClient

mint = MintsoftProductClient()

print("Fetching Mintsoft products...")
products = mint.get_all_products()

print(f"Count: {len(products)}")
print("Sample:", products[0] if products else "No products")
