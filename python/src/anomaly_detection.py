"""
StockSense - Stock Anomaly Detection
=====================================
Identifies unusual stock movements that could indicate:
  - Theft or pilferage (sudden unexplained drops)
  - Data entry errors (abnormally large transactions)
  - Supply chain disruptions (unusual patterns)

Uses statistical methods (Z-Score + IQR) for anomaly detection.

Usage:
  cd python
  venv\\Scripts\\activate
  python src/anomaly_detection.py
"""

import os
import warnings
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

warnings.filterwarnings('ignore')

# --- Database Connection ---
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


# --- Step 1: Extract Stock Ledger Data ---
def extract_ledger_data(engine):
    """Pull all stock ledger entries for analysis."""
    query = text("""
        SELECT
            name,
            item_code,
            warehouse,
            posting_date,
            posting_time,
            actual_qty,
            qty_after_transaction,
            valuation_rate,
            voucher_type,
            voucher_no
        FROM `tabStock Ledger Entry`
        ORDER BY item_code, posting_date, posting_time
    """)
    return pd.read_sql(query, engine)


# --- Step 2: Z-Score Anomaly Detection ---
def detect_zscore_anomalies(df, threshold=2.5):
    """Flag transactions where actual_qty deviates significantly from the item's norm."""
    df = df.copy()

    # Calculate per-item statistics
    item_stats = df.groupby('item_code')['actual_qty'].agg(['mean', 'std']).reset_index()
    item_stats.columns = ['item_code', 'qty_mean', 'qty_std']
    item_stats['qty_std'] = item_stats['qty_std'].replace(0, 1)  # Avoid division by zero

    df = df.merge(item_stats, on='item_code', how='left')

    # Z-Score calculation
    df['z_score'] = (df['actual_qty'] - df['qty_mean']) / df['qty_std']
    df['is_zscore_anomaly'] = df['z_score'].abs() > threshold

    return df


# --- Step 3: IQR-based Anomaly Detection ---
def detect_iqr_anomalies(df, multiplier=1.5):
    """Flag transactions outside the IQR fence per item."""
    df = df.copy()

    iqr_stats = df.groupby('item_code')['actual_qty'].agg(
        lambda x: pd.Series({
            'q1': x.quantile(0.25),
            'q3': x.quantile(0.75)
        })
    )

    # Recalculate properly
    q1 = df.groupby('item_code')['actual_qty'].quantile(0.25).rename('q1')
    q3 = df.groupby('item_code')['actual_qty'].quantile(0.75).rename('q3')
    iqr_df = pd.DataFrame({'q1': q1, 'q3': q3})
    iqr_df['iqr'] = iqr_df['q3'] - iqr_df['q1']
    iqr_df['lower_fence'] = iqr_df['q1'] - multiplier * iqr_df['iqr']
    iqr_df['upper_fence'] = iqr_df['q3'] + multiplier * iqr_df['iqr']

    df = df.merge(iqr_df[['lower_fence', 'upper_fence']], on='item_code', how='left')
    df['is_iqr_anomaly'] = (df['actual_qty'] < df['lower_fence']) | (df['actual_qty'] > df['upper_fence'])

    return df


# --- Step 4: Classify Anomaly Types ---
def classify_anomalies(df):
    """Classify detected anomalies into business-relevant categories."""
    df = df.copy()
    df['is_anomaly'] = df['is_zscore_anomaly'] | df['is_iqr_anomaly']

    conditions = [
        (df['is_anomaly']) & (df['actual_qty'] < 0) & (df['z_score'].abs() > 3),
        (df['is_anomaly']) & (df['actual_qty'] > 0) & (df['z_score'].abs() > 3),
        (df['is_anomaly']) & (df['actual_qty'] < 0),
        (df['is_anomaly']) & (df['actual_qty'] > 0),
    ]
    choices = [
        'CRITICAL: Suspicious large outflow',
        'CRITICAL: Unusually large inflow',
        'WARNING: Above-normal outflow',
        'WARNING: Above-normal inflow'
    ]
    df['anomaly_type'] = np.select(conditions, choices, default='NORMAL')

    return df


# --- Step 5: Generate Report ---
def generate_anomaly_report(df):
    """Save anomaly results for Power BI and review."""
    anomalies = df[df['is_anomaly']].copy()

    output_cols = [
        'name', 'item_code', 'warehouse', 'posting_date',
        'actual_qty', 'qty_after_transaction', 'voucher_type', 'voucher_no',
        'z_score', 'anomaly_type'
    ]

    output_path = Path(__file__).resolve().parent.parent.parent / "data" / "anomaly_report.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not anomalies.empty:
        anomalies[output_cols].to_csv(output_path, index=False)
    else:
        pd.DataFrame(columns=output_cols).to_csv(output_path, index=False)

    print(f"\nAnomaly report saved to: {output_path}")
    return output_path


def detect_anomalies():
    """Extracts stock movements, computes Z-Score & IQR anomalies, and returns structured records."""
    csv_path = Path(__file__).resolve().parent.parent.parent / "data" / "anomaly_report.csv"
    try:
        engine = get_db_engine()
        ledger = extract_ledger_data(engine)
        if not ledger.empty:
            ledger = detect_zscore_anomalies(ledger, threshold=2.5)
            ledger = detect_iqr_anomalies(ledger, multiplier=1.5)
            ledger = classify_anomalies(ledger)
            anomalies = ledger[ledger['is_anomaly']]
            output_cols = [
                'item_code', 'warehouse', 'posting_date', 'actual_qty',
                'qty_after_transaction', 'z_score', 'anomaly_type', 'voucher_type', 'voucher_no'
            ]
            cols = [c for c in output_cols if c in anomalies.columns]
            res = anomalies[cols].copy()
            generate_anomaly_report(ledger)
            records = []
            for r in res.to_dict(orient="records"):
                clean = {}
                for k, v in r.items():
                    if pd.isna(v):
                        clean[k] = None
                    elif isinstance(v, (np.floating, float)):
                        clean[k] = round(float(v), 2)
                    elif isinstance(v, (np.integer, int)):
                        clean[k] = int(v)
                    else:
                        clean[k] = str(v)
                records.append(clean)
            return records
    except Exception as e:
        print(f"[WARN] Live anomaly detection failed: {e}")

    if csv_path.exists():
        try:
            df = pd.read_csv(csv_path)
            return df.to_dict(orient="records")
        except Exception:
            pass
    return []


# --- Main Execution ---
if __name__ == "__main__":
    print("=" * 60)
    print("StockSense - Anomaly Detection Engine")
    print("=" * 60)

    engine = get_db_engine()

    print("\n[1/5] Extracting stock ledger data...")
    ledger = extract_ledger_data(engine)
    print(f"       Loaded {len(ledger)} ledger entries for {ledger['item_code'].nunique()} items")

    print("\n[2/5] Running Z-Score anomaly detection (threshold=2.5)...")
    ledger = detect_zscore_anomalies(ledger, threshold=2.5)
    z_count = ledger['is_zscore_anomaly'].sum()
    print(f"       Found {z_count} Z-Score anomalies")

    print("\n[3/5] Running IQR anomaly detection (multiplier=1.5)...")
    ledger = detect_iqr_anomalies(ledger, multiplier=1.5)
    iqr_count = ledger['is_iqr_anomaly'].sum()
    print(f"       Found {iqr_count} IQR anomalies")

    print("\n[4/5] Classifying anomaly types...")
    ledger = classify_anomalies(ledger)
    total_anomalies = ledger['is_anomaly'].sum()
    print(f"       Total unique anomalies: {total_anomalies}")

    print("\n[5/5] Generating anomaly report...")
    report_path = generate_anomaly_report(ledger)

    # Summary
    print("\n" + "=" * 60)
    print("ANOMALY SUMMARY")
    print("=" * 60)
    if total_anomalies > 0:
        summary = ledger[ledger['is_anomaly']].groupby('anomaly_type').size()
        for atype, count in summary.items():
            print(f"  {atype}: {count}")
    else:
        print("  No anomalies detected. All stock movements look normal.")
    print("=" * 60)
