-- =============================================================================
-- StockSense — Recent Stock Ledger Entries
-- =============================================================================
-- Purpose:  View the most recent stock movements (receipts, issues, transfers).
--           Useful for auditing recent activity and spotting anomalies.
--
-- Source:   tabStock Ledger Entry — ERPNext logs every stock transaction here.
--           actual_qty > 0 = stock IN, actual_qty < 0 = stock OUT.
--
-- ⚠️ READ-ONLY — Do NOT modify ERPNext tables directly.
-- =============================================================================

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
LIMIT 200;
