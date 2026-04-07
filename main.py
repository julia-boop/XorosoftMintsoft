from mains.product_main import run_product_sync
from mains.asn_main import run_asn_sync
from services.order_service import OrderSyncService
# from mains.order_main import run_order_sync
# from mains.shipment_main import run_shipment_sync



try:
    #print("Executing Product Sync")
    #run_product_sync()

    #service = OrderSyncService()
    #service.sync_all_orders()
    print("Executing ASN Sync")
    run_asn_sync()

    #print("Executing Order Sync")
    

except Exception as e:
    print(e)

