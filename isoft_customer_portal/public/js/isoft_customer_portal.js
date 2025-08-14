// Isoft Customer Portal - Main JavaScript File
frappe.provide('isoft_customer_portal');

// Import translation function
const __ = frappe._;

// Global customer portal namespace
window.isoft_customer_portal = window.isoft_customer_portal || {};

// Common utilities for customer portal
isoft_customer_portal.utils = {
    // Get default currency from company settings
    getDefaultCurrency: function() {
        return new Promise((resolve) => {
            frappe.call({
                method: 'isoft_customer_portal.api.get_company_currency_api',
                callback: (r) => {
                    if (r.message) {
                        this.cachedCurrency = r.message;
                        resolve(r.message);
                    } else {
                        this.cachedCurrency = 'USD';
                        resolve('USD');
                    }
                },
                error: () => {
                    this.cachedCurrency = 'USD';
                    resolve('USD');
                }
            });
        });
    },

    // Format currency with proper locale
    formatCurrency: function(amount, currency = null) {
        if (!amount) return '0.00';

        if (!currency) {
            // Use cached currency or default to USD
            currency = this.cachedCurrency || 'USD';
        }

        // Custom currency formatting since frappe.format_currency is not available
        const num = parseFloat(amount);
        if (isNaN(num)) return '0.00';
        
        // Format with 2 decimal places and thousands separator
        const formatted = num.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
        
        // Add currency symbol
        const currencySymbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'AOA': 'Kz',
            'AKZ': 'Kz'
        };
        
        const symbol = currencySymbols[currency] || currency + ' ';
        return symbol + formatted;
    },

    // Format date
    formatDate: function(date) {
        if (!date) return '';
        
        // Custom date formatting since frappe.datetime.str_to_user is not available
        try {
            const dateObj = new Date(date);
            if (isNaN(dateObj.getTime())) return '';
            
            // Format as YYYY-MM-DD
            return dateObj.toISOString().split('T')[0];
        } catch (e) {
            return date;
        }
    },

    // Show error message
    showError: function(message) {
        frappe.show_alert(message, 3);
    },

    // Show success message
    showSuccess: function(message) {
        frappe.show_alert(message, 5);
    },

    // Get customer data
    getCustomerData: function() {
        return new Promise((resolve) => {
            const user = frappe.session.user;
            if (!user || user === 'Guest') {
                resolve(null);
                return;
            }

            frappe.call({
                method: 'isoft_customer_portal.api.get_customer_data_api',
                callback: (r) => {
                    resolve(r.message || null);
                },
                error: () => {
                    resolve(null);
                }
            });
        });
    },

    // Handle customer logout
    logout: function() {
        return new Promise((resolve) => {
            // Call the customer logout API
            frappe.call({
                method: 'isoft_customer_portal.api.customer_logout',
                callback: (r) => {
                    if (r.message && r.message.success) {
                        // Clear any cached data
                        localStorage.removeItem('customer_data');
                        sessionStorage.clear();
                        
                        // Clear any Frappe session data
                        if (frappe.session) {
                            try {
                                if (typeof frappe.session.clear === 'function') {
                                    frappe.session.clear();
                                }
                            } catch (e) {
                                // Session clear error handled silently
                            }
                        }
                        
                        // Redirect to logout page
                        window.location.href = '/customer-logout';
                        resolve(true);
                    } else {
                        // Even if API fails, redirect to logout page
                        window.location.href = '/customer-logout';
                        resolve(false);
                    }
                },
                error: () => {
                    // Even if API fails, redirect to logout page
                    window.location.href = '/customer-logout';
                    resolve(false);
                }
            });
        });
    },

    // Print document using Frappe's print system
    printDocument: function(docType, docName) {
        // Show loading indicator
        frappe.show_alert(__('Preparing document for printing...'), 2);
        
        frappe.call({
            method: 'isoft_customer_portal.api.print_document',
            args: {
                doc_type: docType,
                doc_name: docName
            },
            callback: (r) => {
                if (r.message && r.message.print_format) {
                    // Build print URL manually for website context
                    let baseUrl = window.location.origin;
                    let printUrl = baseUrl + '/printview?' +
                        'doctype=' + encodeURIComponent(docType) +
                        '&name=' + encodeURIComponent(docName) +
                        '&trigger_print=1' +
                        '&format=' + encodeURIComponent(r.message.print_format) +
                        '&no_letterhead=0';
                    
                    // Add language if available
                    if (frappe.lang_code) {
                        printUrl += '&_lang=' + frappe.lang_code;
                    }
                    
                    let w = window.open(printUrl, '_blank');

                    if (!w) {
                        frappe.msgprint(__('Please enable pop-ups for printing.'));
                        return;
                    }
                    
                    // Show success message
                    frappe.show_alert(__('Document opened for printing'), 2);
                    
                } else if (r.message && r.message.error) {
                    this.showError(r.message.error);
                } else {
                    this.showError('Failed to get print format from settings');
                }
            },
            error: (err) => {
                this.showError('Failed to print document. Please try again.');
            }
        });
    },

    // Get customer filters
    getCustomerFilters: function() {
        const user = frappe.session.user;
        if (!user || user === 'Guest') {
            return {};
        }

        return {
            user: user
        };
    },

    // Create pagination controls
    createPagination: function(currentPage, totalPages, callback) {
        const pagination = $('<div class="pagination"></div>');
        
        if (totalPages <= 1) {
            return pagination;
        }

        // Previous button
        if (currentPage > 1) {
            pagination.append(`
                <button class="pagination-btn" data-page="${currentPage - 1}">
                    <i class="fas fa-chevron-left"></i> Previous
                </button>
            `);
        }

        // Page numbers
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);

        for (let i = startPage; i <= endPage; i++) {
            const activeClass = i === currentPage ? 'active' : '';
            pagination.append(`
                <button class="pagination-btn ${activeClass}" data-page="${i}">${i}</button>
            `);
        }

        // Next button
        if (currentPage < totalPages) {
            pagination.append(`
                <button class="pagination-btn" data-page="${currentPage + 1}">
                    Next <i class="fas fa-chevron-right"></i>
                </button>
            `);
        }

        // Bind pagination events
        pagination.on('click', '.pagination-btn', function() {
            const page = $(this).data('page');
            if (callback && typeof callback === 'function') {
                callback(page);
            }
        });

        return pagination;
    },

    // Create status badge
    createStatusBadge: function(status, type = 'default') {
        const statusMap = {
            'Submitted': 'status-submitted',
            'Paid': 'status-paid',
            'Overdue': 'status-overdue',
            'Cancelled': 'status-cancelled',
            'Open': 'status-open',
            'Replied': 'status-replied',
            'Ordered': 'ordered',
            'Lost': 'lost',
            'Expired': 'expired',
            'To Deliver': 'to-deliver',
            'To Bill': 'to-bill',
            'Completed': 'completed',
            'Closed': 'closed',
            'Return': 'return',
            'Not Delivered': 'not-delivered',
            'Fully Delivered': 'fully-delivered',
            'Partially Delivered': 'partially-delivered',
            'Customer': 'customer',
            'Internal': 'internal',
            'Subcontractor': 'subcontractor'
        };

        const statusClass = statusMap[status] || 'default';
        return `<span class="status-badge ${statusClass}">${status || 'Unknown'}</span>`;
    },

    // Export data to Excel
    exportToExcel: function(method, filters = {}, filename = 'export.xlsx') {
        frappe.call({
            method: method,
            args: { filters: filters },
            callback: function(r) {
                if (r.message && r.message.file_url) {
                    const link = document.createElement('a');
                    link.href = r.message.file_url;
                    link.download = filename;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                } else if (r.message && r.message.error) {
                    isoft_customer_portal.utils.showError(r.message.error);
                }
            }
        });
    },

    // Export data to PDF
    exportToPDF: function(method, filters = {}, filename = 'export.pdf') {
        frappe.call({
            method: method,
            args: { filters: filters },
            callback: function(r) {
                if (r.message && r.message.file_url) {
                    window.open(r.message.file_url, '_blank');
                } else if (r.message && r.message.error) {
                    isoft_customer_portal.utils.showError(r.message.error);
                }
            }
        });
    }
};

// Initialize customer portal when Frappe is available
function initializeCustomerPortal() {
    // Check if we're on login/logout pages - don't initialize
    const currentPath = window.location.pathname;
    if (currentPath.includes('login') || currentPath.includes('logout')) {
        return;
    }

    // Add customer portal specific classes to body
    if (frappe.session && frappe.session.user && frappe.session.user !== 'Guest') {
        $('body').addClass('customer-portal-user');
    }

    // Initialize currency
    isoft_customer_portal.utils.getDefaultCurrency().then(currency => {
        isoft_customer_portal.utils.cachedCurrency = currency;
    });

    // Bind logout functionality
    $(document).on('click', '.logout-btn, .customer-logout-btn', function(e) {
        e.preventDefault();
        
        if (confirm(__('Are you sure you want to logout?'))) {
            isoft_customer_portal.utils.logout();
        }
    });

    // Initialize any global customer portal functionality
}

// Wait for Frappe to be available
if (typeof frappe !== 'undefined' && frappe.session) {
    initializeCustomerPortal();
} else {
    // Wait for Frappe to load
    $(document).ready(function() {
        const checkFrappe = setInterval(function() {
            if (typeof frappe !== 'undefined' && frappe.session) {
                clearInterval(checkFrappe);
                initializeCustomerPortal();
            }
        }, 100);
    });
} 