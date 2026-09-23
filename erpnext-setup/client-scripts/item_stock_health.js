// ==============================================================================
// StockSense - ERPNext Client Script: Item Dashboard Enhancement
// ==============================================================================
// This script adds a custom dashboard section to the Item doctype in ERPNext,
// showing real-time stock health indicators directly on the Item form.
//
// Installation:
//   ERPNext -> Setup -> Customize -> Client Script -> New
//   DocType: Item | Script Type: Client | Enabled: Yes
//   Paste this code and Save.
// ==============================================================================

frappe.ui.form.on('Item', {
    refresh: function(frm) {
        // Only show for saved, stock items
        if (!frm.is_new() && frm.doc.is_stock_item) {
            add_stock_health_section(frm);
            add_quick_action_buttons(frm);
        }
    }
});

function add_stock_health_section(frm) {
    // Remove old section if exists (prevents duplication on refresh)
    frm.fields_dict.stock_health && frm.fields_dict.stock_health.$wrapper.remove();

    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Bin',
            filters: { item_code: frm.doc.name },
            fields: ['warehouse', 'actual_qty', 'projected_qty', 'valuation_rate'],
            limit_page_length: 100
        },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                let total_qty = 0;
                let total_value = 0;
                let warehouses = r.message.length;

                r.message.forEach(function(bin) {
                    total_qty += bin.actual_qty;
                    total_value += (bin.actual_qty * (bin.valuation_rate || 0));
                });

                // Determine health status
                let health_color = 'green';
                let health_text = 'Healthy';
                if (total_qty <= 0) {
                    health_color = 'red';
                    health_text = 'OUT OF STOCK';
                } else if (total_qty < 10) {
                    health_color = 'orange';
                    health_text = 'Low Stock';
                }

                // Add dashboard HTML
                let html = `
                    <div style="
                        border: 1px solid var(--border-color);
                        border-radius: 8px;
                        padding: 15px;
                        margin: 10px 0;
                        background: var(--card-bg);
                    ">
                        <h5 style="margin-bottom: 12px; color: var(--heading-color);">
                            <span class="indicator-pill ${health_color}">
                                <span>${health_text}</span>
                            </span>
                            Stock Health Dashboard
                        </h5>
                        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                            <div style="flex: 1; min-width: 120px; text-align: center; padding: 10px; background: var(--bg-color); border-radius: 6px;">
                                <div style="font-size: 24px; font-weight: bold; color: var(--text-color);">${total_qty.toFixed(0)}</div>
                                <div style="font-size: 11px; color: var(--text-muted);">Total Qty</div>
                            </div>
                            <div style="flex: 1; min-width: 120px; text-align: center; padding: 10px; background: var(--bg-color); border-radius: 6px;">
                                <div style="font-size: 24px; font-weight: bold; color: var(--text-color);">${warehouses}</div>
                                <div style="font-size: 11px; color: var(--text-muted);">Warehouses</div>
                            </div>
                            <div style="flex: 1; min-width: 120px; text-align: center; padding: 10px; background: var(--bg-color); border-radius: 6px;">
                                <div style="font-size: 24px; font-weight: bold; color: var(--text-color);">₹${total_value.toLocaleString('en-IN', {maximumFractionDigits: 0})}</div>
                                <div style="font-size: 11px; color: var(--text-muted);">Stock Value</div>
                            </div>
                        </div>
                    </div>
                `;

                // Insert above the form fields
                $(frm.fields_dict['item_name'].wrapper).before(html);
            }
        }
    });
}

function add_quick_action_buttons(frm) {
    // Quick Stock Transfer button
    frm.add_custom_button(__('View Stock Ledger'), function() {
        frappe.route_options = { item_code: frm.doc.name };
        frappe.set_route('query-report', 'Stock Ledger');
    }, __('Stock Actions'));

    // Quick Material Request button
    frm.add_custom_button(__('Request Material'), function() {
        frappe.new_doc('Material Request', {
            items: [{
                item_code: frm.doc.name,
                qty: 1,
                schedule_date: frappe.datetime.add_days(frappe.datetime.nowdate(), 7)
            }]
        });
    }, __('Stock Actions'));

    // Quick Stock Entry button
    frm.add_custom_button(__('New Stock Entry'), function() {
        frappe.new_doc('Stock Entry', {
            stock_entry_type: 'Material Receipt',
            items: [{
                item_code: frm.doc.name,
                qty: 1
            }]
        });
    }, __('Stock Actions'));
}
