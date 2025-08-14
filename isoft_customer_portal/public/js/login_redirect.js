// Customer Portal Login Redirect
frappe.provide('isoft_customer_portal');

isoft_customer_portal.login_redirect = {
    init: function() {
        // Check if user is logged in and redirect accordingly
        if (frappe.session.user && frappe.session.user !== 'Guest') {
            this.check_user_role_and_redirect();
        }
    },

    check_user_role_and_redirect: function() {
        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                doctype: 'User',
                filters: { name: frappe.session.user },
                fieldname: 'roles'
            },
            callback: (r) => {
                if (r.message && r.message.roles) {
                    const roles = r.message.roles;
                    if (roles.includes('Customer')) {
                        // Redirect customer to customer dashboard
                        if (window.location.pathname === '/app' || window.location.pathname === '/desk') {
                            window.location.href = '/customer-dashboard';
                        }
                    }
                }
            }
        });
    }
};

// Initialize on page load
$(document).ready(function() {
    isoft_customer_portal.login_redirect.init();
}); 