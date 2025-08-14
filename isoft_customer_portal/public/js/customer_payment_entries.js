// Customer Payment Entries JavaScript
frappe.provide('isoft_customer_portal');

isoft_customer_portal.CustomerPaymentEntries = class CustomerPaymentEntries {
    constructor() {
        this.currentPage = 1;
        this.totalPages = 1;
        this.pageSize = 10;
        this.totalRecords = 0;
        this.currentFilters = {};
        this.init();
    }

    init() {
        // Initialize currency first, then load data
        isoft_customer_portal.utils.getDefaultCurrency().then(() => {
            this.loadPaymentEntries();
            this.loadSummary();
        });
        this.bindEvents();
    }

    bindEvents() {
        // Filter button
        $(document).on('click', '#filter-btn', () => this.applyFilters());
        
        // Clear filters button
        $(document).on('click', '#clear-filters-btn', () => this.clearFilters());
        
        // Refresh button
        $(document).on('click', '.refresh-btn', () => this.loadPaymentEntries());
        
        // Export buttons
        $(document).on('click', '.export-excel-btn', () => this.exportExcel());
        $(document).on('click', '.export-pdf-btn', () => this.exportPDF());
        
        // Enhanced Pagination
        $(document).on('click', '#first-page', () => this.goToPage(1));
        $(document).on('click', '#prev-page', () => this.previousPage());
        $(document).on('click', '#next-page', () => this.nextPage());
        $(document).on('click', '#last-page', () => this.goToLastPage());
        $(document).on('change', '#page-size-select', () => this.changePageSize());
    }

    loadPaymentEntries(page = 1) {
        this.currentPage = page;
        
        const tbody = $('#payment-entries-list');
        tbody.html('<tr><td colspan="7" class="loading"><i class="fas fa-spinner fa-spin"></i> Loading payment entries...</td></tr>');
        
        frappe.call({
            method: 'isoft_customer_portal.api.get_customer_payment_entries',
            args: {
                filters: JSON.stringify(this.currentFilters),
                page: page,
                page_length: this.pageSize
            },
            callback: (r) => {
                if (r.message) {
                    this.displayPaymentEntries(r.message.entries || []);
                    this.updatePagination(r.message.total || 0, page);
                    this.updateSummary(r.message.summary || {});
                }
            }
        });
    }

    loadSummary() {
        frappe.call({
            method: 'isoft_customer_portal.api.get_customer_payment_entries',
            args: {
                filters: JSON.stringify({}),
                page: 1,
                page_length: 1
            },
            callback: (r) => {
                if (r.message && r.message.summary) {
                    this.updateSummary(r.message.summary);
                }
            }
        });
    }

    displayPaymentEntries(entries) {
        const tbody = $('#payment-entries-list');
        
        if (entries.length === 0) {
            tbody.html('<tr><td colspan="8" class="no-data">No payment entries found</td></tr>');
            return;
        }
        
        tbody.empty();
        
        entries.forEach(entry => {
            // Use currency from entry data or fallback to cached currency
            const currency = entry.currency || isoft_customer_portal.utils.cachedCurrency || 'USD';
            
            // Determine the color class based on payment type
            const amountClass = entry.payment_type === 'Receive' ? 'amount-positive' : 'amount-negative';
            
            const row = `
                <tr>
                    <td><strong>${entry.name}</strong></td>
                    <td>${isoft_customer_portal.utils.formatDate(entry.posting_date)}</td>
                    <td>
                        <span class="status ${entry.payment_type.toLowerCase()}">
                            ${entry.payment_type}
                        </span>
                    </td>
                    <td>${entry.mode_of_payment || '-'}</td>
                    <td class="${amountClass}">
                        <strong>${isoft_customer_portal.utils.formatCurrency(entry.net_amount || 0, currency)}</strong>
                    </td>
                    <td>${entry.reference_no || '-'}</td>
                    <td>
                        <span class="status ${(entry.status || 'submitted').toLowerCase()}">
                            ${entry.status || 'Submitted'}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary print-btn" onclick="event.stopPropagation(); isoft_customer_portal.printDocument('Payment Entry', '${entry.name}')" title="Print Payment Entry">
                            <i class="fas fa-print"></i>
                        </button>
                    </td>
                </tr>
            `;
            tbody.append(row);
        });
    }

    updatePagination(total, page) {
        this.totalRecords = total;
        this.currentPage = page;
        this.totalPages = Math.ceil(total / this.pageSize);
        
        // Update pagination info
        const start = ((page - 1) * this.pageSize) + 1;
        const end = Math.min(page * this.pageSize, total);
        
        $('#total-records').text(total);
        $('#current-page').text(page);
        $('#total-pages').text(this.totalPages);
        $('#range-start').text(start);
        $('#range-end').text(end);
        
        // Update button states
        $('#first-page').prop('disabled', page <= 1);
        $('#prev-page').prop('disabled', page <= 1);
        $('#next-page').prop('disabled', page >= this.totalPages);
        $('#last-page').prop('disabled', page >= this.totalPages);
    }

    updateSummary(summary) {
        const currency = isoft_customer_portal.utils.cachedCurrency || 'USD';
        
        $('#total-entries').text(summary.total_entries || 0);
        $('#total-received').text(isoft_customer_portal.utils.formatCurrency(summary.total_received || 0, currency));
        $('#total-paid').text(isoft_customer_portal.utils.formatCurrency(summary.total_paid || 0, currency));
        
        // Apply color coding for net amount
        const netAmount = summary.net_amount || 0;
        const netAmountElement = $('#net-amount');
        const netAmountCard = $('#net-amount-card');
        
        // Update net amount text
        netAmountElement.text(isoft_customer_portal.utils.formatCurrency(netAmount, currency));
        
        // Remove previous classes
        netAmountElement.removeClass('balance-positive balance-negative balance-zero');
        netAmountCard.removeClass('positive negative');
        
        if (netAmount > 0) {
            // Positive net amount - more received than paid (green)
            netAmountElement.addClass('balance-negative');
            netAmountCard.addClass('negative');
        } else if (netAmount < 0) {
            // Negative net amount - more paid than received (red)
            netAmountElement.addClass('balance-positive');
            netAmountCard.addClass('positive');
        } else {
            // Zero net amount (gray)
            netAmountElement.addClass('balance-zero');
        }
    }

    applyFilters() {
        const filters = {
            from_date: $('#from-date').val(),
            to_date: $('#to-date').val(),
            payment_type: $('#payment-type-filter').val()
        };
        
        // Remove empty filters
        Object.keys(filters).forEach(key => {
            if (!filters[key]) delete filters[key];
        });
        
        this.currentFilters = filters;
        this.loadPaymentEntries(1);
    }

    clearFilters() {
        $('#from-date').val('');
        $('#to-date').val('');
        $('#payment-type-filter').val('');
        this.currentFilters = {};
        this.loadPaymentEntries(1);
    }

    refreshData() {
        this.loadPaymentEntries(this.currentPage);
        this.loadSummary();
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.loadPaymentEntries(this.currentPage - 1);
        }
    }

    nextPage() {
        if (this.currentPage < this.totalPages) {
            this.loadPaymentEntries(this.currentPage + 1);
        }
    }

    goToPage(page) {
        if (page >= 1 && page <= this.totalPages) {
            this.loadPaymentEntries(page);
        }
    }

    goToLastPage() {
        if (this.totalPages > 0) {
            this.loadPaymentEntries(this.totalPages);
        }
    }

    changePageSize() {
        const newPageSize = parseInt($('#page-size-select').val());
        if (newPageSize !== this.pageSize) {
            this.pageSize = newPageSize;
            this.loadPaymentEntries(1); // Reset to first page
        }
    }

    exportExcel() {
        frappe.call({
            method: 'isoft_customer_portal.api.export_payment_entries_excel',
            args: { filters: JSON.stringify(this.currentFilters) },
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
        // For now, show a message that PDF export is not yet implemented
        isoft_customer_portal.utils.showError('PDF export for payment entries will be implemented soon');
    }
};