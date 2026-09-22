-- =============================================================================
-- StockSense — Low Stock Items (Below Reorder Level)
-- =============================================================================
-- Purpose:  Identify items whose current actual stock has fallen below the
--           configured reorder level. Critical for preventing stockouts.
--
-- Source:   tabBin (actual quantities) + tabItem Reorder (reorder thresholds)
--
-- Note:     Not all items have reorder levels configured. This query only
--           returns items that DO have a reorder level set.
--
-- ⚠️ READ-ONLY — Do NOT modify ERPNext tables directly.
-- =============================================================================

SELECT
    b.item_code,
    i.item_name,
    i.item_group,
    b.warehouse,
    b.actual_qty,
    ir.warehouse_reorder_level  AS reorder_level,
    ir.warehouse_reorder_qty    AS reorder_qty,
    (ir.warehouse_reorder_level - b.actual_qty) AS shortfall
FROM
    `tabBin` b
    INNER JOIN `tabItem` i
        ON b.item_code = i.name
    INNER JOIN `tabItem Reorder` ir
        ON ir.parent = b.item_code
        AND ir.warehouse = b.warehouse
WHERE
    i.is_stock_item = 1
    AND b.actual_qty < ir.warehouse_reorder_level
ORDER BY
    shortfall DESC;
