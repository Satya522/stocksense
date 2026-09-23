// =============================================================================
// StockSense - Power BI: Demand Forecast Results
// =============================================================================
// Loads the CSV output from demand_forecast.py into Power BI.
// After running the Python forecast script, this M query reads the results
// so you can build visuals like "Predicted Weekly Demand by Item" charts.
// =============================================================================

let
    Source = Csv.Document(
        File.Contents("C:\Users\18112\Desktop\Automation Project\stocksense\data\demand_forecast_results.csv"),
        [Delimiter=",", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.None]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(PromotedHeaders, {
        {"item_code", type text},
        {"training_samples", Int64.Type},
        {"test_samples", Int64.Type},
        {"mae", type number},
        {"avg_daily_demand_forecast", type number},
        {"weekly_demand_forecast", type number}
    })
in
    TypedColumns
