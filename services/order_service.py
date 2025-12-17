import sys
import os
from datetime import datetime, timezone
from state.sync_state_manager import SyncStateManager
from clients.xorosoft_order_client import XoroSoftOrderClient
from clients.mintsoft_order_client import MintsoftOrderClient
from mappers.order_mapper import map_xoro_order_to_mintsoft_order
from loggers.order_logger import order_logger

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

STATE_FILE = "state/sync_state.json"

class OrderSyncService:

    def __init__(self):
        self.xoro = XoroSoftOrderClient()
        self.mint = MintsoftOrderClient()
        self.state = SyncStateManager(STATE_FILE)

    def sync_new_orders(self, status="released"):
        last_sync = self.state.get("orders", "xorosoft")
        order_logger.info(f"Last Xorosoft order sync: {last_sync}")

        orders = self.xoro.get_sales_orders_since(
            status=status,
            from_date=last_sync
        )

        latest_ts = last_sync

        for order in orders:
            try:
                mapped = map_xoro_order_to_mintsoft_order(order)
                self.mint.create_order(mapped)

                updated = order["SoEstimateHeader"].get("UpdatedDate")
                if updated:
                    ts = datetime.fromisoformat(updated)
                    if not latest_ts or ts > latest_ts:
                        latest_ts = ts

                order_logger.info(
                    f"[SUCCESS] Order synced: {mapped.get('OrderNumber')}"
                )

            except Exception as e:
                order_logger.error(
                    f"[ERROR] Order {order.get('SoEstimateHeader', {}).get('OrderNumber')}: {e}"
                )

        if latest_ts:
            self.state.update("orders", "xorosoft", latest_ts)
