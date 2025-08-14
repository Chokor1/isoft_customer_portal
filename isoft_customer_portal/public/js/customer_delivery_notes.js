// Customer Delivery Notes JavaScript
frappe.provide('isoft_customer_portal');

isoft_customer_portal.CustomerDeliveryNotes = class CustomerDeliveryNotes {
    constructor() {
        this.currentPage = 1;
        this.pageLength = 10;
        this.filters = {};
        this.init();
    }

    init() {
        // Initialize currency first, then load data
        isoft_customer_portal.utils.getDefaultCurrency().then(() => {
            this.loadDeliveryNotesData();
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
        $('.refresh-btn').on('click', () => this.loadDeliveryNotesData());

        // Removed row click handler - no longer redirects to document
    }

    applyFilters() {
        this.filters = {
            from_date: $('#from-date').val(),
            to_date: $('#to-date').val(),
            status: $('#status').val(),
            min_amount: $('#min-amount').val(),
            max_amount: $('#max-amount').val(),
            delivery_type: $('#delivery-type').val()
        };
        
        this.currentPage = 1;
        this.loadDeliveryNotesData();
    }

    clearFilters() {
        $('#filter-form')[0].reset();
        this.filters = {};
        this.currentPage = 1;
        this.loadDeliveryNotesData();
    }

    loadDeliveryNotesData() {
        this.showLoading();
        
        frappe.call({
            method: 'isoft_customer_portal.api.get_customer_delivery_notes',
            args: {
                filters: this.filters,
                page: this.currentPage,
                page_length: this.pageLength
            },
            callback: (r) => {
                if (r.message) {
                    this.updateDeliveryNotesTable(r.message);
                }
                this.hideLoading();
            }
        });
    }

    updateDeliveryNotesTable(data) {
        const container = $('#delivery-notes-list');
        container.empty();

        if (data.delivery_notes && data.delivery_notes.length > 0) {
            data.delivery_notes.forEach(deliveryNote => {
                const row = this.createDeliveryNoteRow(deliveryNote);
                container.append(row);
            });
        } else {
            container.html('<tr><td colspan="6" class="text-center">No delivery notes found</td></tr>');
        }

        this.updatePagination(data);
        this.updateSummary(data.summary);
    }

    createDeliveryNoteRow(deliveryNote) {
        // Use currency from delivery note data or fallback to cached currency
        const currency = deliveryNote.currency || isoft_customer_portal.utils.cachedCurrency || 'USD';
        
        const formattedDate = isoft_customer_portal.utils.formatDate(deliveryNote.posting_date);
        const formattedAmount = isoft_customer_portal.utils.formatCurrency(deliveryNote.grand_total, currency);
        const statusClass = this.getStatusClass(deliveryNote.status);

        return `
            <tr class="delivery-note-row" data-delivery-note="${deliveryNote.name}">
                <td><strong>${deliveryNote.name}</strong></td>
                <td>${formattedDate}</td>
                <td>${deliveryNote.customer || ''}</td>
                <td><strong>${formattedAmount}</strong></td>
                <td><span class="status-badge ${statusClass}">${deliveryNote.status || 'To Bill'}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary print-btn" onclick="event.stopPropagation(); isoft_customer_portal.printDocument('Delivery Note', '${deliveryNote.name}')" title="Print Delivery Note">
                        <i class="fas fa-print"></i>
                    </button>
                </td>
            </tr>
        `;
    }

    getStatusClass(status) {
        const statusMap = {
            'To Bill': 'status-to-bill',
            'Completed': 'status-completed',
            'Cancelled': 'status-cancelled',
            'Closed': 'status-closed',
            'Return': 'status-return'
        };
        return statusMap[status] || 'status-default';
    }

    getDeliveryTypeClass(deliveryType) {
        const statusMap = {
            'Customer': 'status-customer',
            'Internal': 'status-internal',
            'Subcontractor': 'status-subcontractor'
        };
        return statusMap[deliveryType] || 'status-default';
    }

    updatePagination(data) {
        const pageLength = 10;
        this.totalPages = Math.ceil(data.total / pageLength);
        
        $('#page-info').text(`${((this.currentPage - 1) * pageLength) + 1} to ${Math.min(this.currentPage * pageLength, data.total)}`);
        $('#total-entries').text(data.total);
        $('#current-page').text(this.currentPage);
        $('#total-pages').text(this.totalPages);
        
        $('#prev-page').prop('disabled', this.currentPage <= 1);
        $('#next-page').prop('disabled', this.currentPage >= this.totalPages);
    }

    updateSummary(summary) {
        if (summary) {
            const currency = isoft_customer_portal.utils.cachedCurrency || 'USD';
            
            $('#total-deliveries').text(summary.total_deliveries || 0);
            $('#draft-deliveries').text(summary.draft_deliveries || 0);
            $('#submitted-deliveries').text(summary.submitted_deliveries || 0);
            $('#total-amount').text(isoft_customer_portal.utils.formatCurrency(summary.total_amount || 0, currency));
        }
    }

    goToPage(page) {
        this.currentPage = page;
        this.loadDeliveryNotesData();
        $('html, body').animate({ scrollTop: 0 }, 'slow');
    }

    viewDeliveryNote(deliveryNoteName) {
        // Open delivery note in new window/tab
        const url = `/app/delivery-note/${deliveryNoteName}`;
        window.open(url, '_blank');
    }

    exportExcel() {
        frappe.call({
            method: 'isoft_customer_portal.api.export_delivery_notes_excel',
            args: { filters: this.filters },
            callback: (r) => {
                if (r.message) {
                    const link = document.createElement('a');
                    link.href = r.message;
                    link.download = 'customer_delivery_notes.xlsx';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }
            }
        });
    }

    exportPDF() {
        frappe.call({
            method: 'isoft_customer_portal.api.export_delivery_notes_pdf',
            args: { filters: this.filters },
            callback: (r) => {
                if (r.message) {
                    window.open(r.message, '_blank');
                }
            }
        });
    }

    showLoading() {
        $('.delivery-notes-content').addClass('loading');
    }

    hideLoading() {
        $('.delivery-notes-content').removeClass('loading');
    }
};

// Initialize delivery notes when page loads
$(document).ready(() => {
    new isoft_customer_portal.CustomerDeliveryNotes();
}); 