-- =============================================================================
-- StockSense — Sales Order Summary
-- =============================================================================
-- Purpose:  Aggregate sales orders by status, customer, and time period.
--           Gives a high-level view of demand flowing through the warehouse.
--
-- Source:   tabSales Order (header) + tabSales Order Item (line items)
--
-- ⚠️ READ-ONLY — Do NOT modify ERPNext tables directly.
-- =============================================================================

-- ----- Summary by Status -----
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
    total_value DESC;


-- ----- Monthly Sales Trend -----
/*
SELECT
    DATE_FORMAT(so.transaction_date, '%Y-%m')  AS month,
    COUNT(*)                                    AS order_count,
    SUM(so.grand_total)                         AS total_value,
    SUM(so.total_qty)                           AS total_qty
FROM
    `tabSales Order` so
WHERE
    so.docstatus = 1
GROUP BY
    DATE_FORMAT(so.transaction_date, '%Y-%m')
ORDER BY
    month DESC
LIMIT 12;
*/


-- ----- Top 10 Customers by Order Value -----
/*
SELECT
    so.customer,
    so.customer_name,
    COUNT(*)                  AS order_count,
    SUM(so.grand_total)       AS total_value
FROM
    `tabSales Order` so
WHERE
    so.docstatus = 1
GROUP BY
    so.customer,
    so.customer_name
ORDER BY
    total_value DESC
LIMIT 10;
*/
