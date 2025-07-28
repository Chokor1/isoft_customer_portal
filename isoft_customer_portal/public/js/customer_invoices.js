// Customer Invoices JavaScript
frappe.provide('isoft_customer_portal');

isoft_customer_portal.CustomerInvoices = class CustomerInvoices {
    constructor() {
        this.currentPage = 1;
        this.pageLength = 20;
        this.filters = {};
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadInvoicesData();
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
        $('.refresh-btn').on('click', () => this.loadInvoicesData());

        // Invoice row clicks
        $(document).on('click', '.invoice-row', (e) => {
            const invoiceName = $(e.currentTarget).data('invoice');
            this.viewInvoice(invoiceName);
        });
    }

    applyFilters() {
        this.filters = {
            from_date: $('#from-date').val(),
            to_date: $('#to-date').val(),
            status: $('#status').val(),
            min_amount: $('#min-amount').val(),
            max_amount: $('#max-amount').val(),
            outstanding: $('#outstanding').val()
        };
        
        this.currentPage = 1;
        this.loadInvoicesData();
    }

    clearFilters() {
        $('#filter-form')[0].reset();
        this.filters = {};
        this.currentPage = 1;
        this.loadInvoicesData();
    }

    loadInvoicesData() {
        this.showLoading();
        
        frappe.call({
            method: 'isoft_customer_portal.api.get_customer_invoices',
            args: {
                filters: this.filters,
                page: this.currentPage,
                page_length: this.pageLength
            },
            callback: (r) => {
                if (r.message) {
                    this.updateInvoicesTable(r.message);
                }
                this.hideLoading();
            }
        });
    }

    updateInvoicesTable(data) {
        const container = $('#invoices-table tbody');
        container.empty();

        if (data.invoices && data.invoices.length > 0) {
            data.invoices.forEach(invoice => {
                const row = this.createInvoiceRow(invoice);
                container.append(row);
            });
        } else {
            container.html('<tr><td colspan="8" class="text-center">No invoices found</td></tr>');
        }

        this.updatePagination(data);
        this.updateSummary(data.summary);
    }

    createInvoiceRow(invoice) {
        const formattedDate = frappe.format_date(invoice.posting_date);
        const formattedAmount = frappe.format_currency(invoice.grand_total);
        const formattedOutstanding = frappe.format_currency(invoice.outstanding_amount || 0);
        const statusClass = this.getStatusClass(invoice.status);

        return `
            <tr class="invoice-row" data-invoice="${invoice.name}">
                <td>${invoice.name}</td>
                <td>${formattedDate}</td>
                <td>${invoice.customer_name || ''}</td>
                <td class="text-right">${formattedAmount}</td>
                <td class="text-right">${formattedOutstanding}</td>
                <td><span class="status-badge ${statusClass}">${invoice.status || 'Draft'}</span></td>
                <td>${invoice.due_date ? frappe.format_date(invoice.due_date) : '-'}</td>
                <td>
                    <button class="btn btn-sm btn-primary view-invoice-btn" data-invoice="${invoice.name}">
                        <i class="fas fa-eye"></i> View
                    </button>
                </td>
            </tr>
        `;
    }

    getStatusClass(status) {
        const statusMap = {
            'Draft': 'status-draft',
            'Submitted': 'status-submitted',
            'Paid': 'status-paid',
            'Overdue': 'status-overdue',
            'Cancelled': 'status-cancelled',
            'Return': 'status-return'
        };
        return statusMap[status] || 'status-default';
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
            $('#total-invoices').text(summary.total_invoices || 0);
            $('#total-amount').text(frappe.format_currency(summary.total_amount || 0));
            $('#total-outstanding').text(frappe.format_currency(summary.total_outstanding || 0));
        }
    }

    goToPage(page) {
        this.currentPage = page;
        this.loadInvoicesData();
        $('html, body').animate({ scrollTop: 0 }, 'slow');
    }

    viewInvoice(invoiceName) {
        // Open invoice in new window/tab
        const url = `/app/sales-invoice/${invoiceName}`;
        window.open(url, '_blank');
    }

    exportExcel() {
        frappe.call({
            method: 'isoft_customer_portal.api.export_invoices_excel',
            args: { filters: this.filters },
            callback: (r) => {
                if (r.message) {
                    const link = document.createElement('a');
                    link.href = r.message;
                    link.download = 'customer_invoices.xlsx';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }
            }
        });
    }

    exportPDF() {
        frappe.call({
            method: 'isoft_customer_portal.api.export_invoices_pdf',
            args: { filters: this.filters },
            callback: (r) => {
                if (r.message) {
                    window.open(r.message, '_blank');
                }
            }
        });
    }

    showLoading() {
        $('.invoices-content').addClass('loading');
    }

    hideLoading() {
        $('.invoices-content').removeClass('loading');
    }
};

// Initialize invoices when page loads
$(document).ready(() => {
    new isoft_customer_portal.CustomerInvoices();
}); 