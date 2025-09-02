# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.permissions import add_permission

def after_install():
    """Run after app installation"""
    try:
        # Create customer portal role and permissions
        create_customer_portal_role()
        
        # Create comprehensive Isoft Customer Portal user type
        if not frappe.db.exists("User Type", "Isoft Customer Portal"):
            create_isoft_customer_portal_user_type()
        else:
            update_existing_user_type()
        
        # Create website pages
        create_website_pages()
        
        # Set up permissions for existing customers
        setup_permissions()
        
        frappe.msgprint("Isoft Customer Portal setup completed successfully!")
        
    except Exception as e:
        frappe.log_error(f"Error in after_install: {str(e)}")

def create_customer_portal_role():
    """Create Customer Portal role with proper permissions"""
    if not frappe.db.exists("Role", "Customer Portal"):
        role = frappe.get_doc({
            "doctype": "Role",
            "role_name": "Customer Portal",
            "desk_access": 0,
            "restrict_to_domain": None,
            "home_page": "customer-dashboard"
        })
        role.insert()
    
    # Create role permissions for Customer Portal role
    role_permissions = [
        {"doctype": "Sales Invoice", "read": 1, "print": 1},
        {"doctype": "Quotation", "read": 1, "print": 1},
        {"doctype": "Sales Order", "read": 1, "print": 1},
        {"doctype": "Delivery Note", "read": 1, "print": 1},
        {"doctype": "Payment Entry", "read": 1, "print": 1},
        {"doctype": "Customer", "read": 1, "print": 1},
        {"doctype": "Address", "read": 1, "print": 1},
        {"doctype": "Contact", "read": 1, "print": 1},
        {"doctype": "Bank Account", "read": 1, "print": 1},
    ]
    
    for perm in role_permissions:
        try:
            # Check if Custom DocPerm already exists
            existing_perm = frappe.db.exists("Custom DocPerm", {
                "role": "Customer Portal",
                "parent": perm["doctype"]
            })
            
            if not existing_perm:
                # Create Custom DocPerm for proper document-level permissions
                doc_perm = frappe.get_doc({
                    "doctype": "Custom DocPerm",
                    "role": "Customer Portal",
                    "parent": perm["doctype"],
                    "parenttype": "DocType",
                    "parentfield": "permissions",
                    "read": perm.get("read", 0),
                    "write": 0,
                    "create": 0,
                    "delete": 0,
                    "submit": 0,
                    "cancel": 0,
                    "amend": 0,
                    "print": perm.get("print", 0),
                    "email": 0,
                    "report": 0,
                    "import": 0,
                    "export": 0,
                    "share": 0,
                    "if_owner": 0
                })
                doc_perm.insert(ignore_permissions=True)
                frappe.logger().info(f"Created Custom DocPerm for {perm['doctype']} with print permission")
            else:
                # Update existing permission to ensure print is enabled
                doc_perm = frappe.get_doc("Custom DocPerm", existing_perm)
                doc_perm.read = perm.get("read", 0)
                doc_perm.print = perm.get("print", 0)
                doc_perm.write = 0
                doc_perm.create = 0
                doc_perm.delete = 0
                doc_perm.submit = 0
                doc_perm.cancel = 0
                doc_perm.amend = 0
                doc_perm.save(ignore_permissions=True)
                frappe.logger().info(f"Updated Custom DocPerm for {perm['doctype']} with print permission")
                
        except Exception as e:
            frappe.log_error(f"Error creating Custom DocPerm for {perm['doctype']}: {str(e)}")
            continue

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
        
        # Clear existing modules (no modules needed)
        user_type.user_type_modules = []
        
        # Ensure all required user doctypes are present with READ-ONLY permissions
        existing_doctypes = [dt.document_type for dt in user_type.user_doctypes]
        required_doctypes = [
            "Sales Invoice", "Quotation", "Sales Order", "Delivery Note", 
            "Payment Entry", "Customer", "Address", "Contact", "Bank Account"
        ]
        
        for doctype_name in required_doctypes:
            if doctype_name not in existing_doctypes:
                user_type.append("user_doctypes", {
                    "document_type": doctype_name,
                    "is_custom": 0,
                    "read": 1,
                    "write": 0,
                    "create": 0,
                    "submit": 0,
                    "cancel": 0,
                    "amend": 0,
                    "delete": 0
                })
            else:
                # Update existing doctype to ensure read-only permissions
                for dt in user_type.user_doctypes:
                    if dt.document_type == doctype_name:
                        dt.read = 1
                        dt.write = 0
                        dt.create = 0
                        dt.submit = 0
                        dt.cancel = 0
                        dt.amend = 0
                        dt.delete = 0
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
            "write": 0,
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
            "write": 0,
            "create": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "delete": 0
        },
        {
            "document_type": "Contact",
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
            "document_type": "Bank Account",
            "is_custom": 0,
            "read": 1,
            "write": 0,
            "create": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "delete": 0
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
    
    # No modules needed for customer portal - users should not have module access
    
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
    # Create/update role permissions first
    create_customer_portal_role()
    
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

def update_customer_portal_permissions():
    """Update Customer Portal role permissions - can be run manually"""
    frappe.only_for("System Manager")
    
    try:
        # Recreate the role permissions with print access
        create_customer_portal_role()
        frappe.msgprint("Customer Portal role permissions updated successfully with print access!")
        return {"success": True, "message": "Permissions updated successfully"}
    except Exception as e:
        frappe.log_error(f"Error updating Customer Portal permissions: {str(e)}")
        frappe.throw(f"Error updating permissions: {str(e)}")
        return {"success": False, "message": str(e)} 