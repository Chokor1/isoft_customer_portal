// Customer Invoices JavaScript
frappe.provide('isoft_customer_portal');

// Safe print document function that waits for the main portal script to load
window.safePrintDocument = window.safePrintDocument || function(docType, docName) {
    if (window.isoft_customer_portal && window.isoft_customer_portal.printDocument) {
        // Main script is loaded, use the proper function
        window.isoft_customer_portal.printDocument(docType, docName);
    } else {
        // Main script not loaded yet, wait a bit and try again
        let attempts = 0;
        const maxAttempts = 50; // Wait up to 5 seconds
        const checkInterval = setInterval(() => {
            attempts++;
            if (window.isoft_customer_portal && window.isoft_customer_portal.printDocument) {
                clearInterval(checkInterval);
                window.isoft_customer_portal.printDocument(docType, docName);
            } else if (attempts >= maxAttempts) {
                clearInterval(checkInterval);
                // Fallback: show error message
                if (typeof frappe !== 'undefined' && frappe.msgprint) {
                    frappe.msgprint('Print function not available. Please refresh the page and try again.');
                } else {
                    alert('Print function not available. Please refresh the page and try again.');
                }
            }
        }, 100);
    }
};

isoft_customer_portal.CustomerInvoices = class CustomerInvoices {
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
            this.loadInvoices();
            this.loadSummary();
        });
        this.bindEvents();
        
        // Ensure page size selector is set correctly
        $('#page-size-select').val(this.pageSize);
    }

    bindEvents() {
        // Filter button
        $(document).on('click', '#filter-btn', () => {
            this.applyFilters();
        });
        
        // Clear filters button
        $(document).on('click', '#clear-filters-btn', () => {
            this.clearFilters();
        });
        
        // Refresh button
        $(document).on('click', '.refresh-btn', () => {
            this.refreshData();
        });
        
        // Export buttons
        $(document).on('click', '.export-excel-btn', () => this.exportExcel());
        $(document).on('click', '.export-pdf-btn', () => this.exportPDF());
        
        // Enhanced Pagination
        $(document).on('click', '#first-page', () => {
            this.goToPage(1);
        });
        $(document).on('click', '#prev-page', () => {
            this.previousPage();
        });
        $(document).on('click', '#next-page', () => {
            this.nextPage();
        });
        $(document).on('click', '#last-page', () => {
            this.goToLastPage();
        });
        $(document).on('change', '#page-size-select', () => {
            this.changePageSize();
        });
    }

    loadInvoices(page = 1) {
        this.currentPage = page;
        
        const tbody = $('#invoices-list');
        tbody.html('<tr><td colspan="8" class="loading"><i class="fas fa-spinner fa-spin"></i> Loading invoices...</td></tr>');
        
        frappe.call({
            method: 'isoft_customer_portal.api.get_customer_invoices',
            args: {
                filters: JSON.stringify(this.currentFilters),
                page: page,
                page_length: this.pageSize
            },
            callback: (r) => {
                if (r.message) {
                    this.displayInvoices(r.message.invoices || []);
                    this.updatePagination(r.message.total || 0, page);
                    this.updateSummary(r.message.summary || {});
                }
            },
            error: (r) => {
                console.error("Error loading invoices:", r);
            }
        });
    }

    loadSummary() {
        frappe.call({
            method: 'isoft_customer_portal.api.get_customer_invoices',
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

    displayInvoices(invoices) {
        const tbody = $('#invoices-list');
        
        if (invoices.length === 0) {
            tbody.html('<tr><td colspan="8" class="no-data">No invoices found</td></tr>');
            return;
        }
        
        tbody.empty();
        
        invoices.forEach(invoice => {
            // Use currency from invoice data or fallback to cached currency
            const currency = invoice.currency || isoft_customer_portal.utils.cachedCurrency || 'AKZ';
            
            const row = `
                <tr>
                    <td><strong>${invoice.name}</strong></td>
                    <td>${isoft_customer_portal.utils.formatDate(invoice.posting_date)}</td>
                    <td>${isoft_customer_portal.utils.formatDate(invoice.due_date)}</td>
                    <td><strong>${isoft_customer_portal.utils.formatCurrency(invoice.grand_total, currency)}</strong></td>
                    <td>${isoft_customer_portal.utils.formatCurrency(invoice.paid_amount || 0, currency)}</td>
                    <td>${isoft_customer_portal.utils.formatCurrency(invoice.outstanding_amount, currency)}</td>
                    <td><span class="status-badge ${(invoice.status || 'unpaid').toLowerCase()}">${invoice.status || 'Unpaid'}</span></td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary print-btn" onclick="event.stopPropagation(); window.safePrintDocument('Sales Invoice', '${invoice.name}')" title="Print Invoice">
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
        
        // Ensure we have at least 1 page
        if (this.totalPages < 1) this.totalPages = 1;
        
        // Update pagination info
        const start = total > 0 ? ((page - 1) * this.pageSize) + 1 : 0;
        const end = Math.min(page * this.pageSize, total);
        

        
        // Update display elements
        $('#total-records').text(total);
        $('#current-page').text(page);
        $('#total-pages').text(this.totalPages);
        $('#range-start').text(start);
        $('#range-end').text(end);
        
        // Update button states with visual feedback
        const firstBtn = $('#first-page');
        const prevBtn = $('#prev-page');
        const nextBtn = $('#next-page');
        const lastBtn = $('#last-page');
        
        // Disable/enable buttons
        firstBtn.prop('disabled', page <= 1).toggleClass('disabled', page <= 1);
        prevBtn.prop('disabled', page <= 1).toggleClass('disabled', page <= 1);
        nextBtn.prop('disabled', page >= this.totalPages).toggleClass('disabled', page >= this.totalPages);
        lastBtn.prop('disabled', page >= this.totalPages).toggleClass('disabled', page >= this.totalPages);
        
        // Add visual feedback for current page
        $('.pagination button').removeClass('active');
        $(`#page-${page}`).addClass('active');
        

    }

    updateSummary(summary) {
        const currency = isoft_customer_portal.utils.cachedCurrency || 'AKZ';
        
        // Helper function to update element and make it visible
        const updateElement = (selector, value, elementName) => {
            const element = $(selector);
            if (element.length) {
                element.text(value);
                // Mark as updated to prevent dashboard animations from hiding it
                element.attr('data-summary-updated', 'true');
                element.css({
                    'opacity': '1',
                    'transform': 'translateY(0)',
                    'transition': 'all 0.6s ease-out'
                });
            } else {
                console.warn(`Element ${selector} not found`);
            }
        };
        
        // Update all summary elements
        updateElement('#total-invoices', summary.total_invoices || 0, 'total invoices');
        updateElement('#paid-invoices', summary.paid_invoices || 0, 'paid invoices');
        updateElement('#unpaid-invoices', summary.unpaid_invoices || 0, 'unpaid invoices');
        updateElement('#overdue-invoices', summary.overdue_invoices || 0, 'overdue invoices');
        updateElement('#return-invoices', summary.return_invoices || 0, 'return invoices');
        updateElement('#credit-note-invoices', summary.credit_note_invoices || 0, 'credit note invoices');
        updateElement('#total-amount', isoft_customer_portal.utils.formatCurrency(summary.total_amount || 0, currency), 'total amount');
        
        // Update outstanding amount (if element exists)
        if ($('#outstanding-amount').length) {
            updateElement('#outstanding-amount', isoft_customer_portal.utils.formatCurrency(summary.total_outstanding || 0, currency), 'outstanding amount');
        }
    }

    applyFilters() {
        const filters = {
            from_date: $('#from-date').val(),
            to_date: $('#to-date').val(),
            status: $('#status-filter').val()
        };
        
        // Debug: Log the filter values
        console.log('Original filter values:', filters);
        
        // Remove empty filters
        Object.keys(filters).forEach(key => {
            if (!filters[key]) delete filters[key];
        });
        
        console.log('Cleaned filter values:', filters);
        
        this.currentFilters = filters;
        this.loadInvoices(1);
    }

    clearFilters() {
        $('#from-date').val('');
        $('#to-date').val('');
        $('#status-filter').val('');
        this.currentFilters = {};
        this.loadInvoices(1);
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.loadInvoices(this.currentPage - 1);
        }
    }

    nextPage() {
        if (this.currentPage < this.totalPages) {
            this.loadInvoices(this.currentPage + 1);
        }
    }

    goToPage(page) {
        if (page >= 1 && page <= this.totalPages) {
            this.loadInvoices(page);
        }
    }

    goToLastPage() {
        if (this.totalPages > 0) {
            this.loadInvoices(this.totalPages);
        }
    }

    changePageSize() {
        const newPageSize = parseInt($('#page-size-select').val());
        
        if (newPageSize !== this.pageSize) {
            this.pageSize = newPageSize;
            this.loadInvoices(1); // Reset to first page
        }
    }

    exportExcel() {
        frappe.call({
            method: 'isoft_customer_portal.api.export_invoices_excel',
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
        frappe.call({
            method: 'isoft_customer_portal.api.export_invoices_pdf',
            args: { filters: JSON.stringify(this.currentFilters) },
            callback: (r) => {
                if (r.message && r.message.file_url) {
                    window.open(r.message.file_url, '_blank');
                } else {
                    isoft_customer_portal.utils.showError('Error exporting to PDF');
                }
            }
        });
    }
    
    refreshData() {
        this.loadInvoices(this.currentPage);
        this.loadSummary();
    }
}; 