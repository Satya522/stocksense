// =============================================================================
// StockSense - Power BI: Anomaly Detection Results
// =============================================================================
// Loads the CSV output from anomaly_detection.py into Power BI.
// After running the Python anomaly script, this M query reads flagged
// transactions so you can build alerts and investigation dashboards.
// =============================================================================

let
    Source = Csv.Document(
        File.Contents("C:\Users\18112\Desktop\Automation Project\stocksense\data\anomaly_report.csv"),
        [Delimiter=",", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(PromotedHeaders, {
        {"name", type text},
        {"item_code", type text},
        {"warehouse", type text},
        {"posting_date", type date},
        {"actual_qty", type number},
        {"qty_after_transaction", type number},
        {"voucher_type", type text},
        {"voucher_no", type text},
        {"z_score", type number},
        {"anomaly_type", type text}
    })
in
    TypedColumns
