# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

def customer_updated(doc, method):
    """Handle customer updates"""
    try:
        # Update customer portal cache if needed
        if hasattr(doc, 'user') and doc.user:
            frappe.cache().delete_value(f"customer_portal_user_{doc.user}")
    except Exception as e:
        frappe.log_error(f"Error in customer_updated: {str(e)}")

def invoice_updated(doc, method):
    """Handle sales invoice updates"""
    try:
        # Clear customer portal cache for this customer
        if doc.customer:
            frappe.cache().delete_value(f"customer_portal_invoices_{doc.customer}")
    except Exception as e:
        frappe.log_error(f"Error in invoice_updated: {str(e)}")

def payment_updated(doc, method):
    """Handle payment entry updates"""
    try:
        # Clear customer portal cache for this customer
        if doc.party_name:
            frappe.cache().delete_value(f"customer_portal_payments_{doc.party_name}")
    except Exception as e:
        frappe.log_error(f"Error in payment_updated: {str(e)}")

def customer_before_save(doc, method):
    """Handle customer before save - check for user permission creation confirmation"""
    try:
        # Check if user field is set and user type is customer portal
        if doc.user:
            user_doc = frappe.get_doc("User", doc.user)
            if user_doc.user_type == "Isoft Customer Portal":
                # Check if this is a new assignment or if user permissions don't exist yet
                if not doc.get_doc_before_save() or doc.get_doc_before_save().user != doc.user:
                    # This is a new user assignment - we need confirmation
                    if not frappe.flags.confirm_user_permissions:
                        # Set a flag to be handled by the frontend
                        frappe.flags.needs_user_permission_confirmation = True
                        frappe.flags.customer_name = doc.name
                        frappe.flags.user_email = doc.user
                        
    except Exception as e:
        frappe.log_error(f"Error in customer_before_save: {str(e)}")

def customer_after_save(doc, method):
    """Handle customer after save - create user permissions if confirmed"""
    try:
        # Check if user field is set and user type is customer portal
        if doc.user:
            user_doc = frappe.get_doc("User", doc.user)
            if user_doc.user_type == "Isoft Customer Portal":
                # Import here to avoid circular imports
                from isoft_customer_portal.auth import create_user_permission_if_not_exists, create_sales_document_permissions
                
                # Create user permissions for Customer access
                create_user_permission_if_not_exists(doc.user, "Customer", doc.name)
                
                # Create user permissions for sales documents
                create_sales_document_permissions(doc.user, doc.name)
                
                # Also create permissions for Contact if the user is linked via Contact
                contact = frappe.db.get_value("Contact", {"user": doc.user}, "name")
                if contact:
                    create_user_permission_if_not_exists(doc.user, "Contact", contact)
                
                frappe.msgprint(
                    f"User permissions have been created for user {doc.user} on customer {doc.name} and related sales documents.",
                    title="User Permissions Created",
                    indicator="green"
                )
                
    except Exception as e:
        frappe.log_error(f"Error in customer_after_save: {str(e)}")

@frappe.whitelist()
def confirm_user_permission_creation(customer_name, user_email):
    """Confirm and create user permissions for customer portal user"""
    try:
        # Set confirmation flag
        frappe.flags.confirm_user_permissions = True
        
        # Get customer document and save it to trigger the permission creation
        customer_doc = frappe.get_doc("Customer", customer_name)
        customer_doc.save()
        
        return {
            "success": True,
            "message": f"User permissions created successfully for {user_email} on customer {customer_name}"
        }
        
    except Exception as e:
        frappe.log_error(f"Error confirming user permission creation: {str(e)}")
        return {
            "success": False,
            "message": f"Error creating user permissions: {str(e)}"
        } 