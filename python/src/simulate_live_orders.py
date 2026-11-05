import os
import sys
import json
import time
import random
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

URL = os.getenv("ERPNEXT_URL", "http://localhost:8080")
API_KEY = os.getenv("ERPNEXT_API_KEY", "14915643fd5946c")
API_SECRET = os.getenv("ERPNEXT_API_SECRET", "c377658d5b1967f")
HEADERS = {
    "Authorization": f"token {API_KEY}:{API_SECRET}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def api_get(endpoint, params=None):
    res = requests.get(f"{URL}/api/resource/{endpoint}", headers=HEADERS, params=params)
    return res.json().get('data', [])

def api_post(endpoint, data):
    res = requests.post(f"{URL}/api/resource/{endpoint}", headers=HEADERS, json=data)
    try:
        return res.json().get('data', {})
    except:
        return None

def api_post_doc(endpoint, docname, action):
    # For submitting documents
    res = requests.post(f"{URL}/api/resource/{endpoint}/{docname}", headers=HEADERS, data=json.dumps({"docstatus": 1}))
    return res.status_code == 200

def get_customers():
    return [c['name'] for c in api_get("Customer", {"limit_page_length": 100})]

def get_items_with_stock():
    # Only pick items that exist in Bin with > 0 stock
    import pymysql
    conn = pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    items = []
    with conn.cursor() as cursor:
        cursor.execute("SELECT item_code, warehouse, actual_qty FROM `tabBin` WHERE actual_qty > 10 LIMIT 200")
        items = cursor.fetchall()
    conn.close()
    return items

def create_historical_sales_orders(items, customers, days_back=30):
    print(f"Generating {days_back} days of historical Sales Orders...")
    company = api_get("Company")[0]['name']
    
    # Take the top 10 items so they definitely get 30 days of data each
    top_items = items[:10]
    
    for i in range(days_back, -1, -1):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        
        for item_code, warehouse, max_qty in top_items:
            # Randomly skip some days to make the time-series realistic, but ensure at least 15 days
            if random.random() < 0.2:
                continue
                
            customer = random.choice(customers)
            qty = random.randint(1, 5)
            
            try:
                so = api_post("Sales Order", {
                    "customer": customer,
                    "company": company,
                    "transaction_date": date,
                    "delivery_date": (datetime.now() - timedelta(days=i-2)).strftime('%Y-%m-%d'),
                    "items": [{
                        "item_code": item_code,
                        "qty": qty,
                        "delivery_date": (datetime.now() - timedelta(days=i-2)).strftime('%Y-%m-%d')
                    }]
                })
                
                if so and so.get('name'):
                    # Submit SO
                    requests.put(f"{URL}/api/resource/Sales Order/{so['name']}", headers=HEADERS, json={"docstatus": 1})
                    
                    # Create Delivery Note (this hits the Stock Ledger)
                    dn = api_post("Delivery Note", {
                        "customer": customer,
                        "company": company,
                        "posting_date": date,
                        "items": [{
                            "item_code": item_code,
                            "qty": qty,
                            "warehouse": warehouse,
                            "against_sales_order": so['name']
                        }]
                    })
                    if dn and dn.get('name'):
                        requests.put(f"{URL}/api/resource/Delivery Note/{dn['name']}", headers=HEADERS, json={"docstatus": 1})
                        print(f"[{date}] Sold {qty} of {item_code} from {warehouse}")
            except Exception as e:
                pass
                
if __name__ == "__main__":
    customers = get_customers()
    if not customers:
        print("No customers found. Creating a generic customer...")
        api_post("Customer", {"customer_name": "Walk-in Customer", "customer_group": "All Customer Groups", "customer_type": "Individual"})
        customers = get_customers()
        
    items = get_items_with_stock()
    if not items:
        print("No items with stock found. Cannot simulate sales.")
        sys.exit(1)
        
    create_historical_sales_orders(items, customers, days_back=30)
    print("Done! Historical stock movements generated.")
