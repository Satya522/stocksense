"""
StockSense - AI/NLP Stock Query Engine
=======================================
Natural-language interface for querying stock data.
Users can ask questions like:
  - "What's my lowest stock item?"
  - "Show items below reorder level"
  - "Total stock value"
  - "Which warehouse has the most stock?"

Uses keyword matching + SQL query mapping (no external AI API needed).
Can be extended with OpenAI/Gemini API for advanced NLP.

Usage:
  cd python
  venv\\Scripts\\activate
  python src/ai_stock_query.py
"""

import os
import re
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# --- Setup ---
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def get_db_engine():
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    conn_str = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(conn_str)


# --- Query Templates ---
QUERY_MAP = {
    "lowest_stock": {
        "keywords": ["lowest", "least", "minimum", "sabse kam", "kam stock", "low stock"],
        "sql": """
            SELECT b.item_code, i.item_name, b.warehouse, b.actual_qty
            FROM `tabBin` b
            LEFT JOIN `tabItem` i ON b.item_code = i.name
            WHERE i.is_stock_item = 1
            ORDER BY b.actual_qty ASC
            LIMIT 10
        """,
        "response": "Yeh hain sabse kam stock wale items (bottom 10):"
    },
    "highest_stock": {
        "keywords": ["highest", "most", "maximum", "sabse zyada", "top stock", "max stock"],
        "sql": """
            SELECT b.item_code, i.item_name, b.warehouse, b.actual_qty
            FROM `tabBin` b
            LEFT JOIN `tabItem` i ON b.item_code = i.name
            WHERE i.is_stock_item = 1
            ORDER BY b.actual_qty DESC
            LIMIT 10
        """,
        "response": "Yeh hain sabse zyada stock wale items (top 10):"
    },
    "total_value": {
        "keywords": ["total value", "kul value", "stock value", "kitna value", "worth"],
        "sql": """
            SELECT
                SUM(b.actual_qty * b.valuation_rate) AS total_stock_value,
                COUNT(DISTINCT b.item_code) AS total_items,
                SUM(b.actual_qty) AS total_qty
            FROM `tabBin` b
            LEFT JOIN `tabItem` i ON b.item_code = i.name
            WHERE i.is_stock_item = 1
        """,
        "response": "Tumhara total stock summary:"
    },
    "reorder_alert": {
        "keywords": ["reorder", "below reorder", "need to order", "order karna", "khatam", "alert"],
        "sql": """
            SELECT b.item_code, i.item_name, b.warehouse, b.actual_qty,
                   ir.warehouse_reorder_level AS reorder_level,
                   (ir.warehouse_reorder_level - b.actual_qty) AS shortfall
            FROM `tabBin` b
            INNER JOIN `tabItem` i ON b.item_code = i.name
            INNER JOIN `tabItem Reorder` ir ON ir.parent = b.item_code AND ir.warehouse = b.warehouse
            WHERE i.is_stock_item = 1 AND b.actual_qty < ir.warehouse_reorder_level
            ORDER BY shortfall DESC
        """,
        "response": "Yeh items reorder level se neeche hain - turant order karo:"
    },
    "warehouse_summary": {
        "keywords": ["warehouse", "godown", "location", "kahan", "which warehouse"],
        "sql": """
            SELECT
                b.warehouse,
                COUNT(DISTINCT b.item_code) AS total_items,
                SUM(b.actual_qty) AS total_qty,
                SUM(b.actual_qty * b.valuation_rate) AS total_value
            FROM `tabBin` b
            LEFT JOIN `tabItem` i ON b.item_code = i.name
            WHERE i.is_stock_item = 1
            GROUP BY b.warehouse
            ORDER BY total_value DESC
        """,
        "response": "Warehouse-wise stock breakdown:"
    },
    "recent_movements": {
        "keywords": ["recent", "latest", "last", "haal hi", "aaj", "today", "movement", "transaction"],
        "sql": """
            SELECT item_code, warehouse, posting_date, actual_qty,
                   qty_after_transaction, voucher_type, voucher_no
            FROM `tabStock Ledger Entry`
            ORDER BY posting_date DESC, posting_time DESC
            LIMIT 15
        """,
        "response": "Yeh hain sabse recent stock movements:"
    },
    "out_of_stock": {
        "keywords": ["out of stock", "zero", "khatam", "nahi hai", "empty", "0 stock"],
        "sql": """
            SELECT b.item_code, i.item_name, b.warehouse, b.actual_qty
            FROM `tabBin` b
            LEFT JOIN `tabItem` i ON b.item_code = i.name
            WHERE i.is_stock_item = 1 AND b.actual_qty <= 0
            ORDER BY b.item_code
        """,
        "response": "Yeh items out of stock hain (zero ya negative qty):"
    },
    "item_groups": {
        "keywords": ["group", "category", "categories", "item group", "types"],
        "sql": """
            SELECT
                i.item_group,
                COUNT(DISTINCT b.item_code) AS items_count,
                SUM(b.actual_qty) AS total_qty
            FROM `tabBin` b
            LEFT JOIN `tabItem` i ON b.item_code = i.name
            WHERE i.is_stock_item = 1
            GROUP BY i.item_group
            ORDER BY total_qty DESC
        """,
        "response": "Item group-wise stock summary:"
    },
    "item_search": {
        "keywords": ["find", "search", "dhundho", "kahan hai", "show me"],
        "sql": None,  # Dynamic - handled separately
        "response": "Search results:"
    }
}


# --- NLP Engine ---
class StockQueryEngine:
    def __init__(self):
        self.engine = get_db_engine()

    def classify_intent(self, question):
        """Match user question to a query template using keyword matching."""
        question_lower = question.lower().strip()

        # Check each query template
        best_match = None
        best_score = 0

        for intent_name, config in QUERY_MAP.items():
            score = 0
            for keyword in config["keywords"]:
                if keyword in question_lower:
                    score += len(keyword)  # Longer keyword match = higher confidence

            if score > best_score:
                best_score = score
                best_match = intent_name

        return best_match if best_score > 0 else None

    def extract_item_name(self, question):
        """Try to extract a specific item name/code from the question."""
        # Look for SKU pattern
        sku_match = re.search(r'SKU\d+', question, re.IGNORECASE)
        if sku_match:
            return sku_match.group()

        # Look for quoted text
        quoted = re.findall(r'"([^"]+)"', question)
        if quoted:
            return quoted[0]

        return None

    def search_item(self, search_term):
        """Search for a specific item in the database."""
        query = text("""
            SELECT b.item_code, i.item_name, b.warehouse, b.actual_qty,
                   b.valuation_rate, (b.actual_qty * b.valuation_rate) AS stock_value
            FROM `tabBin` b
            LEFT JOIN `tabItem` i ON b.item_code = i.name
            WHERE i.is_stock_item = 1
              AND (b.item_code LIKE :search OR i.item_name LIKE :search)
            ORDER BY b.actual_qty DESC
        """)
        return pd.read_sql(query, self.engine, params={"search": f"%{search_term}%"})

    def ask(self, question):
        """Process a natural language question and return an answer."""
        intent = self.classify_intent(question)

        # Handle item search separately
        item_name = self.extract_item_name(question)
        if item_name:
            result = self.search_item(item_name)
            if result.empty:
                return f"'{item_name}' naam ka koi item nahi mila database mein."
            return f"'{item_name}' ke liye stock data:\n\n{result.to_string(index=False)}"

        if intent is None:
            return self._get_help_text()

        config = QUERY_MAP[intent]
        if config["sql"] is None:
            return self._get_help_text()

        try:
            result = pd.read_sql(text(config["sql"]), self.engine)
            if result.empty:
                return "Koi data nahi mila is query ke liye."

            response = config["response"] + "\n\n"
            response += result.to_string(index=False)
            return response
        except Exception as e:
            return f"Query mein error aaya: {str(e)}"

    def _get_help_text(self):
        return """
Mujhe samajh nahi aaya. Aap yeh pooch sakte ho:

  - "What's my lowest stock item?"
  - "Show me highest stock items"
  - "Total stock value kitni hai?"
  - "Which items need reorder?"
  - "Warehouse wise summary dikhao"
  - "Recent stock movements"
  - "Out of stock items dikhao"
  - "Item groups ka summary"
  - "Find SKU001" ya "Search laptop"

Koi bhi sawal poocho, main database se answer nikalunga!
"""


# --- Interactive CLI ---
def main():
    print("=" * 60)
    print("  StockSense AI - Natural Language Stock Query")
    print("=" * 60)
    print("  Apna sawal poocho (type 'exit' to quit)")
    print("=" * 60)

    engine = StockQueryEngine()

    while True:
        print()
        question = input("You > ").strip()

        if not question:
            continue
        if question.lower() in ['exit', 'quit', 'bye', 'q']:
            print("\nGoodbye! Happy warehousing! :)")
            break

        answer = engine.ask(question)
        print(f"\nAI > {answer}")


if __name__ == "__main__":
    main()
