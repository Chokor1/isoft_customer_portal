// Customer Dashboard JavaScript
frappe.provide('isoft_customer_portal');

isoft_customer_portal.CustomerDashboard = class CustomerDashboard {
    constructor() {
        this.init();
    }

    init() {
        this.loadDashboardData();
        this.bindEvents();
        this.setupAutoRefresh();
    }

    bindEvents() {
        // Export buttons
        $(document).on('click', '.export-excel-btn', () => this.exportExcel());
        $(document).on('click', '.export-pdf-btn', () => this.exportPDF());
        
        // Refresh button
        $(document).on('click', '.refresh-btn', () => this.loadDashboardData());
        
        // Transaction row clicks
        $(document).on('click', '.transaction-row', (e) => {
            const type = $(e.currentTarget).data('type');
            const reference = $(e.currentTarget).data('reference');
            this.viewTransaction(type, reference);
        });
    }

    loadDashboardData() {
        this.showLoading();
        
        // Load statistics
        frappe.call({
            method: 'isoft_customer_portal.api.get_dashboard_statistics',
            callback: (r) => {
                if (r.message) {
                    this.updateStatistics(r.message);
                }
            }
        });

        // Load recent transactions
        frappe.call({
            method: 'isoft_customer_portal.api.get_recent_transactions',
            args: { limit: 10 },
            callback: (r) => {
                if (r.message) {
                    this.updateRecentTransactions(r.message);
                }
                this.hideLoading();
            }
        });
    }

    updateStatistics(stats) {
        $('#total-invoices').text(stats.total_invoices || 0);
        $('#total-quotations').text(stats.total_quotations || 0);
        $('#total-sales-orders').text(stats.total_sales_orders || 0);
        $('#total-deliveries').text(stats.total_deliveries || 0);
        $('#outstanding-amount').text(frappe.format_currency(stats.outstanding_amount || 0));
    }

    updateRecentTransactions(transactions) {
        const container = $('#recent-transactions');
        container.empty();

        if (transactions.length === 0) {
            container.html('<div class="no-data">No recent transactions found</div>');
            return;
        }

        transactions.forEach(transaction => {
            const row = this.createTransactionRow(transaction);
            container.append(row);
        });
    }

    createTransactionRow(transaction) {
        const statusClass = this.getStatusClass(transaction.status);
        const formattedAmount = frappe.format_currency(transaction.amount);
        const formattedDate = frappe.format_date(transaction.date);

        return `
            <div class="transaction-row" data-type="${transaction.type}" data-reference="${transaction.reference}">
                <div class="transaction-info">
                    <div class="transaction-type">
                        <i class="fas ${this.getTransactionIcon(transaction.type)}"></i>
                        ${transaction.type}
                    </div>
                    <div class="transaction-reference">${transaction.reference}</div>
                </div>
                <div class="transaction-details">
                    <div class="transaction-amount">${formattedAmount}</div>
                    <div class="transaction-date">${formattedDate}</div>
                    <div class="transaction-status ${statusClass}">${transaction.status}</div>
                </div>
            </div>
        `;
    }

    getTransactionIcon(type) {
        const icons = {
            'Sales Invoice': 'fa-file-invoice-dollar',
            'Quotation': 'fa-file-contract',
            'Sales Order': 'fa-shopping-cart',
            'Delivery Note': 'fa-truck'
        };
        return icons[type] || 'fa-file';
    }

    getStatusClass(status) {
        const statusMap = {
            'Draft': 'status-draft',
            'Submitted': 'status-submitted',
            'Paid': 'status-paid',
            'Overdue': 'status-overdue',
            'Cancelled': 'status-cancelled',
            'Delivered': 'status-delivered',
            'To Deliver': 'status-to-deliver'
        };
        return statusMap[status] || 'status-default';
    }

    viewTransaction(type, reference) {
        // Navigate to the appropriate page based on transaction type
        const pageMap = {
            'Sales Invoice': 'customer-invoices',
            'Quotation': 'customer-quotations',
            'Sales Order': 'customer-sales-orders',
            'Delivery Note': 'customer-delivery-notes'
        };

        const page = pageMap[type];
        if (page) {
            window.location.href = `/${page}?reference=${reference}`;
        }
    }

    exportExcel() {
        frappe.call({
            method: 'isoft_customer_portal.api.export_dashboard_excel',
            callback: (r) => {
                if (r.message) {
                    // Create and download the Excel file
                    const link = document.createElement('a');
                    link.href = r.message;
                    link.download = 'customer_dashboard.xlsx';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }
            }
        });
    }

    exportPDF() {
        frappe.call({
            method: 'isoft_customer_portal.api.export_dashboard_pdf',
            callback: (r) => {
                if (r.message) {
                    // Open PDF in new window
                    window.open(r.message, '_blank');
                }
            }
        });
    }

    showLoading() {
        $('.dashboard-content').addClass('loading');
    }

    hideLoading() {
        $('.dashboard-content').removeClass('loading');
    }

    setupAutoRefresh() {
        // Auto refresh every 5 minutes
        setInterval(() => {
            this.loadDashboardData();
        }, 5 * 60 * 1000);
    }
};

// Initialize dashboard when page loads
$(document).ready(() => {
    new isoft_customer_portal.CustomerDashboard();
}); 