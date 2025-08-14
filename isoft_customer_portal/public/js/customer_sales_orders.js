// Customer Sales Orders JavaScript
frappe.provide('isoft_customer_portal');

isoft_customer_portal.CustomerSalesOrders = class CustomerSalesOrders {
    constructor() {
        this.currentPage = 1;
        this.pageLength = 10;
        this.filters = {};
        this.init();
    }

    init() {
        // Initialize currency first, then load data
        isoft_customer_portal.utils.getDefaultCurrency().then(() => {
            this.loadSalesOrdersData();
        });
        this.bindEvents();
    }

    bindEvents() {
        // Filter form submission
        $('#filter-form').on('submit', (e) => {
            e.preventDefault();
            this.applyFilters();
        });

        // Clear filters
        $('.clear-filters-btn').on('click', () => {
            this.clearFilters();
        });

        // Pagination
        $(document).on('click', '.pagination-btn', (e) => {
            const page = $(e.currentTarget).data('page');
            this.goToPage(page);
        });

        // Export buttons
        $('.export-excel-btn').on('click', () => this.exportExcel());
        $('.export-pdf-btn').on('click', () => this.exportPDF());

        // Refresh button
        $('.refresh-btn').on('click', () => this.loadSalesOrdersData());

        // Removed row click handler - no longer redirects to document
    }

    applyFilters() {
        this.filters = {
            from_date: $('#from-date').val(),
            to_date: $('#to-date').val(),
            status: $('#status').val(),
            min_amount: $('#min-amount').val(),
            max_amount: $('#max-amount').val(),
            delivery_status: $('#delivery-status').val()
        };
        
        this.currentPage = 1;
        this.loadSalesOrdersData();
    }

    clearFilters() {
        $('#filter-form')[0].reset();
        this.filters = {};
        this.currentPage = 1;
        this.loadSalesOrdersData();
    }

    loadSalesOrdersData() {
        this.showLoading();
        
        frappe.call({
            method: 'isoft_customer_portal.api.get_customer_sales_orders',
            args: {
                filters: this.filters,
                page: this.currentPage,
                page_length: this.pageLength
            },
            callback: (r) => {
                if (r.message) {
                    this.updateSalesOrdersTable(r.message);
                }
                this.hideLoading();
            }
        });
    }

    updateSalesOrdersTable(data) {
        const container = $('#sales-orders-list');
        container.empty();

        if (data.sales_orders && data.sales_orders.length > 0) {
            data.sales_orders.forEach(salesOrder => {
                const row = this.createSalesOrderRow(salesOrder);
                container.append(row);
            });
        } else {
            container.html('<tr><td colspan="6" class="text-center">No sales orders found</td></tr>');
        }

        this.updatePagination(data);
        this.updateSummary(data.summary);
    }

    createSalesOrderRow(salesOrder) {
        // Use currency from sales order data or fallback to cached currency
        const currency = salesOrder.currency || isoft_customer_portal.utils.cachedCurrency || 'USD';
        
        const formattedDate = isoft_customer_portal.utils.formatDate(salesOrder.transaction_date);
        const formattedAmount = isoft_customer_portal.utils.formatCurrency(salesOrder.grand_total, currency);
        const formattedDeliveryDate = salesOrder.delivery_date ? isoft_customer_portal.utils.formatDate(salesOrder.delivery_date) : '-';
        const statusClass = this.getStatusClass(salesOrder.status);

        return `
            <tr class="sales-order-row" data-sales-order="${salesOrder.name}">
                <td><strong>${salesOrder.name}</strong></td>
                <td>${formattedDate}</td>
                <td>${formattedDeliveryDate}</td>
                <td><strong>${formattedAmount}</strong></td>
                <td><span class="status-badge ${statusClass}">${salesOrder.status || 'Draft'}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary print-btn" onclick="event.stopPropagation(); isoft_customer_portal.printDocument('Sales Order', '${salesOrder.name}')" title="Print Sales Order">
                        <i class="fas fa-print"></i>
                    </button>
                </td>
            </tr>
        `;
    }

    getStatusClass(status) {
        const statusMap = {
            'Draft': 'status-draft',
            'To Deliver': 'status-to-deliver',
            'To Bill': 'status-to-bill',
            'Completed': 'status-completed',
            'Cancelled': 'status-cancelled',
            'Closed': 'status-closed'
        };
        return statusMap[status] || 'status-default';
    }

    getDeliveryStatusClass(deliveryStatus) {
        const statusMap = {
            'Not Delivered': 'status-not-delivered',
            'Fully Delivered': 'status-fully-delivered',
            'Partially Delivered': 'status-partially-delivered',
            'Closed': 'status-closed'
        };
        return statusMap[deliveryStatus] || 'status-default';
    }

    updatePagination(data) {
        const pagination = $('.pagination');
        pagination.empty();

        if (data.total_pages <= 1) {
            return;
        }

        // Previous button
        if (this.currentPage > 1) {
            pagination.append(`
                <button class="pagination-btn" data-page="${this.currentPage - 1}">
                    <i class="fas fa-chevron-left"></i> Previous
                </button>
            `);
        }

        // Page numbers
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(data.total_pages, this.currentPage + 2);

        for (let i = startPage; i <= endPage; i++) {
            const activeClass = i === this.currentPage ? 'active' : '';
            pagination.append(`
                <button class="pagination-btn ${activeClass}" data-page="${i}">${i}</button>
            `);
        }

        // Next button
        if (this.currentPage < data.total_pages) {
            pagination.append(`
                <button class="pagination-btn" data-page="${this.currentPage + 1}">
                    Next <i class="fas fa-chevron-right"></i>
                </button>
            `);
        }
    }

    updateSummary(summary) {
        if (summary) {
            $('#total-sales-orders').text(summary.total_sales_orders || 0);
            $('#total-amount').text(isoft_customer_portal.utils.formatCurrency(summary.total_amount || 0));
            $('#pending-delivery').text(summary.pending_delivery || 0);
        }
    }

    goToPage(page) {
        this.currentPage = page;
        this.loadSalesOrdersData();
        $('html, body').animate({ scrollTop: 0 }, 'slow');
    }

    viewSalesOrder(salesOrderName) {
        // Open sales order in new window/tab
        const url = `/app/sales-order/${salesOrderName}`;
        window.open(url, '_blank');
    }

    exportExcel() {
        frappe.call({
            method: 'isoft_customer_portal.api.export_sales_orders_excel',
            args: { filters: this.filters },
            callback: (r) => {
                if (r.message) {
                    const link = document.createElement('a');
                    link.href = r.message;
                    link.download = 'customer_sales_orders.xlsx';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }
            }
        });
    }

    exportPDF() {
        frappe.call({
            method: 'isoft_customer_portal.api.export_sales_orders_pdf',
            args: { filters: this.filters },
            callback: (r) => {
                if (r.message) {
                    window.open(r.message, '_blank');
                }
            }
        });
    }

    showLoading() {
        $('.sales-orders-content').addClass('loading');
    }

    hideLoading() {
        $('.sales-orders-content').removeClass('loading');
    }
};

// Initialize sales orders when page loads
$(document).ready(() => {
    new isoft_customer_portal.CustomerSalesOrders();
}); 