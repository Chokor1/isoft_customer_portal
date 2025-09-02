// Customer Payment Entries JavaScript
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
        
        // Listen for translation updates
        $(document).on('translationsRefreshed', () => {
            this.translateCardLabels();
        });
    }

    translateCardLabels() {
        // Force translate card labels when language changes
        if (window.IsoftTranslation) {
            const cardLabels = {
                '.summary-label': {
                    'Total Entries': 'Total Entries',
                    'Total Received': 'Total Received', 
                    'Total Allocated Amount': 'Total Allocated Amount',
                    'Unallocated Amount': 'Unallocated Amount'
                }
            };

            Object.keys(cardLabels).forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(element => {
                    const originalText = element.textContent.trim();
                    if (cardLabels[selector][originalText]) {
                        const translationKey = cardLabels[selector][originalText];
                        element.textContent = window.IsoftTranslation.t(translationKey);
                    }
                });
            });
        }
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
        
        console.log('DEBUG: loadPaymentEntries called with page:', page);
        console.log('DEBUG: Current filters:', this.currentFilters);
        console.log('DEBUG: Page size:', this.pageSize);
        
        const tbody = $('#payment-entries-list');
        const loadingText = window.IsoftTranslation ? window.IsoftTranslation.t('Loading...') : 'Loading payment entries...';
        tbody.html(`<tr><td colspan="7" class="loading"><i class="fas fa-spinner fa-spin"></i> ${loadingText}</td></tr>`);
        
        frappe.call({
            method: 'isoft_customer_portal.api.get_customer_payment_entries',
            args: {
                filters: JSON.stringify(this.currentFilters),
                page: page,
                page_length: this.pageSize
            },
            callback: (r) => {
                console.log('DEBUG: API response received:', r);
                console.log('DEBUG: API response message:', r.message);
                
                if (r.message) {
                    console.log('DEBUG: Entries data:', r.message.entries);
                    console.log('DEBUG: Total count:', r.message.total);
                    console.log('DEBUG: Summary data:', r.message.summary);
                    
                    this.displayPaymentEntries(r.message.entries || []);
                    this.updatePagination(r.message.total || 0, page);
                    this.updateSummary(r.message.summary || {});
                } else {
                    console.log('DEBUG: No message in API response');
                }
            },
            error: (err) => {
                console.log('DEBUG: API call error:', err);
            }
        });
    }

    loadSummary() {
        console.log('DEBUG: loadSummary called');
        
        frappe.call({
            method: 'isoft_customer_portal.api.get_customer_payment_entries',
            args: {
                filters: JSON.stringify({}),
                page: 1,
                page_length: 1
            },
            callback: (r) => {
                console.log('DEBUG: loadSummary API response:', r);
                console.log('DEBUG: loadSummary API message:', r.message);
                
                if (r.message && r.message.summary) {
                    console.log('DEBUG: loadSummary summary data:', r.message.summary);
                    this.updateSummary(r.message.summary);
                } else {
                    console.log('DEBUG: loadSummary - no summary data found');
                }
            },
            error: (err) => {
                console.log('DEBUG: loadSummary API error:', err);
            }
        });
    }

    displayPaymentEntries(entries) {
        const tbody = $('#payment-entries-list');
        
        if (entries.length === 0) {
            const noDataText = window.IsoftTranslation ? window.IsoftTranslation.t('No data available') : 'No payment entries found';
            tbody.html(`<tr><td colspan="8" class="no-data">${noDataText}</td></tr>`);
            return;
        }
        
        tbody.empty();
        
        entries.forEach(entry => {
            // Use currency from entry data or fallback to cached currency
            const currency = entry.currency || isoft_customer_portal.utils.cachedCurrency || 'AKZ';
            
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
                        <button class="btn btn-sm btn-outline-primary print-btn" onclick="event.stopPropagation(); window.safePrintDocument('Payment Entry', '${entry.name}')" title="Print Payment Entry">
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
        console.log('DEBUG: updateSummary called with:', summary);
        
        const currency = isoft_customer_portal.utils.cachedCurrency || 'AKZ';
        console.log('DEBUG: Using currency:', currency);
        
        // Helper function to update element and make it visible
        const updateElement = (selector, value) => {
            console.log(`DEBUG: Updating element ${selector} with value:`, value);
            const element = $(selector);
            if (element.length) {
                console.log(`DEBUG: Element ${selector} found, updating...`);
                element.text(value);
                // Mark as updated to prevent dashboard animations from hiding it
                element.attr('data-summary-updated', 'true');
                element.css({
                    'opacity': '1',
                    'transform': 'translateY(0)',
                    'transition': 'all 0.6s ease-out'
                });
                console.log(`DEBUG: Element ${selector} updated successfully`);
            } else {
                console.log(`DEBUG: Element ${selector} NOT FOUND!`);
            }
        };
        
        // Update all summary elements
        console.log('DEBUG: Updating total entries:', summary.total_entries || 0);
        updateElement('#total-entries', summary.total_entries || 0);
        
        console.log('DEBUG: Updating total received:', summary.total_received || 0);
        updateElement('#total-received', isoft_customer_portal.utils.formatCurrency(summary.total_received || 0, currency));
        
        console.log('DEBUG: Updating total allocated:', summary.total_allocated_amount || 0);
        updateElement('#total-allocated', isoft_customer_portal.utils.formatCurrency(summary.total_allocated_amount || 0, currency));
        
        console.log('DEBUG: Updating unallocated amount:', summary.unallocated_amount || 0);
        updateElement('#unallocated-amount', isoft_customer_portal.utils.formatCurrency(summary.unallocated_amount || 0, currency));

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