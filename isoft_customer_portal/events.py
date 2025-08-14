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