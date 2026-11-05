import os
import requests
import sys

URL = "http://localhost:8080"
API_KEY = "14915643fd5946c"
API_SECRET = "c377658d5b1967f"
HEADERS = {
    "Authorization": f"token {API_KEY}:{API_SECRET}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def get_count(doctype):
    try:
        res = requests.get(f"{URL}/api/resource/{doctype}?limit_page_length=0", headers=HEADERS)
        data = res.json().get('data', [])
        return len(data)
    except:
        return "Error"

print("--- ERPNext Data Verification ---")
print(f"Total Items: {get_count('Item')}")
print(f"Total Warehouses/Locations: {get_count('Warehouse')}")
print(f"Total Suppliers: {get_count('Supplier')}")
print(f"Total Customers: {get_count('Customer')}")
print(f"Total Territories: {get_count('Territory')}")
print(f"Total Departments: {get_count('Department')}")
print(f"Total Item Groups: {get_count('Item Group')}")
print("---------------------------------")
