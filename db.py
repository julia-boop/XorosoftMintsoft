import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    print(DATABASE_URL)
    return psycopg2.connect(DATABASE_URL)

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor() # Ejecutor de los comandos de SQL en la db
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mintsoft_holiday_products (
            sku VARCHAR(100) PRIMARY KEY,
            name TEXT,
            upc VARCHAR(50),
            price DECIMAL(10, 2),
            image_url TEXT,
            last_updated TIMESTAMP DEFAULT NOW()
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sync_log (
            id SERIAL PRIMARY KEY,
            sync_time TIMESTAMP DEFAULT NOW(),
            products_created INT DEFAULT 0,
            products_updated INT DEFAULT 0
        )
    """)
    
    conn.commit() # Guarda los cambios
    cursor.close() # Frena al ejecutor de cambios
    conn.close() # Cierra la conexion

def upsert_product(cursor, product): # Agrega y actualiza productos en la tabla
    cursor.execute("""
        INSERT INTO mintsoft_holiday_products (sku, name, upc, price, image_url, last_updated, description)
        VALUES (%s, %s, %s, %s, %s, NOW())
        ON CONFLICT (sku) DO UPDATE SET
            name = EXCLUDED.name,
            upc = EXCLUDED.upc,
            price = EXCLUDED.price,
            image_url = EXCLUDED.image_url,
            last_updated = NOW(),
            description = EXCLUDED.description
        """, (
            product.get("SKU"),
            product.get("Name"),
            product.get("Upc"),
            product.get("Price"),
            product.get("ImageURL"),
            product.get("Description"),
        ))

def log_product_sync(cursor, created, updated):
    cursor.execute("""
        INSERT INTO sync_log (products_created, products_updated)
        VALUES (%s, %s)
    """, (
        created,
        updated,
    ))
     
def get_existing_items():
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor) # Diccionario para facilitar comparacion
    cursor.execute("SELECT * FROM mintsoft_holiday_products")
    rows = cursor.fetchall()
    
    # Creamos un diccionario donde la clave es el SKU
    # { 'SKU123': {'ean': '...', 'price': 10.0, ...}, 'SKU456': {...} }
    products_dict = {row['sku']: row for row in rows}
    
    cursor.close()
    conn.close()
    return products_dict