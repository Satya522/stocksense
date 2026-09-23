Attribute VB_Name = "ERPNextAPIUtils"
' ==============================================================================
' StockSense - ERPNext API Utility Functions
' ==============================================================================
' Requirements:
' 1. Tools -> References -> Microsoft XML, v6.0
' 2. Tools -> References -> Microsoft Scripting Runtime
' 3. VBA-JSON imported (JsonConverter.bas) from https://github.com/VBA-tools/VBA-JSON
' ==============================================================================

Public Function GetERPNextAPIUrl() As String
    ' Replace with your actual ERPNext URL
    GetERPNextAPIUrl = "http://localhost:8080"
End Function

Public Function GetAPIHeaders() As Object
    Dim headers As Object
    Set headers = CreateObject("Scripting.Dictionary")
    
    Dim apiKey As String
    Dim apiSecret As String
    
    ' ⚠️ Automatically updated with your actual keys
    apiKey = "14915643fd5946c"
    apiSecret = "c377658d5b1967f"
    
    headers.Add "Authorization", "token " & apiKey & ":" & apiSecret
    headers.Add "Content-Type", "application/json"
    headers.Add "Accept", "application/json"
    
    Set GetAPIHeaders = headers
End Function

Public Function MakeERPNextAPIRequest(method As String, endpoint As String, Optional payload As String = "") As String
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    Dim url As String
    url = GetERPNextAPIUrl() & endpoint
    
    http.Open method, url, False ' False means synchronous request
    
    Dim headers As Object
    Set headers = GetAPIHeaders()
    
    Dim key As Variant
    For Each key In headers.Keys
        http.setRequestHeader key, headers(key)
    Next key
    
    If (method = "POST" Or method = "PUT") And payload <> "" Then
        http.send payload
    Else
        http.send
    End If
    
    If http.Status >= 200 And http.Status < 300 Then
        MakeERPNextAPIRequest = http.responseText
    Else
        Err.Raise vbObjectError + 1, "ERPNextAPI", "API Error " & http.Status & ": " & http.responseText
    End If
End Function
