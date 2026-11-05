import requests
import json
import time

base_url = "http://localhost:8080"
headers = {
    "Authorization": "token 14915643fd5946c:c377658d5b1967f",
    "Content-Type": "application/json"
}

def make_request(method, endpoint, data=None):
    url = f"{base_url}{endpoint}"
    if method == "GET":
        return requests.get(url, headers=headers)
    elif method == "POST":
        return requests.post(url, headers=headers, json=data)
    elif method == "PUT":
        return requests.put(url, headers=headers, json=data)

print("\n===== SUBMITTING STOCK ENTRIES =====")
resp = make_request("GET", "/api/resource/Stock Entry?filters=[[\"docstatus\",\"=\",0]]&limit_page_length=100")
if resp.status_code == 200:
    entries = resp.json().get('data', [])
    for e in entries:
        name = e['name']
        # Fetch the full document first to get the latest modified timestamp
        doc_resp = make_request("GET", f"/api/resource/Stock Entry/{name}")
        if doc_resp.status_code == 200:
            doc = doc_resp.json().get('data')
            doc['company'] = "SK Automation Labs"
            for item in doc.get('items', []):
                item['cost_center'] = "Main - SKAL"
            doc['docstatus'] = 1
            # Submit using frappe.client.submit via POST or by PUT with docstatus = 1
            # But the best way is POST to /api/method/frappe.client.submit
            submit_resp = make_request("POST", "/api/method/frappe.client.submit", data={"doc": doc})
            if submit_resp.status_code == 200:
                print(f"[SUBMIT] Stock Entry: {name}")
            else:
                print(f"[ERR] Submit {name}: {submit_resp.text}")

print("\n===== CREATING SALES ORDERS =====")
sales_orders = [
    {"customer":"Sharma Electronics Pvt Ltd", "company":"SK Automation Labs", "delivery_date":"2026-10-05", "items":[{"item_code":"SKU002","qty":5,"rate":75000, "warehouse": "Stores - SKAL"}, {"item_code":"SKU009","qty":20,"rate":2999, "warehouse": "Stores - SKAL"}]},
    {"customer":"Patel Traders & Sons", "company":"SK Automation Labs", "delivery_date":"2026-10-03", "items":[{"item_code":"SKU001","qty":50,"rate":699, "warehouse": "Stores - SKAL"}, {"item_code":"SKU006","qty":100,"rate":249, "warehouse": "Stores - SKAL"}]},
    {"customer":"Gupta Warehouse Solutions", "company":"SK Automation Labs", "delivery_date":"2026-10-07", "items":[{"item_code":"SKU013","qty":10,"rate":2499, "warehouse": "Stores - SKAL"}, {"item_code":"SKU014","qty":15,"rate":1299, "warehouse": "Stores - SKAL"}]},
    {"customer":"Singh Retail Chain", "company":"SK Automation Labs", "delivery_date":"2026-10-10", "items":[{"item_code":"SKU016","qty":30,"rate":1499, "warehouse": "Stores - SKAL"}, {"item_code":"SKU017","qty":40,"rate":799, "warehouse": "Stores - SKAL"}]},
    {"customer":"Mehta Distributors", "company":"SK Automation Labs", "delivery_date":"2026-10-08", "items":[{"item_code":"SKU004","qty":10,"rate":22000, "warehouse": "Stores - SKAL"}, {"item_code":"SKU007","qty":3,"rate":49999, "warehouse": "Stores - SKAL"}]},
    {"customer":"Rajesh Kumar", "company":"SK Automation Labs", "delivery_date":"2026-10-02", "items":[{"item_code":"SKU005","qty":2,"rate":4500, "warehouse": "Stores - SKAL"}, {"item_code":"SKU011","qty":3,"rate":599, "warehouse": "Stores - SKAL"}]},
    {"customer":"Priya Verma", "company":"SK Automation Labs", "delivery_date":"2026-10-04", "items":[{"item_code":"SKU015","qty":1,"rate":899, "warehouse": "Stores - SKAL"}, {"item_code":"SKU019","qty":2,"rate":499, "warehouse": "Stores - SKAL"}]},
    {"customer":"Arun Mishra", "company":"SK Automation Labs", "delivery_date":"2026-10-06", "items":[{"item_code":"SKU020","qty":1,"rate":3999, "warehouse": "Stores - SKAL"}, {"item_code":"SKU012","qty":5,"rate":199, "warehouse": "Stores - SKAL"}]}
]

for so in sales_orders:
    so["doctype"] = "Sales Order"
    resp = make_request("POST", "/api/resource/Sales Order", data=so)
    if resp.status_code == 200:
        name = resp.json()['data']['name']
        print(f"[OK] Sales Order: {name}")
        # Submit it
        doc_resp = make_request("GET", f"/api/resource/Sales Order/{name}")
        doc = doc_resp.json()['data']
        doc['docstatus'] = 1
        make_request("POST", "/api/method/frappe.client.submit", data={"doc": doc})
    else:
        print(f"[ERR] Sales Order: {resp.text}")

print("\n===== CREATING MATERIAL REQUESTS =====")
material_requests = [
    {"material_request_type":"Purchase", "company": "SK Automation Labs", "schedule_date":"2026-10-15", "items":[{"item_code":"SKU002","qty":20,"schedule_date":"2026-10-15", "warehouse":"Stores - SKAL"}, {"item_code":"SKU010","qty":15,"schedule_date":"2026-10-15", "warehouse":"Stores - SKAL"}]},
    {"material_request_type":"Purchase", "company": "SK Automation Labs", "schedule_date":"2026-10-12", "items":[{"item_code":"SKU007","qty":10,"schedule_date":"2026-10-12", "warehouse":"Stores - SKAL"}, {"item_code":"SKU004","qty":25,"schedule_date":"2026-10-12", "warehouse":"Stores - SKAL"}]}
]

for mr in material_requests:
    mr["doctype"] = "Material Request"
    resp = make_request("POST", "/api/resource/Material Request", data=mr)
    if resp.status_code == 200:
        name = resp.json()['data']['name']
        print(f"[OK] Material Request: {name}")
        # Submit it
        doc_resp = make_request("GET", f"/api/resource/Material Request/{name}")
        doc = doc_resp.json()['data']
        doc['docstatus'] = 1
        make_request("POST", "/api/method/frappe.client.submit", data={"doc": doc})
    else:
        print(f"[ERR] Material Request: {resp.text}")
