"""
StockSense - Backend API Unit & Integration Tests
=================================================
Validates stats calculation, stock telemetry, and full CRUD cycle:
  - Create (add_inventory_item)
  - Read   (get_stock_data, get_dashboard_stats)
  - Update (update_inventory_item)
  - Delete (delete_inventory_item)
  - Reorder placement (create_reorder_request)
"""

import json
import pytest
from ai_query_api import (
    get_dashboard_stats,
    get_stock_data,
    add_inventory_item,
    update_inventory_item,
    delete_inventory_item,
    create_reorder_request,
    load_reorders,
    load_overrides,
    save_overrides,
    get_warehouses,
    get_top_items,
    get_recent_activity,
    REORDERS_FILE,
)


def test_get_dashboard_stats_structure():
    """Verify dashboard stats has required keys and positive values."""
    stats = get_dashboard_stats()
    assert isinstance(stats, dict)
    assert "total_items" in stats
    assert "total_qty" in stats
    assert "total_value" in stats
    assert "low_stock_alerts" in stats
    assert "orders_this_month" in stats
    assert stats["total_items"] > 0
    assert stats["total_qty"] >= 0


def test_get_stock_data_items():
    """Verify stock data contains valid items with health statuses."""
    stock = get_stock_data()
    assert isinstance(stock, list)
    assert len(stock) > 0

    first = stock[0]
    assert "item_code" in first
    assert "warehouse" in first
    assert "qty" in first
    assert "reorder_level" in first
    assert "status" in first
    assert first["status"] in ["healthy", "warning", "critical"]


def test_inventory_crud_lifecycle():
    """
    Test full lifecycle:
    1. Create item
    2. Read & verify presence
    3. Update quantity
    4. Verify update
    5. Delete item
    6. Verify removal
    """
    test_code = "PYTEST-SKU-999"
    test_wh = "WH-North"

    # Clean up prior state if any
    delete_inventory_item({"code": test_code, "warehouse": test_wh})

    # 1. CREATE
    add_payload = {
        "code": test_code,
        "name": "Pytest Sensor Module",
        "warehouse": test_wh,
        "qty": 100,
        "reorder": 25,
        "rate": 350
    }
    res_add = add_inventory_item(add_payload)
    assert res_add["success"] is True
    assert res_add["item"]["item_code"] == test_code

    # 2. READ
    stock = get_stock_data()
    found = [s for s in stock if s.get("item_code") == test_code and s.get("warehouse") == test_wh]
    assert len(found) == 1
    assert float(found[0]["qty"]) == 100.0
    assert float(found[0]["reorder_level"]) == 25.0

    # 3. UPDATE
    update_payload = {
        "code": test_code,
        "warehouse": test_wh,
        "qty": 15,  # Drop below reorder level (25) to trigger 'critical'
        "reorder": 25
    }
    res_up = update_inventory_item(update_payload)
    assert res_up["success"] is True

    # 4. VERIFY UPDATE & STATUS
    stock_after_up = get_stock_data()
    updated = [s for s in stock_after_up if s.get("item_code") == test_code and s.get("warehouse") == test_wh][0]
    assert float(updated["qty"]) == 15.0
    assert updated["status"] == "critical"

    # 5. DELETE
    res_del = delete_inventory_item({"code": test_code, "warehouse": test_wh})
    assert res_del["success"] is True

    # 6. VERIFY REMOVAL
    stock_after_del = get_stock_data()
    deleted_matches = [s for s in stock_after_del if s.get("item_code") == test_code and s.get("warehouse") == test_wh]
    assert len(deleted_matches) == 0

    # Clean up test artifact from deletions
    overrides = load_overrides()
    overrides["deletions"] = [d for d in overrides.get("deletions", []) if test_code not in d]
    save_overrides(overrides)


def test_create_reorder_request():
    """Verify purchase requisition creation and logging."""
    order_payload = {
        "item_code": "SKU001",
        "item_name": "Arduino Uno R3",
        "warehouse": "WH-North",
        "qty": 75,
        "priority": "Urgent",
        "supplier": "Apex Industrial Tech",
        "notes": "Automated replenishment test"
    }
    res = create_reorder_request(order_payload)
    assert res["success"] is True
    assert "order_id" in res
    assert res["order_id"].startswith("MR-")

    # Verify presence in reorder log
    reorders = load_reorders()
    matching = [r for r in reorders if r.get("order_id") == res["order_id"]]
    assert len(matching) == 1
    assert matching[0]["qty"] == 75.0
    assert matching[0]["priority"] == "Urgent"

    # Clean up test reorder entry
    all_reorders = [r for r in load_reorders() if r.get("order_id") != res["order_id"]]
    with open(REORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_reorders, f, indent=2)


def test_get_warehouses_breakdown():
    """Verify warehouse aggregations contain valid counts and numeric totals."""
    whs = get_warehouses()
    assert isinstance(whs, list)
    assert len(whs) > 0
    first = whs[0]
    assert "name" in first
    assert "items" in first
    assert "total_qty" in first
    assert "total_value" in first
    assert float(first["total_qty"]) >= 0


def test_get_top_items_chart_data():
    """Verify top items returned for UI charts with color fill."""
    top = get_top_items()
    assert isinstance(top, list)
    assert len(top) > 0
    assert len(top) <= 8
    first = top[0]
    assert "name" in first
    assert "value" in first
    assert "fill" in first
    assert first["fill"].startswith("#")


def test_get_recent_activity_feed():
    """Verify recent stock movements feed structure."""
    activities = get_recent_activity()
    assert isinstance(activities, list)
    if len(activities) > 0:
        first = activities[0]
        assert "item_code" in first
        assert "warehouse" in first
        assert "voucher_type" in first
