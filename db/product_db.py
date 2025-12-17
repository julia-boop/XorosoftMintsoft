import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "mintsoft_products.db"


class ProductDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS mintsoft_products (
            mintsoft_product_id INTEGER PRIMARY KEY,

            sku TEXT UNIQUE NOT NULL,
            upc TEXT,

            name TEXT,
            description TEXT,

            weight REAL,
            price REAL,
            cost_price REAL,

            image_url TEXT,

            raw_payload TEXT,
            last_updated TEXT
        )
        """)

        self.conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_upc
        ON mintsoft_products(upc)
        """)

        self.conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_sku
        ON mintsoft_products(sku)
        """)

        self.conn.commit()

    def upsert(self, product: dict):
        """
        Upsert a Mintsoft product into the local cache.
        Expects Mintsoft product payload.
        """

        self.conn.execute("""
        INSERT INTO mintsoft_products (
            mintsoft_product_id,
            sku,
            upc,
            name,
            description,
            weight,
            price,
            cost_price,
            image_url,
            raw_payload,
            last_updated
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(mintsoft_product_id) DO UPDATE SET
            sku=excluded.sku,
            upc=excluded.upc,
            name=excluded.name,
            description=excluded.description,
            weight=excluded.weight,
            price=excluded.price,
            cost_price=excluded.cost_price,
            image_url=excluded.image_url,
            raw_payload=excluded.raw_payload,
            last_updated=excluded.last_updated
        """, (
            product["ID"],
            product.get("SKU") or "",
            product.get("UPC") or product.get("EAN") or "",
            product.get("Name") or "",
            product.get("Description") or "",
            product.get("Weight") or 0,
            product.get("Price") or 0,
            product.get("CostPrice") or 0,
            product.get("ImageURL") or "",
            json.dumps(product),
            product.get("LastUpdated")
        ))

        self.conn.commit()

    def get_by_barcode(self, barcode: str):
        cur = self.conn.execute(
            "SELECT * FROM mintsoft_products WHERE upc = ?",
            (barcode,)
        )
        return cur.fetchone()

    def get_by_sku(self, sku: str):
        cur = self.conn.execute(
            "SELECT * FROM mintsoft_products WHERE sku = ?",
            (sku,)
        )
        return cur.fetchone()
