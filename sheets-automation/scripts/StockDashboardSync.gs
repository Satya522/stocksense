/**
 * StockSense - Sync ERPNext Stock to Google Sheets
 * ==========================================================
 * Automatically fetches current stock levels from ERPNext 
 * and writes them to the active Google Sheet.
 */

function fetchStockToSheet() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  
  // Clear existing content
  sheet.clear();
  
  // Set headers
  sheet.appendRow(["Item Code", "Warehouse", "Actual Qty", "Projected Qty"]);
  sheet.getRange("A1:D1").setFontWeight("bold");
  
  try {
    const endpoint = "/api/resource/Bin?fields=[\"item_code\",\"warehouse\",\"actual_qty\",\"projected_qty\"]&limit_page_length=1000";
    const response = makeERPNextRequest(endpoint, "GET");
    
    if (response && response.data && response.data.length > 0) {
      const rows = [];
      response.data.forEach(item => {
        rows.push([item.item_code, item.warehouse, item.actual_qty, item.projected_qty]);
      });
      
      // Batch write to sheet for performance
      sheet.getRange(2, 1, rows.length, rows[0].length).setValues(rows);
      SpreadsheetApp.getUi().alert("✅ Stock data successfully synced from ERPNext!");
    } else {
      SpreadsheetApp.getUi().alert("ℹ️ No stock data found.");
    }
    
  } catch (error) {
    SpreadsheetApp.getUi().alert("❌ Error: " + error.message);
  }
}

/**
 * Add a custom menu to Google Sheets UI
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('StockSense')
      .addItem('Sync Live Stock', 'fetchStockToSheet')
      .addToUi();
}
