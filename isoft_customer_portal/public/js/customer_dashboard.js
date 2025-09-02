// Customer Dashboard JavaScript
frappe.provide('isoft_customer_portal');

isoft_customer_portal.CustomerDashboard = class CustomerDashboard {
    constructor() {
        this.init();
    }

    init() {
        this.loadDashboardData();
        this.bindEvents();
        this.initializeCharts();
    }

    bindEvents() {
        // Export buttons
        $(document).on('click', '.export-excel-btn', () => this.exportExcel());
        $(document).on('click', '.export-pdf-btn', () => this.exportPDF());
        
        // Refresh button
        $(document).on('click', '.refresh-btn', () => this.refreshData());
        
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
            },
            error: (r) => {
                this.hideLoading();
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
            },
            error: (r) => {
                // Error loading recent transactions
            }
        });

        // Load customer balance from ledger
        frappe.call({
            method: 'isoft_customer_portal.api.get_customer_ledger',
            args: {
                filters: JSON.stringify({}),
                page: 1,
                page_length: 1
            },
            callback: (r) => {
                if (r.message && r.message.summary) {
                    this.updateBalance(r.message.summary);
                }
                this.hideLoading();
            },
            error: (r) => {
                this.hideLoading();
            }
        });
    }

    updateStatistics(stats) {
        $('#total-invoices').text(stats.total_invoices || 0);
        $('#total-quotations').text(stats.total_quotations || 0);
        $('#total-sales-orders').text(stats.total_sales_orders || 0);
        $('#total-deliveries').text(stats.total_deliveries || 0);
        $('#total-payments').text(stats.total_payments || 0);
    }

    updateBalance(summary) {
        // Format balance with company currency
        const currency = isoft_customer_portal.utils.cachedCurrency || 'AKZ';
        const balance = summary.balance || 0;
        const formattedBalance = isoft_customer_portal.utils.formatCurrency(balance, currency);
        
        // Update balance text
        $('#current-balance').text(formattedBalance);
        
        // Apply color coding based on balance
        const balanceElement = $('#current-balance');
        const balanceCard = $('#balance-card');
        
        // Remove previous classes
        balanceElement.removeClass('balance-positive balance-negative balance-zero');
        balanceCard.removeClass('positive negative');
        
        if (balance > 0) {
            // Positive balance - customer owes money (red)
            balanceElement.addClass('balance-positive');
            balanceCard.addClass('positive');
        } else if (balance < 0) {
            // Negative balance - customer has credit (green)
            balanceElement.addClass('balance-negative');
            balanceCard.addClass('negative');
        } else {
            // Zero balance (gray)
            balanceElement.addClass('balance-zero');
        }
    }

    updateRecentTransactions(transactions) {
        const container = $('#recent-transactions');
        container.empty();

        if (!transactions || transactions.length === 0) {
            container.html('<tr><td colspan="5" class="no-data">No recent transactions found</td></tr>');
            return;
        }

        transactions.forEach(transaction => {
            const row = this.createTransactionRow(transaction);
            container.append(row);
        });
    }

    createTransactionRow(transaction) {
        // Use currency from transaction data or fallback to cached currency
        const currency = transaction.currency || isoft_customer_portal.utils.cachedCurrency || 'AKZ';
        const formattedAmount = isoft_customer_portal.utils.formatCurrency(transaction.amount, currency);
        const formattedDate = isoft_customer_portal.utils.formatDate(transaction.date);
        const statusClass = this.getStatusClass(transaction.status);

        return `
            <tr>
                <td><strong>${transaction.type}</strong></td>
                <td>${transaction.reference}</td>
                <td><strong>${formattedAmount}</strong></td>
                <td>${formattedDate}</td>
                <td><span class="status-badge ${statusClass}">${transaction.status}</span></td>
            </tr>
        `;
    }

    getTransactionIcon(type) {
        const iconMap = {
            'Sales Invoice': 'fa-file-invoice-dollar',
            'Quotation': 'fa-file-contract',
            'Sales Order': 'fa-shopping-cart',
            'Delivery Note': 'fa-truck',
            'Payment Entry': 'fa-credit-card',
            'Journal Entry': 'fa-book'
        };
        return iconMap[type] || 'fa-file';
    }

    getStatusClass(status) {
        const statusMap = {
            'Draft': 'draft',
            'Submitted': 'submitted',
            'Paid': 'paid',
            'Overdue': 'overdue',
            'Cancelled': 'cancelled',
            'Open': 'open',
            'Replied': 'replied',
            'Ordered': 'ordered',
            'Lost': 'lost',
            'Expired': 'expired',
            'To Deliver': 'to-deliver',
            'To Bill': 'to-bill',
            'Completed': 'completed',
            'Closed': 'closed'
        };
        return statusMap[status] || 'default';
    }

    viewTransaction(type, reference) {
        // Open transaction in new window/tab
        const urlMap = {
            'Sales Invoice': `/app/sales-invoice/${reference}`,
            'Quotation': `/app/quotation/${reference}`,
            'Sales Order': `/app/sales-order/${reference}`,
            'Delivery Note': `/app/delivery-note/${reference}`,
            'Payment Entry': `/app/payment-entry/${reference}`,
            'Journal Entry': `/app/journal-entry/${reference}`
        };
        
        const url = urlMap[type];
        if (url) {
            window.open(url, '_blank');
        }
    }

    exportExcel() {
        frappe.call({
            method: 'isoft_customer_portal.api.export_dashboard_excel',
            callback: (r) => {
                if (r.message && r.message.file_url) {
                    window.open(r.message.file_url, '_blank');
                } else {
                    isoft_customer_portal.utils.showError('Error exporting to Excel');
                }
            }
        });
    }

    exportPDF() {
        frappe.call({
            method: 'isoft_customer_portal.api.export_dashboard_pdf',
            callback: (r) => {
                if (r.message && r.message.file_url) {
                    window.open(r.message.file_url, '_blank');
                } else {
                    isoft_customer_portal.utils.showError('Error exporting to PDF');
                }
            }
        });
    }

    showLoading() {
        // Enhanced loading state with animation
        $('.summary-card .summary-value').addClass('loading-shimmer');
        $('#recent-transactions').html(`
            <tr>
                <td colspan="5" class="loading">
                    <i class="fas fa-spinner fa-spin"></i> 
                    <span>Loading latest data...</span>
                </td>
            </tr>
        `);
    }

    hideLoading() {
        $('.summary-card .summary-value').removeClass('loading-shimmer');
    }
    
    initializeCharts() {
        // Initialize dashboard charts if Chart.js is available
        if (typeof Chart !== 'undefined') {
            // Initialize charts after a short delay to ensure DOM is ready
            setTimeout(() => {
                if ((document.getElementById('revenueChart') || document.getElementById('statusChart')) && !window.dashboardCharts) {
                    window.dashboardCharts = new DashboardCharts();
                }
            }, 500);
        } else {
            console.warn('Chart.js not loaded. Charts will not be displayed.');
        }
    }
    
    refreshData() {
        this.loadDashboardData();
        // Refresh charts if they exist
        if (window.dashboardCharts) {
            window.dashboardCharts.refresh();
        } else {
            // Reinitialize charts if they don't exist
            this.initializeCharts();
        }
    }
};

// Initialize dashboard when Frappe is available
function initializeDashboard() {
    new isoft_customer_portal.CustomerDashboard();
}

// Wait for Frappe to be available
if (typeof frappe !== 'undefined' && frappe.session) {
    initializeDashboard();
} else {
    // Wait for Frappe to load
    $(document).ready(function() {
        const checkFrappe = setInterval(function() {
            if (typeof frappe !== 'undefined' && frappe.session) {
                clearInterval(checkFrappe);
                initializeDashboard();
            }
        }, 100);
    });
} 