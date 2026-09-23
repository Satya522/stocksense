// ==============================================================================
// StockSense - ERPNext Client Script: Low Stock Alert on Dashboard
// ==============================================================================
// This script adds a prominent alert banner on the ERPNext desktop/home page
// whenever any item falls below its reorder level.
//
// Installation:
//   ERPNext -> Setup -> Customize -> Client Script -> New
//   DocType: Desktop | Script Type: Client | Enabled: Yes
// ==============================================================================

frappe.ui.form.on('Desktop', {
    refresh: function(frm) {
        check_low_stock_alerts();
    }
});

function check_low_stock_alerts() {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Bin',
            filters: [['actual_qty', '<', 10]],
            fields: ['item_code', 'warehouse', 'actual_qty'],
            limit_page_length: 20,
            order_by: 'actual_qty asc'
        },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                let items_list = r.message.map(function(b) {
                    return `<b>${b.item_code}</b> (${b.warehouse}): ${b.actual_qty} units`;
                }).join('<br>');

                frappe.show_alert({
                    message: __(`<b>Low Stock Alert!</b> ${r.message.length} items need attention.<br>${items_list}`),
                    indicator: 'orange'
                }, 10);
            }
        }
    });
}
