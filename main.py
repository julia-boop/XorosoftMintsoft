# from mains.product_main import run_product_sync
# from mains.order_main import run_order_sync
# from mains.shipment_main import run_shipment_sync
from db import get_connection
from db import initialize_db
import csv

def seed_from_csv(filepath):
    conn = get_connection()
    cursor = conn.cursor()

    with open(filepath, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute("""
                INSERT INTO mintsoft_holiday_products (sku, name, upc, price, image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (sku) DO NOTHING
            """, (
                row.get("SKU"),
                row.get("Name"),
                row.get("UPCBarcode"),
                row.get("Price"),
                row.get("ImageURL")
            ))

    conn.commit()
    cursor.close()
    conn.close()

try:
    
    initialize_db()

    seed_from_csv("holiday_stock.csv")

except Exception as e:
    print(e)

