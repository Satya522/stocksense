// =============================================================================
// StockSense — Power Query M Script: Sales Order Summary
// =============================================================================
// Paste this into Power BI Desktop → Home → Transform Data → Advanced Editor
// =============================================================================

let
    Source = MySQL.Database("localhost:3306", "_7e269a3c97126b3e", [
        Query = "
            SELECT
                so.status,
                COUNT(*)                  AS order_count,
                SUM(so.grand_total)       AS total_value,
                SUM(so.total_qty)         AS total_qty
            FROM
                `tabSales Order` so
            WHERE
                so.docstatus = 1          -- Only submitted (confirmed) orders
            GROUP BY
                so.status
            ORDER BY
                total_value DESC
        "
    ]),
    TypedColumns = Table.TransformColumnTypes(Source, {
        {"status", type text},
        {"order_count", type number},
        {"total_value", type number},
        {"total_qty", type number}
    })
in
    TypedColumns
