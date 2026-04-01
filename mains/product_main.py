import sys
import os
from datetime import datetime
from clients.db_client import DatabaseClient
from services.product_service import ProductSyncService

product_service = ProductSyncService()
db_service = DatabaseClient()

def run_product_sync():

    print("Extracting Latest Updates to the Xorosoft Catalog")
    xorosoft_items = product_service.extract_xorosoft_catalog()

    if xorosoft_items: # Si hay algun cambio
        conn = db_service.get_connection()
        cursor = conn.cursor() # Ejecutor de los comandos de SQL en la db

        print(f"A total of {len(xorosoft_items)} SKUs have been added/updated in XoroSoft")

        print("Extracting Mintsoft information from the Railway DB")
        mintsoft_items = db_service.get_existing_items()

        created = 0
        updated = 0

        for item in xorosoft_items:
            if item.get("SKU") not in mintsoft_items: # Si es nuevo
                print(f'Creating SKU {item.get("SKU")} in Mintsoft')
                product_service.create_missing_mintsoft_products(item)
                created += 1

                db_service.upsert_product(cursor, item)
            
            else : # Si ya existe
                # Comparo los campos que estan cargados en la base de datos para ese sku
                current_db_item = mintsoft_items[item.get("SKU")]

                has_changed = (
                    str(item.get("Upc")).strip() != str(current_db_item.get("upc")).strip() or
                    float(item.get("Price", 0)) != float(current_db_item.get("price", 0)) or
                    item.get("Description") != current_db_item.get("description") or
                    item.get("ImageURL") != current_db_item.get("image_url")
                )
                
                if has_changed:
                    print(f'SKU {item.get("SKU")} already exists in Mintsoft, it has been updated')
                    product_service.update_missing_mintsoft_products(item)
                    updated += 1

                    db_service.upsert_product(cursor, item)
                
                else:
                    print(f'SKU {item.get("SKU")} already exists in Mintsoft, there were no relevant updates to it')

        db_service.log_product_sync(cursor, created, updated)

        conn.commit()
        cursor.close()
        conn.close()
        print(f"Created: {created}, Updated: {updated}")
    
    else:
        print(f"No new/updated products as of {datetime.now()}")







        
