from mains.product_main import run_product_sync
# from mains.order_main import run_order_sync
# from mains.shipment_main import run_shipment_sync



try:
    print("Executing Product Sync")
    run_product_sync()

    #print("Executing ASN Sync")

    #print("Executing Order Sync")
    

except Exception as e:
    print(e)

