
__version__ = '0.0.1'

# Import API module to ensure it's loaded
import frappe
try:
    if frappe.local.site:
        from . import api
except (AttributeError, RuntimeError):
    # frappe.local.site is not available during pip installation
    pass

