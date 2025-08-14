
__version__ = '0.0.1'

# Import API module to ensure it's loaded
import frappe
if frappe.local.site:
    from . import api

