from . import __version__ as app_version

app_name = "isoft_customer_portal"
app_title = "Isoft Customer Portal"
app_publisher = "Abbass Chokor"
app_description = "The isoft Customer Portal is a user-friendly web application seamlessly integrated with ERPNext, designed to empower customers with real-time access to their business data and transactions."
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "abbasschokor225@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/css/isoft_customer_portal.css"
app_include_js = "/assets/js/isoft_customer_portal.js"

# include js, css files in header of web template
web_include_css = "/assets/css/isoft_customer_portal.css"
web_include_js = "/assets/js/isoft_customer_portal.js"

# include custom scss in every website theme (without file extension ".scss")
website_theme_scss = "isoft_customer_portal/public/scss/website"

# include js in page
page_js = {
    "customer-dashboard": "public/js/customer_dashboard.js",
    "customer-ledger": "public/js/customer_ledger.js",
    "customer-invoices": "public/js/customer_invoices.js",
    "customer-quotations": "public/js/customer_quotations.js",
    "customer-delivery-notes": "public/js/customer_delivery_notes.js",
    "customer-sales-orders": "public/js/customer_sales_orders.js"
}

# Home Pages
# ----------

# application home page (will override Website Settings)
home_page = "customer-dashboard"

# website user home page (by Role)
role_home_page = {
	"Customer": "customer-dashboard"
}

# Generators
# ----------

# automatically create page for each record of this doctype
website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "isoft_customer_portal.install.before_install"
after_install = "isoft_customer_portal.install.after_install"

# Uninstallation
# ------------

before_uninstall = "isoft_customer_portal.install.before_uninstall"
# after_uninstall = "isoft_customer_portal.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "isoft_customer_portal.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"Sales Invoice": "isoft_customer_portal.permissions.get_sales_invoice_permission_query_conditions",
	"Quotation": "isoft_customer_portal.permissions.get_quotation_permission_query_conditions",
	"Delivery Note": "isoft_customer_portal.permissions.get_delivery_note_permission_query_conditions",
	"Sales Order": "isoft_customer_portal.permissions.get_sales_order_permission_query_conditions",
	"GL Entry": "isoft_customer_portal.permissions.get_gl_entry_permission_query_conditions"
}

has_permission = {
	"Sales Invoice": "isoft_customer_portal.permissions.has_sales_invoice_permission",
	"Quotation": "isoft_customer_portal.permissions.has_quotation_permission",
	"Delivery Note": "isoft_customer_portal.permissions.has_delivery_note_permission",
	"Sales Order": "isoft_customer_portal.permissions.has_sales_order_permission",
	"GL Entry": "isoft_customer_portal.permissions.has_gl_entry_permission"
}

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"isoft_customer_portal.tasks.all"
#	],
#	"daily": [
#		"isoft_customer_portal.tasks.daily"
#	],
#	"hourly": [
#		"isoft_customer_portal.tasks.hourly"
#	],
#	"weekly": [
#		"isoft_customer_portal.tasks.weekly"
#	]
#	"monthly": [
#		"isoft_customer_portal.tasks.monthly"
#	]
# }

# Testing
# -------

# before_tests = "isoft_customer_portal.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "isoft_customer_portal.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "isoft_customer_portal.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Request Events
# ----------------
# before_request = ["isoft_customer_portal.utils.before_request"]
# after_request = ["isoft_customer_portal.utils.after_request"]

# Job Events
# ----------
# before_job = ["isoft_customer_portal.utils.before_job"]
# after_job = ["isoft_customer_portal.utils.after_job"]

# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "Sales Invoice",
		"filter_by": "customer",
		"redact_fields": ["customer_address", "shipping_address"],
		"partial": 1,
	},
	{
		"doctype": "Quotation",
		"filter_by": "party_name",
		"partial": 1,
	},
	{
		"doctype": "Delivery Note",
		"filter_by": "customer",
		"partial": 1,
	},
	{
		"doctype": "Sales Order",
		"filter_by": "customer",
		"partial": 1,
	},
	{
		"doctype": "GL Entry",
		"filter_by": "party",
		"partial": 1,
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"isoft_customer_portal.auth.validate"
# ]

