import os
import random
import requests
import json
from pathlib import Path
import sys
import time

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
companies_db = api_get("Company")
if not companies_db:
    print("No company found!")
    sys.exit(1)
company_name = companies_db[0]['name']
print(f"Building EXACT ENTERPRISE ARCHITECTURE for: {company_name}")

# ============================================================
# MASSIVE USER PROVIDED DATA (FULL)
# ============================================================
sk_industries_stores = [
    "SKI Mumbai Phoenix Store", "SKI Mumbai BKC Flagship", "SKI Mumbai Andheri Store", "SKI Mumbai Thane Store", "SKI Navi Mumbai Store",
    "SKI Pune Koregaon Park", "SKI Pune Viman Nagar", "SKI Pune Hinjewadi Store", "SKI Nashik Central Store", "SKI Nagpur Fashion Hub",
    "SKI Delhi Select Citywalk", "SKI Delhi Connaught Place", "SKI Delhi Saket Store", "SKI Gurugram Cyber Hub", "SKI Gurugram Ambience Mall",
    "SKI Noida Sector 18", "SKI Noida Mall Store", "SKI Faridabad Retail Center", "SKI Ahmedabad CG Road", "SKI Ahmedabad SG Highway",
    "SKI Surat VR Mall", "SKI Vadodara Central", "SKI Rajkot Premium Store", "SKI Jaipur Malviya Nagar", "SKI Jaipur World Trade Park",
    "SKI Udaipur Retail Center", "SKI Lucknow Hazratganj", "SKI Lucknow Phoenix Palassio", "SKI Kanpur Mall Store", "SKI Noida Premium Experience",
    "SKI Bengaluru Indiranagar", "SKI Bengaluru Whitefield", "SKI Bengaluru Koramangala", "SKI Chennai Phoenix Mall", "SKI Chennai T Nagar",
    "SKI Hyderabad Banjara Hills", "SKI Hyderabad Jubilee Hills", "SKI Kochi Lulu Mall", "SKI Coimbatore Retail Hub",
    "SKI Kolkata Park Street", "SKI Kolkata Salt Lake", "SKI Bhubaneswar Mall Store", "SKI Patna Retail Hub"
]

sk_electronics_stores = [
    "SKE Bengaluru Innovation Center", "SKE Bengaluru Koramangala Store", "SKE Bengaluru Whitefield Experience Center",
    "SKE Mumbai Technology Store", "SKE Mumbai BKC Experience Center", "SKE Delhi Technology Flagship", "SKE Gurugram Cyber Hub",
    "SKE Noida Electronics Center", "SKE Pune Technology Store", "SKE Hyderabad Innovation Center", "SKE Chennai Technology Store",
    "SKE Kolkata Digital Experience Center", "SKE Ahmedabad Smart Home Center", "SKE Jaipur Technology Store", "SKE Chandigarh Experience Center"
]

sk_mobility_centers = [
    "SKMB Pune EV Service Center", "SKMB Mumbai EV Service Center", "SKMB Bengaluru EV Technology Center", "SKMB Chennai Mobility Center",
    "SKMB Hyderabad EV Center", "SKMB Delhi Fleet Service Hub", "SKMB Gurugram Fleet Center", "SKMB Ahmedabad EV Support Center",
    "SKMB Surat Charging Center", "SKMB Jaipur Mobility Center", "SKMB Noida Autonomous Mobility Lab", "SKMB Nagpur EV Service Center"
]

sk_healthcare_centers = [
    "SKH Mumbai Medical Technology Center", "SKH Delhi Healthcare Service Center", "SKH Bengaluru Medical Equipment Center",
    "SKH Hyderabad Diagnostics Center", "SKH Chennai Healthcare Center", "SKH Kolkata Medical Distribution Center",
    "SKH Pune Medical Technology Center", "SKH Ahmedabad Healthcare Center", "SKH Jaipur Medical Service Center", "SKH Lucknow Healthcare Center"
]

manufacturing_plants = [
    "SKM Pune Robotics Plant", "SKM Vadodara Industrial Plant", "SKM Chennai Automation Plant", "SKM Noida Electronics Assembly Plant",
    "SKM Bengaluru Robotics Plant", "SKM Hyderabad Control Systems Plant", "SKE Noida Electronics Manufacturing Plant",
    "SKE Chennai Display Assembly Plant", "SKE Bengaluru IoT Manufacturing Plant", "SKH Pune Medical Device Plant",
    "SKH Hyderabad Diagnostic Equipment Plant", "SKMB Pune EV Components Plant", "SKMB Chennai Power Electronics Plant",
    "SKMB Ahmedabad Charging Equipment Plant", "SKFC Pune Food Processing Plant", "SKFC Nashik Beverage Plant",
    "SKFC Hyderabad Personal Care Plant", "SKFC Kolkata Consumer Products Plant"
]

warehouses = [
    "SKI Mumbai Central Warehouse", "SKI Mumbai Retail Warehouse", "SKI Pune Distribution Hub", "SKI Delhi NCR Distribution Center",
    "SKI Bengaluru Fulfillment Center", "SKI Hyderabad Regional Warehouse", "SKI Chennai Distribution Center", "SKI Kolkata Warehouse",
    "SKI Ahmedabad Warehouse", "SKI Jaipur Regional Warehouse", "SKI Lucknow Distribution Hub", "SKI Nagpur Central Warehouse",
    "SKM Pune Raw Material Warehouse", "SKM Pune Finished Goods Warehouse", "SKM Vadodara Components Warehouse", "SKM Chennai Parts Warehouse",
    "SKM Noida Assembly Warehouse", "SKM Bengaluru Robotics Warehouse", "SKM Hyderabad Industrial Warehouse", "SKH Mumbai Medical Warehouse",
    "SKH Delhi Medical Distribution Hub", "SKH Bengaluru Healthcare Warehouse", "SKH Hyderabad Medical Supplies Hub", "SKH Chennai Medical Warehouse",
    "SKH Kolkata Healthcare Warehouse", "SKH Pune Diagnostics Warehouse", "SKE Bengaluru Electronics Warehouse", "SKE Noida Distribution Center",
    "SKE Mumbai Consumer Electronics Hub", "SKE Chennai Components Warehouse", "SKE Hyderabad IoT Distribution Hub", "SKE Delhi Technology Warehouse",
    "SKMB Pune EV Components Warehouse", "SKMB Bengaluru Battery Warehouse", "SKMB Chennai Mobility Parts Warehouse", "SKMB Delhi Fleet Parts Warehouse",
    "SKMB Ahmedabad Charging Equipment Warehouse", "SKMB Hyderabad EV Warehouse", "SKFC Mumbai FMCG Distribution Center", "SKFC Pune Food Warehouse",
    "SKFC Nashik Beverage Warehouse", "SKFC Delhi Consumer Distribution Hub", "SKFC Bengaluru FMCG Warehouse", "SKFC Hyderabad Personal Care Warehouse",
    "SKFC Kolkata Distribution Center"
]

item_groups = {
    "Fashion": ["Men's Formal Wear", "Men's Casual Wear", "Women's Formal Wear", "Women's Casual Wear", "Kids Wear", "Sportswear", "Winter Wear", "Premium Apparel", "Footwear", "Bags", "Travel Accessories", "Fashion Accessories"],
    "Electronics": ["Smartphones", "Tablets", "Laptops", "Desktop Computers", "Monitors", "Smart Watches", "Wireless Audio", "Cameras", "Gaming", "Computer Accessories", "Smart Home", "Networking", "IoT Devices"],
    "Industrial": ["Industrial Robots", "Collaborative Robots", "PLC Systems", "Servo Systems", "Motion Controllers", "Industrial Sensors", "Machine Vision", "Motors", "Gearboxes", "Bearings", "Control Panels", "Power Supplies", "Industrial Safety", "Spare Parts"],
    "Healthcare": ["Diagnostic Equipment", "Patient Monitoring", "Medical Imaging", "Laboratory Equipment", "Hospital Beds", "Infusion Systems", "Medical Sensors", "Healthcare IoT", "Remote Patient Monitoring", "Medical Consumables"],
    "Mobility": ["EV Chargers", "Battery Systems", "Power Electronics", "Vehicle Electronics", "Fleet Tracking", "Telematics", "Fleet Cameras", "Lidar Systems", "Radar Systems", "Autonomous Systems", "Charging Accessories", "EV Spare Parts"],
    "Food & Consumer": ["Packaged Foods", "Snacks", "Breakfast Foods", "Ready-to-Eat", "Organic Foods", "Coffee", "Tea", "Juices", "Energy Drinks", "Mineral Water", "Hair Care", "Skin Care", "Oral Care", "Bath & Body", "Household Cleaning", "Laundry Care", "Kitchen Care", "Wellness"]
}

products = [
    # Fashion
    ("SK-FSH-001", "Premium Oxford Shirt", "Men's Formal Wear", 2499), ("SK-FSH-002", "Executive Slim Shirt", "Men's Formal Wear", 2999),
    ("SK-FSH-003", "Performance Stretch Shirt", "Men's Formal Wear", 3499), ("SK-FSH-004", "Premium Cotton T-Shirt", "Men's Casual Wear", 1499),
    ("SK-FSH-005", "Urban Graphic T-Shirt", "Men's Casual Wear", 1299), ("SK-FSH-006", "Tech Performance Polo", "Sportswear", 1999),
    ("SK-FSH-007", "Urban Performance Jacket", "Winter Wear", 5999), ("SK-FSH-008", "TechShell Waterproof Jacket", "Winter Wear", 7999),
    ("SK-FSH-009", "Premium Slim Denim", "Men's Casual Wear", 3299), ("SK-FSH-010", "Executive Women's Dress", "Women's Formal Wear", 4999),
    ("SK-FSH-011", "Premium Women's Blazer", "Women's Formal Wear", 6499), ("SK-FSH-012", "Women's Urban Hoodie", "Women's Casual Wear", 2799),
    ("SK-FSH-013", "Kids Premium Hoodie", "Kids Wear", 1799), ("SK-FSH-014", "Kids Performance Jacket", "Kids Wear", 2499),
    ("SK-FSH-015", "SK Urban Runner", "Footwear", 4999), ("SK-FSH-016", "SK Executive Leather Shoe", "Footwear", 6999),
    ("SK-FSH-017", "SK Trail Performance Shoe", "Footwear", 5999), ("SK-FSH-018", "Executive Laptop Backpack", "Bags", 3999),
    ("SK-FSH-019", "Premium Travel Duffel", "Travel Accessories", 4499), ("SK-FSH-020", "Carbon Fiber Travel Case", "Travel Accessories", 8999),
    # Electronics
    ("SKE-001", "SK Smart Watch X1", "Smart Watches", 12999), ("SKE-002", "SK Smart Watch Ultra", "Smart Watches", 24999),
    ("SKE-003", "SK Wireless Buds Pro", "Wireless Audio", 7999), ("SKE-004", "SK ANC Headphones X", "Wireless Audio", 14999),
    ("SKE-005", "SK Enterprise Laptop 14", "Laptops", 89999), ("SKE-006", "SK Creator Laptop 16", "Laptops", 129999),
    ("SKE-007", "SK Business Laptop 13", "Laptops", 74999), ("SKE-008", "SK Tab Pro 12", "Tablets", 59999),
    ("SKE-009", "SK Tab Air 11", "Tablets", 42999), ("SKE-010", "SK Smart Display 55", "Smart Home", 69999),
    ("SKE-011", "SK Smart Display 65 Pro", "Smart Home", 99999), ("SKE-012", "SK AI Home Hub", "Smart Home", 12999),
    ("SKE-013", "SK Smart Security Camera", "Cameras", 7999), ("SKE-014", "SK AI Security Camera Pro", "Cameras", 14999),
    ("SKE-015", "SK WiFi 7 Enterprise Router", "Networking", 29999), ("SKE-016", "SK Mesh Network Node", "Networking", 11999),
    ("SKE-017", "SK Enterprise Access Point", "Networking", 24999), ("SKE-018", "SK 48-Port Managed Switch", "Networking", 79999),
    ("SKE-019", "SK Thunderbolt Dock Pro", "Computer Accessories", 18999), ("SKE-020", "SK Mechanical Productivity Keyboard", "Computer Accessories", 7999),
    ("SKE-021", "SK Precision Wireless Mouse", "Computer Accessories", 3999), ("SKE-022", "SK 4K Creator Monitor 32", "Monitors", 64999),
    ("SKE-023", "SK Gaming Monitor 27", "Monitors", 39999), ("SKE-024", "SK AI Edge Computing Box", "IoT Devices", 89999),
    # Industrial
    ("SKM-001", "SK Industrial Robotic Arm R7", "Industrial Robots", 1850000), ("SKM-002", "SK Heavy Payload Robot R12", "Industrial Robots", 2950000),
    ("SKM-003", "SK Collaborative Robot C5", "Collaborative Robots", 1450000), ("SKM-004", "SK Autonomous Mobile Robot", "Collaborative Robots", 2250000),
    ("SKM-005", "SK Autonomous Guided Vehicle", "Industrial Robots", 1850000), ("SKM-006", "SK Industrial PLC X500", "PLC Systems", 185000),
    ("SKM-007", "SK Advanced PLC X900", "PLC Systems", 325000), ("SKM-008", "SK Servo Motor 5KW", "Servo Systems", 95000),
    ("SKM-009", "SK Servo Motor 15KW", "Servo Systems", 185000), ("SKM-010", "SK Servo Drive V4", "Servo Systems", 125000),
    ("SKM-011", "SK Motion Controller X", "Motion Controllers", 225000), ("SKM-012", "SK Industrial Lidar Sensor", "Industrial Sensors", 175000),
    ("SKM-013", "SK Precision Temperature Sensor", "Industrial Sensors", 18500), ("SKM-014", "SK Industrial Vision Camera", "Machine Vision", 225000),
    ("SKM-015", "SK AI Inspection Camera", "Machine Vision", 385000), ("SKM-016", "SK Industrial AC Motor", "Motors", 75000),
    ("SKM-017", "SK High Torque Motor", "Motors", 145000), ("SKM-018", "SK Precision Gearbox", "Gearboxes", 95000),
    ("SKM-019", "SK Heavy Load Gearbox", "Gearboxes", 175000), ("SKM-020", "SK Industrial Control Panel", "Control Panels", 285000),
    ("SKM-021", "SK Industrial Power Supply", "Power Supplies", 55000), ("SKM-022", "SK Safety Controller", "Industrial Safety", 85000),
    ("SKM-023", "SK Safety Light Curtain", "Industrial Safety", 45000), ("SKM-024", "SK Robot Adaptive Gripper", "Industrial Robots", 165000),
    # Healthcare
    ("SKH-001", "SK Smart ECG System", "Diagnostic Equipment", 485000), ("SKH-002", "SK ICU Vital Monitor", "Patient Monitoring", 275000),
    ("SKH-003", "SK Bedside Patient Monitor", "Patient Monitoring", 185000), ("SKH-004", "SK Portable Ultrasound Scanner", "Medical Imaging", 1250000),
    ("SKH-005", "SK Digital Blood Analyzer", "Laboratory Equipment", 650000), ("SKH-006", "SK Smart Medical Bed", "Hospital Beds", 325000),
    ("SKH-007", "SK Electric ICU Bed", "Hospital Beds", 485000), ("SKH-008", "SK Smart Infusion Controller", "Infusion Systems", 125000),
    ("SKH-009", "SK Remote Patient Monitor", "Remote Patient Monitoring", 95000), ("SKH-010", "SK Healthcare IoT Gateway", "Healthcare IoT", 175000),
    ("SKH-011", "SK Clinical Data Gateway", "Healthcare IoT", 225000), ("SKH-012", "SK Pulse Oximeter Pro", "Medical Sensors", 6999),
    ("SKH-013", "SK Digital BP Monitor", "Medical Sensors", 5999), ("SKH-014", "SK Infrared Thermometer", "Medical Sensors", 2999),
    ("SKH-015", "SK Portable Patient Alert", "Medical Sensors", 15999),
    # EV/Mobility
    ("SKMB-001", "SK DC Fast Charger 240", "EV Chargers", 850000), ("SKMB-002", "SK Smart AC Charger 22KW", "EV Chargers", 145000),
    ("SKMB-003", "SK Fleet Charging Controller", "EV Chargers", 225000), ("SKMB-004", "SK Battery Management Controller", "Battery Systems", 185000),
    ("SKMB-005", "SK EV Power Inverter", "Power Electronics", 275000), ("SKMB-006", "SK Vehicle Telematics Unit", "Telematics", 45000),
    ("SKMB-007", "SK Fleet AI Camera", "Fleet Cameras", 65000), ("SKMB-008", "SK Autonomous Lidar Kit", "Lidar Systems", 385000),
    ("SKMB-009", "SK Automotive Radar Module", "Radar Systems", 125000), ("SKMB-010", "SK Autonomous Parking Sensor", "Autonomous Systems", 45000),
    ("SKMB-011", "SK Fleet Energy Monitor", "Fleet Tracking", 55000), ("SKMB-012", "SK EV Diagnostic Module", "EV Spare Parts", 85000),
    ("SKMB-013", "SK Smart Charging Controller", "Charging Accessories", 95000), ("SKMB-014", "SK Battery Diagnostic System", "Battery Systems", 165000),
    # FMCG
    ("SKFC-001", "SK Premium Coffee 500g", "Coffee", 499), ("SKFC-002", "SK Organic Green Tea", "Tea", 399),
    ("SKFC-003", "SK Premium Black Tea", "Tea", 349), ("SKFC-004", "SK Energy Drink 500ml", "Energy Drinks", 149),
    ("SKFC-005", "SK Premium Mineral Water", "Mineral Water", 80), ("SKFC-006", "SK Protein Energy Bar", "Snacks", 120),
    ("SKFC-007", "SK Premium Snack Box", "Snacks", 499), ("SKFC-008", "SK Organic Breakfast Mix", "Breakfast Foods", 349),
    ("SKFC-009", "SK Ready Meal Veg", "Ready-to-Eat", 199), ("SKFC-010", "SK Ready Meal Protein", "Ready-to-Eat", 249),
    ("SKFC-011", "SK Herbal Shampoo", "Hair Care", 399), ("SKFC-012", "SK Premium Conditioner", "Hair Care", 449),
    ("SKFC-013", "SK Natural Face Cleanser", "Skin Care", 349), ("SKFC-014", "SK Advanced Moisturizer", "Skin Care", 599),
    ("SKFC-015", "SK Advanced Toothpaste", "Oral Care", 199), ("SKFC-016", "SK Premium Hand Wash", "Bath & Body", 249),
    ("SKFC-017", "SK Surface Cleaner Pro", "Household Cleaning", 299), ("SKFC-018", "SK Premium Laundry Liquid", "Laundry Care", 499),
    ("SKFC-019", "SK Kitchen Degreaser", "Kitchen Care", 299), ("SKFC-020", "SK Wellness Nutrition Mix", "Wellness", 899)
]

suppliers = [
    "Arvind Textile Solutions", "Gujarat Premium Textiles", "Mumbai Apparel Manufacturing", "Bengaluru Fashion Components",
    "Delhi Garment Industries", "Surat Fabric Technologies", "Bengaluru Semiconductor Systems", "Noida Electronics Components",
    "Chennai PCB Technologies", "Pune Embedded Systems", "Hyderabad IoT Components", "Taiwan Technology Components",
    "Bharat Industrial Components", "Precision Motion Systems", "Advanced Servo Technologies", "Industrial Automation India",
    "Global Robotics Components", "Precision Gear Systems", "Industrial Sensor Technologies", "MedTech Components India",
    "Precision Medical Systems", "Global Healthcare Instruments", "Delhi Hospital Supplies", "Pune Medical Plastics",
    "Clinical Electronics India", "Advanced Battery Systems", "EV Power Electronics India", "Automotive Sensor Technologies",
    "Global Charging Infrastructure", "Pune EV Components", "Chennai Automotive Electronics", "Western India Food Processing",
    "Organic Ingredients India", "Nashik Beverage Suppliers", "National FMCG Packaging", "Pune Food Ingredients",
    "Hyderabad Personal Care Manufacturing", "DHL Supply Chain Services", "BlueDart Enterprise Logistics", "Delhivery Enterprise Logistics",
    "National Freight Solutions", "Metro Distribution Services", "Enterprise Cloud Systems", "Global Networking Solutions",
    "AI Computing Technologies", "Data Center Infrastructure India"
]

customers = [
    "Reliance Retail", "Croma Retail Network", "Vijay Sales", "Metro Lifestyle Retail", "National Supermarket Network",
    "Premium Lifestyle Stores", "Tata Industrial Systems", "Mahindra Manufacturing", "Aditya Industrial Group",
    "Global Auto Components", "NextGen Automation", "Bharat Engineering Corporation", "Apollo Healthcare Network",
    "Fortis Medical Group", "Max Healthcare", "Narayana Health", "Regional Hospital Network", "Government Medical Procurement",
    "Fleet Mobility Solutions", "Metro Logistics Group", "National Delivery Network", "Corporate Fleet Services",
    "Urban Mobility Operators", "EV Infrastructure Partners", "Enterprise Technology Partners", "Corporate IT Procurement",
    "Smart Infrastructure Solutions", "Digital Transformation Partners", "National Data Center Group",
    "North India Distribution Network", "South India Distribution Network", "West India Distribution Network",
    "East India Distribution Network", "Central India Distribution Network", "National Hotel Group", "Premium Hospitality Network",
    "Enterprise Catering Services", "National Education Network", "University Technology Procurement", "Private Education Group"
]

territories = [
    "North India", "South India", "West India", "East India", "Central India", "Northeast India",
    "Maharashtra", "Gujarat", "Rajasthan", "Delhi NCR", "Uttar Pradesh", "Punjab", "Madhya Pradesh",
    "Karnataka", "Tamil Nadu", "Telangana", "Kerala", "Andhra Pradesh",
    "West Bengal", "Odisha", "Bihar", "Jharkhand", "Assam"
]

payment_terms = [
    {"name": "Immediate Payment", "credit_days": 0}, {"name": "7 Days", "credit_days": 7}, {"name": "15 Days", "credit_days": 15},
    {"name": "30 Days", "credit_days": 30}, {"name": "45 Days", "credit_days": 45}, {"name": "60 Days", "credit_days": 60},
    {"name": "90 Days Enterprise", "credit_days": 90}
]

# ============================================================
# SEEDING PROCESS
# ============================================================

print(f"\n[1/5] Seeding Configurations (Territories & Terms)...")
api_post("Territory", {"territory_name": "SKAL Global Network", "is_group": 1, "parent_territory": "All Territories"})
for t in territories:
    try: api_post("Territory", {"territory_name": t, "is_group": 0, "parent_territory": "SKAL Global Network"})
    except: pass
for term in payment_terms:
    try: api_post("Payment Term", {"payment_term_name": term["name"], "invoice_portion": 100, "credit_days": term["credit_days"]})
    except: pass

print(f"\n[2/5] Seeding Suppliers ({len(suppliers)}) & Customers ({len(customers)})...")
for s in suppliers:
    try: api_post("Supplier", {"supplier_name": s, "supplier_type": "Company"})
    except: pass
for c in customers:
    try: api_post("Customer", {"customer_name": c, "customer_type": "Company"})
    except: pass

# Combine all locations
all_locations = sk_industries_stores + sk_electronics_stores + sk_mobility_centers + sk_healthcare_centers + manufacturing_plants + warehouses
print(f"\n[3/5] Seeding Entire Logistics Tree ({len(all_locations)} Nodes)...")
api_post("Warehouse", {"warehouse_name": "Mega Enterprise Network", "company": company_name, "is_group": 1})
parent_wh_docs = api_get("Warehouse", {"filters": json.dumps([["warehouse_name", "=", "Mega Enterprise Network"]])})
parent_wh_name = parent_wh_docs[0]['name'] if parent_wh_docs else None

created_leaf_warehouses = []
for loc in all_locations:
    api_post("Warehouse", {"warehouse_name": loc, "company": company_name, "is_group": 0, "parent_warehouse": parent_wh_name})
    act_wh = api_get("Warehouse", {"filters": json.dumps([["warehouse_name", "=", loc]])})
    if act_wh: created_leaf_warehouses.append(act_wh[0]['name'])

print(f"\n[4/5] Seeding Item Groups & Full Product Catalog ({len(products)} SKUs)...")
for group_name, sub_groups in item_groups.items():
    api_post("Item Group", {"item_group_name": group_name, "parent_item_group": "All Item Groups", "is_group": 1})
    for sub in sub_groups:
        api_post("Item Group", {"item_group_name": sub, "parent_item_group": group_name, "is_group": 0})

all_skus = []
for sku, name, category, price in products:
    item_doc = {
        "item_code": sku,
        "item_name": name,
        "item_group": category,
        "stock_uom": "Nos",
        "is_stock_item": 1,
        "valuation_rate": price * 0.4,
        "standard_rate": price
    }
    api_post("Item", item_doc)
    all_skus.append(sku)

print(f"\n[5/5] Submitting Massive Stock Entries for all {len(created_leaf_warehouses)} Nodes...")
# Only seed 30 items per location to avoid massive timeout, but iterate over all 120+ locations
for wh in created_leaf_warehouses:
    wh_items = random.sample(all_skus, k=random.randint(20, min(50, len(all_skus))))
    items_for_receipt = []
    
    for item_code in wh_items:
        reorder_qty = random.randint(25, 400)
        api_put("Item", item_code, {
            "reorder_levels": [{
                "warehouse": wh,
                "warehouse_reorder_level": reorder_qty,
                "warehouse_reorder_qty": reorder_qty,
                "material_request_type": "Purchase"
            }]
        })
        
        qty = random.randint(10, reorder_qty + 500)
        if qty > 0:
            items_for_receipt.append({
                "item_code": item_code,
                "qty": qty,
                "t_warehouse": wh,
                "basic_rate": random.randint(50, 1500000)
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
        except Exception as e: 
            pass

print("\n=== THE EXACT FULL ENTERPRISE ARCHITECTURE HAS BEEN SUCCESSFULLY BUILT ===")
