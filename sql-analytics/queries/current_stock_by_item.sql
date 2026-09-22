-- =============================================================================
-- StockSense — Current Stock by Item
-- =============================================================================
-- Purpose:  Get the current actual stock quantity for each item across all
--           warehouses. This is the most fundamental warehouse visibility query.
--
-- Source:   tabBin — ERPNext maintains this table with real-time stock balances.
--
-- ⚠️ READ-ONLY — Do NOT modify ERPNext tables directly. Use the ERPNext UI
--    or REST API for all data changes.
-- =============================================================================

SELECT
    b.item_code,
    i.item_name,
    i.item_group,
    i.stock_uom,
    SUM(b.actual_qty)     AS total_actual_qty,
    SUM(b.planned_qty)    AS total_planned_qty,
    SUM(b.reserved_qty)   AS total_reserved_qty,
    SUM(b.ordered_qty)    AS total_ordered_qty
FROM
    `tabBin` b
    LEFT JOIN `tabItem` i ON b.item_code = i.name
WHERE
    i.is_stock_item = 1
GROUP BY
    b.item_code,
    i.item_name,
    i.item_group,
    i.stock_uom
ORDER BY
    total_actual_qty DESC;
