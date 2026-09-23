/**
 * StockSense - Google Form to ERPNext Material Request
 * ==========================================================
 * Automatically creates a Material Request in ERPNext whenever 
 * a warehouse staff member submits the linked Google Form.
 * 
 * Setup: Add a trigger to this function for 'On form submit'
 */

function onSubmitMaterialRequest(e) {
  // e.values contains the form answers array. 
  // Assuming Form structure: [Timestamp, Item Code, Quantity, Required By Date]
  if (!e || !e.values) {
    console.error("No form data found.");
    return;
  }
  
  const timestamp = e.values[0];
  const itemCode = e.values[1];
  const quantity = parseFloat(e.values[2]);
  const scheduleDate = e.values[3]; // Format must be YYYY-MM-DD
  
  const payload = {
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
    const endpoint = "/api/resource/Material Request";
    const response = makeERPNextRequest(endpoint, "POST", payload);
    console.log("Successfully created Material Request: " + response.data.name);
  } catch (error) {
    console.error("Failed to create Material Request: " + error.message);
  }
}
