"""
StockSense - Data Extraction Script
===================================
Demonstrates extracting ERPNext data directly into pandas DataFrames via SQL.
This acts as the bridge for future Python-based analytics and forecasting (Phase 3/4).

Usage:
  cd python
  python src/extract_data.py
"""

import os
import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load credentials
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def get_db_engine():
    """Create and return a SQLAlchemy engine using .env credentials."""
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")

    if not db_user or not db_password or not db_name:
        print("[FAIL] Database credentials missing in .env")
        sys.exit(1)

    conn_str = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(conn_str)

def extract_current_stock():
    """Extract current stock using the SQL query from sql-analytics."""
    print("Extracting current stock...")
    query = """
        SELECT
            b.item_code,
            i.item_name,
            i.item_group,
            i.stock_uom,
            SUM(b.actual_qty)     AS total_actual_qty
        FROM `tabBin` b
        LEFT JOIN `tabItem` i ON b.item_code = i.name
        WHERE i.is_stock_item = 1
        GROUP BY b.item_code, i.item_name, i.item_group, i.stock_uom
        ORDER BY total_actual_qty DESC;
    """
    engine = get_db_engine()
    df = pd.read_sql(text(query), engine)
    return df

def main():
    print("[StockSense] Data Extraction Demo")
    print("=" * 40)
    
    try:
        stock_df = extract_current_stock()
        if stock_df.empty:
            print("No stock data found (expected if ERPNext is empty).")
        else:
            print(f"Loaded {len(stock_df)} stock records.")
            print(stock_df.head())
            
            # Example of saving to CSV for manual review
            # output_path = Path(__file__).resolve().parent.parent / "exports" / "stock_extract.csv"
            # output_path.parent.mkdir(exist_ok=True)
            # stock_df.to_csv(output_path, index=False)
            # print(f"Data exported to {output_path}")

    except Exception as e:
        print(f"Extraction failed: {e}")

if __name__ == "__main__":
    main()
