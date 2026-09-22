// =============================================================================
// StockSense — Power Query M Script: Recent Stock Ledger Entries
// =============================================================================
// Paste this into Power BI Desktop → Home → Transform Data → Advanced Editor
// =============================================================================

let
    Source = MySQL.Database("localhost:3306", "_7e269a3c97126b3e", [
        Query = "
            SELECT
                sle.posting_date,
                sle.posting_time,
                sle.item_code,
                i.item_name,
                sle.warehouse,
                sle.actual_qty,
                sle.qty_after_transaction,
                sle.voucher_type,
                sle.voucher_no,
                sle.batch_no,
                sle.valuation_rate
            FROM
                `tabStock Ledger Entry` sle
                LEFT JOIN `tabItem` i ON sle.item_code = i.name
            ORDER BY
                sle.posting_date DESC,
                sle.posting_time DESC
            LIMIT 200
        "
    ]),
    TypedColumns = Table.TransformColumnTypes(Source, {
        {"posting_date", type date},
        {"posting_time", type time},
        {"item_code", type text},
        {"item_name", type text},
        {"warehouse", type text},
        {"actual_qty", type number},
        {"qty_after_transaction", type number},
        {"voucher_type", type text},
        {"voucher_no", type text},
        {"batch_no", type text},
        {"valuation_rate", type number}
    })
in
    TypedColumns
