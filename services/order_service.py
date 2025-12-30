import sys
import os
import json
from datetime import datetime, timezone
from clients.xorosoft_order_client import XorosoftOrderClient
from clients.mintsoft_order_client import MintsoftOrderClient
from mappers.order_mapper import map_xoro_order_to_mintsoft
from loggers.order_logger import order_logger
from utils.datetime_util import iso_to_xorosoft, xorosoft_to_iso

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

FMT = "%m/%d/%Y %I:%M:%S %p"

STATE_DIR = os.path.join(ROOT, "state")
STATE_FILE = os.path.join(STATE_DIR, "sync_state.json")
os.makedirs(STATE_DIR, exist_ok=True)


class OrderSyncService:

    def __init__(self):
        self.xoro = XorosoftOrderClient()
        self.mint = MintsoftOrderClient()

    def _load_order_sync_state(self):
        if not os.path.exists(STATE_FILE):
            return {
                "orders": {
                    "created_at": None,
                    "updated_at": None
                }
            }

        with open(STATE_FILE, "r") as f:
            return json.load(f)

    def _save_order_sync_state(self, created_at=None, updated_at=None):
        state = self._load_order_sync_state()
        state.setdefault("orders", {})

        if created_at:
            state["orders"]["created_at"] = created_at
        if updated_at:
            state["orders"]["updated_at"] = updated_at

        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=4)

    def sync_all_orders(self, status="released"):
        order_logger.info("=== Sync ALL orders started ===")

        state = self._load_order_sync_state()
        created_iso = state["orders"].get("created_at")

        last_created_at = iso_to_xorosoft(created_iso) if created_iso else None

        cutoff = datetime.now(timezone.utc).strftime(FMT)

        order_logger.info(
            "Delta window | created_at: %s → %s",
            last_created_at, cutoff
        )

        order_logger.info("Fetching Xorosoft CREATED orders...")
        orders = self.xoro.get_sales_orders(
            status=status,
            created_at_min=last_created_at,
            created_at_max=cutoff,
        )

        order_logger.info("Total delta orders to process: %s", len(orders))

        stats = {
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
        }

        max_created_seen = state["orders"].get("created_at")
        max_updated_seen = state["orders"].get("updated_at")

        for order in orders.values():
            header = order.get("SoEstimateHeader", {})
            order_number = header.get("OrderNumber")

            try:
                mapped = map_xoro_order_to_mintsoft(order)
                result = self.mint.create_order(mapped)

                if not result.get("Success", True):
                    raise Exception(f"Mintsoft create failed: {result}")

                stats["created"] += 1

                created_at = header.get("CreatedDate")
                updated_at = header.get("UpdatedDate")

                if created_at and (not max_created_seen or created_at > max_created_seen):
                    max_created_seen = xorosoft_to_iso(created_at)

                if updated_at and (not max_updated_seen or updated_at > max_updated_seen):
                    max_updated_seen = xorosoft_to_iso(updated_at)

                order_logger.info("[SUCCESS] Order synced: %s", order_number)

            except Exception as e:
                order_logger.exception("[ERROR] Order %s: %s", order_number, e)
                stats["errors"] += 1

        self._save_order_sync_state(
            created_at=max_created_seen,
            updated_at=max_updated_seen,
        )

        order_logger.info("=== Sync ALL orders finished ===")
        order_logger.info(
            "Created=%s Errors=%s Total=%s",
            stats["created"],
            stats["errors"],
            len(orders),
        )

        return stats
