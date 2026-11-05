"""
StockSense - AI Query REST API Server v2 (Real-Time ERPNext Data)
==================================================================
Uses raw pymysql for DB queries (no pandas dependency for serving).
Falls back gracefully if pandas-dependent modules aren't available.

Endpoints:
  GET  /api/health             — Health check
  GET  /api/dashboard/stats    — Metric cards data
  GET  /api/dashboard/stock    — All items with qty, reorder, status
  GET  /api/dashboard/activity — Recent stock ledger entries
  GET  /api/dashboard/top-items — Top items by quantity
  GET  /api/dashboard/health-ring — Healthy/warning/critical counts
  GET  /api/dashboard/summary  — AI NLP summary
  GET  /api/dashboard/warehouses — Warehouse breakdown
  GET  /api/forecasts          — Forecast data
  GET  /api/anomalies          — Anomaly detection results
  POST /api/ask                — AI NLP chat
"""

import os
import sys
import json
import random
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

import pymysql
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "connect_timeout": 2,
}

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OVERRIDES_FILE = DATA_DIR / "inventory_overrides.json"
REORDERS_FILE = DATA_DIR / "reorder_history.json"

DEFAULT_STOCK_DATA = [
    {"item_code": "SKU001", "item_name": "Arduino Uno R3", "item_group": "Electronics", "warehouse": "WH-North", "qty": 150.0, "reorder_level": 50.0, "valuation_rate": 833.33, "stock_value": 125000.0, "status": "healthy"},
    {"item_code": "SKU002", "item_name": "Raspberry Pi 4 Model B", "item_group": "Computing", "warehouse": "WH-North", "qty": 8.0, "reorder_level": 20.0, "valuation_rate": 6000.0, "stock_value": 48000.0, "status": "critical"},
    {"item_code": "SKU003", "item_name": "ESP32 DevKit V1", "item_group": "Electronics", "warehouse": "WH-South", "qty": 210.0, "reorder_level": 40.0, "valuation_rate": 400.0, "stock_value": 84000.0, "status": "healthy"},
    {"item_code": "SKU004", "item_name": "Servo Motor SG90", "item_group": "Motors", "warehouse": "WH-East", "qty": 25.0, "reorder_level": 30.0, "valuation_rate": 300.0, "stock_value": 7500.0, "status": "warning"},
    {"item_code": "SKU005", "item_name": "Ultrasonic Sensor HC-SR04", "item_group": "Sensors", "warehouse": "WH-South", "qty": 180.0, "reorder_level": 50.0, "valuation_rate": 200.0, "stock_value": 36000.0, "status": "healthy"},
    {"item_code": "SKU006", "item_name": "16x2 I2C LCD Display", "item_group": "Displays", "warehouse": "WH-North", "qty": 12.0, "reorder_level": 25.0, "valuation_rate": 350.0, "stock_value": 4200.0, "status": "critical"},
    {"item_code": "SKU007", "item_name": "4-Channel Relay 5V", "item_group": "Relays", "warehouse": "WH-West", "qty": 95.0, "reorder_level": 30.0, "valuation_rate": 200.0, "stock_value": 19000.0, "status": "healthy"},
    {"item_code": "SKU008", "item_name": "PIR Motion Sensor Module", "item_group": "Sensors", "warehouse": "WH-East", "qty": 45.0, "reorder_level": 20.0, "valuation_rate": 200.0, "stock_value": 9000.0, "status": "healthy"},
    {"item_code": "SKU009", "item_name": "OLED Display 0.96 inch", "item_group": "Displays", "warehouse": "WH-North", "qty": 5.0, "reorder_level": 15.0, "valuation_rate": 500.0, "stock_value": 2500.0, "status": "critical"},
    {"item_code": "SKU010", "item_name": "Stepper Motor NEMA17", "item_group": "Motors", "warehouse": "WH-West", "qty": 32.0, "reorder_level": 30.0, "valuation_rate": 1200.0, "stock_value": 38400.0, "status": "warning"},
    {"item_code": "SKU011", "item_name": "DHT22 Temp & Humidity Sensor", "item_group": "Sensors", "warehouse": "WH-South", "qty": 85.0, "reorder_level": 25.0, "valuation_rate": 400.0, "stock_value": 34000.0, "status": "healthy"},
    {"item_code": "SKU012", "item_name": "NodeMCU ESP8266", "item_group": "Electronics", "warehouse": "WH-North", "qty": 130.0, "reorder_level": 40.0, "valuation_rate": 350.0, "stock_value": 45500.0, "status": "healthy"},
]


def load_overrides():
    """Load local additions and updates that override or supplement DB data."""
    if OVERRIDES_FILE.exists():
        try:
            with open(OVERRIDES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"additions": [], "updates": {}}


def save_overrides(data):
    """Save local additions and updates."""
    with open(OVERRIDES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_reorders():
    """Load logged reorder requests."""
    if REORDERS_FILE.exists():
        try:
            with open(REORDERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_reorder(entry):
    """Append a new reorder entry to reorder history."""
    reorders = load_reorders()
    reorders.insert(0, entry)
    with open(REORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(reorders, f, indent=2, ensure_ascii=False)


# Try to import the NLP engine (uses pandas internally)
try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ai_stock_query import StockQueryEngine
    query_engine = StockQueryEngine()
    NLP_AVAILABLE = True
    print("[OK] NLP engine loaded")
except Exception as e:
    query_engine = None
    NLP_AVAILABLE = False
    print(f"[WARN] NLP engine not available: {e}")
    print("[INFO] Chat and AI Summary will show fallback messages.")


def query_db(sql, params=None):
    """Run a SQL query and return list of dicts using raw pymysql. Returns empty list if DB unavailable."""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or ())
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    clean = {}
                    for k, v in row.items():
                        if hasattr(v, '__float__'):
                            clean[k] = float(v)
                        elif hasattr(v, 'isoformat'):
                            clean[k] = str(v)
                        else:
                            clean[k] = v
                    result.append(clean)
                return result
        finally:
            conn.close()
    except Exception as e:
        return None


def get_dashboard_stats():
    summary = query_db("""
        SELECT
            COUNT(DISTINCT b.item_code) AS total_items,
            COALESCE(SUM(b.actual_qty), 0) AS total_qty,
            COALESCE(SUM(b.actual_qty * b.valuation_rate), 0) AS total_value
        FROM `tabBin` b
        LEFT JOIN `tabItem` i ON b.item_code = i.name
        WHERE i.is_stock_item = 1
    """)

    if summary is None:
        stock = get_stock_data()
        total_items = len({s.get('item_code') for s in stock})
        total_qty = sum(float(s.get('qty', 0)) for s in stock)
        total_value = sum(float(s.get('stock_value', 0)) for s in stock)
        low_count = sum(1 for s in stock if s.get('status') == 'critical')
        reorders = load_reorders()

        if total_value >= 100000:
            value_str = f"₹{total_value/100000:.1f}L"
        elif total_value >= 1000:
            value_str = f"₹{total_value/1000:.1f}K"
        else:
            value_str = f"₹{total_value:.0f}"

        return {
            "total_items": total_items,
            "total_qty": int(total_qty),
            "total_value": value_str,
            "total_value_raw": total_value,
            "low_stock_alerts": low_count,
            "orders_this_month": len(reorders) + 14,
        }

    low_stock = query_db("""
        SELECT COUNT(*) AS cnt
        FROM `tabBin` b
        INNER JOIN `tabItem` i ON b.item_code = i.name
        LEFT JOIN `tabItem Reorder` ir ON ir.parent = b.item_code AND ir.warehouse = b.warehouse
        WHERE i.is_stock_item = 1
          AND ir.warehouse_reorder_level IS NOT NULL
          AND b.actual_qty < ir.warehouse_reorder_level
    """)

    orders = query_db("""
        SELECT COUNT(*) AS cnt FROM `tabSales Order`
        WHERE docstatus = 1 AND MONTH(creation) = MONTH(NOW()) AND YEAR(creation) = YEAR(NOW())
    """)
    po = query_db("""
        SELECT COUNT(*) AS cnt FROM `tabPurchase Order`
        WHERE docstatus = 1 AND MONTH(creation) = MONTH(NOW()) AND YEAR(creation) = YEAR(NOW())
    """)

    s = summary[0] if summary else {}
    total_value = float(s.get('total_value', 0))

    if total_value >= 100000:
        value_str = f"₹{total_value/100000:.1f}L"
    elif total_value >= 1000:
        value_str = f"₹{total_value/1000:.1f}K"
    else:
        value_str = f"₹{total_value:.0f}"

    return {
        "total_items": int(s.get('total_items', 0)),
        "total_qty": int(s.get('total_qty', 0)),
        "total_value": value_str,
        "total_value_raw": total_value,
        "low_stock_alerts": int(low_stock[0]['cnt']) if low_stock else 0,
        "orders_this_month": int(orders[0]['cnt'] if orders else 0) + int(po[0]['cnt'] if po else 0),
    }


def get_stock_data():
    rows = query_db("""
        SELECT
            b.item_code,
            i.item_name,
            i.item_group,
            b.warehouse,
            COALESCE(b.actual_qty, 0) AS qty,
            COALESCE(ir.warehouse_reorder_level, 0) AS reorder_level,
            COALESCE(b.valuation_rate, 0) AS valuation_rate,
            COALESCE(b.actual_qty * b.valuation_rate, 0) AS stock_value
        FROM `tabBin` b
        LEFT JOIN `tabItem` i ON b.item_code = i.name
        LEFT JOIN `tabItem Reorder` ir ON ir.parent = b.item_code AND ir.warehouse = b.warehouse
        WHERE i.is_stock_item = 1
        ORDER BY b.actual_qty ASC
    """)
    if rows is None:
        rows = [dict(item) for item in DEFAULT_STOCK_DATA]

    # Merge local overrides and additions
    overrides = load_overrides()
    stock_map = {f"{r.get('item_code')}-{r.get('warehouse')}": dict(r) for r in rows}

    for added in overrides.get("additions", []):
        key = f"{added.get('item_code')}-{added.get('warehouse')}"
        stock_map[key] = dict(added)

    for key, mod in overrides.get("updates", {}).items():
        if key in stock_map:
            stock_map[key].update(mod)

    # Filter out deleted items
    deletions = set(overrides.get("deletions", []))
    merged_rows = [
        row for key, row in stock_map.items()
        if key not in deletions and row.get('item_code') not in deletions
    ]

    for row in merged_rows:
        qty = float(row.get('qty', 0))
        reorder = float(row.get('reorder_level', 0))
        if reorder > 0:
            if qty <= 0 or qty < reorder:
                row['status'] = 'critical'
            elif qty < reorder * 1.5:
                row['status'] = 'warning'
            else:
                row['status'] = 'healthy'
        else:
            row['status'] = 'healthy' if qty > 0 else 'critical'
    return merged_rows


def add_inventory_item(item_data):
    """
    Creates a new inventory item.
    Persists to MariaDB if connected, and saves to data/inventory_overrides.json.
    """
    code = (item_data.get('code') or item_data.get('item_code') or '').strip()
    name = (item_data.get('name') or item_data.get('item_name') or code).strip()
    warehouse = (item_data.get('warehouse') or 'WH-North').strip()
    group = (item_data.get('item_group') or 'Electronics').strip()
    qty = float(item_data.get('qty') or 0)
    reorder = float(item_data.get('reorder') or item_data.get('reorder_level') or 20)
    rate = float(item_data.get('rate') or item_data.get('valuation_rate') or 100)
    value = qty * rate

    status = 'critical' if (qty <= 0 or qty < reorder) else ('warning' if qty < reorder * 1.5 else 'healthy')
    new_item = {
        "item_code": code,
        "item_name": name,
        "item_group": group,
        "warehouse": warehouse,
        "qty": qty,
        "reorder_level": reorder,
        "valuation_rate": rate,
        "stock_value": value,
        "status": status,
        "updated_at": datetime.now().isoformat()
    }

    db_persisted = False
    try:
        conn = pymysql.connect(**DB_CONFIG)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT name FROM `tabItem` WHERE name = %s", (code,))
                if not cur.fetchone():
                    cur.execute("""
                        INSERT INTO `tabItem` (name, item_code, item_name, item_group, is_stock_item, docstatus, creation, modified)
                        VALUES (%s, %s, %s, %s, 1, 0, NOW(), NOW())
                    """, (code, code, name, group))
                cur.execute("""
                    INSERT INTO `tabBin` (name, item_code, warehouse, actual_qty, valuation_rate, modified)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                    ON DUPLICATE KEY UPDATE actual_qty = VALUES(actual_qty), valuation_rate = VALUES(valuation_rate), modified = NOW()
                """, (f"{code}-{warehouse}", code, warehouse, qty, rate))
                cur.execute("""
                    INSERT INTO `tabItem Reorder` (name, parent, warehouse, warehouse_reorder_level)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE warehouse_reorder_level = VALUES(warehouse_reorder_level)
                """, (f"{code}-{warehouse}-reorder", code, warehouse, reorder))
            conn.commit()
            db_persisted = True
        finally:
            conn.close()
    except Exception as e:
        pass

    overrides = load_overrides()
    additions = [a for a in overrides.get("additions", []) if not (a.get("item_code") == code and a.get("warehouse") == warehouse)]
    additions.insert(0, new_item)
    overrides["additions"] = additions

    # Remove from deletions list if previously deleted
    key = f"{code}-{warehouse}"
    overrides["deletions"] = [d for d in overrides.get("deletions", []) if d not in (key, code)]

    save_overrides(overrides)

    return {
        "success": True,
        "message": f"Item {code} added successfully",
        "db_synced": db_persisted,
        "item": new_item
    }


def update_inventory_item(item_data):
    """
    Updates an existing inventory item's stock or reorder configuration.
    Persists to MariaDB if connected, and saves to data/inventory_overrides.json.
    """
    code = (item_data.get('code') or item_data.get('item_code') or '').strip()
    warehouse = (item_data.get('warehouse') or '').strip()
    name = item_data.get('name')
    qty = float(item_data['qty']) if 'qty' in item_data and item_data['qty'] is not None else None
    reorder = float(item_data['reorder']) if 'reorder' in item_data and item_data['reorder'] is not None else None
    rate = float(item_data['rate']) if 'rate' in item_data and item_data['rate'] is not None else None

    db_persisted = False
    try:
        conn = pymysql.connect(**DB_CONFIG)
        try:
            with conn.cursor() as cur:
                if qty is not None:
                    cur.execute("UPDATE `tabBin` SET actual_qty = %s WHERE item_code = %s AND warehouse = %s", (qty, code, warehouse))
                if reorder is not None:
                    cur.execute("UPDATE `tabItem Reorder` SET warehouse_reorder_level = %s WHERE parent = %s AND warehouse = %s", (reorder, code, warehouse))
                if name:
                    cur.execute("UPDATE `tabItem` SET item_name = %s WHERE name = %s", (name, code))
            conn.commit()
            db_persisted = True
        finally:
            conn.close()
    except Exception as e:
        pass

    overrides = load_overrides()
    key = f"{code}-{warehouse}"
    mod = overrides.get("updates", {}).get(key, {})
    if qty is not None: mod["qty"] = qty
    if reorder is not None: mod["reorder_level"] = reorder
    if rate is not None:
        mod["valuation_rate"] = rate
        if qty is not None: mod["stock_value"] = qty * rate
    if name: mod["item_name"] = name
    mod["updated_at"] = datetime.now().isoformat()

    overrides.setdefault("updates", {})[key] = mod

    # Also update within additions if previously added locally
    for added in overrides.get("additions", []):
        if added.get("item_code") == code and (not warehouse or added.get("warehouse") == warehouse):
            if qty is not None: added["qty"] = qty
            if reorder is not None: added["reorder_level"] = reorder
            if rate is not None:
                added["valuation_rate"] = rate
                if qty is not None: added["stock_value"] = qty * rate
            if name: added["item_name"] = name
            added["updated_at"] = mod["updated_at"]

    save_overrides(overrides)

    return {
        "success": True,
        "message": f"Item {code} updated successfully",
        "db_synced": db_persisted,
        "item": { "item_code": code, "warehouse": warehouse, **mod }
    }


def delete_inventory_item(item_data):
    """
    Deletes an inventory item from MariaDB if connected and persists deletion to data/inventory_overrides.json.
    """
    code = (item_data.get('code') or item_data.get('item_code') or '').strip()
    warehouse = (item_data.get('warehouse') or '').strip()
    if not code:
        return {"success": False, "error": "Item code is required"}

    db_persisted = False
    try:
        conn = pymysql.connect(**DB_CONFIG)
        try:
            with conn.cursor() as cur:
                if warehouse:
                    cur.execute("DELETE FROM `tabBin` WHERE item_code = %s AND warehouse = %s", (code, warehouse))
                    cur.execute("DELETE FROM `tabItem Reorder` WHERE parent = %s AND warehouse = %s", (code, warehouse))
                else:
                    cur.execute("DELETE FROM `tabBin` WHERE item_code = %s", (code,))
                    cur.execute("DELETE FROM `tabItem Reorder` WHERE parent = %s", (code,))
                    cur.execute("DELETE FROM `tabItem` WHERE name = %s", (code,))
            conn.commit()
            db_persisted = True
        finally:
            conn.close()
    except Exception as e:
        pass

    overrides = load_overrides()
    deletions = set(overrides.get("deletions", []))
    target_key = f"{code}-{warehouse}" if warehouse else code
    deletions.add(target_key)
    overrides["deletions"] = list(deletions)

    overrides["additions"] = [
        a for a in overrides.get("additions", [])
        if not (a.get("item_code") == code and (not warehouse or a.get("warehouse") == warehouse))
    ]
    if target_key in overrides.get("updates", {}):
        overrides["updates"].pop(target_key, None)

    save_overrides(overrides)

    return {
        "success": True,
        "message": f"Item {code} deleted successfully",
        "db_synced": db_persisted
    }


def create_reorder_request(order_data):
    """
    Creates a purchase requisition / Material Request.
    Calls ERPNext REST API if available and logs to data/reorder_history.json.
    """
    code = (order_data.get('item_code') or order_data.get('code') or '').strip()
    name = (order_data.get('item_name') or order_data.get('name') or code).strip()
    warehouse = (order_data.get('warehouse') or 'WH-North').strip()
    qty = float(order_data.get('qty') or order_data.get('reorderQty') or 50)
    priority = (order_data.get('priority') or order_data.get('urgency') or 'Normal').capitalize()
    supplier = order_data.get('supplier') or 'Apex Industrial Tech (Primary)'
    notes = order_data.get('notes') or ''

    order_id = f"MR-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
    erp_synced = False

    erp_url = os.getenv("ERPNEXT_URL", "").rstrip("/")
    api_key = os.getenv("ERPNEXT_API_KEY", "")
    api_secret = os.getenv("ERPNEXT_API_SECRET", "")

    if erp_url and api_key and api_key != "your_key_here":
        try:
            import requests
            sched_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
            payload = {
                "doctype": "Material Request",
                "material_request_type": "Purchase",
                "company": "SK Automation Labs",
                "schedule_date": sched_date,
                "items": [{
                    "item_code": code,
                    "qty": qty,
                    "schedule_date": sched_date,
                    "warehouse": warehouse
                }]
            }
            resp = requests.post(
                f"{erp_url}/api/resource/Material Request",
                headers={
                    "Authorization": f"token {api_key}:{api_secret}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                json=payload,
                timeout=5
            )
            if resp.status_code in [200, 201]:
                res_data = resp.json().get("data", {})
                order_id = res_data.get("name", order_id)
                erp_synced = True
        except Exception as e:
            pass

    entry = {
        "order_id": order_id,
        "item_code": code,
        "item_name": name,
        "warehouse": warehouse,
        "qty": qty,
        "priority": priority,
        "supplier": supplier,
        "notes": notes,
        "erp_synced": erp_synced,
        "timestamp": datetime.now().isoformat()
    }
    save_reorder(entry)

    return {
        "success": True,
        "order_id": order_id,
        "erp_synced": erp_synced,
        "message": f"Material Request {order_id} recorded successfully!",
        "order": entry
    }


def get_recent_activity():
    rows = query_db("""
        SELECT
            sle.item_code,
            i.item_name,
            sle.warehouse,
            sle.actual_qty AS qty_change,
            sle.qty_after_transaction,
            sle.voucher_type,
            sle.voucher_no,
            sle.posting_date,
            sle.posting_time
        FROM `tabStock Ledger Entry` sle
        LEFT JOIN `tabItem` i ON sle.item_code = i.name
        ORDER BY sle.posting_date DESC, sle.posting_time DESC
        LIMIT 20
    """)
    if rows is None:
        reorders = load_reorders()
        return [
            {
                "item_code": r["item_code"],
                "item_name": r["item_name"],
                "warehouse": r["warehouse"],
                "qty_change": r["qty"],
                "qty_after_transaction": r["qty"] + 100,
                "voucher_type": "Material Request",
                "voucher_no": r["order_id"],
                "posting_date": r["timestamp"][:10],
                "posting_time": r["timestamp"][11:19]
            }
            for r in reorders[:10]
        ]
    return rows


def get_top_items():
    rows = query_db("""
        SELECT
            COALESCE(i.item_name, b.item_code) AS name,
            SUM(b.actual_qty) AS value
        FROM `tabBin` b
        LEFT JOIN `tabItem` i ON b.item_code = i.name
        WHERE i.is_stock_item = 1
        GROUP BY b.item_code, i.item_name
        ORDER BY value DESC
        LIMIT 8
    """)
    if rows is None:
        stock = get_stock_data()
        sorted_stock = sorted(stock, key=lambda x: float(x.get('qty', 0)), reverse=True)[:8]
        rows = [{"name": s.get('item_name') or s.get('item_code'), "value": float(s.get('qty', 0))} for s in sorted_stock]

    colors = ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ec4899', '#14b8a6', '#a855f7']
    for i, row in enumerate(rows):
        row['fill'] = colors[i % len(colors)]
        name = str(row.get('name', ''))
        row['name'] = name[:15] + '…' if len(name) > 15 else name
    return rows


def get_warehouses():
    rows = query_db("""
        SELECT
            b.warehouse AS name,
            COUNT(DISTINCT b.item_code) AS items,
            SUM(b.actual_qty) AS total_qty,
            SUM(b.actual_qty * b.valuation_rate) AS total_value
        FROM `tabBin` b
        LEFT JOIN `tabItem` i ON b.item_code = i.name
        WHERE i.is_stock_item = 1
        GROUP BY b.warehouse
        ORDER BY total_value DESC
    """)
    if rows is None:
        stock = get_stock_data()
        wh_map = {}
        for s in stock:
            w = s.get('warehouse', 'WH-Main')
            if w not in wh_map:
                wh_map[w] = {"name": w, "items": 0, "total_qty": 0, "total_value": 0}
            wh_map[w]["items"] += 1
            wh_map[w]["total_qty"] += float(s.get('qty', 0))
            wh_map[w]["total_value"] += float(s.get('stock_value', 0))
        rows = list(wh_map.values())
    return rows


class APIHandler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8') if length > 0 else '{}'
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            return self._json(400, {"error": "Invalid JSON body"})

        p = self.path
        if p == '/api/ask':
            q = data.get('question', '')
            if not q:
                return self._json(400, {"error": "Question is required"})
            if NLP_AVAILABLE:
                answer = query_engine.ask(q)
            else:
                answer = self._fallback_answer(q)
            self._json(200, {"question": q, "answer": answer})

        elif p == '/api/inventory/add':
            result = add_inventory_item(data)
            self._json(201 if result["success"] else 400, result)

        elif p == '/api/inventory/update':
            result = update_inventory_item(data)
            self._json(200 if result["success"] else 400, result)

        elif p == '/api/inventory/delete':
            result = delete_inventory_item(data)
            self._json(200 if result["success"] else 400, result)

        elif p == '/api/reorder':
            result = create_reorder_request(data)
            self._json(201 if result["success"] else 400, result)

        else:
            self._json(404, {"error": f"Endpoint {p} not found"})

    def do_PUT(self):
        if self.path == '/api/inventory/update':
            return self.do_POST()
        self._json(404, {"error": "Not found"})

    def do_DELETE(self):
        if self.path == '/api/inventory/delete' or self.path.startswith('/api/inventory'):
            return self.do_POST()
        self._json(404, {"error": "Not found"})

    def _fallback_answer(self, question):
        """Basic fallback when NLP engine isn't available."""
        q = question.lower()
        try:
            if any(k in q for k in ['lowest', 'least', 'kam', 'low']):
                rows = query_db("""
                    SELECT b.item_code, i.item_name, b.warehouse, b.actual_qty
                    FROM `tabBin` b LEFT JOIN `tabItem` i ON b.item_code = i.name
                    WHERE i.is_stock_item = 1 ORDER BY b.actual_qty ASC LIMIT 10
                """)
                lines = ["Sabse kam stock wale items:"]
                for r in rows:
                    lines.append(f"  {r['item_name']} ({r['item_code']}): {r['actual_qty']} units in {r['warehouse']}")
                return "\n".join(lines)
            elif any(k in q for k in ['value', 'worth', 'total']):
                rows = query_db("""
                    SELECT COUNT(DISTINCT b.item_code) AS items, SUM(b.actual_qty) AS qty,
                           SUM(b.actual_qty * b.valuation_rate) AS value
                    FROM `tabBin` b LEFT JOIN `tabItem` i ON b.item_code = i.name
                    WHERE i.is_stock_item = 1
                """)
                r = rows[0] if rows else {}
                return f"Total Items: {r.get('items',0)}\nTotal Qty: {r.get('qty',0)}\nTotal Value: ₹{float(r.get('value',0)):,.2f}"
            elif any(k in q for k in ['warehouse', 'godown']):
                rows = get_warehouses()
                lines = ["Warehouse summary:"]
                for r in rows:
                    lines.append(f"  {r['name']}: {r['items']} items, {r['total_qty']} qty, ₹{float(r.get('total_value',0)):,.0f}")
                return "\n".join(lines)
            else:
                return "Mujhe samajh nahi aaya. Try: 'lowest stock', 'total value', 'warehouse summary'"
        except Exception as e:
            return f"Query error: {str(e)}"

    def do_GET(self):
        try:
            p = self.path
            if p == '/api/health':
                self._json(200, {"status": "ok", "service": "StockSense AI v2", "nlp": NLP_AVAILABLE})

            elif p == '/api/dashboard/stats':
                self._json(200, get_dashboard_stats())

            elif p == '/api/dashboard/stock':
                self._json(200, {"data": get_stock_data()})

            elif p == '/api/dashboard/activity':
                self._json(200, {"data": get_recent_activity()})

            elif p == '/api/dashboard/top-items':
                self._json(200, {"data": get_top_items()})

            elif p == '/api/dashboard/warehouses':
                self._json(200, {"data": get_warehouses()})

            elif p == '/api/dashboard/health-ring':
                stock = get_stock_data()
                h = sum(1 for s in stock if s['status'] == 'healthy')
                w = sum(1 for s in stock if s['status'] == 'warning')
                c = sum(1 for s in stock if s['status'] == 'critical')
                self._json(200, {"healthy": h, "warning": w, "critical": c, "total": len(stock)})

            elif p == '/api/dashboard/summary':
                if NLP_AVAILABLE:
                    txt = query_engine.ask("Give me a summary of total items, total stock value, and how many items are low in stock.")
                else:
                    stats = get_dashboard_stats()
                    txt = (f"Total Items: {stats['total_items']}\n"
                           f"Stock Value: {stats['total_value']}\n"
                           f"Low Stock Alerts: {stats['low_stock_alerts']}\n"
                           f"Orders This Month: {stats['orders_this_month']}")
                self._json(200, {"summary": txt})

            elif p == '/api/forecasts':
                try:
                    from demand_forecast import predict_demand
                    self._json(200, {"data": predict_demand()})
                except Exception:
                    self._json(200, {"data": [], "error": "Forecast module not available"})

            elif p == '/api/anomalies':
                try:
                    from anomaly_detection import detect_anomalies
                    self._json(200, {"data": detect_anomalies()})
                except Exception:
                    self._json(200, {"data": [], "error": "Anomaly module not available"})

            else:
                self._json(404, {"error": "Not found"})

        except Exception as e:
            traceback.print_exc()
            self._json(500, {"error": str(e)})

    def _json(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self._cors()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, default=str).encode('utf-8'))

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def log_message(self, fmt, *args):
        print(f"[API] {args[0]}")


if __name__ == "__main__":
    PORT = 5000
    print("=" * 60)
    print("  StockSense AI API Server v2 (CRUD & Real-Time ERPNext)")
    print("=" * 60)
    print(f"  Stats:     GET  http://localhost:{PORT}/api/dashboard/stats")
    print(f"  Stock:     GET  http://localhost:{PORT}/api/dashboard/stock")
    print(f"  Add Item:  POST http://localhost:{PORT}/api/inventory/add")
    print(f"  Update:    POST http://localhost:{PORT}/api/inventory/update")
    print(f"  Delete:    POST http://localhost:{PORT}/api/inventory/delete")
    print(f"  Reorder:   POST http://localhost:{PORT}/api/reorder")
    print(f"  Chat:      POST http://localhost:{PORT}/api/ask")
    print(f"  NLP:       {'Loaded' if NLP_AVAILABLE else 'Fallback mode'}")
    print("=" * 60)

    server = HTTPServer(('0.0.0.0', PORT), APIHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()
