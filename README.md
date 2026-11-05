# 📦 StockSense

**Warehouse Operations Analytics & Intelligence Platform — Built on ERPNext**

[![StockSense CI/CD Pipeline](https://github.com/Satya522/stocksense/actions/workflows/ci.yml/badge.svg)](https://github.com/Satya522/stocksense/actions/workflows/ci.yml)
![React 19](https://img.shields.io/badge/React-19.0-61dafb?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-8.3-646cff?logo=vite&logoColor=white)
![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776ab?logo=python&logoColor=white)
![ERPNext](https://img.shields.io/badge/ERPNext-v15-0089FF?logo=frappe&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ed?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

> **StockSense** gives you a smart, 360-degree view of your warehouse operations — from raw ERP data all the way to AI-driven insights. Built by a warehouse operations professional transitioning into IT, this platform solves real-world inventory visibility, replenishment, and stock anomaly challenges using **ERPNext** as the open-source ERP backbone, layered with a high-performance **React 19 Command Center**, **Scikit-Learn ML forecasting**, and **Power BI / Power Query** analytics.

---

## 📹 Working Video & Live UI Showcase

### ⚡ Live Demo Walkthrough (Animated Preview)

![StockSense Command Center Walkthrough](docs/screenshots/stocksense_demo.gif)

> 💡 **Working Video Recording**: An end-to-end screencast walkthrough demonstrating live stock movements, AI queries in Hindi/English, and instant Material Request generation is available in the documentation media kit.

---

## 🖥️ Screen-by-Screen Visual Walkthrough

### 1. Operations Command Center (Dashboard)
Real-time KPI telemetry rail, valuation metrics, interactive Stock Health Ring, top stock items distribution bar chart, and recent transaction audit trail.

![Operations Dashboard](docs/screenshots/01_dashboard.png)

---

### 2. Virtualized Inventory Management & CRUD Actions
Blazing-fast inventory table supporting instant multi-column filtering, low-stock threshold triggers, Excel-style conditional filters, export to 10 formats (CSV, Excel, TSV, JSON, SQL, etc.), and interactive Glassmorphism modals for Adding, Editing, and Reordering SKUs.

![Inventory Management](docs/screenshots/02_inventory_management.png)

---

### 3. Machine Learning Demand Forecasting
Gradient Boosting Regressor (GBR) time-series model predicting future weekly replenishment demand based on historical stock ledger velocity, rolling averages, and lag features.

![Demand Forecasting](docs/screenshots/03_demand_forecasting.png)

---

### 4. Statistical Anomaly & Outlier Detection
Automated statistical detection of transaction anomalies using **Z-Score** (>2.5 threshold) and **Interquartile Range (IQR)** to identify unexpected stock outflows, suspicious inventory shrinkages, and sudden receipt spikes.

![Anomaly Detection](docs/screenshots/04_anomaly_detection.png)

---

### 5. AI Stock Assistant (Bilingual Natural Language Q&A)
Built-in conversational AI assistant powered by NLP and fuzzy keyword matching capable of answering stock, valuation, and reorder queries in both **English and Hindi**.

![AI Assistant Chat](docs/screenshots/06_ai_query_assistant.png)

---

### 6. System Architecture & Live Topology Map
Real-time telemetry showing heartbeat latency and connection status across MariaDB, ERPNext REST APIs, Python Analytics engine, and the React client.

![System Topology](docs/screenshots/05_system_topology.png)

---

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph ERP ["🏭 Core ERP Backbone (Docker)"]
        ERPUI["ERPNext Web UI"]
        ERPAPI["ERPNext REST API"]
        ERPDB[("MariaDB / MySQL")]
    end

    subgraph DataLayer ["📊 Data & Analytics Layer"]
        SQL["SQL Analytics<br/>(Read-Only Views)"]
        PQ["Power Query (M)<br/>ETL Pipelines"]
        PBI["Power BI<br/>Executive Dashboards"]
    end

    subgraph Intelligence ["🧠 Intelligence & ML Engine"]
        PY["Python Analytics Server<br/>(ai_query_api.py)"]
        FORECAST["Demand Forecasting<br/>(GradientBoosting)"]
        ANOMALY["Anomaly Detection<br/>(Z-Score & IQR)"]
        AI["NLP Assistant<br/>(Bilingual Stock Queries)"]
    end

    subgraph CommandCenter ["⚡ Modern Command Center (React 19)"]
        DASH["Operations Dashboard"]
        INV["Inventory CRUD & Modals"]
        REORDER["Automated Reorder Requisition"]
        CHAT["AI Chatbox"]
    end

    %% Data Connections
    ERPDB -->|Direct SQL| SQL
    SQL -->|Shaped by| PQ
    PQ -->|Feeds| PBI

    ERPDB -->|pymysql / sqlalchemy| PY
    ERPAPI <-->|REST API / Reorders| PY
    PY --> FORECAST
    PY --> ANOMALY
    PY --> AI

    PY <-->|REST Endpoints (Port 5000)| CommandCenter
```

---

## 🛠️ Tech Stack & Key Technologies

| Technology | Category | Role in StockSense |
|---|---|---|
| **React 19 + Vite** | Frontend | Lightning-fast reactive Command Center SPA |
| **Tailwind CSS + Lucide** | UI & Styling | Glassmorphism design system, responsive layout, modern iconography |
| **Recharts** | Data Viz | Animated telemetry rings, stock breakdown bar charts, forecast lines |
| **Python 3.11** | Backend & ML | Lightweight REST API, ML modeling, and data pipelines |
| **Scikit-Learn & Pandas** | Machine Learning | Time-series feature engineering, Gradient Boosting, statistical Z-score/IQR |
| **ERPNext (v15)** | ERP Backbone | Item master, Stock Ledger Entries, Bin records, and Material Requests |
| **MariaDB** | Database | Underlying transactional database backing ERPNext |
| **Power BI & Power Query** | BI & Reporting | Executive business intelligence dashboards with automated M-queries |
| **Docker & Docker Compose**| DevOps | Multi-container orchestration (`stocksense-api`, `stocksense-frontend`, ERPNext) |
| **GitHub Actions** | CI/CD | Automated lint, build, syntax verification, and Pytest unit test pipeline |

---

## 📁 Repository Structure

```
stocksense/
├── stocksense-frontend/      → React 19 + Vite Command Center web application
│   ├── src/pages/            → Dashboard, Inventory, Forecasts, Anomalies, SystemMap
│   ├── src/components/       → Sidebar, AIChatBox, MetricCard, StockHealthRing, StockTable
│   ├── src/lib/api.js        → Dynamic REST API client with fallback handling
│   ├── Dockerfile            → Multi-stage production Nginx Alpine container
│   ├── nginx.conf            → Production web server routing & gzip caching
│   └── vercel.json           → One-click Vercel cloud deployment rewrite rules
├── python/                   → Python backend, ML engines, and test suite
│   ├── src/ai_query_api.py   → Core REST API server & persistence engine
│   ├── src/demand_forecast.py→ GradientBoosting time-series demand forecaster
│   ├── src/anomaly_detection.py → Z-Score & IQR stock transaction anomaly detector
│   ├── src/ai_stock_query.py → Natural language query search engine
│   ├── tests/                → Automated Pytest suite (API CRUD, ML models, CI)
│   ├── Dockerfile            → Python 3.11-slim production API container
│   └── requirements.txt      → Python dependencies
├── data/                     → Baseline datasets, override layers & verification scripts
│   ├── demand_forecast_results.csv → Pre-computed ML demand forecast metrics
│   ├── anomaly_report.csv          → Detected transaction anomaly records
│   ├── inventory_overrides.json    → Local persistent CRUD layer
│   └── reorder_history.json        → Audit log of generated Material Requests
├── deployment/               → Docker Compose multi-service deployment orchestrator
│   └── docker-compose.stocksense.yml
├── docs/                     → Architecture diagrams, roadmap & UI screenshots
│   └── screenshots/          → Real HD UI captures and animated demo GIF
├── .github/workflows/ci.yml  → GitHub Actions CI test and build workflow
└── README.md                 → Project documentation
```

---

## 🔌 Backend REST API Reference

The backend API server operates on `http://localhost:5000` (configurable via `PORT` environment variable):

| Method | Endpoint | Description | Sample Request / Response |
|---|---|---|---|
| `GET` | `/api/health` | Health check and NLP engine availability | `{"status": "ok", "service": "StockSense AI v2", "nlp": true}` |
| `GET` | `/api/dashboard/stats` | Aggregated metrics (total items, quantity, valuation, alerts) | `{"total_items": 120, "total_value": "₹45.2L", "low_stock_alerts": 4}` |
| `GET` | `/api/dashboard/stock` | Full inventory telemetry with health statuses | Returns list of SKUs with calculated `healthy` / `warning` / `critical` |
| `POST` | `/api/inventory/add` | Add new item & bin record (persisted in MariaDB & JSON layer) | `{"code": "SKU-99", "name": "Sensor", "warehouse": "WH-North", "qty": 100, "rate": 250}` |
| `POST` | `/api/inventory/update` | Update existing SKU stock quantity or reorder threshold | `{"code": "SKU-99", "warehouse": "WH-North", "qty": 80, "reorder": 20}` |
| `POST` | `/api/inventory/delete` | Remove SKU from active warehouse tracking | `{"code": "SKU-99", "warehouse": "WH-North"}` |
| `POST` | `/api/reorder` | Generate official Material Request requisition | `{"item_code": "SKU-01", "qty": 50, "priority": "Urgent", "supplier": "Apex Tech"}` |
| `GET` | `/api/forecasts` | Returns ML demand forecast projections | List of items with `avg_daily_demand_forecast` & `weekly_demand_forecast` |
| `GET` | `/api/anomalies` | Returns Z-Score and IQR detected outliers | List of transactions with `z_score`, `anomaly_type`, and voucher metadata |
| `POST` | `/api/ask` | Natural language question answering (English/Hindi) | `{"question": "sabse kam stock kisme hai?"}` |

---

## 🧪 Automated Testing Suite (Pytest)

The project includes an automated test suite verifying data integrity, CRUD persistence, and ML predictions:

```bash
cd stocksense
.\python\venv\Scripts\pytest.exe python/tests -v
```

### Test Coverage Highlights:
- **`test_get_dashboard_stats_structure`**: Validates summary calculation keys and numeric types.
- **`test_get_stock_data_items`**: Verifies stock telemetry and dynamic status assignment.
- **`test_inventory_crud_lifecycle`**: Executes a complete lifecycle: **Create** → **Read** → **Update** → **Status Trigger** → **Delete** → **Verify Removal**.
- **`test_create_reorder_request`**: Validates Material Request ID format (`MR-YYYYMMDD-XXXX`) and audit log persistence.
- **`test_predict_demand_records`**: Validates time-series prediction schema and positive values.
- **`test_create_features_pipeline`**: Verifies lag-1 and rolling window 3-day feature engineering math.
- **`test_detect_anomalies_records`**: Verifies outlier classification and Z-score thresholding.
- **`test_api_handler_fallback_answers`**: Tests NLP / conversational query parsing logic.

---

## 🚀 Quickstart Guide

### 1. Launch Modern React Command Center (Frontend)

```bash
cd stocksense/stocksense-frontend
npm install
npm run dev
```
Open **`http://localhost:5173`** in your browser.

Direct Tab URLs supported:
- Dashboard: `http://localhost:5173/#dashboard`
- Inventory: `http://localhost:5173/#inventory`
- Forecasts: `http://localhost:5173/#forecasts`
- Anomalies: `http://localhost:5173/#anomalies`
- System Map: `http://localhost:5173/#system`
- AI Assistant: `http://localhost:5173/#chat`

### 2. Launch Python ML & REST API Server (Backend)

```bash
cd stocksense/python
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS / Linux
pip install -r requirements.txt
python src/ai_query_api.py
```
API server runs on **`http://localhost:5000`**.

### 3. Launch Full Stack with Docker Compose

To boot the complete enterprise ecosystem (MariaDB, ERPNext, Python ML API, and Nginx React Frontend):

```bash
cd stocksense
docker compose -f deployment/docker-compose.stocksense.yml up -d
```

- **React Command Center**: `http://localhost:3000`
- **Python ML API**: `http://localhost:5000`
- **ERPNext Enterprise Desk**: `http://localhost:8080`

---

## 🗺️ Project Roadmap & Milestones

| Phase | Focus Area | Status |
|---|---|---|
| **Phase 1** | Core ERPNext setup, MariaDB schema, and SQL analytics views | ✅ Complete |
| **Phase 2** | Excel VBA macros & Google Apps Script automated Material Requests | ✅ Complete |
| **Phase 3** | Power Query multi-source ETL, GBR Demand Forecasting & Anomaly Engine | ✅ Complete |
| **Phase 4** | AI NLP Query Assistant, Client Scripts, and Docker containerization | ✅ Complete |
| **Phase 5** | React 19 Command Center, Full CRUD Modals, Pytest suite & GitHub Actions CI | ✅ Complete |

---

## 📄 License

This project is licensed under the MIT License — built for portfolio demonstration and educational purposes.
