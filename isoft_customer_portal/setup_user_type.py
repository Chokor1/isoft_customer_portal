#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to manually set up or update the Isoft Customer Portal user type.
This can be run from the Frappe bench console or as a custom command.
"""

import frappe
from frappe import _

def setup_isoft_customer_portal_user_type():
    """Set up the Isoft Customer Portal user type manually"""
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
        
        # Create or update the user type
        if not frappe.db.exists("User Type", "Isoft Customer Portal"):
            create_user_type()
        else:
            update_user_type()
        
        # Set up permissions for existing customers
        setup_customer_permissions()
        
        return True
        
    except Exception as e:
        frappe.log_error(f"Error setting up user type: {str(e)}")
        return False

def create_user_type():
    """Create the Isoft Customer Portal user type"""
    user_type = frappe.get_doc({
        "doctype": "User Type",
        "name": "Isoft Customer Portal",
        "role": "Customer Portal",
        "apply_user_permission_on": "Contact",  # Changed from Customer to Contact
        "user_id_field": "user"  # Changed from "user_id" to "user"
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
            "write": 0,  # Read-only
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
            "write": 0,  # Read-only
            "create": 0,  # No create
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "delete": 0  # No delete
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

def update_user_type():
    """Update existing Isoft Customer Portal user type"""
    user_type = frappe.get_doc("User Type", "Isoft Customer Portal")
    
    # Update basic fields if needed
    if user_type.role != "Customer Portal":
        user_type.role = "Customer Portal"
    if user_type.apply_user_permission_on != "Contact":  # Changed from Customer to Contact
        user_type.apply_user_permission_on = "Contact"
    if user_type.user_id_field != "user":  # Changed from "user_id" to "user"
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

def setup_customer_permissions():
    """Set up permissions for existing customers"""
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
                
            except Exception as e:
                frappe.log_error(f"Error setting up permissions for user {customer.user}: {str(e)}")
                continue

if __name__ == "__main__":
    # This script can be run from the Frappe bench console
    setup_isoft_customer_portal_user_type()
