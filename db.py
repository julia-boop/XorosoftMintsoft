import os
import psycopg2

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
        INSERT INTO mintsoft_holiday_products (sku, name, upc, price, image_url, last_updated)
        VALUES (%s, %s, %s, %s, %s, NOW())
        ON CONFLICT (sku) DO UPDATE SET
            name = EXCLUDED.name,
            upc = EXCLUDED.upc,
            price = EXCLUDED.price,
            image_url = EXCLUDED.image_url,
            last_updated = NOW()
        """, (
            product.get("ItemNumber"),
            product.get("Description"),
            product.get("ItemUPC"),
            product.get("StandardUnitPrice"),
            product.get("ImagePath")
        ))