import sys
import os
from datetime import datetime
from services.asn_service import AsnSyncService

service = AsnSyncService()

def run_asn_sync():
    print("Checking for missing ASNs in Mintsoft")
    asns_to_sync = service.check_missing_mint_asns()

    if asns_to_sync:
        print(f"Found {len(asns_to_sync)} in Xorosoft not in Mintsoft")

        #print("Creating Missing ASNs")
        #response = service.sync_asns(asns_to_sync)




    else:
        print("Found no missing ASNs in Mintsoft")
