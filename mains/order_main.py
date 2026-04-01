import os 
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from services.order_service import OrderSyncService

# Pasos e ideas:
# - Automatizar fulfill wave?
# - Crear Volume para sync_state.json
# -Traer ordenes de waves a mintsoft, chequear si siempre es 1 orden por wave o más, sino iterar 
# -Chejear que bajen bien.
# -ACK de las ordenes de las waves

if __name__ == "__main__":
    service = OrderSyncService()

    # Test one order:
    #service.sync_one_order("TEST-LOCAL-001")
        
    # Or sync all:
    service.sync_all_orders()
