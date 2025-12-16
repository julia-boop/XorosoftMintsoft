from clients.xorosoft_order_client import XoroSoftOrderClient
from clients.mintsoft_order_client import MintsoftOrderClient
from mappers.order_mapper import map_xoro_order_to_mintsoft_order
from loggers.order_logger import order_logger


class OrderSyncService:

    def __init__(self):
        self.xoro = XoroSoftOrderClient()
        self.mint = MintsoftOrderClient()

    def sync_all_orders(self, status="released"):
        order_logger.info(f"=== Fetching Xorosoft orders with status '{status}' ===")

        xorosoft_orders = self.xoro.get_all_sales_orders(status)
        order_logger.info(f"Fetched {len(xorosoft_orders)} orders")

        for order in xorosoft_orders:
            try:
                mapped = map_xoro_order_to_mintsoft_order(order)
                response = self.mint.create_order(mapped)

                order_logger.info(
                    f"[SUCCESS] Mintsoft Order Created: {mapped.get('OrderNumber')}"
                )

            except Exception as e:
                order_logger.error(
                    f"[ERROR] Failed creating order {order.get('SoEstimateHeader', {}).get('OrderNumber')}: {e}"
                )

    def sync_one_order(self, order_number):
        order_logger.info(f"=== Fetching Xorosoft order {order_number} ===")

        order = self.xoro.get_order_by_number(order_number)

        if not order:
            order_logger.warning(f"Order not found in Xorosoft: {order_number}")
            return

        try:
            mapped = map_xoro_order_to_mintsoft_order(order)
            response = self.mint.create_order(mapped)

            order_logger.info(f"[SUCCESS] Mintsoft Order Created: {mapped.get('OrderNumber')}")
            return response

        except Exception as e:
            order_logger.error(f"[ERROR] Creating order {order_number}: {e}")
            return None
