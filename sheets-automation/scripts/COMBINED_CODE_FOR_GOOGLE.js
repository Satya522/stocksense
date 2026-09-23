/**
 * StockSense - ERPNext API Utilities for Google Apps Script
 * ==========================================================
 * This file handles authentication and API requests to ERPNext.
 * NOTE: If ERPNext is on localhost, Google's servers cannot reach it without a tunnel (like ngrok).
 */

// Live ngrok tunnel URL (valid while ngrok is running)
const ERPNEXT_BASE_URL = "https://handwash-semisweet-dandruff.ngrok-free.dev"; 

// API credentials (from .env)
const API_KEY = "14915643fd5946c";
const API_SECRET = "c377658d5b1967f";

/**
 * Helper function to make API requests to ERPNext
 */
function makeERPNextRequest(endpoint, method = "GET", payload = null) {
  const url = ERPNEXT_BASE_URL + endpoint;
  
  const options = {
    method: method,
    headers: {
      "Authorization": "token " + API_KEY + ":" + API_SECRET,
      "Content-Type": "application/json",
      "Accept": "application/json"
    },
    muteHttpExceptions: true
  };
  
  if (payload && (method === "POST" || method === "PUT")) {
    options.payload = JSON.stringify(payload);
  }
  
  const response = UrlFetchApp.fetch(url, options);
  const responseCode = response.getResponseCode();
  
  if (responseCode >= 200 && responseCode < 300) {
    return JSON.parse(response.getContentText());
  } else {
    throw new Error("ERPNext API Error " + responseCode + ": " + response.getContentText());
  }
}

// ==========================================================
// Stock Dashboard Sync
// ==========================================================

function fetchStockToSheet() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  
  sheet.clear();
  
  sheet.appendRow(["Item Code", "Warehouse", "Actual Qty", "Projected Qty"]);
  sheet.getRange("A1:D1").setFontWeight("bold");
  
  try {
    const endpoint = '/api/resource/Bin?fields=["item_code","warehouse","actual_qty","projected_qty"]&limit_page_length=1000';
    const response = makeERPNextRequest(endpoint, "GET");
    
    if (response && response.data && response.data.length > 0) {
      const rows = [];
      response.data.forEach(function(item) {
        rows.push([item.item_code, item.warehouse, item.actual_qty, item.projected_qty]);
      });
      
      sheet.getRange(2, 1, rows.length, rows[0].length).setValues(rows);
      SpreadsheetApp.getUi().alert("Stock data successfully synced from ERPNext!");
    } else {
      SpreadsheetApp.getUi().alert("No stock data found.");
    }
    
  } catch (error) {
    SpreadsheetApp.getUi().alert("Error: " + error.message);
  }
}

function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('StockSense')
      .addItem('Sync Live Stock', 'fetchStockToSheet')
      .addToUi();
}

// ==========================================================
// Google Form to ERPNext Material Request
// ==========================================================

function onSubmitMaterialRequest(e) {
  if (!e || !e.values) {
    console.error("No form data found.");
    return;
  }
  
  var timestamp = e.values[0];
  var itemCode = e.values[1];
  var quantity = parseFloat(e.values[2]);
  var scheduleDate = e.values[3];
  
  var payload = {
    "doctype": "Material Request",
    "material_request_type": "Purchase",
    "schedule_date": scheduleDate,
    "items": [
      {
        "item_code": itemCode,
        "qty": quantity,
        "schedule_date": scheduleDate
      }
    ]
  };
  
  try {
    var endpoint = "/api/resource/Material Request";
    var response = makeERPNextRequest(endpoint, "POST", payload);
    console.log("Successfully created Material Request: " + response.data.name);
  } catch (error) {
    console.error("Failed to create Material Request: " + error.message);
  }
}
