# Power BI Dashboards

> **Note:** Power BI `.pbix` files are binary and don't diff well in git.
> This folder contains setup instructions and M query templates. The actual `.pbix`
> dashboard file is created manually in Power BI Desktop.

---

## Connecting Power BI to your local ERPNext MariaDB

### Prerequisites

1. **MySQL Connector/NET** — Power BI needs this to connect to MySQL/MariaDB.
   Download from: https://dev.mysql.com/downloads/connector/net/
   Install it and restart Power BI Desktop.

2. Your ERPNext MariaDB must be accessible from your host machine (it should be
   if you're running Docker with port 3306 mapped).

### Step-by-step setup

1. **Open Power BI Desktop**

2. **Get Data → MySQL database**
   - Click **Home** → **Get Data** → **More...**
   - Search for **MySQL database** and select it
   - Click **Connect**

3. **Enter connection details**
   - **Server:** `localhost:3306` (or whatever your `DB_HOST:DB_PORT` is)
   - **Database:** your ERPNext database name (e.g., `_1bd4c572c4ab6149`)
     - To find this: run `SHOW DATABASES;` in your MariaDB client
   - Click **OK**

4. **Enter credentials**
   - Select **Database** tab (not Windows)
   - **User name:** your `DB_USER` (typically `root`)
   - **Password:** your `DB_PASSWORD`
   - Click **Connect**

5. **Select tables or write a custom query**
   - You can browse tables in the Navigator, OR
   - Click **Advanced options** and paste a SQL query (see below)

6. **Load or Transform**
   - Click **Transform Data** to open Power Query Editor for shaping
   - Or click **Load** to import directly

### Using custom SQL in Power BI

Instead of selecting tables from the Navigator, you can paste any of the SQL
queries from `sql-analytics/queries/` into the **Advanced options** SQL field.

### Using Power Query M scripts

1. In Power Query Editor, click **New Source** → **Blank Query**
2. Click **Advanced Editor**
3. Paste the contents of a `.m` file from `power-query/m-queries/`
4. Update the server address and database name
5. Click **Done** → enter credentials when prompted

See [`power-query/m-queries/current_stock.m`](../power-query/m-queries/current_stock.m)
for a ready-to-use template.

---

## Suggested Dashboard Pages

Once connected, build these dashboard pages:

| Page | Key Visuals |
|---|---|
| **Stock Overview** | Total stock value card, stock by item group (bar chart), stock by warehouse (treemap) |
| **Low Stock Alerts** | Table of items below reorder level, shortfall gauge |
| **Stock Movement** | Daily in/out volume (line chart), top moved items (bar) |
| **Sales Analysis** | Monthly sales trend, top customers, order status breakdown |

---

## Tips

- **Refresh schedule:** Use Power BI's **Refresh** button to pull latest data.
  For automatic refresh, you'd need Power BI Gateway (not needed for Phase 1).
- **Relationships:** Power BI may auto-detect relationships between tables. Verify
  them in **Model** view — the key join is `item_code` across most tables.
- **Date table:** Create a dedicated date dimension table for proper time intelligence.
