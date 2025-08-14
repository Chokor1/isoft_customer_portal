// Customer Quotations JavaScript
frappe.provide('isoft_customer_portal');

isoft_customer_portal.CustomerQuotations = class CustomerQuotations {
    constructor() {
        this.currentPage = 1;
        this.pageLength = 10;
        this.filters = {};
        this.init();
    }

    init() {
        // Initialize currency first, then load data
        isoft_customer_portal.utils.getDefaultCurrency().then(() => {
            this.loadQuotationsData();
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
        $('.refresh-btn').on('click', () => this.loadQuotationsData());

        // Removed row click handler - no longer redirects to document
    }

    applyFilters() {
        this.filters = {
            from_date: $('#from-date').val(),
            to_date: $('#to-date').val(),
            status: $('#status').val(),
            min_amount: $('#min-amount').val(),
            max_amount: $('#max-amount').val(),
            valid_till: $('#valid-till').val()
        };
        
        this.currentPage = 1;
        this.loadQuotationsData();
    }

    clearFilters() {
        $('#filter-form')[0].reset();
        this.filters = {};
        this.currentPage = 1;
        this.loadQuotationsData();
    }

    loadQuotationsData() {
        this.showLoading();
        
        frappe.call({
            method: 'isoft_customer_portal.api.get_customer_quotations',
            args: {
                filters: this.filters,
                page: this.currentPage,
                page_length: this.pageLength
            },
            callback: (r) => {
                if (r.message) {
                    this.updateQuotationsTable(r.message);
                }
                this.hideLoading();
            }
        });
    }

    updateQuotationsTable(data) {
        const container = $('#quotations-list');
        container.empty();

        if (data.quotations && data.quotations.length > 0) {
            data.quotations.forEach(quotation => {
                const row = this.createQuotationRow(quotation);
                container.append(row);
            });
        } else {
            container.html('<tr><td colspan="6" class="text-center">No quotations found</td></tr>');
        }

        this.updatePagination(data);
        this.updateSummary(data.summary);
    }

    createQuotationRow(quotation) {
        // Use currency from quotation data or fallback to cached currency
        const currency = quotation.currency || isoft_customer_portal.utils.cachedCurrency || 'USD';
        
        const formattedDate = isoft_customer_portal.utils.formatDate(quotation.transaction_date);
        const formattedAmount = isoft_customer_portal.utils.formatCurrency(quotation.grand_total, currency);
        const formattedValidTill = quotation.valid_till ? isoft_customer_portal.utils.formatDate(quotation.valid_till) : '-';
        const statusClass = this.getStatusClass(quotation.status);

        return `
            <tr class="quotation-row" data-quotation="${quotation.name}">
                <td><strong>${quotation.name}</strong></td>
                <td>${formattedDate}</td>
                <td>${formattedValidTill}</td>
                <td><strong>${formattedAmount}</strong></td>
                <td><span class="status-badge ${statusClass}">${quotation.status || 'Open'}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary print-btn" onclick="event.stopPropagation(); isoft_customer_portal.printDocument('Quotation', '${quotation.name}')" title="Print Quotation">
                        <i class="fas fa-print"></i>
                    </button>
                </td>
            </tr>
        `;
    }

    getStatusClass(status) {
        const statusMap = {
            'Open': 'status-open',
            'Replied': 'status-replied',
            'Ordered': 'status-ordered',
            'Lost': 'status-lost',
            'Cancelled': 'status-cancelled',
            'Expired': 'status-expired'
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
            $('#total-quotations').text(summary.total_quotations || 0);
            $('#total-amount').text(isoft_customer_portal.utils.formatCurrency(summary.total_amount || 0));
            $('#open-quotations').text(summary.open_quotations || 0);
        }
    }

    goToPage(page) {
        this.currentPage = page;
        this.loadQuotationsData();
        $('html, body').animate({ scrollTop: 0 }, 'slow');
    }

    viewQuotation(quotationName) {
        // Open quotation in new window/tab
        const url = `/app/quotation/${quotationName}`;
        window.open(url, '_blank');
    }

    exportExcel() {
        frappe.call({
            method: 'isoft_customer_portal.api.export_quotations_excel',
            args: { filters: this.filters },
            callback: (r) => {
                if (r.message) {
                    const link = document.createElement('a');
                    link.href = r.message;
                    link.download = 'customer_quotations.xlsx';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }
            }
        });
    }

    exportPDF() {
        frappe.call({
            method: 'isoft_customer_portal.api.export_quotations_pdf',
            args: { filters: this.filters },
            callback: (r) => {
                if (r.message) {
                    window.open(r.message, '_blank');
                }
            }
        });
    }

    showLoading() {
        $('.quotations-content').addClass('loading');
    }

    hideLoading() {
        $('.quotations-content').removeClass('loading');
    }
};

// Initialize quotations when page loads
$(document).ready(() => {
    new isoft_customer_portal.CustomerQuotations();
}); 