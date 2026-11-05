"""
StockSense - Machine Learning & Analytics Unit Tests
===================================================
Validates:
  1. Demand forecasting output format and accuracy
  2. Feature engineering pipeline for time-series models
  3. Anomaly detection extraction and classification
  4. Natural language query fallback logic
"""

import pytest
import pandas as pd
from demand_forecast import predict_demand, create_features
from anomaly_detection import detect_anomalies
from ai_query_api import APIHandler


def test_predict_demand_records():
    """Verify demand forecasting returns valid structured predictions."""
    forecasts = predict_demand()
    assert isinstance(forecasts, list)
    assert len(forecasts) > 0

    first = forecasts[0]
    assert "item_code" in first
    assert "avg_daily_demand_forecast" in first
    assert "weekly_demand_forecast" in first
    assert float(first["weekly_demand_forecast"]) >= 0


def test_create_features_pipeline():
    """Verify feature engineering generates correct lag and rolling window columns."""
    sample_data = pd.DataFrame([
        {"item_code": "SKU-01", "movement_date": "2026-09-01", "daily_outflow": 10.0, "daily_inflow": 0.0, "transaction_count": 1},
        {"item_code": "SKU-01", "movement_date": "2026-09-02", "daily_outflow": 15.0, "daily_inflow": 0.0, "transaction_count": 2},
        {"item_code": "SKU-01", "movement_date": "2026-09-03", "daily_outflow": 20.0, "daily_inflow": 50.0, "transaction_count": 1},
        {"item_code": "SKU-01", "movement_date": "2026-09-04", "daily_outflow": 25.0, "daily_inflow": 0.0, "transaction_count": 1},
    ])

    features_df = create_features(sample_data)
    assert "day_of_week" in features_df.columns
    assert "rolling_avg_3d" in features_df.columns
    assert "lag_1d" in features_df.columns
    assert len(features_df) == 4
    # Lag 1 of row index 1 should match outflow of row index 0
    assert float(features_df.iloc[1]["lag_1d"]) == 10.0


def test_detect_anomalies_records():
    """Verify anomaly detection returns structured anomaly items."""
    anomalies = detect_anomalies()
    assert isinstance(anomalies, list)
    assert len(anomalies) > 0

    first = anomalies[0]
    assert "item_code" in first
    assert "anomaly_type" in first
    assert "z_score" in first
    assert float(first["z_score"]) > 0


def test_api_handler_fallback_answers():
    """Verify NLP/fallback Q&A produces coherent replies for inventory queries."""
    handler = APIHandler.__new__(APIHandler)

    # Test 'lowest' query
    lowest_ans = handler._fallback_answer("What items have the lowest stock?")
    assert isinstance(lowest_ans, str)
    assert len(lowest_ans) > 0

    # Test 'value' or 'total' query
    val_ans = handler._fallback_answer("What is the total value of stock?")
    assert isinstance(val_ans, str)
    assert len(val_ans) > 0

    # Test unknown query
    default_ans = handler._fallback_answer("Tell me about weather in warehouse")
    assert isinstance(default_ans, str)
    assert len(default_ans) > 0
