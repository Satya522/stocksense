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
| **React 19 + Vite** | Modern Command Center Frontend (Dashboard, Inventory, Forecasts, Anomalies, AI Chat) |
| **Tailwind CSS + Recharts** | High-performance responsive charts, telemetry rings, and glassmorphism UI |
| **ERPNext (Docker)** | Core ERP — Items, Stock, Sales Orders, Purchase Orders |
| **MariaDB / MySQL** | ERPNext's underlying database — direct SQL analytics |
| **Power Query (M)** | ETL layer — transform and shape data for dashboards |
| **Power BI** | Interactive BI dashboards for stock, sales, and ops KPIs |
| **Python / FastAPI / HTTP** | REST API server, ML demand forecasting (GBR), Z-Score anomaly detection |
| **Excel VBA** | Bulk operations macros calling ERPNext REST API |
| **Google Apps Script** | Google Forms → ERPNext automation (Material Requests) |
| **JavaScript** | ERPNext client-side customization |
| **Docker Compose** | Full-stack containerised deployment |

---

## Folder Structure

```
stocksense/
├── stocksense-frontend/     → React 19 + Vite Command Center web application
├── erpnext-setup/           → Docker connection notes & custom DocType docs
├── excel-automation/        → VBA macros for bulk order processing
├── sheets-automation/       → Google Apps Script automation
├── sql-analytics/           → Read-only SQL analytics queries against ERPNext DB
├── power-query/             → Power Query M scripts for ETL transformations
├── powerbi-dashboards/      → Power BI setup guide & M query templates
├── python/                  → Python REST API, forecasting, anomaly detection, AI query engine
├── data/                    → Seed datasets, forecast reports, and verification scripts
├── docs/                    → Architecture diagrams & project roadmap
├── .gitignore
└── README.md                → You are here
```

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ (for Frontend)
- Python 3.10+
- Docker with ERPNext (optional for live database sync; sample fallbacks included)
- Power BI Desktop (for .pbix dashboards)
- Git

### 1. Launch Modern React Command Center (Frontend)

```bash
cd stocksense-frontend
npm install
npm run dev
```

Visit `http://localhost:5173` to explore:
- **Operations Dashboard**: Real-time KPI rail, stock valuation, inventory health ring, top items bar chart.
- **Virtualized Inventory Table**: Blazing-fast filtering, Excel-style conditional filters, 10 export formats (CSV, Excel, TSV, JSON, SQL, HTML, Markdown, etc.), Edit / Reorder / Add modals.
- **ML Demand Forecasts**: Recharts interactive demand projection vs actuals, item-level predictions, and confidence indicators.
- **Anomaly Detection**: Statistical Z-Score and IQR outliers, critical alert ribbons, and one-click resolution.
- **AI Stock Assistant**: Natural language query engine with Hindi & English conversational support.

### 2. Launch Python API & ML Forecasting Engine (Backend)

```bash
cd python
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
python src/ai_query_api.py
```

API will run on `http://localhost:5000`:
- `GET  /api/health` — Service health
- `GET  /api/dashboard/stats` — Summary metrics
- `GET  /api/dashboard/stock` — Inventory telemetry
- `GET  /api/forecasts` — Predictive demand forecasts
- `GET  /api/anomalies` — Z-Score anomaly reports
- `POST /api/ask` — Natural language AI queries

---

## 🗺️ Roadmap & Milestones

| Phase | Focus | Status |
|---|---|---|
| **Phase 1** | ERPNext + SQL + Power BI core dashboard | ✅ Complete |
| **Phase 2** | Excel VBA + Google Sheets/Apps Script automation | ✅ Complete |
| **Phase 3** | Power Query multi-source ETL + Python ML forecasting | ✅ Complete |
| **Phase 4** | AI NLP layer + JS ERPNext customization + Docker Compose | ✅ Complete |
| **Phase 5** | React 19 Command Center + Virtualized Inventory & Real-Time Telemetry | ✅ Complete |

See the full roadmap → [`docs/roadmap.md`](docs/roadmap.md)

---

## License

This project is for educational and portfolio purposes.
