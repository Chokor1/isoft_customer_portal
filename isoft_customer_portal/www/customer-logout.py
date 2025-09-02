import frappe
from frappe import _

def get_context(context):
    """Handle customer logout page context"""
    try:
        # Ensure user is logged out by clearing any remaining session
        if frappe.session.user != "Guest":
            # Clear session from database
            if frappe.session.sid:
                frappe.db.sql("DELETE FROM `tabSessions` WHERE sid = %s", frappe.session.sid)
            
            # Clear all user sessions for security
            frappe.db.sql("DELETE FROM `tabSessions` WHERE user = %s", frappe.session.user)
            
            # Use Frappe's logout mechanism
            frappe.local.login_manager.logout()
            
            # Force clear session
            frappe.session.user = "Guest"
            frappe.session.sid = None
            
            # Clear local references
            if hasattr(frappe.local, 'session'):
                frappe.local.session = None
            if hasattr(frappe.local, 'user'):
                frappe.local.user = None
                
            # Clear user permissions cache
            if hasattr(frappe.local, 'user_perms'):
                frappe.local.user_perms = {}
            
            # Commit changes
            frappe.db.commit()
        
        # Set context for the logout page
        context.update({
            "title": "Logged Out - Isoft Customer Portal",
            "no_cache": 1,
            "no_sidebar": 1,
            "no_header": 1,
            "show_sidebar": False,
            "logout_success": True
        })
        
        return context
        
    except Exception as e:
        frappe.log_error(f"Customer logout page error: {str(e)}")
        
        # Force logout even if error occurs
        try:
            frappe.session.user = "Guest"
            frappe.session.sid = None
            frappe.db.commit()
        except:
            pass
        
        # Return basic context
        context.update({
            "title": "Logged Out - Isoft Customer Portal",
            "no_cache": 1,
            "no_sidebar": 1,
            "no_header": 1,
            "show_sidebar": False,
            "logout_success": True
        })
        
        return context 