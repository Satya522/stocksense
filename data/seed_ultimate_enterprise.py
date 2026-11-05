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
print(f"Building ULTIMATE ENTERPRISE ARCHITECTURE for: {company_name}")


# ============================================================
# MASSIVE MASTER DATA INJECTION
# ============================================================

territories = ["North India", "South India", "West India", "East India", "Central India", "Northeast India",
    "Maharashtra", "Gujarat", "Rajasthan", "Delhi NCR", "Uttar Pradesh", "Punjab", "Madhya Pradesh",
    "Karnataka", "Tamil Nadu", "Telangana", "Kerala", "Andhra Pradesh",
    "West Bengal", "Odisha", "Bihar", "Jharkhand", "Assam"]

departments = ["Executive Management", "Finance", "Accounting", "Accounts Payable", "Accounts Receivable",
    "Treasury", "Procurement", "Strategic Sourcing", "Supply Chain", "Logistics", "Warehouse Operations",
    "Inventory Control", "Sales", "Retail Sales", "B2B Sales", "B2C Sales", "Enterprise Sales", "Customer Success",
    "Customer Support", "Marketing", "Digital Marketing", "Product Management", "Engineering", "Software Engineering",
    "Data Engineering", "AI & Machine Learning", "Robotics Engineering", "Electronics Engineering", "Manufacturing",
    "Production Planning", "Quality Assurance", "Quality Control", "Research & Development", "Healthcare Operations",
    "EV Technology", "Retail Operations", "Store Management", "Human Resources", "Talent Acquisition", "Legal",
    "Compliance", "Information Technology", "Cybersecurity", "Facilities", "Administration"]

payment_terms = [
    {"name": "Immediate Payment", "credit_days": 0},
    {"name": "7 Days", "credit_days": 7},
    {"name": "15 Days", "credit_days": 15},
    {"name": "30 Days", "credit_days": 30},
    {"name": "45 Days", "credit_days": 45},
    {"name": "60 Days", "credit_days": 60},
    {"name": "90 Days Enterprise", "credit_days": 90}
]

warehouses = [
    # Manufacturing Plants
    "SKM Pune Robotics Plant", "SKM Vadodara Industrial Plant", "SKM Chennai Automation Plant", "SKM Noida Electronics Assembly Plant",
    "SKM Bengaluru Robotics Plant", "SKH Pune Medical Device Plant", "SKMB Pune EV Components Plant", "SKFC Pune Food Processing Plant",
    # Warehouses
    "SKI Mumbai Central Warehouse", "SKI Delhi NCR Distribution Center", "SKM Pune Raw Material Warehouse", "SKM Pune Finished Goods Warehouse",
    "SKH Mumbai Medical Warehouse", "SKH Delhi Medical Distribution Hub", "SKE Bengaluru Electronics Warehouse", "SKE Noida Distribution Center",
    "SKMB Pune EV Components Warehouse", "SKMB Bengaluru Battery Warehouse", "SKFC Mumbai FMCG Distribution Center", "SKFC Pune Food Warehouse",
    # Retail & Centers
    "SKI Mumbai Phoenix Store", "SKI Mumbai BKC Flagship", "SKI Delhi Select Citywalk", "SKI Bengaluru Indiranagar",
    "SKE Bengaluru Innovation Center", "SKE Mumbai Technology Store", "SKMB Pune EV Service Center", "SKMB Bengaluru EV Technology Center",
    "SKH Mumbai Medical Technology Center", "SKH Delhi Healthcare Service Center"
]

products = [
    ("SK-FSH-001", "Premium Oxford Shirt", "Men's Formal Wear", 2499),
    ("SK-FSH-007", "Urban Performance Jacket", "Winter Wear", 5999),
    ("SK-FSH-015", "SK Urban Runner", "Footwear", 4999),
    ("SKE-002", "SK Smart Watch Ultra", "Smart Watches", 24999),
    ("SKE-005", "SK Enterprise Laptop 14", "Laptops", 89999),
    ("SKE-015", "SK WiFi 7 Enterprise Router", "Networking", 29999),
    ("SKE-024", "SK AI Edge Computing Box", "IoT Devices", 89999),
    ("SKM-001", "SK Industrial Robotic Arm R7", "Industrial Robots", 1850000),
    ("SKM-004", "SK Autonomous Mobile Robot", "Collaborative Robots", 2250000),
    ("SKM-006", "SK Industrial PLC X500", "PLC Systems", 185000),
    ("SKM-014", "SK Industrial Vision Camera", "Machine Vision", 225000),
    ("SKH-001", "SK Smart ECG System", "Diagnostic Equipment", 485000),
    ("SKH-004", "SK Portable Ultrasound Scanner", "Medical Imaging", 1250000),
    ("SKH-010", "SK Healthcare IoT Gateway", "Healthcare IoT", 175000),
    ("SKMB-001", "SK DC Fast Charger 240", "EV Chargers", 850000),
    ("SKMB-008", "SK Autonomous Lidar Kit", "Lidar Systems", 385000),
    ("SKFC-001", "SK Premium Coffee 500g", "Coffee", 499),
    ("SKFC-006", "SK Protein Energy Bar", "Snacks", 120),
]

suppliers = ["Arvind Textile Solutions", "Bengaluru Semiconductor Systems", "Bharat Industrial Components", "MedTech Components India", "Advanced Battery Systems", "DHL Supply Chain Services"]
customers = ["Reliance Retail", "Tata Industrial Systems", "Apollo Healthcare Network", "Fleet Mobility Solutions", "Enterprise Technology Partners"]


# ============================================================
# SEEDING EXECUTION
# ============================================================

print("\n--- 1. Seeding Enterprise Structures (Territories, Departments, Terms) ---")
# Setup Territories
api_post("Territory", {"territory_name": "SKAL Global", "is_group": 1, "parent_territory": "All Territories"})
for t in territories[:5]:
    try: api_post("Territory", {"territory_name": t, "is_group": 0, "parent_territory": "SKAL Global"})
    except: pass

# Setup Departments
api_post("Department", {"department_name": "SKAL Enterprise", "is_group": 1, "parent_department": "All Departments"})
for d in departments:
    try: api_post("Department", {"department_name": d, "company": company_name, "is_group": 0, "parent_department": "SKAL Enterprise"})
    except: pass

# Setup Payment Terms
for term in payment_terms:
    try: api_post("Payment Term", {"payment_term_name": term["name"], "invoice_portion": 100, "credit_days": term["credit_days"]})
    except: pass


print("\n--- 2. Seeding Supplier & Customer Networks ---")
for s in suppliers:
    try: api_post("Supplier", {"supplier_name": s, "supplier_type": "Company"})
    except: pass
for c in customers:
    try: api_post("Customer", {"customer_name": c, "customer_type": "Company"})
    except: pass


print("\n--- 3. Seeding Massive Logistics Tree (Plants, Centers, Retail, WH) ---")
all_leaf_warehouses = []
api_post("Warehouse", {"warehouse_name": "Global Conglomerate Network", "company": company_name, "is_group": 1})
actual_parent_docs = api_get("Warehouse", {"filters": json.dumps([["warehouse_name", "=", "Global Conglomerate Network"]])})
parent_id = actual_parent_docs[0]['name'] if actual_parent_docs else None

for w in warehouses:
    api_post("Warehouse", {"warehouse_name": w, "company": company_name, "is_group": 0, "parent_warehouse": parent_id})
    actual_wh = api_get("Warehouse", {"filters": json.dumps([["warehouse_name", "=", w]])})
    if actual_wh: all_leaf_warehouses.append(actual_wh[0]['name'])


print("\n--- 4. Seeding Ultimate SKU Portfolio ---")
all_item_codes = []
for sku, name, group, price in products:
    try: api_post("Item Group", {"item_group_name": group, "parent_item_group": "All Item Groups", "is_group": 0})
    except: pass
    
    item_doc = {
        "item_code": sku,
        "item_name": name,
        "item_group": group,
        "stock_uom": "Nos",
        "is_stock_item": 1,
        "valuation_rate": price * 0.45,
        "standard_rate": price
    }
    api_post("Item", item_doc)
    all_item_codes.append(sku)


print(f"\n--- 5. Pumping B2B/B2C Stock into {len(all_leaf_warehouses)} Ecosystem Nodes ---")
for wh in all_leaf_warehouses:
    wh_items = random.sample(all_item_codes, k=random.randint(5, len(all_item_codes)))
    items_for_receipt = []
    
    for item_code in wh_items:
        reorder_qty = random.randint(10, 100)
        api_put("Item", item_code, {
            "reorder_levels": [{
                "warehouse": wh,
                "warehouse_reorder_level": reorder_qty,
                "warehouse_reorder_qty": reorder_qty,
                "material_request_type": "Purchase"
            }]
        })
        
        qty = random.randint(5, reorder_qty + 200)
        if qty > 0:
            items_for_receipt.append({
                "item_code": item_code,
                "qty": qty,
                "t_warehouse": wh,
                "basic_rate": random.randint(100, 1000000) # Heavy valuation for enterprise goods
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

print("\n=== ULTIMATE ENTERPRISE ERP SIMULATION SUCCESSFULLY BUILT ===")
