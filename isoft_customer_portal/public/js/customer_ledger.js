// Customer Ledger JavaScript
frappe.provide('isoft_customer_portal');

isoft_customer_portal.CustomerLedger = class CustomerLedger {
    constructor() {
        this.currentPage = 1;
        this.pageLength = 20;
        this.filters = {};
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadLedgerData();
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
        $('.refresh-btn').on('click', () => this.loadLedgerData());
    }

    applyFilters() {
        this.filters = {
            from_date: $('#from-date').val(),
            to_date: $('#to-date').val(),
            voucher_type: $('#voucher-type').val(),
            min_amount: $('#min-amount').val(),
            max_amount: $('#max-amount').val()
        };
        
        this.currentPage = 1;
        this.loadLedgerData();
    }

    clearFilters() {
        $('#filter-form')[0].reset();
        this.filters = {};
        this.currentPage = 1;
        this.loadLedgerData();
    }

    loadLedgerData() {
        this.showLoading();
        
        frappe.call({
            method: 'isoft_customer_portal.api.get_customer_ledger',
            args: {
                filters: this.filters,
                page: this.currentPage,
                page_length: this.pageLength
            },
            callback: (r) => {
                if (r.message) {
                    this.updateLedgerTable(r.message);
                }
                this.hideLoading();
            }
        });
    }

    updateLedgerTable(data) {
        const container = $('#ledger-table tbody');
        container.empty();

        if (data.entries && data.entries.length > 0) {
            data.entries.forEach(entry => {
                const row = this.createLedgerRow(entry);
                container.append(row);
            });
        } else {
            container.html('<tr><td colspan="7" class="text-center">No ledger entries found</td></tr>');
        }

        this.updatePagination(data);
        this.updateSummary(data.summary);
    }

    createLedgerRow(entry) {
        const formattedDate = frappe.format_date(entry.posting_date);
        const formattedDebit = frappe.format_currency(entry.debit || 0);
        const formattedCredit = frappe.format_currency(entry.credit || 0);
        const formattedBalance = frappe.format_currency(entry.balance || 0);

        return `
            <tr class="ledger-row" data-voucher="${entry.voucher_no}">
                <td>${formattedDate}</td>
                <td>${entry.voucher_type || ''}</td>
                <td>${entry.voucher_no || ''}</td>
                <td>${entry.against || ''}</td>
                <td class="text-right">${formattedDebit}</td>
                <td class="text-right">${formattedCredit}</td>
                <td class="text-right">${formattedBalance}</td>
            </tr>
        `;
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
            $('#total-debit').text(frappe.format_currency(summary.total_debit || 0));
            $('#total-credit').text(frappe.format_currency(summary.total_credit || 0));
            $('#net-balance').text(frappe.format_currency(summary.net_balance || 0));
        }
    }

    goToPage(page) {
        this.currentPage = page;
        this.loadLedgerData();
        $('html, body').animate({ scrollTop: 0 }, 'slow');
    }

    exportExcel() {
        frappe.call({
            method: 'isoft_customer_portal.api.export_ledger_excel',
            args: { filters: this.filters },
            callback: (r) => {
                if (r.message) {
                    const link = document.createElement('a');
                    link.href = r.message;
                    link.download = 'customer_ledger.xlsx';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }
            }
        });
    }

    exportPDF() {
        frappe.call({
            method: 'isoft_customer_portal.api.export_ledger_pdf',
            args: { filters: this.filters },
            callback: (r) => {
                if (r.message) {
                    window.open(r.message, '_blank');
                }
            }
        });
    }

    showLoading() {
        $('.ledger-content').addClass('loading');
    }

    hideLoading() {
        $('.ledger-content').removeClass('loading');
    }
};

// Initialize ledger when page loads
$(document).ready(() => {
    new isoft_customer_portal.CustomerLedger();
}); 