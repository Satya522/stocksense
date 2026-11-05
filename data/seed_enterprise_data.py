import os
import random
import requests
import json
from pathlib import Path
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
        pass # Silently fail on duplicates
    return res.json().get('data', {})

def api_put(endpoint, docname, data):
    res = requests.put(f"{URL}/api/resource/{endpoint}/{docname}", headers=HEADERS, json=data)
    return res.json().get('data', {})

print("Fetching Company...")
companies = api_get("Company")
if not companies:
    print("No company found!")
    sys.exit(1)
company_name = companies[0]['name']
print(f"Building Enterprise Architecture for: {company_name}")

# 1. Create Enterprise Warehouse Hierarchy
print("Building Multi-Tier Global Warehouse Tree...")
hierarchy = {
    "Global Distribution Center": {
        "APAC Region": {
            "National Hub - India": ["North Zone (Delhi)", "West Zone (Mumbai)", "South Zone (Bangalore)"]
        },
        "EMEA Region": {
            "EU Hub (Frankfurt)": [],
            "UK Hub (London)": []
        },
        "NA Region": {
            "East Coast Hub (NY)": [],
            "West Coast Hub (SF)": []
        }
    }
}

leaf_warehouses = []

def create_warehouse_tree(node, parent=None):
    if isinstance(node, dict):
        for wh, children in node.items():
            wh_full = f"{wh} - {company_name[:4].upper()}" if len(company_name) > 3 else f"{wh} - {company_name}"
            try:
                api_post("Warehouse", {
                    "warehouse_name": wh,
                    "company": company_name,
                    "is_group": 1, # Group warehouse
                    "parent_warehouse": parent
                })
            except: pass
            
            # Fetch actual name for linking
            actual_wh = api_get("Warehouse", {"filters": json.dumps([["warehouse_name", "=", wh]])})
            if actual_wh:
                create_warehouse_tree(children, actual_wh[0]['name'])
    elif isinstance(node, list):
        for wh in node:
            try:
                api_post("Warehouse", {
                    "warehouse_name": wh,
                    "company": company_name,
                    "is_group": 0, # Leaf warehouse
                    "parent_warehouse": parent
                })
            except: pass
            
            actual_wh = api_get("Warehouse", {"filters": json.dumps([["warehouse_name", "=", wh]])})
            if actual_wh:
                leaf_warehouses.append(actual_wh[0]['name'])

# Create root parent if needed, then build tree
root_wh_docs = api_get("Warehouse", {"filters": json.dumps([["warehouse_name", "=", "Global Distribution Center"]])})
root_wh_name = root_wh_docs[0]['name'] if root_wh_docs else ""
if not root_wh_name:
    api_post("Warehouse", {"warehouse_name": "Global Distribution Center", "company": company_name, "is_group": 1})
    root_wh_docs = api_get("Warehouse", {"filters": json.dumps([["warehouse_name", "=", "Global Distribution Center"]])})
    if root_wh_docs: root_wh_name = root_wh_docs[0]['name']

create_warehouse_tree(hierarchy["Global Distribution Center"], root_wh_name)


# 2. High-Tech Item Groups
print("Creating High-Tech Enterprise SKUs...")
groups = ["Smart Home Automation", "Drones & Robotics", "Enterprise Computing", "Energy Storage"]
for g in groups:
    api_post("Item Group", {"item_group_name": g, "parent_item_group": "All Item Groups", "is_group": 0})

types = {
    "Smart Home Automation": ["Smart Hub AI", "Biometric Lock", "Thermal Sensor", "Smart Relay"],
    "Drones & Robotics": ["Inspection Drone Quad", "Delivery Bot V2", "Automated Arm", "Lidar Module"],
    "Enterprise Computing": ["Blade Server 64 Core", "AI Edge Workstation", "100G Network Switch", "NVMe Storage Array"],
    "Energy Storage": ["Grid Inverter 10kW", "LiFePO4 Rack", "Solar Microinverter", "Power Controller"]
}

items_created = []
print("Generating Premium Enterprise Items...")
for group, variants in types.items():
    for variant in variants:
        # Create 3 tiers (Basic, Pro, Enterprise) for each variant
        for tier in ["Basic", "Pro", "Enterprise"]:
            item_name = f"{variant} - {tier} Edition"
            item_code = f"NX-{group[:3].upper()}-{variant[:3].upper()}-{tier[:1].upper()}-{random.randint(100,999)}"
            
            price = random.randint(15000, 450000) if group == "Enterprise Computing" else random.randint(5000, 150000)
            
            item_doc = {
                "item_code": item_code,
                "item_name": item_name,
                "item_group": group,
                "stock_uom": "Nos",
                "is_stock_item": 1,
                "valuation_rate": price * 0.6,
                "standard_rate": price
            }
            
            api_post("Item", item_doc)
            items_created.append(item_code)

print(f"Created {len(items_created)} Enterprise items.")

# 3. Stocking the Global Hubs
print("Stocking the global warehouses...")
for wh in leaf_warehouses:
    items_for_receipt = []
    
    # Stock 30 random high-tech items per hub
    stocked_items = random.sample(items_created, k=30)
    
    for item_code in stocked_items:
        reorder_qty = random.randint(20, 150)
        api_put("Item", item_code, {
            "reorder_levels": [{
                "warehouse": wh,
                "warehouse_reorder_level": reorder_qty,
                "warehouse_reorder_qty": reorder_qty,
                "material_request_type": "Purchase"
            }]
        })
        
        # Tech stocks move fast, keep 40% healthy, 40% warning, 20% critical
        state = random.choices(["healthy", "warning", "critical"], weights=[40, 40, 20])[0]
        if state == "healthy": qty = random.randint(reorder_qty + 10, reorder_qty + 500)
        elif state == "warning": qty = random.randint(int(reorder_qty * 0.4), reorder_qty)
        else: qty = random.randint(0, int(reorder_qty * 0.4) - 1)
            
        if qty > 0:
            items_for_receipt.append({
                "item_code": item_code,
                "qty": qty,
                "t_warehouse": wh,
                "basic_rate": random.randint(5000, 250000)
            })
            
    if items_for_receipt:
        try:
            receipt = api_post("Stock Entry", {
                "stock_entry_type": "Material Receipt",
                "purpose": "Material Receipt",
                "company": company_name,
                "items": items_for_receipt
            })
            if receipt and receipt.get('name'):
                api_put("Stock Entry", receipt['name'], {"docstatus": 1})
        except:
            pass

print("✅ Enterprise Architecture successfully built in ERPNext!")
