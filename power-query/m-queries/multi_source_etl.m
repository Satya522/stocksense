// =============================================================================
// StockSense - Multi-Source ETL: ERP Stock + External Market Prices
// =============================================================================
// This M script demonstrates pulling data from two sources:
//   1. ERPNext MariaDB (internal stock data)
//   2. An external CSV/API (simulated market pricing data)
// and merging them into a single enriched dataset for Power BI analysis.
// =============================================================================

let
    // --- Source 1: Internal ERPNext Stock Data ---
    ERPStock = MySQL.Database("localhost:3306", "_7e269a3c97126b3e", [
        Query = "
            SELECT
                b.item_code,
                i.item_name,
                i.item_group,
                i.stock_uom,
                b.warehouse,
                b.actual_qty,
                b.valuation_rate,
                (b.actual_qty * b.valuation_rate) AS stock_value,
                b.projected_qty,
                i.last_purchase_rate,
                i.standard_rate
            FROM
                `tabBin` b
                LEFT JOIN `tabItem` i ON b.item_code = i.name
            WHERE
                i.is_stock_item = 1
            ORDER BY
                stock_value DESC
        "
    ]),

    // --- Source 2: External Market Price Data (CSV) ---
    // In production, replace this path with an API URL or shared drive path
    ExternalPrices = Csv.Document(
        File.Contents("C:\Users\18112\Desktop\Automation Project\stocksense\data\market_prices.csv"),
        [Delimiter=",", Columns=3, Encoding=65001, QuoteStyle=QuoteStyle.None]
    ),
    PromotedHeaders = Table.PromoteHeaders(ExternalPrices, [PromoteAllScalars=true]),
    TypedPrices = Table.TransformColumnTypes(PromotedHeaders, {
        {"item_code", type text},
        {"market_price", type number},
        {"price_date", type date}
    }),

    // --- Merge: Enrich internal stock with external market prices ---
    MergedData = Table.NestedJoin(
        ERPStock, {"item_code"},
        TypedPrices, {"item_code"},
        "MarketData", JoinKind.LeftOuter
    ),
    ExpandedMarket = Table.ExpandTableColumn(
        MergedData, "MarketData",
        {"market_price", "price_date"},
        {"market_price", "price_date"}
    ),

    // --- Calculated Columns ---
    WithMargin = Table.AddColumn(ExpandedMarket, "price_margin_pct",
        each if [market_price] <> null and [valuation_rate] > 0
             then (([market_price] - [valuation_rate]) / [valuation_rate]) * 100
             else null,
        type number
    ),
    WithAlert = Table.AddColumn(WithMargin, "margin_alert",
        each if [price_margin_pct] <> null and [price_margin_pct] < 10
             then "LOW MARGIN"
             else if [price_margin_pct] <> null and [price_margin_pct] > 50
             then "HIGH MARGIN"
             else "NORMAL",
        type text
    ),

    // --- Final Type Enforcement ---
    FinalTyped = Table.TransformColumnTypes(WithAlert, {
        {"item_code", type text},
        {"item_name", type text},
        {"item_group", type text},
        {"warehouse", type text},
        {"actual_qty", type number},
        {"valuation_rate", type number},
        {"stock_value", type number},
        {"market_price", type number},
        {"price_margin_pct", type number},
        {"margin_alert", type text}
    })
in
    FinalTyped
