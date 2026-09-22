import frappe
from frappe.core.doctype.user.user import generate_keys

frappe.init(site="frontend")
frappe.connect()

result = generate_keys("Administrator")
frappe.db.commit()

api_key = frappe.db.get_value("User", "Administrator", "api_key")
api_secret = result.get("api_secret", "")

print(f"GENERATED_API_KEY={api_key}")
print(f"GENERATED_API_SECRET={api_secret}")
