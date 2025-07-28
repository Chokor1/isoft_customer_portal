import frappe
from frappe import _

def get_sales_invoice_permission_query_conditions(user):
    """Get permission query conditions for Sales Invoice"""
    if not user:
        user = frappe.session.user
    
    if "System Manager" in frappe.get_roles(user):
        return ""
    
    if "Customer" in frappe.get_roles(user):
        customer = get_customer_from_user(user)
        if customer:
            return f"`tabSales Invoice`.customer = '{customer}'"
    
    return "1=0"

def has_sales_invoice_permission(user, ptype, share, doctype, docname, doc=None):
    """Check if user has permission for Sales Invoice"""
    if not user:
        user = frappe.session.user
    
    if "System Manager" in frappe.get_roles(user):
        return True
    
    if "Customer" in frappe.get_roles(user):
        customer = get_customer_from_user(user)
        if customer and doc:
            return doc.customer == customer
    
    return False

def get_quotation_permission_query_conditions(user):
    """Get permission query conditions for Quotation"""
    if not user:
        user = frappe.session.user
    
    if "System Manager" in frappe.get_roles(user):
        return ""
    
    if "Customer" in frappe.get_roles(user):
        customer = get_customer_from_user(user)
        if customer:
            return f"`tabQuotation`.party_name = '{customer}'"
    
    return "1=0"

def has_quotation_permission(user, ptype, share, doctype, docname, doc=None):
    """Check if user has permission for Quotation"""
    if not user:
        user = frappe.session.user
    
    if "System Manager" in frappe.get_roles(user):
        return True
    
    if "Customer" in frappe.get_roles(user):
        customer = get_customer_from_user(user)
        if customer and doc:
            return doc.party_name == customer
    
    return False

def get_delivery_note_permission_query_conditions(user):
    """Get permission query conditions for Delivery Note"""
    if not user:
        user = frappe.session.user
    
    if "System Manager" in frappe.get_roles(user):
        return ""
    
    if "Customer" in frappe.get_roles(user):
        customer = get_customer_from_user(user)
        if customer:
            return f"`tabDelivery Note`.customer = '{customer}'"
    
    return "1=0"

def has_delivery_note_permission(user, ptype, share, doctype, docname, doc=None):
    """Check if user has permission for Delivery Note"""
    if not user:
        user = frappe.session.user
    
    if "System Manager" in frappe.get_roles(user):
        return True
    
    if "Customer" in frappe.get_roles(user):
        customer = get_customer_from_user(user)
        if customer and doc:
            return doc.customer == customer
    
    return False

def get_sales_order_permission_query_conditions(user):
    """Get permission query conditions for Sales Order"""
    if not user:
        user = frappe.session.user
    
    if "System Manager" in frappe.get_roles(user):
        return ""
    
    if "Customer" in frappe.get_roles(user):
        customer = get_customer_from_user(user)
        if customer:
            return f"`tabSales Order`.customer = '{customer}'"
    
    return "1=0"

def has_sales_order_permission(user, ptype, share, doctype, docname, doc=None):
    """Check if user has permission for Sales Order"""
    if not user:
        user = frappe.session.user
    
    if "System Manager" in frappe.get_roles(user):
        return True
    
    if "Customer" in frappe.get_roles(user):
        customer = get_customer_from_user(user)
        if customer and doc:
            return doc.customer == customer
    
    return False

def get_gl_entry_permission_query_conditions(user):
    """Get permission query conditions for GL Entry"""
    if not user:
        user = frappe.session.user
    
    if "System Manager" in frappe.get_roles(user):
        return ""
    
    if "Customer" in frappe.get_roles(user):
        customer = get_customer_from_user(user)
        if customer:
            return f"`tabGL Entry`.party = '{customer}'"
    
    return "1=0"

def has_gl_entry_permission(user, ptype, share, doctype, docname, doc=None):
    """Check if user has permission for GL Entry"""
    if not user:
        user = frappe.session.user
    
    if "System Manager" in frappe.get_roles(user):
        return True
    
    if "Customer" in frappe.get_roles(user):
        customer = get_customer_from_user(user)
        if customer and doc:
            return doc.party == customer
    
    return False

def get_customer_from_user(user=None):
    """Get customer linked to user"""
    if not user:
        user = frappe.session.user
    
    try:
        # Get customer linked to user
        customer = frappe.db.get_value("Customer", {"user": user})
        if not customer:
            # Try to get customer by email
            customer = frappe.db.get_value("Customer", {"email_id": frappe.get_value("User", user, "email")})
        
        return customer
    except Exception as e:
        frappe.log_error(f"Error in get_customer_from_user: {str(e)}")
        return None 