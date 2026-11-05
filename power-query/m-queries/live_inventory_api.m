// =============================================================================
// StockSense — Live Inventory API Power Query
// =============================================================================
// Purpose: Fetch live inventory stock data directly from the Python API 
//          (ERPNext backend) into Excel.
//
// Usage in Excel:
// 1. Open Excel -> Data -> Get Data -> From Other Sources -> Blank Query
// 2. Open Advanced Editor (View -> Advanced Editor)
// 3. Paste this entire code and click Done.
// 4. Name the query "Live_Inventory" and Close & Load.
// =============================================================================

let
    // 1. Fetch JSON data from the StockSense API
    Source = Json.Document(Web.Contents("http://localhost:5000/api/dashboard/stock")),
    
    // 2. Convert the list of records to a Table
    ConvertedToTable = Table.FromList(Source, Splitter.SplitByNothing(), null, null, ExtraValues.Error),
    
    // 3. Expand the JSON records into individual Excel columns
    ExpandedColumn = Table.ExpandRecordColumn(ConvertedToTable, "Column1", 
        {"item", "code", "warehouse", "qty", "reorder", "value", "status"}, 
        {"Item Name", "Item Code", "Warehouse", "Actual Qty", "Reorder Level", "Stock Value", "Health Status"}
    ),
    
    // 4. Change column data types for accurate sorting and filtering in Excel
    ChangedTypes = Table.TransformColumnTypes(ExpandedColumn, {
        {"Item Name", type text}, 
        {"Item Code", type text}, 
        {"Warehouse", type text}, 
        {"Actual Qty", type number}, 
        {"Reorder Level", type number}, 
        {"Stock Value", type number}, 
        {"Health Status", type text}
    }),
    
    // 5. (Optional) Filter out fully depleted items if desired
    // FilteredRows = Table.SelectRows(ChangedTypes, each [Actual Qty] > 0),
    
    // 6. Sort by Qty ascending (lowest stock first) to see critical items quickly
    SortedRows = Table.Sort(ChangedTypes, {{"Actual Qty", Order.Ascending}})
in
    SortedRows
