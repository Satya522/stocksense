// StockSense - Google Apps Script (ERPNext Integration)

const ERPNEXT_BASE_URL = "https://handwash-semisweet-dandruff.ngrok-free.dev"; 
const API_KEY = "14915643fd5946c";
const API_SECRET = "c377658d5b1967f";

function makeERPNextRequest(endpoint, method, payload) {
  method = method || "GET";
  payload = payload || null;
  
  var url = ERPNEXT_BASE_URL + endpoint;
  
  var options = {
    method: method,
    headers: {
      "Authorization": "token " + API_KEY + ":" + API_SECRET,
      "Content-Type": "application/json",
      "Accept": "application/json",
      "ngrok-skip-browser-warning": "true"
    },
    muteHttpExceptions: true
  };
  
  if (payload && (method === "POST" || method === "PUT")) {
    options.payload = JSON.stringify(payload);
  }
  
  var response = UrlFetchApp.fetch(url, options);
  var code = response.getResponseCode();
  
  if (code >= 200 && code < 300) {
    return JSON.parse(response.getContentText());
  } else {
    throw new Error("API Error " + code + ": " + response.getContentText());
  }
}

function fetchStockToSheet() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  sheet.clear();
  sheet.appendRow(["Item Code", "Warehouse", "Actual Qty", "Projected Qty"]);
  sheet.getRange("A1:D1").setFontWeight("bold");
  
  try {
    var endpoint = '/api/resource/Bin?fields=%5B%22item_code%22%2C%22warehouse%22%2C%22actual_qty%22%2C%22projected_qty%22%5D&limit_page_length=1000';
    var response = makeERPNextRequest(endpoint, "GET");
    
    if (response && response.data && response.data.length > 0) {
      var rows = [];
      for (var i = 0; i < response.data.length; i++) {
        var item = response.data[i];
        rows.push([item.item_code, item.warehouse, item.actual_qty, item.projected_qty]);
      }
      sheet.getRange(2, 1, rows.length, rows[0].length).setValues(rows);
      SpreadsheetApp.getUi().alert("Stock synced! " + rows.length + " items loaded.");
    } else {
      SpreadsheetApp.getUi().alert("No stock data found.");
    }
  } catch (error) {
    SpreadsheetApp.getUi().alert("Error: " + error.message);
  }
}

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('StockSense')
    .addItem('Sync Live Stock', 'fetchStockToSheet')
    .addToUi();
}

function onSubmitMaterialRequest(e) {
  if (!e || !e.values) return;
  
  var itemCode = e.values[1];
  var quantity = parseFloat(e.values[2]);
  var scheduleDate = e.values[3];
  
  var payload = {
    "doctype": "Material Request",
    "material_request_type": "Purchase",
    "company": "SK Automation Labs",
    "schedule_date": scheduleDate,
    "items": [{ "item_code": itemCode, "qty": quantity, "schedule_date": scheduleDate }]
  };
  
  try {
    var response = makeERPNextRequest("/api/resource/Material Request", "POST", payload);
    console.log("Material Request created: " + response.data.name);
  } catch (error) {
    console.error("Failed: " + error.message);
  }
}
