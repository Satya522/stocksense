"""
StockSense - Python Web Dashboard (Streamlit)
=============================================
A modern, live dashboard reading directly from ERPNext MariaDB.
To run: 
  cd python
  venv\Scripts\activate
  streamlit run src/dashboard.py
"""

import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# --- Configuration & Setup ---
st.set_page_config(page_title="StockSense Dashboard", page_icon="📦", layout="wide")

@st.cache_resource
def get_db_engine():
    """Create and cache the database connection."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
    
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")

    if not all([db_user, db_password, db_name]):
        st.error("Database credentials missing in .env file.")
        st.stop()

    conn_str = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(conn_str)

@st.cache_data(ttl=60)
def load_data(query):
    """Fetch data from MariaDB and cache it for 60 seconds."""
    engine = get_db_engine()
    return pd.read_sql(text(query), engine)

# --- Queries ---
CURRENT_STOCK_QUERY = """
    SELECT b.item_code, i.item_name, i.item_group, SUM(b.actual_qty) AS total_qty
    FROM `tabBin` b
    LEFT JOIN `tabItem` i ON b.item_code = i.name
    WHERE i.is_stock_item = 1
    GROUP BY b.item_code, i.item_name, i.item_group
    ORDER BY total_qty DESC;
"""

LOW_STOCK_QUERY = """
    SELECT b.item_code, i.item_name, b.warehouse, b.actual_qty, 
           ir.warehouse_reorder_level AS reorder_level,
           (ir.warehouse_reorder_level - b.actual_qty) AS shortfall
    FROM `tabBin` b
    INNER JOIN `tabItem` i ON b.item_code = i.name
    INNER JOIN `tabItem Reorder` ir ON ir.parent = b.item_code AND ir.warehouse = b.warehouse
    WHERE i.is_stock_item = 1 AND b.actual_qty < ir.warehouse_reorder_level
    ORDER BY shortfall DESC;
"""

# --- Dashboard UI ---
st.title("📦 StockSense Intelligence")
st.markdown("Live warehouse analytics powered by ERPNext data.")

try:
    # Load Data
    df_stock = load_data(CURRENT_STOCK_QUERY)
    df_low = load_data(LOW_STOCK_QUERY)

    # --- Top KPIs ---
    col1, col2, col3 = st.columns(3)
    
    total_items = len(df_stock)
    total_qty = df_stock['total_qty'].sum() if not df_stock.empty else 0
    low_stock_alerts = len(df_low)

    col1.metric("Total Unique Items in Stock", f"{total_items:,}")
    col2.metric("Total Physical Quantity", f"{total_qty:,.2f}")
    col3.metric("🚨 Low Stock Alerts", f"{low_stock_alerts:,}")

    st.markdown("---")

    # --- Charts & Tables ---
    left_col, right_col = st.columns((2, 1))

    with left_col:
        st.subheader("Current Stock Levels (Top 15)")
        if not df_stock.empty:
            chart_data = df_stock.head(15).set_index('item_name')['total_qty']
            st.bar_chart(chart_data, use_container_width=True)
        else:
            st.info("No stock data available yet.")

    with right_col:
        st.subheader("⚠️ Critical Low Stock")
        if not df_low.empty:
            st.dataframe(
                df_low[['item_name', 'actual_qty', 'shortfall']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("All items are well stocked!")

    st.markdown("---")
    st.subheader("Full Stock Directory")
    st.dataframe(df_stock, use_container_width=True)

except Exception as e:
    st.error(f"Failed to load dashboard data: {e}")
