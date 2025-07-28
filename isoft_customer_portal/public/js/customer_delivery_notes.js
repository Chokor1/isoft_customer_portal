// Customer Delivery Notes JavaScript
frappe.provide('isoft_customer_portal');

isoft_customer_portal.CustomerDeliveryNotes = class CustomerDeliveryNotes {
    constructor() {
        this.currentPage = 1;
        this.pageLength = 20;
        this.filters = {};
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadDeliveryNotesData();
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

        // Delivery note row clicks
        $(document).on('click', '.delivery-note-row', (e) => {
            const deliveryNoteName = $(e.currentTarget).data('delivery-note');
            this.viewDeliveryNote(deliveryNoteName);
        });
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
        const container = $('#delivery-notes-table tbody');
        container.empty();

        if (data.delivery_notes && data.delivery_notes.length > 0) {
            data.delivery_notes.forEach(deliveryNote => {
                const row = this.createDeliveryNoteRow(deliveryNote);
                container.append(row);
            });
        } else {
            container.html('<tr><td colspan="9" class="text-center">No delivery notes found</td></tr>');
        }

        this.updatePagination(data);
        this.updateSummary(data.summary);
    }

    createDeliveryNoteRow(deliveryNote) {
        const formattedDate = frappe.format_date(deliveryNote.posting_date);
        const formattedAmount = frappe.format_currency(deliveryNote.grand_total);
        const formattedDeliveryDate = deliveryNote.delivery_date ? frappe.format_date(deliveryNote.delivery_date) : '-';
        const statusClass = this.getStatusClass(deliveryNote.status);
        const deliveryTypeClass = this.getDeliveryTypeClass(deliveryNote.delivery_type);

        return `
            <tr class="delivery-note-row" data-delivery-note="${deliveryNote.name}">
                <td>${deliveryNote.name}</td>
                <td>${formattedDate}</td>
                <td>${deliveryNote.customer_name || ''}</td>
                <td class="text-right">${formattedAmount}</td>
                <td><span class="status-badge ${statusClass}">${deliveryNote.status || 'Draft'}</span></td>
                <td><span class="status-badge ${deliveryTypeClass}">${deliveryNote.delivery_type || 'Customer'}</span></td>
                <td>${formattedDeliveryDate}</td>
                <td>${deliveryNote.per_billed || 0}%</td>
                <td>
                    <button class="btn btn-sm btn-primary view-delivery-note-btn" data-delivery-note="${deliveryNote.name}">
                        <i class="fas fa-eye"></i> View
                    </button>
                </td>
            </tr>
        `;
    }

    getStatusClass(status) {
        const statusMap = {
            'Draft': 'status-draft',
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
            $('#total-delivery-notes').text(summary.total_delivery_notes || 0);
            $('#total-amount').text(frappe.format_currency(summary.total_amount || 0));
            $('#pending-billing').text(summary.pending_billing || 0);
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