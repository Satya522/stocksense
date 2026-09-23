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
    throw new Error(`ERPNext API Error ${responseCode}: ${response.getContentText()}`);
  }
}
