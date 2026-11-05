import requests
import json

base_url = "http://localhost:8080"
headers = {
    "Authorization": "token 14915643fd5946c:c377658d5b1967f",
    "Content-Type": "application/json"
}

# Try to create a Sales Order
so_data = {
    "doctype": "Sales Order",
    "customer": "Sharma Electronics Pvt Ltd",
    "delivery_date": "2026-10-05",
    "items": [
        {"item_code": "SKU002", "qty": 5, "rate": 75000},
        {"item_code": "SKU009", "qty": 20, "rate": 2999}
    ]
}

response = requests.post(f"{base_url}/api/resource/Sales Order", headers=headers, json=so_data)
print("Sales Order Status:", response.status_code)
print("Response:", response.text)
