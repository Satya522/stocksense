# StockSense — Project Roadmap

## Overview

StockSense is built in four phases, each adding a new capability layer.
Every phase produces working, demonstrable output.

---

## ✅ Phase 1: Core Analytics Dashboard *(COMPLETE)*

**Goal:** Get real-time warehouse visibility through SQL analytics and Power BI dashboards.

### Deliverables

| # | Task | Status |
|---|---|---|
| 1.1 | ERPNext running in Docker with sample data | ✅ |
| 1.2 | Python connection scripts (API + DB) validated | ✅ |
| 1.3 | SQL analytics queries written and tested | ✅ |
| 1.4 | Power BI connected to MariaDB (M Scripts loaded) | ✅ |
| 1.5 | Stock Overview dashboard page built (Power BI + data loaded) | ✅ |
| 1.6 | Low Stock Alerts dashboard page built (M Script loaded) | ✅ |
| 1.7 | Stock Movement dashboard page built (M Script loaded) | ✅ |
| 1.8 | Sales Analysis dashboard page built (M Script loaded) | ✅ |

### Skills Demonstrated
- ERP administration (ERPNext)
- SQL analytics on a production database schema
- Power Query ETL transformations
- Power BI dashboard design and data modeling
- Python scripting and API integration

---

## ✅ Phase 2: Automation (Excel VBA + Google Apps Script) *(COMPLETE)*

**Goal:** Automate repetitive warehouse workflows that currently require manual ERP data entry.

### Deliverables

| # | Task | Status |
|---|---|---|
| 2.1 | Excel VBA: Bulk Sales Order upload macro | ✅ |
| 2.2 | Excel VBA: Stock level pull-to-Excel macro | ✅ |
| 2.3 | Google Apps Script: ERPNext API utility | ✅ |
| 2.4 | Apps Script: Form → ERPNext Material Request | ✅ |
| 2.5 | Apps Script: Stock Dashboard Sync to Google Sheets | ✅ |
| 2.6 | Error handling and logging in all macros/scripts | ✅ |

### Skills Demonstrated
- VBA programming and REST API integration
- Google Apps Script and Workspace automation
- API authentication and error handling
- Building user-facing tools for non-technical warehouse staff

---

## ✅ Phase 3: Advanced ETL + Python Analytics *(COMPLETE)*

**Goal:** Multi-source ETL pipelines and predictive analytics (demand forecasting, anomaly detection).

### Deliverables

| # | Task | Status |
|---|---|---|
| 3.1 | Power Query: multi-source ETL (ERP + external market data) | ✅ |
| 3.2 | Python: demand forecasting model (GradientBoosting) | ✅ |
| 3.3 | Python: stock anomaly detection (Z-Score + IQR) | ✅ |
| 3.4 | Jupyter notebook documenting full analysis workflow | ✅ |
| 3.5 | Forecast/anomaly results integrated into Power BI (M scripts) | ✅ |

### Skills Demonstrated
- Advanced Power Query (M language)
- Data wrangling with pandas
- Machine learning for time series forecasting
- Anomaly detection algorithms
- End-to-end data science workflow

---

## 🟡 Phase 4: AI Layer + ERPNext Customization + Deployment *(PARTIAL - AI Deferred)*

**Goal:** Natural-language querying, ERPNext UI enhancements, and a fully containerised deployment.

### Deliverables

| # | Task | Status |
|---|---|---|
| 4.1 | AI/NLP: natural-language stock queries | 🔜 Deferred |
| 4.2 | JavaScript: ERPNext client script customizations (Stock Health + Alerts) | ✅ |
| 4.3 | Docker Compose: full-stack deployment package | ✅ |
| 4.4 | Documentation: deployment guide and user manual | ✅ |

### Skills Demonstrated
- JavaScript client-side development
- Docker Compose multi-service orchestration
- Technical documentation and deployment automation

---

## Timeline (Suggested)

```
Phase 1  ████████████░░░░░░░░░░░░  Weeks 1-3
Phase 2  ░░░░░░░░░░░░████████░░░░  Weeks 4-5
Phase 3  ░░░░░░░░░░░░░░░░░░██████  Weeks 6-8
Phase 4  ░░░░░░░░░░░░░░░░░░░░████  Weeks 9-10
```

> Timelines are flexible — each phase is self-contained and can be adjusted
> based on learning pace and available time.
