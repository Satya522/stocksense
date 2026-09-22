# Database Schema Notes — ERPNext MariaDB

## ⚠️ IMPORTANT: READ-ONLY Access

All SQL queries in this project are **strictly read-only (SELECT statements)**.
**Never run INSERT, UPDATE, DELETE, ALTER, or DROP** against ERPNext tables directly.
All data modifications should go through ERPNext's UI or REST API.

## ERPNext Table Naming Convention

ERPNext prefixes all DocType tables with `tab`. Examples:

| DocType | Table Name |
|---|---|
| Item | `tabItem` |
| Warehouse | `tabWarehouse` |
| Bin | `tabBin` |
| Stock Ledger Entry | `tabStock Ledger Entry` |
| Stock Entry | `tabStock Entry` |
| Sales Order | `tabSales Order` |
| Sales Order Item | `tabSales Order Item` |
| Purchase Order | `tabPurchase Order` |
| Material Request | `tabMaterial Request` |
| Item Price | `tabItem Price` |

> **Note:** Table/column names with spaces must be enclosed in backticks in SQL:
> `` `tabStock Ledger Entry` ``

## Key Tables for Warehouse Analytics

### `tabItem`
Master list of all items. Key columns: `name` (item_code), `item_name`,
`item_group`, `stock_uom`, `has_variants`, `is_stock_item`.

### `tabBin`
Current stock balance per item per warehouse. Key columns: `item_code`,
`warehouse`, `actual_qty`, `planned_qty`, `reserved_qty`, `ordered_qty`.

### `tabStock Ledger Entry`
Every stock transaction (receipt, issue, transfer). Key columns: `item_code`,
`warehouse`, `actual_qty` (positive=in, negative=out), `posting_date`,
`voucher_type`, `voucher_no`.

### `tabSales Order` / `tabSales Order Item`
Sales orders and their line items. Link via `parent` column in the Item table.

### `tabItem Reorder`
Reorder levels per item per warehouse. Key columns: `parent` (item_code),
`warehouse`, `warehouse_reorder_level`, `warehouse_reorder_qty`.

---

## How to find your database name

```sql
SHOW DATABASES;
```

Look for a database name matching your ERPNext site (often a hash like
`_1bd4c572c4ab6149` or a site name like `site1_local`).
