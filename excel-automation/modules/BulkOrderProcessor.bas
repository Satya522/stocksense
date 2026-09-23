Attribute VB_Name = "BulkOrderProcessor"
' ==============================================================================
' StockSense - Bulk Order Processor Macro
' ==============================================================================
' This macro reads rows from an Excel sheet named "BulkOrders" and sends them
' to ERPNext to automatically generate Sales Orders.
' ==============================================================================

Sub ProcessBulkSalesOrders()
    On Error GoTo ErrorHandler
    
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets("BulkOrders")
    
    Dim lastRow As Long
    lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).row
    
    If lastRow < 2 Then
        MsgBox "No data found in BulkOrders sheet.", vbInformation
        Exit Sub
    End If
    
    Dim row As Long
    Dim customer As String
    Dim deliveryDate As String
    Dim itemCode As String
    Dim qty As Double
    Dim rate As Double
    
    ' Loop through the rows to read data and build JSON
    For row = 2 To lastRow
        ' Skip already processed rows (Assuming column F holds status)
        If ws.Cells(row, 6).Value <> "Success" Then
            
            customer = ws.Cells(row, 1).Value
            deliveryDate = ws.Cells(row, 2).Value
            itemCode = ws.Cells(row, 3).Value
            qty = ws.Cells(row, 4).Value
            rate = ws.Cells(row, 5).Value
            
            ' Build JSON payload for Sales Order
            Dim payload As Object
            Set payload = CreateObject("Scripting.Dictionary")
            
            payload.Add "doctype", "Sales Order"
            payload.Add "customer", customer
            payload.Add "delivery_date", deliveryDate
            
            ' Add items array
            Dim itemsArray As New Collection
            Dim itemDict As Object
            Set itemDict = CreateObject("Scripting.Dictionary")
            
            itemDict.Add "item_code", itemCode
            itemDict.Add "qty", qty
            itemDict.Add "rate", rate
            
            itemsArray.Add itemDict
            payload.Add "items", itemsArray
            
            ' Convert to JSON String
            Dim jsonPayload As String
            jsonPayload = JsonConverter.ConvertToJson(payload)
            
            ' Call API
            Dim response As String
            On Error Resume Next
            response = MakeERPNextAPIRequest("POST", "/api/resource/Sales Order", jsonPayload)
            
            If Err.Number = 0 Then
                ws.Cells(row, 6).Value = "Success"
                ws.Cells(row, 7).Value = response
            Else
                ws.Cells(row, 6).Value = "Failed"
                ws.Cells(row, 7).Value = Err.Description
                Err.Clear
            End If
            On Error GoTo ErrorHandler
            
        End If
    Next row
    
    MsgBox "Bulk order processing complete!", vbInformation
    Exit Sub
    
ErrorHandler:
    MsgBox "Critical Error on Row " & row & ": " & Err.Description, vbCritical, "Process Failed"
End Sub
