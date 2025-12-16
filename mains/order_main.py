from services.order_service import OrderSyncService

if __name__ == "__main__":
    service = OrderSyncService()

    # Test one order:
    service.sync_one_order("TEST-LOCAL-001")

    # Or sync all:
    # service.sync_all_orders("released")
