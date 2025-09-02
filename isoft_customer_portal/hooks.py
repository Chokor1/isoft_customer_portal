# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# App configuration
app_name = "isoft_customer_portal"
app_title = "Isoft Customer Portal"
app_publisher = "Isoft"
app_description = "Customer Portal for ERPNext"
app_email = "support@isoft.ao"
app_license = "MIT"

# Include assets
app_include_js = [
    "/assets/js/isoft_customer_portal.js",
    "/assets/js/customer_dashboard.js",
    "/assets/js/customer_ledger.js",
    "/assets/js/customer_invoices.js",
    "/assets/js/customer_quotations.js",
    "/assets/js/customer_sales_orders.js",
    "/assets/js/customer_delivery_notes.js",
    "/assets/js/customer_payment_entries.js",
    "/assets/js/dashboard_charts.js",
    "/assets/js/dashboard_animations.js",
    "/assets/js/sidebar_navigation.js",
    "/assets/js/customer_user_permissions.js"
]

app_include_css = [
    "/assets/css/isoft_customer_portal.css"
]

# Website context
website_context = {
    "favicon": "/assets/isoft_customer_portal/images/favicon.ico",
    "splash_image": "/assets/isoft_customer_portal/images/splash.svg"
}

# Website pages
website_pages = [
    {
        "doctype": "Web Page",
        "title": "Customer Dashboard",
        "name": "customer-dashboard",
        "published": 1,
        "route": "/customer-dashboard"
    },
    {
        "doctype": "Web Page", 
        "title": "Customer Invoices",
        "name": "customer-invoices",
        "published": 1,
        "route": "/customer-invoices"
    },
    {
        "doctype": "Web Page",
        "title": "Customer Ledger", 
        "name": "customer-ledger",
        "published": 1,
        "route": "/customer-ledger"
    },
    {
        "doctype": "Web Page",
        "title": "Customer Quotations",
        "name": "customer-quotations", 
        "published": 1,
        "route": "/customer-quotations"
    },
    {
        "doctype": "Web Page",
        "title": "Customer Sales Orders",
        "name": "customer-sales-orders",
        "published": 1,
        "route": "/customer-sales-orders"
    },
    {
        "doctype": "Web Page",
        "title": "Customer Delivery Notes",
        "name": "customer-delivery-notes",
        "published": 1,
        "route": "/customer-delivery-notes"
    },
    {
        "doctype": "Web Page",
        "title": "Customer Payment Entries",
        "name": "customer-payment-entries",
        "published": 1,
        "route": "/customer-payment-entries"
    },
    {
        "doctype": "Web Page",
        "title": "Customer Logout",
        "name": "customer-logout",
        "published": 1,
        "route": "/customer-logout"
    }
]

# Installation
after_install = "isoft_customer_portal.install.after_install"

# Session hooks - runs after login when session is established
on_session_creation = "isoft_customer_portal.auth.create_customer_user_permission_on_login"

# Login hooks - runs immediately after successful login
on_login = "isoft_customer_portal.auth.create_customer_user_permission_on_login"

# Permissions
has_permission = {
    "Customer": "isoft_customer_portal.auth.has_customer_permission",
    "Sales Invoice": "isoft_customer_portal.auth.has_customer_permission",
    "Quotation": "isoft_customer_portal.auth.has_customer_permission",
    "Sales Order": "isoft_customer_portal.auth.has_customer_permission",
    "Delivery Note": "isoft_customer_portal.auth.has_customer_permission",
    "Payment Entry": "isoft_customer_portal.auth.has_customer_permission",
    "Bank Account": "isoft_customer_portal.auth.has_customer_permission"
}

# DocTypes
doc_events = {
    "Customer": {
        "before_save": "isoft_customer_portal.events.customer_before_save",
        "after_save": "isoft_customer_portal.events.customer_after_save",
        "on_update": "isoft_customer_portal.events.customer_updated"
    },
    "Sales Invoice": {
        "on_update": "isoft_customer_portal.events.invoice_updated"
    },
    "Payment Entry": {
        "on_update": "isoft_customer_portal.events.payment_updated"
    }
}

