import frappe
from frappe import _

def after_install():
    """Setup customer portal after installation"""
    create_customer_role()
    create_customer_portal_pages()
    setup_permissions()

def create_customer_role():
    """Create Customer role if it doesn't exist"""
    if not frappe.db.exists("Role", "Customer"):
        role = frappe.get_doc({
            "doctype": "Role",
            "role_name": "Customer",
            "desk_access": 0,  # No desk access for customers
            "restrict_to_domain": None
        })
        role.insert(ignore_permissions=True)
        frappe.db.commit()

def create_customer_portal_pages():
    """Create customer portal pages"""
    pages = [
        {
            "name": "customer-dashboard",
            "title": "Customer Dashboard",
            "published": 1,
            "route": "customer-dashboard"
        },
        {
            "name": "customer-ledger",
            "title": "Customer Ledger",
            "published": 1,
            "route": "customer-ledger"
        },
        {
            "name": "customer-invoices",
            "title": "Customer Invoices",
            "published": 1,
            "route": "customer-invoices"
        },
        {
            "name": "customer-quotations",
            "title": "Customer Quotations",
            "published": 1,
            "route": "customer-quotations"
        },
        {
            "name": "customer-sales-orders",
            "title": "Customer Sales Orders",
            "published": 1,
            "route": "customer-sales-orders"
        },
        {
            "name": "customer-delivery-notes",
            "title": "Customer Delivery Notes",
            "published": 1,
            "route": "customer-delivery-notes"
        }
    ]
    
    for page_data in pages:
        if not frappe.db.exists("Web Page", page_data["name"]):
            page = frappe.get_doc({
                "doctype": "Web Page",
                "title": page_data["title"],
                "route": page_data["route"],
                "published": page_data["published"],
                "template_path": f"isoft_customer_portal/www/{page_data['name']}.html"
            })
            page.insert(ignore_permissions=True)
    
    frappe.db.commit()

def setup_permissions():
    """Setup permissions for customer role"""
    # Add Customer role to existing users who are customers
    customers = frappe.get_all("Customer", fields=["name", "customer_name"])
    
    for customer in customers:
        # Check if customer has a user account
        user = frappe.db.get_value("User", {"email": customer.name})
        if user:
            # Add Customer role to user
            user_doc = frappe.get_doc("User", user)
            if "Customer" not in [role.role for role in user_doc.roles]:
                user_doc.append("roles", {
                    "role": "Customer"
                })
                user_doc.save(ignore_permissions=True)

def before_uninstall():
    """Cleanup before uninstall"""
    # Remove customer portal pages
    pages = [
        "customer-dashboard",
        "customer-ledger", 
        "customer-invoices",
        "customer-quotations",
        "customer-sales-orders",
        "customer-delivery-notes"
    ]
    
    for page_name in pages:
        if frappe.db.exists("Web Page", page_name):
            frappe.delete_doc("Web Page", page_name, ignore_permissions=True)
    
    frappe.db.commit() 