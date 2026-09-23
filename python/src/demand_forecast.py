"""
StockSense - Demand Forecasting Model
======================================
Uses historical stock ledger data from ERPNext to predict future demand
for each item using time-series analysis and scikit-learn.

Usage:
  cd python
  venv\\Scripts\\activate
  python src/demand_forecast.py
"""

import os
import warnings
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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


# --- Step 1: Extract Historical Movement Data ---
def extract_stock_movements(engine):
    """Pull stock ledger entries grouped by item and date."""
    query = text("""
        SELECT
            item_code,
            DATE(posting_date) AS movement_date,
            SUM(CASE WHEN actual_qty < 0 THEN ABS(actual_qty) ELSE 0 END) AS daily_outflow,
            SUM(CASE WHEN actual_qty > 0 THEN actual_qty ELSE 0 END) AS daily_inflow,
            COUNT(*) AS transaction_count
        FROM `tabStock Ledger Entry`
        GROUP BY item_code, DATE(posting_date)
        ORDER BY item_code, movement_date
    """)
    return pd.read_sql(query, engine)


# --- Step 2: Feature Engineering ---
def create_features(df):
    """Create time-series features for demand prediction."""
    df = df.copy()
    df['movement_date'] = pd.to_datetime(df['movement_date'])
    df['day_of_week'] = df['movement_date'].dt.dayofweek
    df['day_of_month'] = df['movement_date'].dt.day
    df['month'] = df['movement_date'].dt.month
    df['week_of_year'] = df['movement_date'].dt.isocalendar().week.astype(int)
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)

    # Rolling averages per item
    for window in [3, 7, 14]:
        df[f'rolling_avg_{window}d'] = (
            df.groupby('item_code')['daily_outflow']
            .transform(lambda x: x.rolling(window, min_periods=1).mean())
        )

    # Lag features
    for lag in [1, 3, 7]:
        df[f'lag_{lag}d'] = (
            df.groupby('item_code')['daily_outflow']
            .transform(lambda x: x.shift(lag))
        )

    df = df.fillna(0)
    return df


# --- Step 3: Train Forecast Model ---
def train_forecast_model(df):
    """Train a simple gradient boosting model per item."""
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.model_selection import TimeSeriesSplit
    from sklearn.metrics import mean_absolute_error

    feature_cols = [
        'day_of_week', 'day_of_month', 'month', 'week_of_year', 'is_weekend',
        'rolling_avg_3d', 'rolling_avg_7d', 'rolling_avg_14d',
        'lag_1d', 'lag_3d', 'lag_7d', 'daily_inflow', 'transaction_count'
    ]

    models = {}
    results = []

    items = df['item_code'].unique()
    print(f"\nTraining models for {len(items)} items...")

    for item in items:
        item_df = df[df['item_code'] == item].sort_values('movement_date')

        if len(item_df) < 10:
            print(f"  [SKIP] {item}: Not enough data ({len(item_df)} rows)")
            continue

        X = item_df[feature_cols]
        y = item_df['daily_outflow']

        # Use last 20% as test
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            random_state=42
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)

        models[item] = model

        # Predict next 7 days average demand
        avg_predicted = float(np.mean(y_pred[-7:])) if len(y_pred) >= 7 else float(np.mean(y_pred))

        results.append({
            'item_code': item,
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'mae': round(mae, 2),
            'avg_daily_demand_forecast': round(avg_predicted, 2),
            'weekly_demand_forecast': round(avg_predicted * 7, 2)
        })

        print(f"  [OK] {item}: MAE={mae:.2f}, Forecast={avg_predicted:.2f}/day")

    return models, pd.DataFrame(results)


# --- Step 4: Generate Forecast Report ---
def generate_forecast_report(forecast_df):
    """Save forecast results to CSV for Power BI consumption."""
    output_path = Path(__file__).resolve().parent.parent.parent / "data" / "demand_forecast_results.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    forecast_df.to_csv(output_path, index=False)
    print(f"\nForecast report saved to: {output_path}")
    return output_path


# --- Main Execution ---
if __name__ == "__main__":
    print("=" * 60)
    print("StockSense - Demand Forecasting Engine")
    print("=" * 60)

    engine = get_db_engine()

    print("\n[1/4] Extracting stock movement history...")
    movements = extract_stock_movements(engine)
    print(f"       Loaded {len(movements)} movement records for {movements['item_code'].nunique()} items")

    print("\n[2/4] Engineering features...")
    features = create_features(movements)
    print(f"       Created {len(features.columns)} features")

    print("\n[3/4] Training forecast models...")
    models, forecast_df = train_forecast_model(features)

    print("\n[4/4] Generating forecast report...")
    report_path = generate_forecast_report(forecast_df)

    print("\n" + "=" * 60)
    print("FORECAST SUMMARY")
    print("=" * 60)
    if not forecast_df.empty:
        print(forecast_df.to_string(index=False))
    else:
        print("No items had enough data for forecasting.")
    print("=" * 60)
