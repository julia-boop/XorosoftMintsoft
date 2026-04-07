import sys
import os
from datetime import datetime
from services.asn_service import AsnSyncService

service = AsnSyncService()

def run_asn_sync():
    #print("Checking for missing ASNs in Mintsoft")
    asns_to_sync = service.check_missing_mint_asns()

    response = service.update_xoro_asn_status()
    print(response)

    if asns_to_sync:
        print(f"Found {len(asns_to_sync)} ASN in Xorosoft not in Mintsoft")

        #print("Creating Missing ASNs")
        #response = service.create_mint_asns(asns_to_sync)




    else:
        print("Found no missing ASNs in Mintsoft")
