# 📦 StockSense

**Warehouse Operations Analytics & Intelligence Platform — built on ERPNext**

> **StockSense** gives you a smart, 360-degree view of your warehouse operations —
> from raw ERP data all the way to AI-driven insights. Built by a warehouse operations
> professional transitioning into IT, this project solves real inventory visibility
> and stock-management problems using ERPNext as the open-source ERP backbone.
> The rest of the stack layers on analytics, automation, and intelligence to make
> warehouse data truly actionable.

---

## Tech Stack

| Technology | Role in StockSense |
|---|---|
| **ERPNext (Docker)** | Core ERP — Items, Stock, Sales Orders, Purchase Orders |
| **MariaDB / MySQL** | ERPNext's underlying database — direct SQL analytics |
| **Power Query (M)** | ETL layer — transform and shape data for dashboards |
| **Power BI** | Interactive BI dashboards for stock, sales, and ops KPIs |
| **Python** | Data scripts, API integration, forecasting, anomaly detection |
| **Excel VBA** | Bulk operations macros calling ERPNext REST API |
| **Google Apps Script** | Google Forms → ERPNext automation (Material Requests) |
| **JavaScript** | ERPNext client-side customization |
| **Docker Compose** | Full-stack containerised deployment (Phase 4) |

---

## Folder Structure

```
stocksense/
├── erpnext-setup/           → Docker connection notes & custom DocType docs
├── excel-automation/        → VBA macros for bulk order processing (Phase 2)
├── sheets-automation/       → Google Apps Script automation (Phase 2)
├── sql-analytics/           → Read-only SQL analytics queries against ERPNext DB
├── power-query/             → Power Query M scripts for ETL transformations
├── powerbi-dashboards/      → Power BI setup guide & M query templates
├── python/                  → Python scripts: API tests, data analysis, AI (Phase 3-4)
├── docs/                    → Architecture diagrams & project roadmap
├── .gitignore
└── README.md                → You are here
```

---

## 🚀 Getting Started (Phase 1)

### Prerequisites

- Docker with ERPNext running locally
- Python 3.10+
- Power BI Desktop
- Git

### Step 1 — Clone & set up Python environment

```bash
cd stocksense/python
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

### Step 2 — Configure your environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your ERPNext URL, API key/secret, and MariaDB credentials.

> **How to get ERPNext API keys:**
> 1. Log in to your ERPNext site (e.g. `http://localhost:8000`)
> 2. Go to **Settings → User** → select your user
> 3. Scroll to **API Access** → click **Generate Keys**
> 4. Copy the API Key and API Secret into your `.env`

### Step 3 — Test connections

```bash
cd python
python src/test_connection.py
```

You should see Item counts from both the REST API and direct database connections.

### Step 4 — Run SQL queries

Use any MySQL/MariaDB client (DBeaver, MySQL Workbench, or the `mysql` CLI) to run
the queries in `sql-analytics/queries/` against your ERPNext database.

### Step 5 — Connect Power BI

Follow the instructions in `powerbi-dashboards/README.md` to connect Power BI
Desktop to your local MariaDB and start building dashboards.

---

## 🗺️ Roadmap

| Phase | Focus | Status |
|---|---|---|
| **Phase 1** | ERPNext + SQL + Power BI core dashboard | 🟢 Current |
| **Phase 2** | Excel VBA + Google Sheets/Apps Script automation | ⬜ Planned |
| **Phase 3** | Power Query multi-source ETL + Python forecasting | ⬜ Planned |
| **Phase 4** | AI NLP layer + JS ERPNext customization + Docker Compose | ⬜ Planned |

See the full roadmap → [`docs/roadmap.md`](docs/roadmap.md)

---

## License

This project is for educational and portfolio purposes.
