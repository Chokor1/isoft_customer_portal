import frappe
from frappe import _
from frappe.utils import now_datetime

def check_customer_auth():
    """Check if user is authenticated as customer with Isoft Customer Portal user type"""
    if not frappe.session.user or frappe.session.user == 'Guest':
        return False
    
    # Check if user has Customer Portal role
    user_roles = frappe.get_roles(frappe.session.user)
    if "Customer Portal" not in user_roles:
        return False
    
    # Check if user has Isoft Customer Portal user type
    try:
        user_doc = frappe.get_doc("User", frappe.session.user)
        if not user_doc.enabled:
            return False
        
        # Check if user has the correct user type
        if user_doc.user_type != "Isoft Customer Portal":
            return False
            
    except:
        return False
    
    return True

def require_customer_auth():
    """Decorator to require customer authentication"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            if not check_customer_auth():
                frappe.throw(_("Authentication required. Please login as a customer with Isoft Customer Portal access."), frappe.AuthenticationError)
            return f(*args, **kwargs)
        return wrapper
    return decorator

def get_customer_from_user():
    """Get customer linked to current user via Contact"""
    try:
        user = frappe.session.user
        if not user or user == 'Guest':
            return None
        
        # Get contact linked to the user
        contact = frappe.db.get_value("Contact", {"user": user})
        if not contact:
            return None
        
        # Get customer from contact's dynamic link
        customer = frappe.db.get_value("Dynamic Link", {
            "parent": contact,
            "link_doctype": "Customer"
        }, "link_name")
        
        return customer
    except Exception as e:
        frappe.log_error(f"Error in get_customer_from_user: {str(e)}")
        return None

def validate_customer_access():
    """Validate that user has access to customer data"""
    customer = get_customer_from_user()
    if not customer:
        frappe.throw(_("No customer linked to your account. Please contact administrator."), frappe.AuthenticationError)
    return customer

def get_user_type_info():
    """Get information about the current user's user type"""
    try:
        user = frappe.session.user
        if not user or user == 'Guest':
            return None
        
        user_doc = frappe.get_doc("User", user)
        if user_doc.user_type:
            user_type_doc = frappe.get_doc("User Type", user_doc.user_type)
            return {
                "name": user_type_doc.name,
                "role": user_type_doc.role,
                "apply_user_permission_on": user_type_doc.apply_user_permission_on,
                "user_id_field": user_type_doc.user_id_field
            }
        return None
    except Exception as e:
        frappe.log_error(f"Error in get_user_type_info: {str(e)}")
        return None 