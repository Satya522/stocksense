# StockSense - Realistic Sample Data Loader
# Adds Indian business data to ERPNext for real testing

$headers = @{
    "Authorization" = "token 14915643fd5946c:c377658d5b1967f"
    "Content-Type"  = "application/json"
}
$baseUrl = "http://localhost:8080"

function Create-Doc($doctype, $data) {
    $body = $data | ConvertTo-Json -Depth 5
    try {
        $resp = Invoke-RestMethod -Uri "$baseUrl/api/resource/$doctype" -Method POST -Headers $headers -Body $body
        Write-Host "[OK] $doctype : $($resp.data.name)" -ForegroundColor Green
        return $resp.data.name
    } catch {
        $err = $_.ErrorDetails.Message
        if ($err -match "DuplicateEntryError") {
            Write-Host "[SKIP] $doctype : Already exists" -ForegroundColor Yellow
        } else {
            Write-Host "[ERR] $doctype : $($_.Exception.Message)" -ForegroundColor Red
        }
        return $null
    }
}

Write-Host "`n===== ADDING CUSTOMERS =====" -ForegroundColor Cyan

$customers = @(
    @{ customer_name="Sharma Electronics Pvt Ltd"; customer_type="Company"; customer_group="Commercial"; territory="India" },
    @{ customer_name="Patel Traders & Sons"; customer_type="Company"; customer_group="Commercial"; territory="India" },
    @{ customer_name="Gupta Warehouse Solutions"; customer_type="Company"; customer_group="Commercial"; territory="India" },
    @{ customer_name="Singh Retail Chain"; customer_type="Company"; customer_group="Commercial"; territory="India" },
    @{ customer_name="Mehta Distributors"; customer_type="Company"; customer_group="Commercial"; territory="India" },
    @{ customer_name="Rajesh Kumar"; customer_type="Individual"; customer_group="Individual"; territory="India" },
    @{ customer_name="Priya Verma"; customer_type="Individual"; customer_group="Individual"; territory="India" },
    @{ customer_name="Arun Mishra"; customer_type="Individual"; customer_group="Individual"; territory="India" }
)

foreach ($c in $customers) { Create-Doc "Customer" $c }

Write-Host "`n===== ADDING SUPPLIERS =====" -ForegroundColor Cyan

$suppliers = @(
    @{ supplier_name="Mumbai Electronics Wholesale"; supplier_group="Local"; supplier_type="Company"; country="India" },
    @{ supplier_name="Delhi Tech Imports"; supplier_group="Local"; supplier_type="Company"; country="India" },
    @{ supplier_name="Chennai Gadgets Hub"; supplier_group="Local"; supplier_type="Company"; country="India" },
    @{ supplier_name="Bangalore Components Ltd"; supplier_group="Local"; supplier_type="Company"; country="India" }
)

foreach ($s in $suppliers) { Create-Doc "Supplier" $s }

Write-Host "`n===== ADDING ITEM GROUPS =====" -ForegroundColor Cyan

$groups = @(
    @{ item_group_name="Electronics"; parent_item_group="All Item Groups" },
    @{ item_group_name="Clothing"; parent_item_group="All Item Groups" },
    @{ item_group_name="Accessories"; parent_item_group="All Item Groups" },
    @{ item_group_name="Books & Stationery"; parent_item_group="All Item Groups" }
)

foreach ($g in $groups) { Create-Doc "Item Group" $g }

Write-Host "`n===== ADDING NEW ITEMS =====" -ForegroundColor Cyan

$newItems = @(
    @{ item_code="SKU011"; item_name="Wireless Mouse"; item_group="Electronics"; stock_uom="Nos"; is_stock_item=1; standard_rate=599; opening_stock=0 },
    @{ item_code="SKU012"; item_name="USB-C Cable"; item_group="Electronics"; stock_uom="Nos"; is_stock_item=1; standard_rate=199; opening_stock=0 },
    @{ item_code="SKU013"; item_name="Bluetooth Speaker"; item_group="Electronics"; stock_uom="Nos"; is_stock_item=1; standard_rate=2499; opening_stock=0 },
    @{ item_code="SKU014"; item_name="Power Bank 10000mAh"; item_group="Electronics"; stock_uom="Nos"; is_stock_item=1; standard_rate=1299; opening_stock=0 },
    @{ item_code="SKU015"; item_name="Laptop Sleeve 15inch"; item_group="Accessories"; stock_uom="Nos"; is_stock_item=1; standard_rate=899; opening_stock=0 },
    @{ item_code="SKU016"; item_name="Denim Jeans"; item_group="Clothing"; stock_uom="Nos"; is_stock_item=1; standard_rate=1499; opening_stock=0 },
    @{ item_code="SKU017"; item_name="Polo T-Shirt"; item_group="Clothing"; stock_uom="Nos"; is_stock_item=1; standard_rate=799; opening_stock=0 },
    @{ item_code="SKU018"; item_name="Notebook A4 Pack"; item_group="Books & Stationery"; stock_uom="Nos"; is_stock_item=1; standard_rate=249; opening_stock=0 },
    @{ item_code="SKU019"; item_name="Smartwatch Band"; item_group="Accessories"; stock_uom="Nos"; is_stock_item=1; standard_rate=399; opening_stock=0 },
    @{ item_code="SKU020"; item_name="Webcam HD 1080p"; item_group="Electronics"; stock_uom="Nos"; is_stock_item=1; standard_rate=3499; opening_stock=0 }
)

foreach ($item in $newItems) { Create-Doc "Item" $item }

Write-Host "`n===== ADDING STOCK ENTRIES (Material Receipt) =====" -ForegroundColor Cyan

$stockItems = @(
    @{ item_code="SKU001"; qty=150; rate=499 },
    @{ item_code="SKU002"; qty=25; rate=65000 },
    @{ item_code="SKU003"; qty=200; rate=350 },
    @{ item_code="SKU004"; qty=40; rate=18000 },
    @{ item_code="SKU005"; qty=80; rate=3500 },
    @{ item_code="SKU006"; qty=300; rate=199 },
    @{ item_code="SKU007"; qty=15; rate=42000 },
    @{ item_code="SKU008"; qty=60; rate=1800 },
    @{ item_code="SKU009"; qty=100; rate=2500 },
    @{ item_code="SKU010"; qty=20; rate=35000 },
    @{ item_code="SKU011"; qty=200; rate=400 },
    @{ item_code="SKU012"; qty=500; rate=120 },
    @{ item_code="SKU013"; qty=50; rate=1800 },
    @{ item_code="SKU014"; qty=75; rate=900 },
    @{ item_code="SKU015"; qty=40; rate=600 },
    @{ item_code="SKU016"; qty=90; rate=1000 },
    @{ item_code="SKU017"; qty=120; rate=500 },
    @{ item_code="SKU018"; qty=250; rate=150 },
    @{ item_code="SKU019"; qty=180; rate=250 },
    @{ item_code="SKU020"; qty=30; rate=2800 }
)

foreach ($si in $stockItems) {
    $entry = @{
        stock_entry_type = "Material Receipt"
        items = @(
            @{
                item_code = $si.item_code
                qty = $si.qty
                basic_rate = $si.rate
                t_warehouse = "Stores - SKAL"
            }
        )
    }
    Create-Doc "Stock Entry" $entry
}

# Submit stock entries
Write-Host "`n===== SUBMITTING STOCK ENTRIES =====" -ForegroundColor Cyan
$entries = Invoke-RestMethod -Uri "$baseUrl/api/resource/Stock Entry?filters=[[`"docstatus`",`"=`",0]]&limit_page_length=100" -Headers $headers
foreach ($e in $entries.data) {
    try {
        Invoke-RestMethod -Uri "$baseUrl/api/resource/Stock Entry/$($e.name)" -Method PUT -Headers $headers -Body (@{docstatus=1} | ConvertTo-Json)
        Write-Host "[SUBMIT] Stock Entry: $($e.name)" -ForegroundColor Green
    } catch {
        Write-Host "[ERR] Submit $($e.name): $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n===== CREATING SALES ORDERS =====" -ForegroundColor Cyan

$salesOrders = @(
    @{ customer="Sharma Electronics Pvt Ltd"; delivery_date="2026-10-05"; items=@(@{item_code="SKU002";qty=5;rate=75000},@{item_code="SKU009";qty=20;rate=2999}) },
    @{ customer="Patel Traders & Sons"; delivery_date="2026-10-03"; items=@(@{item_code="SKU001";qty=50;rate=699},@{item_code="SKU006";qty=100;rate=249}) },
    @{ customer="Gupta Warehouse Solutions"; delivery_date="2026-10-07"; items=@(@{item_code="SKU013";qty=10;rate=2499},@{item_code="SKU014";qty=15;rate=1299}) },
    @{ customer="Singh Retail Chain"; delivery_date="2026-10-10"; items=@(@{item_code="SKU016";qty=30;rate=1499},@{item_code="SKU017";qty=40;rate=799}) },
    @{ customer="Mehta Distributors"; delivery_date="2026-10-08"; items=@(@{item_code="SKU004";qty=10;rate=22000},@{item_code="SKU007";qty=3;rate=49999}) },
    @{ customer="Rajesh Kumar"; delivery_date="2026-10-02"; items=@(@{item_code="SKU005";qty=2;rate=4500},@{item_code="SKU011";qty=3;rate=599}) },
    @{ customer="Priya Verma"; delivery_date="2026-10-04"; items=@(@{item_code="SKU015";qty=1;rate=899},@{item_code="SKU019";qty=2;rate=499}) },
    @{ customer="Arun Mishra"; delivery_date="2026-10-06"; items=@(@{item_code="SKU020";qty=1;rate=3999},@{item_code="SKU012";qty=5;rate=199}) }
)

foreach ($so in $salesOrders) {
    Create-Doc "Sales Order" $so
}

Write-Host "`n===== CREATING MATERIAL REQUESTS =====" -ForegroundColor Cyan

$materialRequests = @(
    @{ material_request_type="Purchase"; schedule_date="2026-10-15"; items=@(@{item_code="SKU002";qty=20;schedule_date="2026-10-15"},@{item_code="SKU010";qty=15;schedule_date="2026-10-15"}) },
    @{ material_request_type="Purchase"; schedule_date="2026-10-12"; items=@(@{item_code="SKU007";qty=10;schedule_date="2026-10-12"},@{item_code="SKU004";qty=25;schedule_date="2026-10-12"}) }
)

foreach ($mr in $materialRequests) {
    Create-Doc "Material Request" $mr
}

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "  DATA LOADING COMPLETE!" -ForegroundColor Green
Write-Host "  Customers: 8  |  Suppliers: 4" -ForegroundColor White
Write-Host "  Items: 20     |  Stock Entries: 20" -ForegroundColor White
Write-Host "  Sales Orders: 8  |  Material Requests: 2" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Cyan
