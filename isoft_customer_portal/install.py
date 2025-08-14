# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

def after_install():
    """Run after app installation"""
    try:
        # Create customer portal role if it doesn't exist
        if not frappe.db.exists("Role", "Customer Portal"):
            role = frappe.get_doc({
                "doctype": "Role",
                "role_name": "Customer Portal",
                "desk_access": 0,
                "restrict_to_domain": None
            })
            role.insert()
        
        # Create comprehensive Isoft Customer Portal user type if it doesn't exist
        if not frappe.db.exists("User Type", "Isoft Customer Portal"):
            create_isoft_customer_portal_user_type()
        else:
            # Update existing user type if needed
            update_existing_user_type()
        
        # Create website pages
        create_website_pages()
        
        # Set up permissions
        setup_permissions()
        
        # Test the setup
        test_user_type_setup()
        
        frappe.msgprint("Isoft Customer Portal setup completed successfully!")
        
    except Exception as e:
        frappe.log_error(f"Error in after_install: {str(e)}")

def test_user_type_setup():
    """Test that the user type setup is working correctly"""
    try:
        # Verify user type exists
        if not frappe.db.exists("User Type", "Isoft Customer Portal"):
            frappe.log_error("Isoft Customer Portal user type was not created")
            return False
        
        user_type = frappe.get_doc("User Type", "Isoft Customer Portal")
        
        # Verify basic fields
        if user_type.role != "Customer Portal":
            frappe.log_error(f"User type role is incorrect: {user_type.role}")
            return False
        
        if user_type.apply_user_permission_on != "Contact":
            frappe.log_error(f"User type apply_user_permission_on is incorrect: {user_type.apply_user_permission_on}")
            return False
        
        # Verify user doctypes
        user_doctypes = [dt.document_type for dt in user_type.user_doctypes]
        required_doctypes = ["Sales Invoice", "Quotation", "Sales Order", "Delivery Note", "Payment Entry", "Customer", "Address", "Contact"]
        
        for doctype in required_doctypes:
            if doctype not in user_doctypes:
                frappe.log_error(f"Required doctype {doctype} not found in user type")
                return False
        
        # Verify select doctypes
        select_doctypes = [dt.document_type for dt in user_type.select_doctypes]
        required_select_doctypes = ["Company", "Currency", "Customer Group", "Territory"]
        
        for doctype in required_select_doctypes:
            if doctype not in select_doctypes:
                frappe.log_error(f"Required select doctype {doctype} not found in user type")
                return False
        
        # Verify modules
        modules = [m.module for m in user_type.user_type_modules]
        required_modules = ["Selling", "Stock", "Accounts", "CRM"]
        
        for module in required_modules:
            if module not in modules:
                frappe.log_error(f"Required module {module} not found in user type")
                return False
        

        return True
        
    except Exception as e:
        frappe.log_error(f"Error testing user type setup: {str(e)}")
        return False

def update_existing_user_type():
    """Update existing Isoft Customer Portal user type with latest permissions"""
    try:
        user_type = frappe.get_doc("User Type", "Isoft Customer Portal")
        
        # Update basic fields if needed
        if user_type.role != "Customer Portal":
            user_type.role = "Customer Portal"
        if user_type.apply_user_permission_on != "Contact":
            user_type.apply_user_permission_on = "Contact"
        if user_type.user_id_field != "user":
            user_type.user_id_field = "user"
        
        # Ensure all required user doctypes are present with READ-ONLY permissions
        existing_doctypes = [dt.document_type for dt in user_type.user_doctypes]
        required_doctypes = [
            "Sales Invoice", "Quotation", "Sales Order", "Delivery Note", 
            "Payment Entry", "Customer", "Address", "Contact"
        ]
        
        for doctype_name in required_doctypes:
            if doctype_name not in existing_doctypes:
                user_type.append("user_doctypes", {
                    "document_type": doctype_name,
                    "is_custom": 0,
                    "read": 1,
                    "write": 0,  # All documents are read-only
                    "create": 0,  # No create permission
                    "submit": 0,
                    "cancel": 0,
                    "amend": 0,
                    "delete": 0  # No delete permission
                })
            else:
                # Update existing doctype to ensure read-only permissions
                for dt in user_type.user_doctypes:
                    if dt.document_type == doctype_name:
                        dt.read = 1
                        dt.write = 0  # Ensure read-only
                        dt.create = 0  # Ensure no create
                        dt.submit = 0
                        dt.cancel = 0
                        dt.amend = 0
                        dt.delete = 0  # Ensure no delete
                        break
        
        # Ensure all required select doctypes are present
        existing_select_doctypes = [dt.document_type for dt in user_type.select_doctypes]
        required_select_doctypes = [
            "Company", "Currency", "Customer Group", "Territory", "Payment Terms Template",
            "Mode of Payment", "Sales Partner", "Sales Person", "Item Group", "Brand",
            "Warehouse", "Cost Center", "Project", "Tax Category", "Tax Rule",
            "Letter Head", "Print Heading", "Terms and Conditions"
        ]
        
        for doctype_name in required_select_doctypes:
            if doctype_name not in existing_select_doctypes:
                user_type.append("select_doctypes", {
                    "document_type": doctype_name
                })
        
        # Ensure all required modules are present
        existing_modules = [m.module for m in user_type.user_type_modules]
        required_modules = ["Selling", "Stock", "Accounts", "CRM"]
        
        for module_name in required_modules:
            if module_name not in existing_modules:
                user_type.append("user_type_modules", {
                    "module": module_name
                })
        
        user_type.save()
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Error updating existing user type: {str(e)}")

def create_isoft_customer_portal_user_type():
    """Create comprehensive Isoft Customer Portal user type"""
    user_type = frappe.get_doc({
        "doctype": "User Type",
        "name": "Isoft Customer Portal",
        "role": "Customer Portal",
        "apply_user_permission_on": "Contact",
        "user_id_field": "user"
    })
    
    # Add user doctypes with READ-ONLY permissions for all documents
    user_doctypes = [
        {
            "document_type": "Sales Invoice",
            "is_custom": 0,
            "read": 1,
            "write": 0,
            "create": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "delete": 0
        },
        {
            "document_type": "Quotation",
            "is_custom": 0,
            "read": 1,
            "write": 0,
            "create": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "delete": 0
        },
        {
            "document_type": "Sales Order",
            "is_custom": 0,
            "read": 1,
            "write": 0,
            "create": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "delete": 0
        },
        {
            "document_type": "Delivery Note",
            "is_custom": 0,
            "read": 1,
            "write": 0,
            "create": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "delete": 0
        },
        {
            "document_type": "Payment Entry",
            "is_custom": 0,
            "read": 1,
            "write": 0,
            "create": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "delete": 0
        },
        {
            "document_type": "Customer",
            "is_custom": 0,
            "read": 1,
            "write": 0,  # Changed to read-only
            "create": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "delete": 0
        },
        {
            "document_type": "Address",
            "is_custom": 0,
            "read": 1,
            "write": 0,  # Changed to read-only
            "create": 0,  # Changed to no create
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "delete": 0  # Changed to no delete
        },
        {
            "document_type": "Contact",
            "is_custom": 0,
            "read": 1,
            "write": 0,  # Changed to read-only
            "create": 0,  # Changed to no create
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "delete": 0  # Changed to no delete
        }
    ]
    
    for doctype_data in user_doctypes:
        user_type.append("user_doctypes", doctype_data)
    
    # Add select doctypes for dropdowns and references
    select_doctypes = [
        "Company", "Currency", "Customer Group", "Territory", "Payment Terms Template",
        "Mode of Payment", "Sales Partner", "Sales Person", "Item Group", "Brand",
        "Warehouse", "Cost Center", "Project", "Tax Category", "Tax Rule",
        "Letter Head", "Print Heading", "Terms and Conditions"
    ]
    
    for doctype_name in select_doctypes:
        user_type.append("select_doctypes", {
            "document_type": doctype_name
        })
    
    # Add user type modules
    user_type_modules = ["Selling", "Stock", "Accounts", "CRM"]
    
    for module_name in user_type_modules:
        user_type.append("user_type_modules", {
            "module": module_name
        })
    
    user_type.insert()

def create_website_pages():
    """Create website pages for customer portal"""
    pages = [
        {
            "doctype": "Web Page",
            "title": "Customer Dashboard",
            "name": "customer-dashboard",
            "published": 1,
            "route": "/customer-dashboard",
            "content": "{% extends 'templates/base_portal.html' %}\n{% block page_content %}{% include 'templates/includes/customer_dashboard.html' %}{% endblock %}"
        },
        {
            "doctype": "Web Page",
            "title": "Customer Invoices", 
            "name": "customer-invoices",
            "published": 1,
            "route": "/customer-invoices",
            "content": "{% extends 'templates/base_portal.html' %}\n{% block page_content %}{% include 'templates/includes/customer_invoices.html' %}{% endblock %}"
        },
        {
            "doctype": "Web Page",
            "title": "Customer Ledger",
            "name": "customer-ledger", 
            "published": 1,
            "route": "/customer-ledger",
            "content": "{% extends 'templates/base_portal.html' %}\n{% block page_content %}{% include 'templates/includes/customer_ledger.html' %}{% endblock %}"
        },
        {
            "doctype": "Web Page",
            "title": "Customer Quotations",
            "name": "customer-quotations",
            "published": 1,
            "route": "/customer-quotations", 
            "content": "{% extends 'templates/base_portal.html' %}\n{% block page_content %}{% include 'templates/includes/customer_quotations.html' %}{% endblock %}"
        },
        {
            "doctype": "Web Page",
            "title": "Customer Sales Orders",
            "name": "customer-sales-orders",
            "published": 1,
            "route": "/customer-sales-orders",
            "content": "{% extends 'templates/base_portal.html' %}\n{% block page_content %}{% include 'templates/includes/customer_sales_orders.html' %}{% endblock %}"
        },
        {
            "doctype": "Web Page",
            "title": "Customer Delivery Notes",
            "name": "customer-delivery-notes",
            "published": 1,
            "route": "/customer-delivery-notes",
            "content": "{% extends 'templates/base_portal.html' %}\n{% block page_content %}{% include 'templates/includes/customer_delivery_notes.html' %}{% endblock %}"
        },
        {
            "doctype": "Web Page",
            "title": "Customer Payment Entries",
            "name": "customer-payment-entries",
            "published": 1,
            "route": "/customer-payment-entries",
            "content": "{% extends 'templates/base_portal.html' %}\n{% block page_content %}{% include 'templates/includes/customer_payment_entries.html' %}{% endblock %}"
        }
    ]
    
    for page_data in pages:
        if not frappe.db.exists("Web Page", page_data["name"]):
            page = frappe.get_doc(page_data)
            page.insert()

def setup_permissions():
    """Set up permissions for customer portal"""
    # Add customer portal role and user type to existing customers
    customers = frappe.get_all("Customer", fields=["name", "user"])
    for customer in customers:
        if customer.user:
            try:
                user = frappe.get_doc("User", customer.user)
                
                # Add Customer Portal role if not present
                if "Customer Portal" not in user.get_roles():
                    user.add_roles("Customer Portal")
                
                # Set user type to Isoft Customer Portal
                if user.user_type != "Isoft Customer Portal":
                    user.user_type = "Isoft Customer Portal"
                
                user.save()
                frappe.db.commit()
                
            except Exception as e:
                frappe.log_error(f"Error setting up permissions for user {customer.user}: {str(e)}")
                continue 