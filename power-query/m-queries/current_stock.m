// =============================================================================
// StockSense — Power Query M Script: Current Stock by Item
// =============================================================================
// Paste this into Power BI Desktop → Home → Transform Data → Advanced Editor
//
// Before using:
// 1. Replace "localhost" with your DB_HOST if different
// 2. Replace "your_erpnext_site_db" with your actual ERPNext database name
//    (run SHOW DATABASES; in MariaDB to find it)
// 3. You'll be prompted for credentials on first run — use your DB_USER / DB_PASSWORD
// =============================================================================

let
    Source = MySQL.Database("localhost:3306", "_7e269a3c97126b3e", [
        Query = "
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
                total_actual_qty DESC
        "
    ]),
    // Ensure proper data types
    TypedColumns = Table.TransformColumnTypes(Source, {
        {"item_code", type text},
        {"item_name", type text},
        {"item_group", type text},
        {"stock_uom", type text},
        {"total_actual_qty", type number},
        {"total_planned_qty", type number},
        {"total_reserved_qty", type number},
        {"total_ordered_qty", type number}
    })
in
    TypedColumns
