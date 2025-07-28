// Isoft Customer Portal - Main JavaScript File
frappe.provide('isoft_customer_portal');

// Global customer portal namespace
window.isoft_customer_portal = window.isoft_customer_portal || {};

// Common utilities for customer portal
isoft_customer_portal.utils = {
    // Format currency with proper locale
    formatCurrency: function(amount, currency = 'USD') {
        if (!amount) return '0.00';
        return frappe.format_currency(amount, currency);
    },

    // Format date with proper locale
    formatDate: function(date) {
        if (!date) return '';
        return frappe.format_date(date);
    },

    // Show loading spinner
    showLoading: function(container) {
        if (container) {
            container.addClass('loading');
        }
    },

    // Hide loading spinner
    hideLoading: function(container) {
        if (container) {
            container.removeClass('loading');
        }
    },

    // Show success message
    showSuccess: function(message) {
        frappe.show_alert(message, 3);
    },

    // Show error message
    showError: function(message) {
        frappe.show_alert(message, 5, 'red');
    },

    // Validate customer access
    validateCustomerAccess: function() {
        // In web context, we'll validate through the backend API
        return true;
    },

    // Get customer from current user
    getCustomerFromUser: function() {
        // In web context, we'll get customer info from the backend
        return null;
    },

    // Create pagination controls
    createPagination: function(currentPage, totalPages, callback) {
        const pagination = $('<div class="pagination"></div>');
        
        if (totalPages <= 1) return pagination;

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
            'Draft': 'status-draft',
            'Submitted': 'status-submitted',
            'Paid': 'status-paid',
            'Overdue': 'status-overdue',
            'Cancelled': 'status-cancelled',
            'Open': 'status-open',
            'Replied': 'status-replied',
            'Ordered': 'status-ordered',
            'Lost': 'status-lost',
            'Expired': 'status-expired',
            'To Deliver': 'status-to-deliver',
            'To Bill': 'status-to-bill',
            'Completed': 'status-completed',
            'Closed': 'status-closed',
            'Return': 'status-return',
            'Not Delivered': 'status-not-delivered',
            'Fully Delivered': 'status-fully-delivered',
            'Partially Delivered': 'status-partially-delivered',
            'Customer': 'status-customer',
            'Internal': 'status-internal',
            'Subcontractor': 'status-subcontractor'
        };

        const statusClass = statusMap[status] || 'status-default';
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

// Initialize customer portal when document is ready
$(document).ready(function() {
    // Add customer portal specific classes to body
    $('body').addClass('customer-portal-user');

    // Initialize any global customer portal functionality
    console.log('Isoft Customer Portal initialized');
}); 