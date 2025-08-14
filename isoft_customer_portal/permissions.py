# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

def has_customer_permission(doc, ptype, user):
    """Check if user has permission to access customer documents"""
    if not user:
        return False
    
    # Allow system managers and administrators
    if frappe.has_permission(doc.doctype, ptype, user=user):
        return True
    
    # Check if user is linked to a customer
    customer = get_customer_from_user(user)
    if not customer:
        return False
    
    # For customer documents, check if the customer matches
    if hasattr(doc, 'customer') and doc.customer == customer:
        return True
    
    if hasattr(doc, 'party_name') and doc.party_name == customer:
        return True
    
    return False

def get_customer_from_user(user=None):
    """Get customer linked to user"""
    if not user:
        user = frappe.session.user
    
    # Check if user is a customer
    customer = frappe.db.get_value("Customer", {"user": user})
    if customer:
        return customer
    
    # Check if user is linked to a customer via Contact
    contact = frappe.db.get_value("Contact", {"user": user})
    if contact:
        customer = frappe.db.get_value("Contact", contact, "customer")
        if customer:
            return customer
    
    return None 