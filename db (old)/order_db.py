# db/order_db.py
import sqlite3
import json

class OrderDB:
    def __init__(self, db_path="sync.db"):
        self.conn = sqlite3.connect(db_path)
        self._init()

    def _init(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            external_id TEXT,
            status TEXT,
            created_at TEXT,
            updated_at TEXT,
            payload TEXT,
            UNIQUE(source, external_id)
        )
        """)
        self.conn.commit()

    def upsert(self, source, external_id, status, created_at, updated_at, payload):
        self.conn.execute("""
        INSERT INTO orders (source, external_id, status, created_at, updated_at, payload)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(source, external_id)
        DO UPDATE SET
            status=excluded.status,
            updated_at=excluded.updated_at,
            payload=excluded.payload
        """, (
            source,
            external_id,
            status,
            created_at,
            updated_at,
            json.dumps(payload)
        ))
        self.conn.commit()
