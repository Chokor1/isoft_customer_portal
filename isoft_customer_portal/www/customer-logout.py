import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def customer_logout():
    """Handle customer logout route"""
    try:
        # Store session info before logout
        original_user = frappe.session.user
        original_sid = frappe.session.sid
        
        # Proper logout using Frappe's session management
        if frappe.session.user != "Guest":
            # Use Frappe's built-in logout mechanism
            frappe.local.login_manager.logout()
            
            # Clear any remaining session data
            if hasattr(frappe.local, 'session'):
                frappe.local.session = None
            if hasattr(frappe.local, 'user'):
                frappe.local.user = None
            
            # Commit any pending database changes
            frappe.db.commit()
        else:
            # User is already Guest, no action needed
            pass
        
        # Return context for the logout page
        context = {
            "title": "Logged Out",
            "no_cache": 1,
            "no_sidebar": 1,
            "no_header": 1
        }
        
        return context
        
    except Exception as e:
        frappe.log_error(f"Customer logout route error: {str(e)}")
        # Return basic context even if error occurs
        return {
            "title": "Logged Out",
            "no_cache": 1,
            "no_sidebar": 1,
            "no_header": 1
        } 