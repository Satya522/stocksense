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
print(f"Building Massive Enterprise Architecture for: {company_name}")

# --- CATALOG DEFINITION ---
enterprise_catalog = {
    "SK Industries": {
        "divisions": {
            "Fashion": ["Men's Formal Wear", "Men's Casual Wear", "Women's Formal Wear", "Women's Casual Wear", "Sportswear", "Kids Wear", "Winter Wear", "Footwear", "Bags & Accessories", "Premium Apparel"],
            "Consumer Electronics": ["Smartphones", "Tablets", "Smart Watches", "Wireless Audio", "Laptops", "Computer Accessories", "Smart Home", "Cameras", "Gaming Accessories", "Networking"],
            "Home & Lifestyle": ["Kitchen Appliances", "Air Purifiers", "Vacuum Cleaners", "Lighting", "Furniture", "Home Automation", "Travel Accessories", "Personal Care Appliances"],
            "Medical & Wellness": ["Blood Pressure Monitors", "Digital Thermometers", "Pulse Oximeters", "Fitness Trackers", "First Aid", "Home Healthcare", "Wellness Devices"]
        },
        "items": [
            {"sku": "SK-FSH-SHIRT-001", "name": "Premium Oxford Shirt", "category": "Men's Formal Wear", "price": 2500},
            {"sku": "SK-FSH-SHIRT-002", "name": "Performance Stretch Shirt", "category": "Men's Formal Wear", "price": 2800},
            {"sku": "SK-FSH-TSHIRT-001", "name": "Premium Cotton T-Shirt", "category": "Men's Casual Wear", "price": 1200},
            {"sku": "SK-FSH-JACKET-001", "name": "Urban Performance Jacket", "category": "Winter Wear", "price": 5500},
            {"sku": "SK-FSH-JACKET-002", "name": "TechShell Waterproof Jacket", "category": "Winter Wear", "price": 7500},
            {"sku": "SK-FSH-JEANS-001", "name": "Premium Slim Denim", "category": "Men's Casual Wear", "price": 3500},
            {"sku": "SK-FSH-DRESS-001", "name": "Executive Women's Dress", "category": "Women's Formal Wear", "price": 4500},
            {"sku": "SK-FSH-HOODIE-001", "name": "Urban Tech Hoodie", "category": "Sportswear", "price": 3200},
            {"sku": "SK-FSH-SHOE-001", "name": "SK Urban Runner", "category": "Footwear", "price": 6000},
            {"sku": "SK-FSH-SHOE-002", "name": "SK Executive Leather Shoe", "category": "Footwear", "price": 8500},
            {"sku": "SK-FSH-BAG-001", "name": "Executive Laptop Backpack", "category": "Bags & Accessories", "price": 4000},
            {"sku": "SK-FSH-BAG-002", "name": "Premium Travel Duffel", "category": "Bags & Accessories", "price": 6500},
            {"sku": "SK-ELE-WATCH-001", "name": "SK Smart Watch X1", "category": "Smart Watches", "price": 12000},
            {"sku": "SK-ELE-WATCH-002", "name": "SK Smart Watch Ultra", "category": "Smart Watches", "price": 25000},
            {"sku": "SK-ELE-EARBUD-001", "name": "SK Wireless Buds Pro", "category": "Wireless Audio", "price": 8000},
            {"sku": "SK-ELE-HEAD-001", "name": "SK ANC Headphones X", "category": "Wireless Audio", "price": 15000},
            {"sku": "SK-ELE-TAB-001", "name": "SK Tab Pro 12", "category": "Tablets", "price": 45000},
            {"sku": "SK-ELE-LAP-001", "name": "SK Enterprise Laptop 14", "category": "Laptops", "price": 85000},
            {"sku": "SK-ELE-LAP-002", "name": "SK Creator Laptop 16", "category": "Laptops", "price": 125000},
            {"sku": "SK-ELE-CAM-001", "name": "SK Smart Security Camera", "category": "Cameras", "price": 6500},
            {"sku": "SK-ELE-HUB-001", "name": "SK AI Home Hub", "category": "Smart Home", "price": 9000},
            {"sku": "SK-ELE-ROUTER-001", "name": "SK WiFi 7 Router", "category": "Networking", "price": 18000},
            {"sku": "SK-HOM-AC-001", "name": "SK Smart Air Purifier", "category": "Air Purifiers", "price": 22000},
            {"sku": "SK-HOM-VAC-001", "name": "SK Robotic Vacuum Pro", "category": "Vacuum Cleaners", "price": 35000},
            {"sku": "SK-HOM-LIGHT-001", "name": "SK Smart Ambient Light", "category": "Lighting", "price": 2500},
            {"sku": "SK-HOM-KITCHEN-001", "name": "SK Smart Induction System", "category": "Kitchen Appliances", "price": 12000},
            {"sku": "SK-HOM-COFFEE-001", "name": "SK Smart Coffee Machine", "category": "Kitchen Appliances", "price": 45000},
            {"sku": "SK-HOM-AUTO-001", "name": "SK Home Automation Gateway", "category": "Home Automation", "price": 15000},
            {"sku": "SK-MED-BP-001", "name": "SK Digital BP Monitor", "category": "Blood Pressure Monitors", "price": 2500},
            {"sku": "SK-MED-OXI-001", "name": "SK Pulse Oximeter Pro", "category": "Pulse Oximeters", "price": 1500},
            {"sku": "SK-MED-TEMP-001", "name": "SK Infrared Thermometer", "category": "Digital Thermometers", "price": 1800},
            {"sku": "SK-MED-ECG-001", "name": "SK Portable ECG Monitor", "category": "Home Healthcare", "price": 15000},
            {"sku": "SK-MED-HEALTH-001", "name": "SK Wellness Monitoring Kit", "category": "Wellness Devices", "price": 8500}
        ],
        "warehouses": [
            "SKI Mumbai Central Warehouse", "SKI Delhi NCR Distribution Hub", "SKI Bengaluru Fulfillment Center",
            "SKI Hyderabad Regional Warehouse", "SKI Chennai Distribution Center", "SKI Kolkata Warehouse",
            "SKI Pune Inventory Hub", "SKI Ahmedabad Warehouse", "SKI Jaipur Regional Warehouse", "SKI Lucknow Distribution Hub",
            "SK Industries Mumbai Flagship", "SK Industries Delhi Select Citywalk", "SK Industries Bengaluru Indiranagar",
            "SK Industries Pune Koregaon Park", "SK Industries Hyderabad Banjara Hills", "SK Industries Chennai Phoenix Mall"
        ]
    },
    "SK Manufacturing": {
        "divisions": {
            "Industrial Automation": ["PLC Systems", "Industrial Controllers", "Servo Systems", "Motion Controllers", "Industrial Sensors", "Machine Vision"],
            "Robotics": ["Robotic Arms", "Collaborative Robots", "Robot Grippers", "AGV Systems", "AMR Systems", "Robotics Controllers"],
            "Industrial Components": ["Motors", "Gearboxes", "Bearings", "Control Panels", "Power Supplies", "Electrical Components"],
            "Safety Systems": ["Emergency Stop Systems", "Safety Controllers", "Industrial Light Curtains", "Safety Sensors"]
        },
        "items": [
            {"sku": "SKM-ROB-ARM-001", "name": "SK Industrial Robotic Arm R7", "category": "Robotic Arms", "price": 850000},
            {"sku": "SKM-ROB-ARM-002", "name": "SK Heavy Payload Robot R12", "category": "Robotic Arms", "price": 1250000},
            {"sku": "SKM-ROB-COBOT-001", "name": "SK Collaborative Robot C5", "category": "Collaborative Robots", "price": 650000},
            {"sku": "SKM-ROB-GRIP-001", "name": "SK Adaptive Robot Gripper", "category": "Robot Grippers", "price": 45000},
            {"sku": "SKM-ROB-AGV-001", "name": "SK Autonomous Guided Vehicle", "category": "AGV Systems", "price": 450000},
            {"sku": "SKM-ROB-AMR-001", "name": "SK Autonomous Mobile Robot", "category": "AMR Systems", "price": 550000},
            {"sku": "SKM-PLC-001", "name": "SK Industrial PLC X500", "category": "PLC Systems", "price": 25000},
            {"sku": "SKM-SERVO-001", "name": "SK Servo Motor 5KW", "category": "Servo Systems", "price": 35000},
            {"sku": "SKM-SERVO-002", "name": "SK Servo Drive V4", "category": "Servo Systems", "price": 28000},
            {"sku": "SKM-VISION-001", "name": "SK Machine Vision Camera", "category": "Machine Vision", "price": 85000},
            {"sku": "SKM-SENSOR-001", "name": "SK Industrial Lidar Sensor", "category": "Industrial Sensors", "price": 120000},
            {"sku": "SKM-SENSOR-002", "name": "SK Precision Temperature Sensor", "category": "Industrial Sensors", "price": 8000},
            {"sku": "SKM-MOTOR-001", "name": "SK Industrial AC Motor", "category": "Motors", "price": 45000},
            {"sku": "SKM-GEAR-001", "name": "SK Precision Gearbox", "category": "Gearboxes", "price": 32000},
            {"sku": "SKM-BEAR-001", "name": "SK Heavy Load Bearing", "category": "Bearings", "price": 5000},
            {"sku": "SKM-CTRL-001", "name": "SK Industrial Control Panel", "category": "Control Panels", "price": 150000}
        ],
        "warehouses": [
            "Pune Raw Material Warehouse", "Pune Finished Goods Warehouse", "Vadodara Components Warehouse",
            "Chennai Parts Distribution Center", "Noida Finished Goods Hub", "Bengaluru Spare Parts Warehouse"
        ]
    },
    "SK Healthcare": {
        "divisions": {
            "Diagnostics": ["ECG Systems", "Patient Monitoring", "Imaging Equipment", "Blood Analysis", "Diagnostic Sensors"],
            "Hospital Equipment": ["Smart Hospital Beds", "Infusion Systems", "ICU Equipment", "Medical Furniture"],
            "Digital Health": ["Remote Patient Monitoring", "Healthcare IoT", "Clinical Data Systems", "Telemedicine Equipment"]
        },
        "items": [
            {"sku": "SKH-ECG-001", "name": "SK Smart ECG System", "category": "ECG Systems", "price": 125000},
            {"sku": "SKH-MON-001", "name": "SK ICU Vital Monitor", "category": "Patient Monitoring", "price": 250000},
            {"sku": "SKH-MON-002", "name": "SK Bedside Patient Monitor", "category": "Patient Monitoring", "price": 85000},
            {"sku": "SKH-IMG-001", "name": "SK Portable Ultrasound Scanner", "category": "Imaging Equipment", "price": 450000},
            {"sku": "SKH-BLD-001", "name": "SK Digital Blood Analyzer", "category": "Blood Analysis", "price": 850000},
            {"sku": "SKH-BED-001", "name": "SK Smart Medical Bed", "category": "Smart Hospital Beds", "price": 180000},
            {"sku": "SKH-INF-001", "name": "SK Smart Infusion Controller", "category": "Infusion Systems", "price": 45000},
            {"sku": "SKH-REMOTE-001", "name": "SK Remote Patient Monitor", "category": "Remote Patient Monitoring", "price": 35000},
            {"sku": "SKH-IOT-001", "name": "SK Healthcare IoT Gateway", "category": "Healthcare IoT", "price": 25000},
            {"sku": "SKH-DATA-001", "name": "SK Clinical Data Gateway", "category": "Clinical Data Systems", "price": 150000}
        ],
        "warehouses": [
            "Mumbai Medical Distribution Center", "Delhi Medical Warehouse", "Bengaluru Healthcare Warehouse",
            "Hyderabad Medical Supplies Hub", "Chennai Healthcare Warehouse", "Kolkata Medical Distribution Center"
        ]
    },
    "SK Electronics": {
        "divisions": {
            "Computing": ["Business Laptops", "Creator Laptops", "Mini PCs", "Workstations", "Docking Stations"],
            "Smart Home": ["Smart Displays", "Smart Speakers", "Security Cameras", "Smart Sensors", "Home Hubs"],
            "Networking": ["Enterprise Routers", "WiFi Access Points", "Mesh Systems", "Network Switches", "IoT Gateways"]
        },
        "items": [
            {"sku": "SKE-LAP-001", "name": "SK Business Laptop 14", "category": "Business Laptops", "price": 65000},
            {"sku": "SKE-LAP-002", "name": "SK Creator Laptop 16", "category": "Creator Laptops", "price": 115000},
            {"sku": "SKE-PC-001", "name": "SK Mini PC Enterprise", "category": "Mini PCs", "price": 45000},
            {"sku": "SKE-DOCK-001", "name": "SK Thunderbolt Dock Pro", "category": "Docking Stations", "price": 18000},
            {"sku": "SKE-DISPLAY-001", "name": "SK Smart Display 55", "category": "Smart Displays", "price": 45000},
            {"sku": "SKE-DISPLAY-002", "name": "SK Smart Display 65 Pro", "category": "Smart Displays", "price": 85000},
            {"sku": "SKE-CAM-001", "name": "SK AI Security Camera", "category": "Security Cameras", "price": 8500},
            {"sku": "SKE-HUB-001", "name": "SK AI Home Hub", "category": "Home Hubs", "price": 12000},
            {"sku": "SKE-ROUTER-001", "name": "SK WiFi 7 Enterprise Router", "category": "Enterprise Routers", "price": 25000},
            {"sku": "SKE-AP-001", "name": "SK Enterprise Access Point", "category": "WiFi Access Points", "price": 15000},
            {"sku": "SKE-SWITCH-001", "name": "SK 48-Port Managed Switch", "category": "Network Switches", "price": 35000}
        ],
        "warehouses": [
            "Bengaluru Electronics Warehouse", "Noida Electronics Distribution Center", "Mumbai Consumer Electronics Hub",
            "Chennai Components Warehouse", "Hyderabad IoT Distribution Hub"
        ]
    },
    "SK Mobility": {
        "divisions": {
            "EV Systems": ["EV Charging", "Battery Systems", "Power Electronics", "Vehicle Electronics"],
            "Fleet Technology": ["Fleet Tracking", "Telematics", "Fleet Cameras", "Energy Management"],
            "Autonomous Mobility": ["Lidar Systems", "Radar Systems", "Parking Sensors", "Autonomous Controllers"]
        },
        "items": [
            {"sku": "SKMOB-CHG-001", "name": "SK DC Fast Charger 240", "category": "EV Charging", "price": 450000},
            {"sku": "SKMOB-CHG-002", "name": "SK Smart AC Charger 22KW", "category": "EV Charging", "price": 65000},
            {"sku": "SKMOB-BMS-001", "name": "SK Battery Management Controller", "category": "Battery Systems", "price": 35000},
            {"sku": "SKMOB-INV-001", "name": "SK EV Power Inverter", "category": "Power Electronics", "price": 85000},
            {"sku": "SKMOB-TEL-001", "name": "SK Vehicle Telematics Unit", "category": "Telematics", "price": 15000},
            {"sku": "SKMOB-CAM-001", "name": "SK Fleet AI Camera", "category": "Fleet Cameras", "price": 12000},
            {"sku": "SKMOB-LIDAR-001", "name": "SK Autonomous Lidar Kit", "category": "Lidar Systems", "price": 180000},
            {"sku": "SKMOB-RADAR-001", "name": "SK Automotive Radar Module", "category": "Radar Systems", "price": 45000},
            {"sku": "SKMOB-PARK-001", "name": "SK Autonomous Parking Sensor", "category": "Parking Sensors", "price": 8500}
        ],
        "warehouses": [
            "Pune EV Components Warehouse", "Bengaluru Battery Components Hub", "Chennai Mobility Parts Warehouse",
            "Delhi Fleet Parts Distribution Center", "Ahmedabad Charging Equipment Warehouse"
        ]
    },
    "SK Food & Consumer": {
        "divisions": {
            "Packaged Foods": ["Snacks", "Breakfast Foods", "Ready-to-Eat", "Organic Foods", "Premium Foods"],
            "Beverages": ["Coffee", "Tea", "Energy Drinks", "Juices", "Mineral Water"],
            "Personal Care": ["Hair Care", "Skin Care", "Oral Care", "Bath & Body"],
            "Household": ["Surface Cleaners", "Laundry Care", "Kitchen Care", "Home Essentials"]
        },
        "items": [
            {"sku": "SKFC-SNK-001", "name": "SK Premium Snack Box", "category": "Snacks", "price": 450},
            {"sku": "SKFC-SNK-002", "name": "SK Protein Energy Bar", "category": "Snacks", "price": 120},
            {"sku": "SKFC-ORG-001", "name": "SK Organic Breakfast Mix", "category": "Organic Foods", "price": 350},
            {"sku": "SKFC-COF-001", "name": "SK Premium Coffee 500g", "category": "Coffee", "price": 850},
            {"sku": "SKFC-TEA-001", "name": "SK Organic Green Tea", "category": "Tea", "price": 450},
            {"sku": "SKFC-ENG-001", "name": "SK Energy Drink 500ml", "category": "Energy Drinks", "price": 150},
            {"sku": "SKFC-WAT-001", "name": "SK Premium Mineral Water", "category": "Mineral Water", "price": 60},
            {"sku": "SKFC-SHAM-001", "name": "SK Herbal Shampoo", "category": "Hair Care", "price": 350},
            {"sku": "SKFC-SKIN-001", "name": "SK Natural Face Cleanser", "category": "Skin Care", "price": 450},
            {"sku": "SKFC-ORAL-001", "name": "SK Advanced Toothpaste", "category": "Oral Care", "price": 180},
            {"sku": "SKFC-CLEAN-001", "name": "SK Surface Cleaner Pro", "category": "Surface Cleaners", "price": 250},
            {"sku": "SKFC-LAUNDRY-001", "name": "SK Premium Laundry Liquid", "category": "Laundry Care", "price": 450}
        ],
        "warehouses": [
            "Mumbai FMCG Distribution Center", "Pune Food Warehouse", "Nashik Beverage Warehouse",
            "Delhi Consumer Distribution Hub", "Bengaluru FMCG Warehouse", "Hyderabad Personal Care Warehouse",
            "Kolkata Distribution Center", "SK Food & Consumer Mumbai Superstore", "SK Food & Consumer Pune Superstore"
        ]
    }
}

suppliers_list = [
    "Arvind Textile Solutions", "Raymond Industrial Fabrics", "Gujarat Premium Textiles", "Mumbai Apparel Manufacturing",
    "Bengaluru Semiconductor Systems", "Noida Electronics Components", "Chennai PCB Technologies", "Pune Embedded Systems",
    "Bharat Industrial Components", "Precision Motion Systems", "Advanced Servo Technologies", "Industrial Automation India",
    "MedTech Components India", "Precision Medical Systems", "Global Healthcare Instruments", "Delhi Hospital Supplies",
    "Advanced Battery Systems", "EV Power Electronics India", "Automotive Sensor Technologies", "Global Charging Infrastructure",
    "Western India Food Processing", "Organic Ingredients India", "Nashik Beverage Suppliers", "National FMCG Packaging",
    "BlueDart Enterprise Logistics", "DHL Supply Chain Services", "National Distribution Network", "Metro Freight Solutions",
    "Cloud Infrastructure Systems", "Enterprise Networking Solutions", "AI Computing Technologies", "Global Data Center Systems"
]

customers_list = [
    "Reliance Retail", "Croma Retail Network", "Vijay Sales", "Metro Lifestyle Retail", "National Supermarket Network",
    "Tata Enterprise Systems", "Mahindra Industrial Group", "Aditya Enterprise Solutions", "Global Manufacturing Partners",
    "National Infrastructure Corporation", "Apollo Healthcare Network", "Fortis Medical Group", "Max Healthcare",
    "Narayana Health", "Regional Hospital Network", "Fleet Mobility Solutions", "National Logistics Network",
    "Urban Mobility Operators", "Corporate Fleet Services", "Enterprise Technology Partners", "Corporate IT Procurement",
    "Smart Infrastructure Solutions", "Digital Transformation Partners", "North India Distribution Network",
    "South India Distribution Network", "West India Distribution Network", "East India Distribution Network",
    "Government Medical Procurement", "Public Infrastructure Authority", "State Technology Procurement", "National Industrial Procurement"
]

# ==========================================
# 1. B2B Entities: Suppliers and Customers
# ==========================================
print("\n--- Generating Enterprise B2B Ecosystem ---")
def create_customer(name):
    try: api_post("Customer", {"customer_name": name, "customer_type": "Company", "customer_group": "Commercial"})
    except: pass

def create_supplier(name):
    try: api_post("Supplier", {"supplier_name": name, "supplier_type": "Company", "supplier_group": "Hardware"})
    except: pass

for s in suppliers_list: create_supplier(s)
for c in customers_list: create_customer(c)
print(f"Added {len(suppliers_list)} Suppliers & {len(customers_list)} Enterprise Customers")


# ==========================================
# 2. Warehouses & Item Groups
# ==========================================
print("\n--- Building Deep Logistics & Catalog Hierarchy ---")
all_leaf_warehouses = []
all_skus = []

for company, data in enterprise_catalog.items():
    # Parent Warehouse for Company
    group_wh = f"{company} Group WH"
    api_post("Warehouse", {"warehouse_name": group_wh, "company": company_name, "is_group": 1})
    actual_parent = api_get("Warehouse", {"filters": json.dumps([["warehouse_name", "=", group_wh]])})
    parent_id = actual_parent[0]['name'] if actual_parent else None
    
    # Leaf Warehouses
    for wh_name in data["warehouses"]:
        api_post("Warehouse", {"warehouse_name": wh_name, "company": company_name, "is_group": 0, "parent_warehouse": parent_id})
        actual_wh = api_get("Warehouse", {"filters": json.dumps([["warehouse_name", "=", wh_name]])})
        if actual_wh: all_leaf_warehouses.append(actual_wh[0]['name'])

    # Item Groups & Nested Divisions
    for div, subcats in data["divisions"].items():
        api_post("Item Group", {"item_group_name": div, "parent_item_group": "All Item Groups", "is_group": 1})
        for subcat in subcats:
            api_post("Item Group", {"item_group_name": subcat, "parent_item_group": div, "is_group": 0})

    # Items
    for item in data["items"]:
        item_doc = {
            "item_code": item["sku"],
            "item_name": item["name"],
            "item_group": item["category"],
            "stock_uom": "Nos",
            "is_stock_item": 1,
            "valuation_rate": item["price"] * 0.45,
            "standard_rate": item["price"]
        }
        api_post("Item", item_doc)
        all_skus.append(item["sku"])


# ==========================================
# 3. Massive B2B / B2C Stock Simulation
# ==========================================
print(f"\n--- Inwarding Massive Stock across {len(all_leaf_warehouses)} Warehouses ---")

for wh in all_leaf_warehouses:
    # Find items that somewhat match this warehouse's division or just randomize to simulate complex supply chains
    wh_items = random.sample(all_skus, k=random.randint(15, 30))
    items_for_receipt = []
    
    for item_code in wh_items:
        # Set Reorder Level
        reorder_qty = random.randint(50, 500)
        api_put("Item", item_code, {
            "reorder_levels": [{
                "warehouse": wh,
                "warehouse_reorder_level": reorder_qty,
                "warehouse_reorder_qty": reorder_qty,
                "material_request_type": "Purchase"
            }]
        })
        
        # Determine stock level (Healthy, Warning, Critical)
        state = random.choices(["healthy", "warning", "critical"], weights=[50, 30, 20])[0]
        if state == "healthy": qty = random.randint(reorder_qty + 20, reorder_qty + 800)
        elif state == "warning": qty = random.randint(int(reorder_qty * 0.5), reorder_qty)
        else: qty = random.randint(0, int(reorder_qty * 0.4))
        
        if qty > 0:
            items_for_receipt.append({
                "item_code": item_code,
                "qty": qty,
                "t_warehouse": wh,
                "basic_rate": random.randint(100, 250000)
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

print("\n--- Massive Enterprise Data Simulation Complete! ---")
