import requests

class MintsoftClient:

    BASE_URL = "https://api.mintsoft.co.uk"

    def __init__(self, username, password):
        self.api_key = self.authenticate(username, password)

    def authenticate(self, username, password):
        url = f"{self.BASE_URL}/api/Auth"
        payload = {"Username": username, "Password": password}

        r = requests.post(url, json=payload)
        r.raise_for_status()
        return r.json()

    def create_order(self, order_payload):
        url = f"{self.BASE_URL}/api/Order"
        headers = {"ms-apikey": self.api_key}
        r = requests.put(url, json=order_payload, headers=headers)
        r.raise_for_status()
        return r.json()
