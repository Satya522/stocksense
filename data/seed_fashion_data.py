import os
import random
import requests
import json
from pathlib import Path

# Load env variables (assuming we run from data/ but loading from python/.env)
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent / "python" / "src"))
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent / "python" / ".env"
    load_dotenv(dotenv_path=env_path)
except:
    pass

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
    if res.status_code not in (200, 201):
        print(f"Error POST {endpoint}: {res.text}")
    return res.json().get('data', {})

def api_put(endpoint, docname, data):
    res = requests.put(f"{URL}/api/resource/{endpoint}/{docname}", headers=HEADERS, json=data)
    if res.status_code not in (200, 201):
        print(f"Error PUT {endpoint}: {res.text}")
    return res.json().get('data', {})

print("Fetching Company...")
companies = api_get("Company")
if not companies:
    print("No company found!")
    sys.exit(1)
company_name = companies[0]['name']
print(f"Using Company: {company_name}")

# 1. Create Item Groups
groups = ["Men Apparel", "Women Apparel", "Kids Apparel", "Fashion Accessories", "Footwear"]
for g in groups:
    try:
        api_post("Item Group", {"item_group_name": g, "parent_item_group": "All Item Groups", "is_group": 0})
        print(f"Created Item Group: {g}")
    except:
        pass # Already exists

# 2. Create Warehouses for Go Fashion India
cities = ["Mumbai", "Delhi", "Hyderabad", "Chennai", "Bangalore"]
wh_names = []
for city in cities:
    wh_name = f"Go Fashion {city}"
    try:
        data = api_post("Warehouse", {
            "warehouse_name": wh_name,
            "company": company_name,
            "is_group": 0
        })
        wh_names.append(data.get('name'))
        print(f"Created Warehouse: {wh_name}")
    except Exception as e:
        # Fetch if exists
        wh_docs = api_get("Warehouse", {"filters": json.dumps([["warehouse_name", "=", wh_name]])})
        if wh_docs:
            wh_names.append(wh_docs[0]['name'])
            print(f"Warehouse {wh_name} already exists.")

# 3. Create 100+ Items
types = {
    "Men Apparel": ["T-Shirt", "Shirt", "Jeans", "Trousers", "Jacket", "Kurta"],
    "Women Apparel": ["Top", "Dress", "Jeans", "Skirt", "Saree", "Kurti", "Leggings"],
    "Kids Apparel": ["T-Shirt", "Shorts", "Frock", "Pajamas", "Sweater"],
    "Fashion Accessories": ["Belt", "Wallet", "Sunglasses", "Cap", "Watch", "Handbag"],
    "Footwear": ["Sneakers", "Formal Shoes", "Sandals", "Heels", "Sports Shoes"]
}

colors = ["Black", "White", "Navy", "Red", "Olive", "Grey", "Pink", "Blue", "Beige"]
sizes = ["S", "M", "L", "XL", "XXL", "Free Size"]

items_created = []

print("Generating 120 items...")
for i in range(120):
    group = random.choice(groups)
    type_name = random.choice(types[group])
    color = random.choice(colors)
    size = random.choice(sizes) if group != "Fashion Accessories" else "Free Size"
    
    item_name = f"{color} {type_name} ({size})"
    item_code = f"GF-{group[:3].upper()}-{type_name[:3].upper()}-{i+1:03d}-{size}"
    
    price = random.randint(499, 4999)
    
    item_doc = {
        "item_code": item_code,
        "item_name": item_name,
        "item_group": group,
        "stock_uom": "Nos",
        "is_stock_item": 1,
        "valuation_rate": price * 0.4,  # Cost is 40% of retail
        "standard_rate": price
    }
    
    try:
        created = api_post("Item", item_doc)
        if created:
            items_created.append(item_code)
            # print(f"Created Item: {item_code}")
    except:
        items_created.append(item_code)

print(f"Created/Verified {len(items_created)} items.")

# 4. Set Reorder Levels & Create Stock Entries
print("Generating Stock Entries for Warehouses...")

for wh in wh_names:
    print(f"Processing warehouse: {wh}")
    items_for_receipt = []
    
    # Randomly pick 60 items to stock in this warehouse
    stocked_items = random.sample(items_created, k=60)
    
    for item_code in stocked_items:
        # Set reorder level first
        reorder_qty = random.randint(10, 50)
        try:
            # We must fetch the item, then append to reorder levels
            item_data = api_get(f"Item/{item_code}")
            if item_data:
                # Add reorder level via a PUT
                api_put("Item", item_code, {
                    "reorder_levels": [{
                        "warehouse": wh,
                        "warehouse_reorder_level": reorder_qty,
                        "warehouse_reorder_qty": reorder_qty,
                        "material_request_type": "Purchase"
                    }]
                })
        except:
            pass
        
        # Decide current stock based on reorder to simulate health states
        state = random.choices(["healthy", "warning", "critical"], weights=[50, 30, 20])[0]
        if state == "healthy":
            qty = random.randint(reorder_qty + 5, reorder_qty + 100)
        elif state == "warning":
            qty = random.randint(int(reorder_qty * 0.5), reorder_qty)
        else:
            qty = random.randint(0, int(reorder_qty * 0.5) - 1)
            
        if qty > 0:
            items_for_receipt.append({
                "item_code": item_code,
                "qty": qty,
                "t_warehouse": wh,
                "basic_rate": random.randint(200, 2000) # valuation
            })
            
    # Submit a Material Receipt for this warehouse
    if items_for_receipt:
        try:
            receipt = api_post("Stock Entry", {
                "stock_entry_type": "Material Receipt",
                "purpose": "Material Receipt",
                "company": company_name,
                "items": items_for_receipt
            })
            # Submit it
            if receipt and receipt.get('name'):
                api_put("Stock Entry", receipt['name'], {"docstatus": 1})
                print(f"  -> Submitted Stock Entry for {wh} with {len(items_for_receipt)} items.")
        except Exception as e:
            print(f"  -> Failed Stock Entry for {wh}: {e}")

print("✅ Data seeding complete!")
