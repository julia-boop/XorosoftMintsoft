import os
from dotenv import load_dotenv

from clients.mintsoft_order_client import MintsoftClient
from mappers.order_mapper import map_wave_to_mintsoft   # <-- UPDATED MAPPER

load_dotenv()  

sample_wave_order = {
    "OrderData": {
        "OrderNumber": "TEST-WAVE-001",
        "CustomerName": "John Doe",
        "ShipToAddr": "123 Test St",
        "ShipToCity": "New York",
        "ShipToZpCode": "10001",
        "ShipToCountryISO2": "US",
        "ShipToEmail": "johndoe@example.com",
        "ShipToPhoneNumber": "5551231234",
        "ShipServiceCode": "UPS Ground"
    },
    "WaveData": {
        "WaveDetailAllocationArr": [
            {"ItemNumber": "SKU-123", "QtyAllocated": 1},
            {"ItemNumber": "SKU-XYZ", "QtyAllocated": 2}
        ]
    }
}

print("Authenticating with Mintsoft...")

mint = MintsoftClient(
    os.getenv("MINTSOFT_USERNAME"),
    os.getenv("MINTSOFT_PASSWORD")
)

print("API Key acquired.")

mapped_order = map_wave_to_mintsoft(sample_wave_order)
print("Mapped Order:")
print(mapped_order)

print("\nSending order to Mintsoft...")

try:
    response = mint.create_order(mapped_order)
    print("\nSUCCESS — Mintsoft Response:")
    print(response)

except Exception as e:
    print("\nFAILED — Error returned by Mintsoft:")
    print(str(e))
