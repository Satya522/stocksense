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
import traceback
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
}

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
    """Run a SQL query and return list of dicts using raw pymysql."""
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            rows = cursor.fetchall()
            # Convert Decimal and other types to JSON-safe
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
    for row in rows:
        qty = float(row.get('qty', 0))
        reorder = float(row.get('reorder_level', 0))
        if reorder > 0:
            if qty <= 0:
                row['status'] = 'critical'
            elif qty < reorder:
                row['status'] = 'critical'
            elif qty < reorder * 1.5:
                row['status'] = 'warning'
            else:
                row['status'] = 'healthy'
        else:
            row['status'] = 'healthy' if qty > 0 else 'critical'
    return rows


def get_recent_activity():
    return query_db("""
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
    return rows


class APIHandler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/ask':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            try:
                data = json.loads(body)
                q = data.get('question', '')
                if not q:
                    return self._json(400, {"error": "Question is required"})
                if NLP_AVAILABLE:
                    answer = query_engine.ask(q)
                else:
                    # Fallback: run a basic query
                    answer = self._fallback_answer(q)
                self._json(200, {"question": q, "answer": answer})
            except json.JSONDecodeError:
                self._json(400, {"error": "Invalid JSON"})
            except Exception as e:
                self._json(500, {"error": str(e)})
        else:
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
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def log_message(self, fmt, *args):
        print(f"[API] {args[0]}")


if __name__ == "__main__":
    PORT = 5000
    print("=" * 60)
    print("  StockSense AI API Server v2 (Real-Time ERPNext)")
    print("=" * 60)
    print(f"  Stats:    http://localhost:{PORT}/api/dashboard/stats")
    print(f"  Stock:    http://localhost:{PORT}/api/dashboard/stock")
    print(f"  Activity: http://localhost:{PORT}/api/dashboard/activity")
    print(f"  Chat:     http://localhost:{PORT}/api/ask")
    print(f"  NLP:      {'Loaded' if NLP_AVAILABLE else 'Fallback mode'}")
    print("=" * 60)

    server = HTTPServer(('0.0.0.0', PORT), APIHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()
