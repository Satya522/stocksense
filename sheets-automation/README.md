# Google Sheets + Apps Script Automation

> **Status:** Phase 2 — not yet implemented.

## What will go here

This folder will contain **Google Apps Script files (.gs)** that automate warehouse
workflows between Google Sheets/Forms and ERPNext.

### Planned scripts

| Script | Purpose |
|---|---|
| `FormToMaterialRequest.gs` | When a warehouse worker submits a Google Form (requesting materials), this script reads the form response and creates a **Material Request** in ERPNext via the REST API |
| `StockDashboardSync.gs` | Periodically pull current stock levels from ERPNext into a Google Sheet for sharing with non-ERP users |
| `ERPNextAPI.gs` | Shared utility: authenticated API calls to ERPNext from Apps Script |

### How it will work

1. A Google Form collects: Item Code, Quantity Needed, Warehouse, Requested By
2. On form submit, an Apps Script trigger fires
3. The script calls ERPNext API:
   - `POST /api/resource/Material Request` with the form data
4. Confirmation is logged in the linked Google Sheet

### Prerequisites for Phase 2
- Google Cloud project with Apps Script API enabled
- ERPNext API credentials stored in Apps Script PropertiesService
- Google Form linked to a Google Sheet

---

*The `scripts/` subfolder will contain the `.gs` files once developed.*
