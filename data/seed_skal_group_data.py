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
    return res.json().get('data', {})

def api_put(endpoint, docname, data):
    res = requests.put(f"{URL}/api/resource/{endpoint}/{docname}", headers=HEADERS, json=data)
    return res.json().get('data', {})

print("Fetching Default Company...")
companies = api_get("Company")
if not companies:
    print("No company found!")
    sys.exit(1)
company_name = companies[0]['name']
print(f"Building Mega-Conglomerate under: {company_name}")

# --- THE DATA ---
enterprise_data = {
    "SK Industries": {
        "abbr": "SKI",
        "warehouses": [
            "SKI Mumbai Central", "SKI Delhi NCR Hub", "SKI Bengaluru Hub", "SKI Hyderabad Regional", "SKI Chennai DC", "SKI Pune Hub"
        ],
        "retail_stores": [
            "SKI Mumbai Flagship", "SKI Delhi Select", "SKI Bengaluru Indiranagar"
        ],
        "item_groups": ["Fashion & Clothing", "Consumer Electronics", "Home & Lifestyle", "Medical & Wellness", "Accessories"],
        "items": [
            "SK Premium Cotton Shirt", "SK Performance Jacket", "SK Urban Sneakers", "SK Smart Watch X1", "SK Wireless Earbuds Pro", "SK Smart Home Hub", "SK Air Purifier Pro"
        ]
    },
    "SK Manufacturing": {
        "abbr": "SKM",
        "warehouses": ["Pune Raw Material", "Pune Finished Goods", "Vadodara Components", "Chennai Parts DC", "Noida Finished Goods"],
        "plants": ["Pune Robotics Plant", "Vadodara Equipment Plant", "Chennai Automation Plant"],
        "item_groups": ["Industrial Machinery", "Robotics", "Automation Components", "Electrical Components", "Spare Parts"],
        "items": ["SK Industrial Robotic Arm R7", "SK Autonomous Pick Module", "SK Conveyor Control Unit", "SK Industrial Servo Motor", "SK PLC Automation Controller", "SK Vision Inspection Camera"]
    },
    "SK Healthcare": {
        "abbr": "SKH",
        "warehouses": ["Mumbai Medical DC", "Delhi Medical WH", "Bengaluru Healthcare WH", "Hyderabad Medical Hub", "Chennai Healthcare WH"],
        "service_centers": ["Mumbai Tech Center", "Delhi Service Center", "Bengaluru Equipment Center"],
        "item_groups": ["Diagnostic Equipment", "Patient Monitoring", "Medical Devices", "Hospital Supplies", "Healthcare Technology"],
        "items": ["SK Patient Monitor X5", "SK Smart ECG System", "SK Digital Ultrasound Scanner", "SK Portable Oxygen Monitor", "SK ICU Vital Monitor", "SK Smart Infusion Controller"]
    },
    "SK Electronics": {
        "abbr": "SKE",
        "warehouses": ["Bengaluru Electronics WH", "Noida Electronics DC", "Mumbai Consumer Electronics", "Chennai Components WH", "Hyderabad IoT Hub"],
        "experience_centers": ["SKE Bengaluru Experience", "SKE Mumbai Experience", "SKE Delhi Experience"],
        "item_groups": ["Smart Devices", "IoT Products", "Networking Equipment", "Computing Accessories", "Home Electronics"],
        "items": ["SK Smart Display 55", "SK Smart Display 65 Pro", "SK AI Home Hub", "SK WiFi 7 Enterprise Router", "SK Mesh Network Node", "SK IoT Gateway Pro", "SK Smart Security Camera"]
    },
    "SK Mobility": {
        "abbr": "SKMOB",
        "warehouses": ["Pune EV Components", "Bengaluru Battery Hub", "Chennai Mobility Parts", "Delhi Fleet Parts", "Ahmedabad Charging Equip"],
        "service_centers": ["Pune EV Service", "Bengaluru EV Tech Center", "Delhi Fleet Hub"],
        "item_groups": ["EV Components", "Charging Infrastructure", "Fleet Technology", "Battery Systems", "Autonomous Mobility"],
        "items": ["SK EV Charging Station V3", "SK DC Fast Charger 240", "SK Fleet Tracking Gateway", "SK Autonomous Lidar Kit", "SK Battery Management Controller", "SK EV Power Inverter"]
    },
    "SK Food & Consumer": {
        "abbr": "SKFC",
        "warehouses": ["Mumbai FMCG DC", "Pune Food WH", "Nashik Beverage WH", "Delhi Consumer Hub", "Bengaluru FMCG WH"],
        "superstores": ["SKFC Mumbai Superstore", "SKFC Pune Superstore", "SKFC Bengaluru Superstore"],
        "item_groups": ["Packaged Foods", "Beverages", "Personal Care", "Household Products", "Nutrition & Wellness"],
        "items": ["SK Premium Coffee 500g", "SK Organic Green Tea", "SK Energy Drink 500ml", "SK Mineral Water 1L", "SK Protein Nutrition Mix", "SK Herbal Shampoo", "SK Premium Hand Wash"]
    }
}

# 1. Create Parent Warehouses and Sub-Warehouses
print("\n--- Building Warehouse Infrastructure ---")
all_leaf_warehouses = []
for div_name, div_data in enterprise_data.items():
    div_parent = f"{div_name} Group"
    api_post("Warehouse", {"warehouse_name": div_parent, "company": company_name, "is_group": 1})
    
    actual_parent_docs = api_get("Warehouse", {"filters": json.dumps([["warehouse_name", "=", div_parent]])})
    actual_parent = actual_parent_docs[0]['name'] if actual_parent_docs else None

    locations = div_data.get("warehouses", []) + div_data.get("retail_stores", []) + div_data.get("plants", []) + div_data.get("service_centers", []) + div_data.get("experience_centers", []) + div_data.get("superstores", [])
    
    for loc in locations:
        api_post("Warehouse", {"warehouse_name": loc, "company": company_name, "is_group": 0, "parent_warehouse": actual_parent})
        actual_wh = api_get("Warehouse", {"filters": json.dumps([["warehouse_name", "=", loc]])})
        if actual_wh: all_leaf_warehouses.append(actual_wh[0]['name'])

# 2. Create Item Groups & Items
print("\n--- Creating SKU Portfolio ---")
all_items = []
for div_name, div_data in enterprise_data.items():
    for ig in div_data["item_groups"]:
        api_post("Item Group", {"item_group_name": ig, "parent_item_group": "All Item Groups", "is_group": 0})

    for item_name in div_data["items"]:
        item_code = f"{div_data['abbr']}-{item_name[:5].upper()}-{random.randint(100,999)}"
        group = random.choice(div_data["item_groups"])
        
        price = random.randint(1500, 250000)
        item_doc = {
            "item_code": item_code,
            "item_name": item_name,
            "item_group": group,
            "stock_uom": "Nos",
            "is_stock_item": 1,
            "valuation_rate": price * 0.5,
            "standard_rate": price
        }
        api_post("Item", item_doc)
        all_items.append(item_code)

print(f"Total Unique SKUs Created: {len(all_items)}")

# 3. Massive Stock Inward
print("\n--- Pumping Stock into the Conglomerate ---")
for wh in all_leaf_warehouses:
    items_for_receipt = []
    
    # Random 10 to 15 items per warehouse
    stocked_items = random.sample(all_items, k=random.randint(10, 15))
    
    for item_code in stocked_items:
        reorder_qty = random.randint(50, 200)
        api_put("Item", item_code, {
            "reorder_levels": [{
                "warehouse": wh,
                "warehouse_reorder_level": reorder_qty,
                "warehouse_reorder_qty": reorder_qty,
                "material_request_type": "Purchase"
            }]
        })
        
        qty = random.randint(10, reorder_qty + 300)
            
        if qty > 0:
            items_for_receipt.append({
                "item_code": item_code,
                "qty": qty,
                "t_warehouse": wh,
                "basic_rate": random.randint(5000, 100000)
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
        except: pass

print("\n--- Conglomerate Seeded Successfully! ---")
