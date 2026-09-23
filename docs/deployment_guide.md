# StockSense - Deployment Guide & User Manual

## Table of Contents
1. [System Requirements](#1-system-requirements)
2. [Quick Start (Docker)](#2-quick-start-docker)
3. [ERPNext Configuration](#3-erpnext-configuration)
4. [Power BI Dashboard Setup](#4-power-bi-dashboard-setup)
5. [Excel VBA Automation](#5-excel-vba-automation)
6. [Google Sheets Integration](#6-google-sheets-integration)
7. [Python Analytics](#7-python-analytics)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. System Requirements

| Component | Minimum | Recommended |
|---|---|---|
| OS | Windows 10 / macOS 12 | Windows 11 / macOS 14 |
| RAM | 8 GB | 16 GB |
| Disk | 20 GB free | 50 GB free |
| Docker Desktop | v4.0+ | Latest |
| Power BI Desktop | Latest | Latest |
| Python | 3.10+ | 3.13+ |
| Excel | 2016+ | Microsoft 365 |
| Browser | Chrome/Edge | Chrome |

---

## 2. Quick Start (Docker)

### Start ERPNext
```bash
cd frappe_docker
docker compose -f pwd.yml up -d
```

### Access ERPNext
- URL: http://localhost:8080
- Username: Administrator
- Password: admin

### Stop ERPNext
```bash
cd frappe_docker
docker compose -f pwd.yml stop
```

### Full-Stack Deployment (Production)
```bash
cd stocksense/deployment
docker compose -f docker-compose.stocksense.yml up -d
```

---

## 3. ERPNext Configuration

### API Keys Setup
1. Login to ERPNext as Administrator
2. Go to: Settings -> User -> Administrator
3. Under "API Access", generate API Key and Secret
4. Save credentials in `python/.env`:
   ```
   ERPNEXT_API_KEY=your_key_here
   ERPNEXT_API_SECRET=your_secret_here
   ```

### Client Script Installation
1. Go to: Setup -> Customize -> Client Script -> New
2. Set DocType: `Item`
3. Set Script Type: `Client`
4. Paste code from `erpnext-setup/client-scripts/item_stock_health.js`
5. Enable and Save

---

## 4. Power BI Dashboard Setup

### Prerequisites
- Install MySQL Connector/NET from https://dev.mysql.com/downloads/connector/net/

### Loading Data
1. Open Power BI Desktop
2. Get Data -> Blank Query -> Advanced Editor
3. Paste code from any `.m` file in `power-query/m-queries/`
4. Available queries:
   - `current_stock.m` - Current stock levels by item
   - `low_stock_items.m` - Items below reorder level
   - `stock_ledger_recent.m` - Recent stock movements
   - `sales_order_summary.m` - Sales order analytics
   - `multi_source_etl.m` - Multi-source merged data
   - `forecast_results.m` - Demand forecast results (from Python)
   - `anomaly_results.m` - Anomaly detection results (from Python)

### Database Credentials
- Server: `localhost:3306`
- Database: `_7e269a3c97126b3e`
- Authentication: Database (not Windows)

---

## 5. Excel VBA Automation

### Setup
1. Open Excel -> ALT+F11 (VBA Editor)
2. Tools -> References -> Enable:
   - Microsoft XML, v6.0
   - Microsoft Scripting Runtime
3. File -> Import File -> Import all `.bas` files from `excel-automation/modules/`
4. Save as `.xlsm` (Macro-Enabled Workbook)

### Available Macros
| Macro | Function | How to Run |
|---|---|---|
| `FetchLiveStock` | Pulls live stock data into Excel | Run from VBA (F5) |
| `ProcessBulkSalesOrders` | Pushes orders from Excel to ERPNext | Create "BulkOrders" sheet first |

### BulkOrders Sheet Format
| Column A | Column B | Column C | Column D | Column E | Column F | Column G |
|---|---|---|---|---|---|---|
| Customer | Delivery Date | Item Code | Qty | Rate | Status | Response |

---

## 6. Google Sheets Integration

### Prerequisites
- ngrok installed and running: `ngrok http 8080`
- Google Account with Sheets access

### Setup
1. Create a new Google Sheet
2. Extensions -> Apps Script
3. Paste code from `sheets-automation/scripts/COMBINED_CODE_FOR_GOOGLE.js`
4. Update `ERPNEXT_BASE_URL` with your ngrok URL
5. Save and Run `fetchStockToSheet`

### Google Form -> Material Request
1. Create a Google Form with fields: Item Code, Quantity, Required By Date
2. Link it to a Google Sheet
3. In Apps Script, add trigger: `onSubmitMaterialRequest` -> On Form Submit

---

## 7. Python Analytics

### Setup
```bash
cd stocksense/python
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Available Scripts
| Script | Purpose | Command |
|---|---|---|
| `test_connection.py` | Verify DB + API connectivity | `python src/test_connection.py` |
| `extract_data.py` | Extract data to pandas DataFrames | `python src/extract_data.py` |
| `demand_forecast.py` | Run demand forecasting model | `python src/demand_forecast.py` |
| `anomaly_detection.py` | Detect unusual stock movements | `python src/anomaly_detection.py` |

### Jupyter Notebook
```bash
jupyter notebook notebooks/stocksense_analysis.ipynb
```

---

## 8. Troubleshooting

### Common Issues

| Problem | Solution |
|---|---|
| Power BI: "MissingClientLibrary" | Install MySQL Connector/NET |
| Power BI: "Can't authenticate" | Use "Database" auth, not "Windows" |
| VBA: "ActiveX component can't create object" | Change `XMLHTTP60` to `XMLHTTP` |
| VBA: "User-defined type not defined" | Enable Microsoft Scripting Runtime in References |
| VBA: "Ambiguous name detected" | Remove duplicate imported modules |
| Python: "DLL load failed" | IT policy blocking; run inside Docker instead |
| Google Apps Script: "Connection refused" | ERPNext is on localhost; use ngrok tunnel |
| ERPNext API: 401 Unauthorized | Regenerate API keys via bench command |

### Useful Commands
```bash
# Check Docker containers
docker ps

# View ERPNext logs
docker logs frappe_docker-backend-1

# Start ngrok tunnel
ngrok http 8080

# Stop all Docker containers
docker compose -f pwd.yml stop
```

---

> **StockSense v1.0** | Built with ERPNext, Power BI, Python, Excel VBA, and Google Apps Script
