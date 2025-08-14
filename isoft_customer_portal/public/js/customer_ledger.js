// Customer Ledger JavaScript
frappe.provide('isoft_customer_portal');

isoft_customer_portal.CustomerLedger = class CustomerLedger {
    constructor() {
        this.currentPage = 1;
        this.totalPages = 1;
        this.pageSize = 10;
        this.totalRecords = 0;
        this.currentFilters = {};
        this.runningBalance = 0;
        this.isLoadingSummary = false;
        this.isLoadingLedger = false;
        
        // Disable Frappe's global loading mechanisms
        this.disableFrappeLoading();
        this.init();
    }

    disableFrappeLoading() {
        // Override Frappe's freeze mechanism to prevent global loading overlays
        if (typeof frappe !== 'undefined') {
            frappe.freeze_count = 0;
            frappe.freeze = function() { return false; };
            frappe.unfreeze = function() { return false; };
            frappe.show_loading = function() { return false; };
            frappe.hide_loading = function() { return false; };
        }
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.initializeAfterDOMReady();
            });
        } else {
            this.initializeAfterDOMReady();
        }
    }

    initializeAfterDOMReady() {
        // Check if required DOM elements exist
        const requiredElements = [
            '#ledger-entries',
            '#total-records',
            '#current-page',
            '#total-pages',
            '#range-start',
            '#range-end',
            '#total-debits',
            '#total-credits',
            '#current-balance',
            '#balance-card'
        ];
        
        const missingElements = [];
        requiredElements.forEach(selector => {
            const element = $(selector);
            if (!element || element.length === 0) {
                missingElements.push(selector);
            }
        });
        
        if (missingElements.length > 0) {
            return;
        }
        
        // Initialize currency first, then load data
        isoft_customer_portal.utils.getDefaultCurrency().then(() => {
            // Load ledger first, summary will be updated with the ledger response
            this.loadLedger();
        });
        this.bindEvents();
        this.loadSavedFilters();
        
        // Ensure page size selector is set correctly
        const pageSizeSelect = $('#page-size-select');
        if (pageSizeSelect && pageSizeSelect.length > 0) {
            pageSizeSelect.val(this.pageSize);
        }
    }

    bindEvents() {
        // Filter button
        $(document).on('click', '#filter-btn', () => this.applyFilters());
        
        // Clear filters button
        $(document).on('click', '#clear-filters-btn', () => this.clearFilters());
        
        // Refresh button
        $(document).on('click', '.refresh-btn', () => this.refreshData());
        
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

    loadLedger(page = 1) {
        // Prevent multiple loading states
        if (this.isLoadingLedger) {
            return;
        }
        
        this.isLoadingLedger = true;
        this.currentPage = page;
        
        const tbody = $('#ledger-entries');
        if (!tbody || tbody.length === 0) {
            this.isLoadingLedger = false;
            return;
        }
        
        // Clear any existing loading states and show single loading indicator
        tbody.empty();
        tbody.html('<tr><td colspan="7" class="ledger-loading-custom"><div class="ledger-spinner-wrapper"><i class="fas fa-circle-notch fa-spin"></i><span>Loading ledger entries...</span></div></td></tr>');
        
        frappe.call({
            method: 'isoft_customer_portal.api.get_customer_ledger',
            args: {
                filters: JSON.stringify(this.currentFilters),
                page: page,
                page_length: this.pageSize
            },
            freeze: false,
            callback: (r) => {
                try {
                    // Check if tbody still exists
                    const tbody = $('#ledger-entries');
                    if (!tbody || tbody.length === 0) {
                        this.isLoadingLedger = false;
                        return;
                    }
                    
                    if (r.message) {
                        // Handle case when no records found
                        if (!r.message.entries || r.message.entries.length === 0) {
                            tbody.html('<tr><td colspan="7" class="no-data">No ledger entries found for the current customer</td></tr>');
                            // Set pagination to 0
                            this.updatePagination(0, 1);
                            this.updateSummary(r.message.summary || {});
                            this.isLoadingLedger = false;
                            return;
                        }
                        
                        this.displayLedgerEntries(r.message.entries || []);
                        this.updatePagination(r.message.total || 0, page);
                        this.updateSummary(r.message.summary || {});
                    } else {
                        tbody.html('<tr><td colspan="7" class="no-data">No data received from server</td></tr>');
                    }
                } catch (error) {
                    const tbody = $('#ledger-entries');
                    if (tbody && tbody.length > 0) {
                        tbody.html('<tr><td colspan="7" class="error">Error processing data: ' + error.message + '</td></tr>');
                    }
                } finally {
                    this.isLoadingLedger = false;
                }
            },
            error: (r) => {
                const tbody = $('#ledger-entries');
                if (tbody && tbody.length > 0) {
                    tbody.html('<tr><td colspan="7" class="error">Error loading ledger entries</td></tr>');
                }
                this.isLoadingLedger = false;
            }
        });
    }

    loadSummary() {
        // Only load summary if not already loading
        if (this.isLoadingSummary) {
            return;
        }
        
        this.isLoadingSummary = true;
        
        frappe.call({
            method: 'isoft_customer_portal.api.get_customer_ledger',
            args: {
                filters: JSON.stringify({}),
                page: 1,
                page_length: 1
            },
            freeze: false,
            callback: (r) => {
                try {
                    if (r.message && r.message.summary) {
                        this.updateSummary(r.message.summary);
                    }
                } catch (error) {
                    // Silent error handling
                } finally {
                    this.isLoadingSummary = false;
                }
            },
            error: (r) => {
                // Silent error handling
                this.isLoadingSummary = false;
            }
        });
    }

    displayLedgerEntries(entries) {
        try {
            const tbody = $('#ledger-entries');
            
            if (!tbody || tbody.length === 0) {
                return;
            }
            
            if (entries.length === 0) {
                tbody.html('<tr><td colspan="7" class="no-data">No ledger entries found</td></tr>');
                return;
            }
            
            tbody.empty();
            this.runningBalance = 0;
            
            const currency = isoft_customer_portal.utils.cachedCurrency || 'USD';
            
            entries.forEach((entry, index) => {
                const debit = parseFloat(entry.debit || 0);
                const credit = parseFloat(entry.credit || 0);
                this.runningBalance += debit - credit;
                
                const formattedDate = isoft_customer_portal.utils.formatDate(entry.posting_date);
                const formattedDebit = isoft_customer_portal.utils.formatCurrency(debit, currency);
                const formattedCredit = isoft_customer_portal.utils.formatCurrency(credit, currency);
                const formattedBalance = isoft_customer_portal.utils.formatCurrency(this.runningBalance, currency);
                
                const row = `
                    <tr>
                        <td>${formattedDate}</td>
                        <td><strong>${entry.voucher_no}</strong></td>
                        <td>${entry.voucher_type}</td>
                        <td class="debit-amount">${formattedDebit}</td>
                        <td class="credit-amount">${formattedCredit}</td>
                        <td class="balance-amount ${this.runningBalance >= 0 ? 'balance-positive' : 'balance-negative'}">${formattedBalance}</td>
                        <td>${entry.remarks || '-'}</td>
                    </tr>
                `;
                
                tbody.append(row);
            });
        } catch (error) {
            const tbody = $('#ledger-entries');
            if (tbody && tbody.length > 0) {
                tbody.html('<tr><td colspan="7" class="error">Error displaying ledger entries: ' + error.message + '</td></tr>');
            }
        }
    }

    updatePagination(total, page) {
        try {
            this.totalRecords = total;
            this.currentPage = page;
            this.totalPages = Math.ceil(total / this.pageSize);
            
            // Update pagination info
            const start = ((page - 1) * this.pageSize) + 1;
            const end = Math.min(page * this.pageSize, total);
            
            // Helper function to safely update element text
            const safeUpdateText = (selector, value) => {
                const element = $(selector);
                if (element && element.length > 0 && element[0]) {
                    try {
                        element.text(value);
                        return true;
                    } catch (e) {
                        return false;
                    }
                }
                return false;
            };
            
            // Helper function to safely update button state
            const safeUpdateButton = (selector, disabled) => {
                const element = $(selector);
                if (element && element.length > 0 && element[0]) {
                    try {
                        element.prop('disabled', disabled);
                        return true;
                    } catch (e) {
                        return false;
                    }
                }
                return false;
            };
            
            // Update pagination elements
            safeUpdateText('#total-records', total);
            safeUpdateText('#current-page', page);
            safeUpdateText('#total-pages', this.totalPages);
            safeUpdateText('#range-start', start);
            safeUpdateText('#range-end', end);
            
            // Update button states
            safeUpdateButton('#first-page', page <= 1);
            safeUpdateButton('#prev-page', page <= 1);
            safeUpdateButton('#next-page', page >= this.totalPages);
            safeUpdateButton('#last-page', page >= this.totalPages);
            
        } catch (error) {
            // Silent error handling
        }
    }

    updateSummary(summary) {
        try {
            const currency = isoft_customer_portal.utils.cachedCurrency || 'USD';
            
            // Helper function to safely update element text
            const safeUpdateText = (selector, value) => {
                const element = $(selector);
                if (element && element.length > 0 && element[0]) {
                    try {
                        element.text(value);
                        return true;
                    } catch (e) {
                        return false;
                    }
                }
                return false;
            };
            
            // Helper function to safely update element classes
            const safeUpdateClasses = (selector, classesToRemove, classesToAdd) => {
                const element = $(selector);
                if (element && element.length > 0 && element[0]) {
                    try {
                        if (classesToRemove) {
                            element.removeClass(classesToRemove);
                        }
                        if (classesToAdd) {
                            element.addClass(classesToAdd);
                        }
                        return true;
                    } catch (e) {
                        return false;
                    }
                }
                return false;
            };
            
            // Update summary values
            safeUpdateText('#total-debits', isoft_customer_portal.utils.formatCurrency(summary.total_debits || 0, currency));
            safeUpdateText('#total-credits', isoft_customer_portal.utils.formatCurrency(summary.total_credits || 0, currency));
            
            // Update balance with color coding
            const balance = summary.balance || 0;
            const formattedBalance = isoft_customer_portal.utils.formatCurrency(balance, currency);
            
            // Update balance text
            safeUpdateText('#current-balance', formattedBalance);
            
            // Apply color coding based on balance
            if (balance > 0) {
                // Positive balance - customer owes money (red)
                safeUpdateClasses('#current-balance', 'balance-positive balance-negative balance-zero', 'balance-positive');
                safeUpdateClasses('#balance-card', 'positive negative', 'positive');
            } else if (balance < 0) {
                // Negative balance - customer has credit (green)
                safeUpdateClasses('#current-balance', 'balance-positive balance-negative balance-zero', 'balance-negative');
                safeUpdateClasses('#balance-card', 'positive negative', 'negative');
            } else {
                // Zero balance (gray)
                safeUpdateClasses('#current-balance', 'balance-positive balance-negative balance-zero', 'balance-zero');
                safeUpdateClasses('#balance-card', 'positive negative', null);
            }
            
        } catch (error) {
            // Silent error handling
        }
    }

    applyFilters() {
        const filters = {
            from_date: $('#from-date').val(),
            to_date: $('#to-date').val(),
            voucher_type: $('#voucher-type').val()
        };
        
        // Remove empty filters
        Object.keys(filters).forEach(key => {
            if (!filters[key]) delete filters[key];
        });
        
        this.currentFilters = filters;
        this.saveFilters();
        this.loadLedger(1);
    }

    clearFilters() {
        $('#from-date').val('');
        $('#to-date').val('');
        $('#voucher-type').val('');
        this.currentFilters = {};
        this.loadLedger(1);
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.loadLedger(this.currentPage - 1);
        }
    }

    nextPage() {
        if (this.currentPage < this.totalPages) {
            this.loadLedger(this.currentPage + 1);
        }
    }

    goToPage(page) {
        if (page >= 1 && page <= this.totalPages) {
            this.loadLedger(page);
        }
    }

    goToLastPage() {
        if (this.totalPages > 0) {
            this.loadLedger(this.totalPages);
        }
    }

    changePageSize() {
        const newPageSize = parseInt($('#page-size-select').val());
        
        if (newPageSize !== this.pageSize) {
            this.pageSize = newPageSize;
            this.loadLedger(1); // Reset to first page
        }
    }



    saveFilters() {
        localStorage.setItem('customer_ledger_filters', JSON.stringify(this.currentFilters));
    }

    loadSavedFilters() {
        try {
            const saved = localStorage.getItem('customer_ledger_filters');
            if (saved) {
                this.currentFilters = JSON.parse(saved);
                
                // Apply saved filters to form
                $('#from-date').val(this.currentFilters.from_date || '');
                $('#to-date').val(this.currentFilters.to_date || '');
                $('#voucher-type').val(this.currentFilters.voucher_type || '');
            }
        } catch (e) {
            // Silent error handling
        }
    }

    refreshData() {
        // Add loading state to refresh button
        const refreshBtn = $('.refresh-btn');
        const refreshIcon = refreshBtn.find('i');
        
        // Disable button and add loading animation
        refreshBtn.prop('disabled', true);
        refreshIcon.addClass('refreshing');
        
        // Load data - only call loadLedger as it updates summary automatically
        this.loadLedger(this.currentPage);
        
        // Re-enable button after a short delay
        setTimeout(() => {
            refreshBtn.prop('disabled', false);
            refreshIcon.removeClass('refreshing');
        }, 1000);
    }

    exportExcel() {
        frappe.call({
            method: 'isoft_customer_portal.api.export_ledger_excel',
            args: { filters: JSON.stringify(this.currentFilters) },
            freeze: false,
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
            method: 'isoft_customer_portal.api.export_ledger_pdf',
            args: { filters: JSON.stringify(this.currentFilters) },
            freeze: false,
            callback: (r) => {
                if (r.message && r.message.file_url) {
                    window.open(r.message.file_url, '_blank');
                } else {
                    isoft_customer_portal.utils.showError('Error exporting to PDF');
                }
            }
        });
    }
}; 