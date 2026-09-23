Attribute VB_Name = "StockUpdateHelper"
' ==============================================================================
' StockSense - Stock Fetching Macro
' ==============================================================================
' This macro pulls live stock levels from ERPNext and populates an active
' Excel sheet. Useful for quick audits without opening Power BI.
' ==============================================================================

Sub FetchLiveStock()
    On Error GoTo ErrorHandler
    
    ' Ensure we are on a clean sheet named "LiveStock"
    Dim ws As Worksheet
    On Error Resume Next
    Set ws = ThisWorkbook.Sheets("LiveStock")
    On Error GoTo ErrorHandler
    
    If ws Is Nothing Then
        Set ws = ThisWorkbook.Sheets.Add
        ws.Name = "LiveStock"
    End If
    
    ws.Cells.Clear
    
    ' Set up headers
    ws.Range("A1:D1").Value = Array("Item Code", "Warehouse", "Actual Qty", "Projected Qty")
    ws.Range("A1:D1").Font.Bold = True
    
    ' We will fetch from the Bin DocType (which stores warehouse stock levels)
    Dim endpoint As String
    endpoint = "/api/resource/Bin?fields=[""item_code"",""warehouse"",""actual_qty"",""projected_qty""]&limit_page_length=1000"
    
    ' Make the request using our utility function
    Dim jsonResponse As String
    jsonResponse = MakeERPNextAPIRequest("GET", endpoint)
    
    ' Parse JSON
    ' REQUIRES: JsonConverter (https://github.com/VBA-tools/VBA-JSON)
    Dim parsedData As Object
    Set parsedData = JsonConverter.ParseJson(jsonResponse)
    
    Dim dataArray As Object
    Set dataArray = parsedData("data")
    
    If dataArray.Count = 0 Then
        MsgBox "No stock data found.", vbInformation
        Exit Sub
    End If
    
    Dim row As Integer
    row = 2
    
    Dim item As Object
    For Each item In dataArray
        ws.Cells(row, 1).Value = item("item_code")
        ws.Cells(row, 2).Value = item("warehouse")
        ws.Cells(row, 3).Value = item("actual_qty")
        ws.Cells(row, 4).Value = item("projected_qty")
        row = row + 1
    Next item
    
    ws.Columns("A:D").AutoFit
    MsgBox "Stock data successfully fetched!", vbInformation, "Success"
    Exit Sub
    
ErrorHandler:
    MsgBox "Error: " & Err.Description, vbCritical, "Fetch Failed"
End Sub
