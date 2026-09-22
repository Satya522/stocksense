# Excel Automation (VBA Macros)

> **Status:** Phase 2 — not yet implemented.

## What will go here

This folder will contain **VBA macro modules (.bas files)** for automating warehouse
operations tasks from Excel, calling the ERPNext REST API.

### Planned modules

| Module | Purpose |
|---|---|
| `BulkOrderProcessor.bas` | Read a list of Sales/Purchase Orders from an Excel sheet, validate them, and push them to ERPNext via the API in bulk |
| `StockUpdateHelper.bas` | Fetch current stock levels from ERPNext and populate an Excel sheet for review/editing |
| `ERPNextAPIUtils.bas` | Shared utility functions: HTTP requests, JSON parsing, auth header generation |

### How it will work

1. User opens an Excel workbook with a structured input sheet (Item Code, Qty, Warehouse, etc.)
2. A VBA macro reads the rows, validates data, and calls ERPNext's REST API:
   - `POST /api/resource/Sales Order`
   - `POST /api/resource/Purchase Order`
3. Results (success/errors) are logged back into the Excel sheet

### Prerequisites for Phase 2
- ERPNext API key and secret (already in `.env`)
- VBA reference to `Microsoft XML, v6.0` for HTTP requests
- `VBA-JSON` library for JSON parsing (https://github.com/VBA-tools/VBA-JSON)

---

*The `modules/` subfolder will contain the `.bas` files once developed.*
