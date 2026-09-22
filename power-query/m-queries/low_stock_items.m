// =============================================================================
// StockSense — Power Query M Script: Low Stock Items
// =============================================================================
// Paste this into Power BI Desktop → Home → Transform Data → Advanced Editor
// =============================================================================

let
    Source = MySQL.Database("localhost:3306", "_7e269a3c97126b3e", [
        Query = "
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
                shortfall DESC
        "
    ]),
    TypedColumns = Table.TransformColumnTypes(Source, {
        {"item_code", type text},
        {"item_name", type text},
        {"item_group", type text},
        {"warehouse", type text},
        {"actual_qty", type number},
        {"reorder_level", type number},
        {"reorder_qty", type number},
        {"shortfall", type number}
    })
in
    TypedColumns
