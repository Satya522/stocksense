# StockSense — Architecture

## System Architecture Diagram

```mermaid
graph TB
    subgraph ERP ["🏭 ERPNext (Docker)"]
        ERPUI["ERPNext Web UI"]
        ERPAPI["REST API"]
        ERPDB[("MariaDB")]
    end

    subgraph DataLayer ["📊 Data & Analytics Layer"]
        SQL["SQL Queries<br/>(Read-Only Analytics)"]
        PQ["Power Query (M)<br/>ETL Transforms"]
        PBI["Power BI<br/>Dashboards"]
    end

    subgraph Automation ["⚙️ Automation Layer"]
        VBA["Excel VBA<br/>Bulk Operations"]
        GAS["Google Apps Script<br/>Form → ERP"]
        JS["JS Client Scripts<br/>ERPNext Customization"]
    end

    subgraph Intelligence ["🧠 Intelligence Layer"]
        PY["Python<br/>pandas / sqlalchemy"]
        FORECAST["Forecasting<br/>& Anomaly Detection"]
        AI["AI / NLP<br/>Natural Language Queries"]
    end

    %% Data flow: ERP → Analytics
    ERPDB -->|Direct SQL| SQL
    SQL -->|Shaped by| PQ
    PQ -->|Feeds| PBI

    %% Automation → ERP API
    VBA -->|REST API calls| ERPAPI
    GAS -->|REST API calls| ERPAPI
    JS -->|Client Script| ERPUI

    %% Intelligence layer
    ERPDB -->|pymysql / sqlalchemy| PY
    ERPAPI -->|requests / frappeclient| PY
    PY --> FORECAST
    PY --> AI
    AI -.->|"Insights feed back<br/>into dashboards"| PBI

    %% Styling
    classDef erp fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20
    classDef data fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef auto fill:#fff3e0,stroke:#ef6c00,stroke-width:2px,color:#e65100
    classDef intel fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c

    class ERPUI,ERPAPI,ERPDB erp
    class SQL,PQ,PBI data
    class VBA,GAS,JS auto
    class PY,FORECAST,AI intel
```

## Data Flow Summary

### Phase 1 — Core Analytics Pipeline (Current)
```
ERPNext MariaDB → SQL Queries → Power Query (M) → Power BI Dashboards
ERPNext REST API → Python test scripts (connection validation)
```

### Phase 2 — Automation
```
Excel VBA macros → ERPNext REST API (bulk order processing)
Google Forms → Apps Script → ERPNext REST API (Material Requests)
```

### Phase 3 — Advanced Analytics
```
MariaDB + External Sources → Power Query (multi-source ETL) → Power BI
MariaDB → Python pandas → Forecasting models → Dashboard integration
```

### Phase 4 — AI & Deployment
```
User natural language → AI layer → SQL/API → Answers
JavaScript client scripts → ERPNext UI customization
Docker Compose → Full-stack packaged deployment
```

## Key Design Principles

1. **ERPNext is the single source of truth** — all data originates from and is
   managed through ERPNext. External tools only read from or write via the API.

2. **Database queries are read-only** — we never modify ERPNext tables via direct
   SQL. All writes go through the REST API to preserve ERPNext's business logic.

3. **Layered architecture** — each layer (data, automation, intelligence) is
   independent and can be developed/deployed incrementally.

4. **Credentials are never hardcoded** — all secrets live in `.env` files that
   are excluded from version control.
