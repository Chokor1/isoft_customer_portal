import frappe
from frappe import _
from frappe.utils import getdate, today, add_days, formatdate
from frappe.utils.file_manager import save_file
import json
import pandas as pd
from datetime import datetime, timedelta
from .auth import check_customer_auth, get_customer_from_user, validate_customer_access

def validate_date_format(date_str):
    """Validate and format date string with multiple format support"""
    try:
        if not date_str:
            return None
        
        # Try different date formats
        date_formats = [
            '%Y-%m-%d',      # 2024-01-01
            '%m/%d/%Y',      # 01/01/2024
            '%d/%m/%Y',      # 01/01/2024 (European)
            '%Y-%m-%d %H:%M:%S',  # 2024-01-01 00:00:00
        ]
        
        from datetime import datetime
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(str(date_str), fmt)
                formatted_date = date_obj.strftime('%Y-%m-%d')
                return formatted_date
            except ValueError:
                continue
        
        # If none of the formats work, try Frappe's getdate
        try:
            date_obj = getdate(date_str)
            formatted_date = date_obj.strftime('%Y-%m-%d')
            return formatted_date
        except Exception:
            return None
            
    except Exception:
        return None

def validate_date_range(from_date, to_date):
    """Validate date range - ensure from_date is not after to_date"""
    try:
        if from_date and to_date:
            from_dt = getdate(from_date)
            to_dt = getdate(to_date)
            if from_dt > to_dt:
                return False, "From date cannot be after to date"
        return True, None
    except Exception:
        return False, "Invalid date format"

def build_date_filter(filters, date_field):
    """Build date filter with proper validation"""
    if not filters:
        return {}
    
    from_date = validate_date_format(filters.get('from_date'))
    to_date = validate_date_format(filters.get('to_date'))
    
    # Validate date range
    if from_date and to_date:
        is_valid, error_msg = validate_date_range(from_date, to_date)
        if not is_valid:
            frappe.log_error(f"Date validation error: {error_msg}")
            return {}
    
    query_filters = {}
    
    if from_date and to_date:
        query_filters[date_field] = ['between', [from_date, to_date]]
    elif from_date:
        query_filters[date_field] = [">=", from_date]
    elif to_date:
        query_filters[date_field] = ["<=", to_date]
    
    return query_filters

def get_company_currency():
    """Get the default currency for the current company using ERPNext method"""
    try:
        from erpnext import get_default_currency
        return get_default_currency() or 'USD'
    except ImportError:
        # Fallback if ERPNext is not available
        try:
            company = frappe.defaults.get_global_default('company')
            if company:
                return frappe.db.get_value('Company', company, 'default_currency') or 'USD'
            return 'USD'
        except Exception:
            return 'USD'

@frappe.whitelist(allow_guest=True)
def get_company_currency_api():
    """API method to get company currency"""
    try:
        currency = get_company_currency()
        return currency
    except Exception as e:
        frappe.log_error(f"Error in get_company_currency_api: {str(e)}")
        return 'USD'

@frappe.whitelist(allow_guest=True)
def get_customer_name():
    """API method to get customer name for current user"""
    try:
        # Check authentication
        if not check_customer_auth():
            return "Guest"
        
        customer = get_customer_from_user()
        if customer:
            return customer
        return "Customer"
    except Exception as e:
        frappe.log_error(f"Error in get_customer_name: {str(e)}")
        return "Customer"

def get_total_invoices(customer):
    """Get total number of invoices for customer"""
    try:
        return frappe.db.count("Sales Invoice", {"customer": customer, "docstatus": ["!=", 2]})
    except:
        return 0

def get_total_quotations(customer):
    """Get total number of quotations for customer"""
    try:
        return frappe.db.count("Quotation", {"party_name": customer, "docstatus": ["!=", 2]})
    except:
        return 0

def get_total_deliveries(customer):
    """Get total number of delivery notes for customer"""
    try:
        return frappe.db.count("Delivery Note", {"customer": customer, "docstatus": ["!=", 2]})
    except:
        return 0

def get_total_sales_orders(customer):
    """Get total number of sales orders for customer"""
    try:
        return frappe.db.count("Sales Order", {"customer": customer, "docstatus": ["!=", 2]})
    except:
        return 0

def get_total_payments(customer):
    """Get total number of payment entries for customer"""
    try:
        return frappe.db.count("Payment Entry", {"party_name": customer, "docstatus": ["!=", 2]})
    except:
        return 0

def get_outstanding_amount(customer):
    """Get outstanding amount for customer"""
    try:
        outstanding = frappe.db.sql("""
            SELECT COALESCE(SUM(outstanding_amount), 0)
            FROM `tabSales Invoice`
            WHERE customer = %s AND docstatus = 1 AND outstanding_amount > 0
        """, customer)
        
        return outstanding[0][0] if outstanding else 0
    except:
        return 0

def get_ledger_summary(customer, filters=None):
    """Get ledger summary for customer"""
    try:
        query_filters = {"party": customer}
        
        # Add date filters with validation
        date_filters = build_date_filter(filters, "posting_date")
        query_filters.update(date_filters)
        
        # Use frappe.get_all to get the summary with proper filters
        entries = frappe.get_all(
            "GL Entry",
            filters=query_filters,
            fields=["debit", "credit"]
        )
        
        total_debits = sum(entry.get('debit', 0) or 0 for entry in entries)
        total_credits = sum(entry.get('credit', 0) or 0 for entry in entries)
        balance = total_debits - total_credits
        
        return {
            'total_debits': total_debits,
            'total_credits': total_credits,
            'balance': balance
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_ledger_summary: {str(e)}")
        return {'total_debits': 0, 'total_credits': 0, 'balance': 0}

def get_invoices_summary(customer, filters=None):
    """Get invoices summary for customer"""
    try:
        query_filters = {"customer": customer, "docstatus": ["!=", 2]}
        
        # Add date filters with validation
        date_filters = build_date_filter(filters, "posting_date")
        query_filters.update(date_filters)
        
        if filters and filters.get('status'):
            query_filters["status"] = filters.get('status')
        
        result = frappe.db.sql("""
            SELECT 
                COUNT(*) as total_invoices,
                COALESCE(SUM(grand_total), 0) as total_amount,
                COALESCE(SUM(outstanding_amount), 0) as total_outstanding,
                COUNT(CASE WHEN status = 'Paid' THEN 1 END) as paid_invoices,
                COUNT(CASE WHEN status = 'Unpaid' THEN 1 END) as unpaid_invoices
            FROM `tabSales Invoice`
            WHERE customer = %s AND docstatus != 2
        """, customer)
        
        if result:
            return {
                'total_invoices': result[0][0] or 0,
                'total_amount': result[0][1] or 0,
                'total_outstanding': result[0][2] or 0,
                'paid_invoices': result[0][3] or 0,
                'unpaid_invoices': result[0][4] or 0
            }
        
        return {'total_invoices': 0, 'total_amount': 0, 'total_outstanding': 0, 'paid_invoices': 0, 'unpaid_invoices': 0}
        
    except Exception as e:
        frappe.log_error(f"Error in get_invoices_summary: {str(e)}")
        return {'total_invoices': 0, 'total_amount': 0, 'total_outstanding': 0, 'paid_invoices': 0, 'unpaid_invoices': 0}

def get_quotations_summary(customer, filters=None):
    """Get quotations summary for customer"""
    try:
        query_filters = {"party_name": customer, "docstatus": ["!=", 2]}
        
        # Add date filters with validation
        date_filters = build_date_filter(filters, "transaction_date")
        query_filters.update(date_filters)
        
        if filters and filters.get('status'):
            query_filters["status"] = filters.get('status')
        
        result = frappe.db.sql("""
            SELECT 
                COUNT(*) as total_quotations,
                COALESCE(SUM(grand_total), 0) as total_amount,
                COUNT(CASE WHEN status = 'Draft' THEN 1 END) as draft_quotations,
                COUNT(CASE WHEN status = 'Submitted' THEN 1 END) as submitted_quotations
            FROM `tabQuotation`
            WHERE party_name = %s AND docstatus != 2
        """, customer)
        
        if result:
            return {
                'total_quotations': result[0][0] or 0,
                'total_amount': result[0][1] or 0,
                'draft_quotations': result[0][2] or 0,
                'submitted_quotations': result[0][3] or 0
            }
        
        return {'total_quotations': 0, 'total_amount': 0, 'draft_quotations': 0, 'submitted_quotations': 0}
        
    except Exception as e:
        frappe.log_error(f"Error in get_quotations_summary: {str(e)}")
        return {'total_quotations': 0, 'total_amount': 0, 'draft_quotations': 0, 'submitted_quotations': 0}

def get_sales_orders_summary(customer, filters=None):
    """Get sales orders summary for customer"""
    try:
        query_filters = {"customer": customer, "docstatus": ["!=", 2]}
        
        # Add date filters with validation
        date_filters = build_date_filter(filters, "transaction_date")
        query_filters.update(date_filters)
        
        if filters and filters.get('status'):
            query_filters["status"] = filters.get('status')
        
        result = frappe.db.sql("""
            SELECT 
                COUNT(*) as total_orders,
                COALESCE(SUM(grand_total), 0) as total_amount,
                COUNT(CASE WHEN status = 'Draft' THEN 1 END) as draft_orders,
                COUNT(CASE WHEN status = 'Submitted' THEN 1 END) as submitted_orders
            FROM `tabSales Order`
            WHERE customer = %s AND docstatus != 2
        """, customer)
        
        if result:
            return {
                'total_orders': result[0][0] or 0,
                'total_amount': result[0][1] or 0,
                'draft_orders': result[0][2] or 0,
                'submitted_orders': result[0][3] or 0
            }
        
        return {'total_orders': 0, 'total_amount': 0, 'draft_orders': 0, 'submitted_orders': 0}
        
    except Exception as e:
        frappe.log_error(f"Error in get_sales_orders_summary: {str(e)}")
        return {'total_orders': 0, 'total_amount': 0, 'draft_orders': 0, 'submitted_orders': 0}

def get_delivery_notes_summary(customer, filters=None):
    """Get delivery notes summary for customer"""
    try:
        query_filters = {"customer": customer, "docstatus": ["!=", 2]}
        
        # Add date filters with validation
        date_filters = build_date_filter(filters, "posting_date")
        query_filters.update(date_filters)
        
        if filters and filters.get('status'):
            query_filters["status"] = filters.get('status')
        
        result = frappe.db.sql("""
            SELECT 
                COUNT(*) as total_deliveries,
                COALESCE(SUM(grand_total), 0) as total_amount,
                COUNT(CASE WHEN status = 'Draft' THEN 1 END) as draft_deliveries,
                COUNT(CASE WHEN status = 'Submitted' THEN 1 END) as submitted_deliveries
            FROM `tabDelivery Note`
            WHERE customer = %s AND docstatus != 2
        """, customer)
        
        if result:
            return {
                'total_deliveries': result[0][0] or 0,
                'total_amount': result[0][1] or 0,
                'draft_deliveries': result[0][2] or 0,
                'submitted_deliveries': result[0][3] or 0
            }
        
        return {'total_deliveries': 0, 'total_amount': 0, 'draft_deliveries': 0, 'submitted_deliveries': 0}
        
    except Exception as e:
        frappe.log_error(f"Error in get_delivery_notes_summary: {str(e)}")
        return {'total_deliveries': 0, 'total_amount': 0, 'draft_deliveries': 0, 'submitted_deliveries': 0}


@frappe.whitelist(allow_guest=True)
def get_dashboard_statistics():
    """Get dashboard statistics for the current customer"""
    try:
        # Check authentication
        if not check_customer_auth():
            return {"error": "Authentication required"}
        
        customer = get_customer_from_user()
        if not customer:
            return {"error": "No customer linked to account"}
        
        stats = {
            'total_invoices': get_total_invoices(customer),
            'total_quotations': get_total_quotations(customer),
            'total_deliveries': get_total_deliveries(customer),
            'total_sales_orders': get_total_sales_orders(customer),
            'total_payments': get_total_payments(customer),
            'outstanding_amount': get_outstanding_amount(customer)
        }
        
        return stats
    except Exception as e:
        frappe.log_error(f"Error in get_dashboard_statistics: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=True)
def get_recent_transactions(limit=10):
    """Get recent transactions for the current customer"""
    try:
        # Convert limit to integer (JavaScript might pass it as string)
        try:
            limit = int(limit)
        except (ValueError, TypeError):
            limit = 10
        
        customer = get_customer_from_user()
        if not customer:
            return []
        
        transactions = []
        
        # Get recent invoices
        invoices = frappe.get_all(
            "Sales Invoice",
            filters={"customer": customer, "docstatus": ["!=", 2]},
            fields=["name", "posting_date", "grand_total", "status", "outstanding_amount"],
            order_by="posting_date desc",
            limit=limit
        )
        
        for invoice in invoices:
            transactions.append({
                'date': invoice.posting_date,
                'type': 'Sales Invoice',
                'reference': invoice.name,
                'amount': invoice.grand_total,
                'status': invoice.status or 'Draft'
            })

        # Get recent quotations
        quotations = frappe.get_all(
            "Quotation",
            filters={"party_name": customer, "docstatus": ["!=", 2]},
            fields=["name", "transaction_date", "grand_total", "status"],
            order_by="transaction_date desc",
            limit=limit
        )
        
        for quotation in quotations:
            transactions.append({
                'date': quotation.transaction_date,
                'type': 'Quotation',
                'reference': quotation.name,
                'amount': quotation.grand_total,
                'status': quotation.status or 'Draft'
            })
        
        # Get recent sales orders
        sales_orders = frappe.get_all(
            "Sales Order",
            filters={"customer": customer, "docstatus": ["!=", 2]},
            fields=["name", "transaction_date", "grand_total", "status"],
            order_by="transaction_date desc",
            limit=limit
        )
        
        for so in sales_orders:
            transactions.append({
                'date': so.transaction_date,
                'type': 'Sales Order',
                'reference': so.name,
                'amount': so.grand_total,
                'status': so.status or 'Draft'
            })
        
        # Get recent delivery notes
        delivery_notes = frappe.get_all(
            "Delivery Note",
            filters={"customer": customer, "docstatus": ["!=", 2]},
            fields=["name", "posting_date", "grand_total", "status"],
            order_by="posting_date desc",
            limit=limit
        )
        
        for dn in delivery_notes:
            transactions.append({
                'date': dn.posting_date,
                'type': 'Delivery Note',
                'reference': dn.name,
                'amount': dn.grand_total,
                'status': dn.status or 'Draft'
            })
        
        # Get recent payment entries
        payment_entries = frappe.get_all(
            "Payment Entry",
            filters={"party_name": customer, "docstatus": ["!=", 2]},
            fields=["name", "posting_date", "paid_amount", "payment_type", "status"],
            order_by="posting_date desc",
            limit=limit
        )
        
        for payment in payment_entries:
            transactions.append({
                'date': payment.posting_date,
                'type': 'Payment Entry',
                'reference': payment.name,
                'amount': payment.paid_amount,
                'status': payment.status or 'Draft',
                'payment_type': payment.payment_type
            })
        
        # Sort by date and return top limit
        transactions.sort(key=lambda x: x['date'], reverse=True)
        
        # Return limited transactions (Python 3.8 compatible)
        limited_transactions = []
        for i, transaction in enumerate(transactions):
            if i >= limit:
                break
            limited_transactions.append(transaction)
        
        return limited_transactions
        
    except Exception as e:
        frappe.log_error(f"Error in get_recent_transactions: {str(e)}")
        return []

@frappe.whitelist(allow_guest=True)
def get_customer_ledger(filters=None, page=1, page_length=10):
    """Get customer ledger entries"""
    try:
        # Convert parameters to integers (JavaScript might pass them as strings)
        try:
            page = int(page)
        except (ValueError, TypeError):
            page = 1
            
        try:
            page_length = int(page_length)
        except (ValueError, TypeError):
            page_length = 10
        
        customer = get_customer_from_user()
        
        if not customer:
            return {"entries": [], "total": 0, "summary": {}}
        
        if filters:
            if isinstance(filters, str):
                filters = json.loads(filters)
        else:
            filters = {}
        
        # Build query filters
        query_filters = {"party": customer}
        
        # Add date filters with validation
        date_filters = build_date_filter(filters, "posting_date")
        query_filters.update(date_filters)
        
        # Get total count
        total = frappe.db.count("GL Entry", query_filters)
        
        # Get entries with pagination
        start_index = (page - 1) * page_length
        
        entries = frappe.get_all(
            "GL Entry",
            filters=query_filters,
            fields=["name", "posting_date", "voucher_type", "voucher_no", "debit", "credit", "debit_in_account_currency", "credit_in_account_currency", "account_currency", "remarks"],
            order_by="posting_date desc, creation desc",
            start=start_index,
            page_length=page_length
        )
        
        # Add currency to each entry
        currency = get_company_currency()
        for entry in entries:
            entry['currency'] = currency
        
        # Get summary
        summary = get_ledger_summary(customer, filters)
        
        return {
            "entries": entries,
            "total": total,
            "summary": summary
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_customer_ledger: {str(e)}")
        return {"entries": [], "total": 0, "summary": {}}

@frappe.whitelist(allow_guest=True)
def get_customer_invoices(filters=None, page=1, page_length=10):
    """Get customer invoices"""
    try:
        # Convert parameters to integers (JavaScript might pass them as strings)
        try:
            page = int(page)
        except (ValueError, TypeError):
            page = 1
            
        try:
            page_length = int(page_length)
        except (ValueError, TypeError):
            page_length = 10
        
        customer = get_customer_from_user()
        if not customer:
            return {"invoices": [], "total": 0, "summary": {}}
        
        if filters:
            filters = json.loads(filters)
        else:
            filters = {}
        
        # Build query filters
        query_filters = {"customer": customer, "docstatus": ["!=", 2]}
        
        # Add date filters with validation
        date_filters = build_date_filter(filters, "posting_date")
        query_filters.update(date_filters)
        
        if filters.get('status'):
            query_filters["status"] = filters.get('status')
        
        # Get total count
        total = frappe.db.count("Sales Invoice", query_filters)
        
        # Get invoices with pagination
        start_index = (page - 1) * page_length
        
        invoices = frappe.get_all(
            "Sales Invoice",
            filters=query_filters,
            fields=["name", "posting_date", "due_date", "grand_total", "outstanding_amount", "status", "currency"],
            order_by="posting_date desc",
            start=start_index,
            page_length=page_length
        )
        
        # Calculate paid amount for each invoice
        for invoice in invoices:
            invoice['paid_amount'] = invoice['grand_total'] - invoice['outstanding_amount']
            # Ensure currency is set
            if not invoice.get('currency'):
                invoice['currency'] = get_company_currency()
        
        # Get summary
        summary = get_invoices_summary(customer, filters)
        
        return {
            "invoices": invoices,
            "total": total,
            "summary": summary
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_customer_invoices: {str(e)}")
        return {"invoices": [], "total": 0, "summary": {}}

@frappe.whitelist(allow_guest=True)
def get_customer_quotations(filters=None, page=1, page_length=10):
    """Get customer quotations"""
    try:
        # Convert parameters to integers (JavaScript might pass them as strings)
        try:
            page = int(page)
        except (ValueError, TypeError):
            page = 1
            
        try:
            page_length = int(page_length)
        except (ValueError, TypeError):
            page_length = 10
        
        customer = get_customer_from_user()
        if not customer:
            return {"quotations": [], "total": 0, "summary": {}}
        
        if filters:
            filters = json.loads(filters)
        else:
            filters = {}
        
        # Build query filters
        query_filters = {"party_name": customer, "docstatus": ["!=", 2]}
        
        # Add date filters with validation
        date_filters = build_date_filter(filters, "transaction_date")
        query_filters.update(date_filters)
        
        if filters.get('status'):
            query_filters["status"] = filters.get('status')
        
        # Get total count
        total = frappe.db.count("Quotation", query_filters)
        
        # Get quotations with pagination
        quotations = frappe.get_all(
            "Quotation",
            filters=query_filters,
            fields=["name", "transaction_date", "valid_till", "grand_total", "status", "currency"],
            order_by="transaction_date desc",
            start=(page - 1) * page_length,
            page_length=page_length
        )
        
        # Ensure currency is set for each quotation
        for quotation in quotations:
            if not quotation.get('currency'):
                quotation['currency'] = get_company_currency()
        
        # Get summary
        summary = get_quotations_summary(customer, filters)
        
        return {
            "quotations": quotations,
            "total": total,
            "summary": summary
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_customer_quotations: {str(e)}")
        return {"quotations": [], "total": 0, "summary": {}}

@frappe.whitelist(allow_guest=True)
def get_customer_delivery_notes(filters=None, page=1, page_length=10):
    """Get customer delivery notes"""
    try:
        # Convert parameters to integers (JavaScript might pass them as strings)
        try:
            page = int(page)
        except (ValueError, TypeError):
            page = 1
            
        try:
            page_length = int(page_length)
        except (ValueError, TypeError):
            page_length = 10
        
        customer = get_customer_from_user()
        if not customer:
            return {"delivery_notes": [], "total": 0, "summary": {}}
        
        if filters:
            filters = json.loads(filters)
        else:
            filters = {}
        
        # Build query filters
        query_filters = {"customer": customer, "docstatus": ["!=", 2]}
        
        # Add date filters with validation
        date_filters = build_date_filter(filters, "posting_date")
        query_filters.update(date_filters)
        
        if filters.get('status'):
            query_filters["status"] = filters.get('status')
        
        frappe.log_error(f"Delivery notes query - Customer: {customer}, Filters: {query_filters}")
        
        # Get total count
        total = frappe.db.count("Delivery Note", query_filters)
        
        # Get delivery notes with pagination
        delivery_notes = frappe.get_all(
            "Delivery Note",
            filters=query_filters,
            fields=["name", "posting_date", "customer", "grand_total", "status", "currency"],
            order_by="posting_date desc",
            start=(page - 1) * page_length,
            page_length=page_length
        )
        
        frappe.log_error(f"Delivery notes found - Count: {len(delivery_notes)}, Notes: {delivery_notes}")
        
        # Ensure currency is set for each delivery note
        for delivery_note in delivery_notes:
            if not delivery_note.get('currency'):
                delivery_note['currency'] = get_company_currency()
        
        # Get summary
        summary = get_delivery_notes_summary(customer, filters)
        
        return {
            "delivery_notes": delivery_notes,
            "total": total,
            "summary": summary
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_customer_delivery_notes: {str(e)}")
        return {"delivery_notes": [], "total": 0, "summary": {}}

@frappe.whitelist(allow_guest=True)
def get_customer_sales_orders(filters=None, page=1, page_length=10):
    """Get customer sales orders"""
    try:
        # Convert parameters to integers (JavaScript might pass them as strings)
        try:
            page = int(page)
        except (ValueError, TypeError):
            page = 1
            
        try:
            page_length = int(page_length)
        except (ValueError, TypeError):
            page_length = 10
        
        customer = get_customer_from_user()
        if not customer:
            return {"sales_orders": [], "total": 0, "summary": {}}
        
        if filters:
            filters = json.loads(filters)
        else:
            filters = {}
        
        # Build query filters
        query_filters = {"customer": customer, "docstatus": ["!=", 2]}
        
        # Add date filters with validation
        date_filters = build_date_filter(filters, "transaction_date")
        query_filters.update(date_filters)
        
        if filters.get('status'):
            query_filters["status"] = filters.get('status')
        
        # Get total count
        total = frappe.db.count("Sales Order", query_filters)
        
        # Get sales orders with pagination
        sales_orders = frappe.get_all(
            "Sales Order",
            filters=query_filters,
            fields=["name", "transaction_date", "delivery_date", "grand_total", "status", "currency"],
            order_by="transaction_date desc",
            start=(page - 1) * page_length,
            page_length=page_length
        )
        
        # Ensure currency is set for each sales order
        for sales_order in sales_orders:
            if not sales_order.get('currency'):
                sales_order['currency'] = get_company_currency()
        
        # Get summary
        summary = get_sales_orders_summary(customer, filters)
        
        return {
            "sales_orders": sales_orders,
            "total": total,
            "summary": summary
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_customer_sales_orders: {str(e)}")
        return {"sales_orders": [], "total": 0, "summary": {}}

@frappe.whitelist(allow_guest=True)
def export_ledger_excel(filters=None):
    """Export ledger to Excel"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Authentication required"}
        
        if filters:
            filters = json.loads(filters)
        else:
            filters = {}
        
        # Build query filters
        query_filters = {"party": customer}
        
        # Add date filters with validation
        date_filters = build_date_filter(filters, "posting_date")
        query_filters.update(date_filters)
        
        # Get all entries
        entries = frappe.get_all(
            "GL Entry",
            filters=query_filters,
            fields=["posting_date", "voucher_type", "voucher_no", "debit", "credit", "remarks"],
            order_by="posting_date desc, creation desc"
        )
        
        # Create DataFrame
        df = pd.DataFrame(entries)
        
        # Add running balance
        running_balance = 0
        balance_column = []
        for _, row in df.iterrows():
            running_balance += (row['debit'] or 0) - (row['credit'] or 0)
            balance_column.append(running_balance)
        
        df['Balance'] = balance_column
        
        # Format dates
        df['posting_date'] = pd.to_datetime(df['posting_date']).dt.strftime('%Y-%m-%d')
        
        # Save to Excel
        filename = f"customer_ledger_{customer}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = f"/tmp/{filename}"
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Ledger', index=False)
        
        # Save file to Frappe
        with open(file_path, 'rb') as f:
            file_doc = save_file(filename, f.read(), None, None, is_private=1)
        
        return {"file_url": file_doc.file_url}
        
    except Exception as e:
        frappe.log_error(f"Error in export_ledger_excel: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=True)
def export_ledger_pdf(filters=None):
    """Export ledger to PDF"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Authentication required"}
        
        if filters:
            filters = json.loads(filters)
        else:
            filters = {}
        
        # Build query filters
        query_filters = {"party": customer}
        
        # Add date filters with validation
        date_filters = build_date_filter(filters, "posting_date")
        query_filters.update(date_filters)
        
        # Get all entries
        entries = frappe.get_all(
            "GL Entry",
            filters=query_filters,
            fields=["posting_date", "voucher_type", "voucher_no", "debit", "credit", "remarks"],
            order_by="posting_date desc, creation desc"
        )
        
        # Create HTML content
        html_content = f"""
        <html>
        <head>
            <title>Customer Ledger - {customer}</title>
            <style>
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Customer Ledger - {customer}</h1>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Reference</th>
                        <th>Description</th>
                        <th>Debit</th>
                        <th>Credit</th>
                        <th>Balance</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        running_balance = 0
        for entry in entries:
            running_balance += (entry.debit or 0) - (entry.credit or 0)
            html_content += f"""
                <tr>
                    <td>{entry.posting_date}</td>
                    <td>{entry.voucher_no}</td>
                    <td>{entry.remarks or '-'}</td>
                    <td>{entry.debit or 0}</td>
                    <td>{entry.credit or 0}</td>
                    <td>{running_balance}</td>
                </tr>
            """
        
        html_content += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        # Save to PDF
        filename = f"customer_ledger_{customer}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = f"/tmp/{filename}"
        
        # For now, save as HTML (you can convert to PDF later)
        with open(file_path, 'w') as f:
            f.write(html_content)
        
        # Save file to Frappe
        with open(file_path, 'rb') as f:
            file_doc = save_file(filename, f.read(), None, None, is_private=1)
        
        return {"file_url": file_doc.file_url}
        
    except Exception as e:
        frappe.log_error(f"Error in export_ledger_pdf: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=True)
def get_customer_payment_entries(filters=None, page=1, page_length=10):
    """Get customer payment entries"""
    try:
        # Convert parameters to integers
        try:
            page = int(page)
        except (ValueError, TypeError):
            page = 1
            
        try:
            page_length = int(page_length)
        except (ValueError, TypeError):
            page_length = 10
        
        customer = get_customer_from_user()
        if not customer:
            return {"entries": [], "total": 0, "summary": {}}
        
        if filters:
            filters = json.loads(filters)
        else:
            filters = {}
        
        # Build query filters
        query_filters = {"party": customer, "party_type": "Customer", "docstatus": ["!=", 2]}
        
        # Add date filters with validation
        date_filters = build_date_filter(filters, "posting_date")
        query_filters.update(date_filters)
        
        if filters.get('payment_type'):
            query_filters["payment_type"] = filters.get('payment_type')
        
        # Get total count
        total = frappe.db.count("Payment Entry", query_filters)
        
        # Get payment entries with pagination
        entries = frappe.get_all(
            "Payment Entry",
            filters=query_filters,
            fields=[
                "name", "posting_date", "payment_type", "mode_of_payment", 
                "paid_amount", "received_amount", "reference_no", "reference_date",
                "source_exchange_rate", "target_exchange_rate", "total_allocated_amount",
                "unallocated_amount", "status", "remarks"
            ],
            order_by="posting_date desc, creation desc",
            start=(page - 1) * page_length,
            page_length=page_length
        )
        
        # Add currency information
        currency = get_company_currency()
        for entry in entries:
            entry['currency'] = currency
            # Calculate net amount (for display purposes)
            if entry['payment_type'] == 'Receive':
                entry['net_amount'] = entry['received_amount']
            else:
                entry['net_amount'] = entry['paid_amount']
        
        # Get summary
        summary = get_payment_entries_summary(customer, filters)
        
        return {
            "entries": entries,
            "total": total,
            "summary": summary
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_customer_payment_entries: {str(e)}")
        return {"entries": [], "total": 0, "summary": {}}

def get_payment_entries_summary(customer, filters=None):
    """Get payment entries summary for customer"""
    try:
        # Build base filters
        base_filters = {"party": customer, "party_type": "Customer", "docstatus": ["!=", 2]}
        
        # Add date filters with validation
        date_filters = build_date_filter(filters, "posting_date")
        base_filters.update(date_filters)
        
        # Get payment entries statistics
        total_entries = frappe.db.count("Payment Entry", base_filters)
        
        # Get total received amount
        received_filters = base_filters.copy()
        received_filters["payment_type"] = "Receive"
        total_received = frappe.db.sql("""
            SELECT SUM(received_amount) 
            FROM `tabPayment Entry` 
            WHERE party = %s AND party_type = 'Customer' AND payment_type = 'Receive' 
            AND docstatus != 2
        """, [customer])[0][0] or 0
        
        # Get total paid amount (refunds, etc.)
        paid_filters = base_filters.copy()
        paid_filters["payment_type"] = "Pay"
        total_paid = frappe.db.sql("""
            SELECT SUM(paid_amount) 
            FROM `tabPayment Entry` 
            WHERE party = %s AND party_type = 'Customer' AND payment_type = 'Pay' 
            AND docstatus != 2
        """, [customer])[0][0] or 0
        
        return {
            "total_entries": total_entries,
            "total_received": total_received,
            "total_paid": total_paid,
            "net_amount": total_received - total_paid
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_payment_entries_summary: {str(e)}")
        return {
            "total_entries": 0,
            "total_received": 0,
            "total_paid": 0,
            "net_amount": 0
        }

@frappe.whitelist(allow_guest=True)
def export_payment_entries_excel(filters=None):
    """Export payment entries to Excel"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Customer not found"}
        
        if filters:
            filters = json.loads(filters)
        else:
            filters = {}
        
        # Get all payment entries (no pagination for export)
        result = get_customer_payment_entries(filters, page=1, page_length=1000)
        entries = result.get('entries', [])
        
        if not entries:
            return {"error": "No payment entries found"}
        
        # Create DataFrame
        df_data = []
        for entry in entries:
            df_data.append({
                'Payment Entry': entry['name'],
                'Date': entry['posting_date'],
                'Type': entry['payment_type'],
                'Mode of Payment': entry['mode_of_payment'] or '',
                'Reference No': entry['reference_no'] or '',
                'Reference Date': entry['reference_date'] or '',
                'Amount': entry['net_amount'],
                'Status': entry['status'] or 'Draft',
                'Remarks': entry['remarks'] or ''
            })
        
        df = pd.DataFrame(df_data)
        
        # Save to Excel
        filename = f"customer_payment_entries_{customer}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = f"/tmp/{filename}"
        df.to_excel(file_path, index=False)
        
        # Save file to Frappe
        with open(file_path, 'rb') as f:
            file_doc = save_file(filename, f.read(), None, None, is_private=1)
        
        return {"file_url": file_doc.file_url}
        
    except Exception as e:
        frappe.log_error(f"Error in export_payment_entries_excel: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=True)
def export_invoices_excel(filters=None):
    """Export invoices to Excel"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Authentication required"}
        
        if filters:
            filters = json.loads(filters)
        else:
            filters = {}
        
        # Get all invoices (no pagination for export)
        result = get_customer_invoices(filters, page=1, page_length=1000)
        invoices = result.get('invoices', [])
        
        if not invoices:
            return {"error": "No invoices found"}
        
        # Create DataFrame
        df_data = []
        for invoice in invoices:
            df_data.append({
                'Invoice': invoice['name'],
                'Date': invoice['posting_date'],
                'Due Date': invoice['due_date'],
                'Amount': invoice['grand_total'],
                'Outstanding': invoice['outstanding_amount'],
                'Status': invoice['status']
            })
        
        df = pd.DataFrame(df_data)
        
        # Save to Excel
        filename = f"customer_invoices_{customer}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = f"/tmp/{filename}"
        df.to_excel(file_path, index=False)
        
        # Save file to Frappe
        with open(file_path, 'rb') as f:
            file_doc = save_file(filename, f.read(), None, None, is_private=1)
        
        return {"file_url": file_doc.file_url}
        
    except Exception as e:
        frappe.log_error(f"Error in export_invoices_excel: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=True)
def export_quotations_excel(filters=None):
    """Export quotations to Excel"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Authentication required"}
        
        if filters:
            filters = json.loads(filters)
        else:
            filters = {}
        
        # Get all quotations (no pagination for export)
        result = get_customer_quotations(filters, page=1, page_length=1000)
        quotations = result.get('quotations', [])
        
        if not quotations:
            return {"error": "No quotations found"}
        
        # Create DataFrame
        df_data = []
        for quotation in quotations:
            df_data.append({
                'Quotation': quotation['name'],
                'Date': quotation['transaction_date'],
                'Valid Till': quotation['valid_till'],
                'Amount': quotation['grand_total'],
                'Status': quotation['status']
            })
        
        df = pd.DataFrame(df_data)
        
        # Save to Excel
        filename = f"customer_quotations_{customer}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = f"/tmp/{filename}"
        df.to_excel(file_path, index=False)
        
        # Save file to Frappe
        with open(file_path, 'rb') as f:
            file_doc = save_file(filename, f.read(), None, None, is_private=1)
        
        return {"file_url": file_doc.file_url}
        
    except Exception as e:
        frappe.log_error(f"Error in export_quotations_excel: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=True)
def export_sales_orders_excel(filters=None):
    """Export sales orders to Excel"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Authentication required"}
        
        if filters:
            filters = json.loads(filters)
        else:
            filters = {}
        
        # Get all sales orders (no pagination for export)
        result = get_customer_sales_orders(filters, page=1, page_length=1000)
        sales_orders = result.get('sales_orders', [])
        
        if not sales_orders:
            return {"error": "No sales orders found"}
        
        # Create DataFrame
        df_data = []
        for order in sales_orders:
            df_data.append({
                'Sales Order': order['name'],
                'Date': order['transaction_date'],
                'Delivery Date': order['delivery_date'],
                'Amount': order['grand_total'],
                'Status': order['status']
            })
        
        df = pd.DataFrame(df_data)
        
        # Save to Excel
        filename = f"customer_sales_orders_{customer}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = f"/tmp/{filename}"
        df.to_excel(file_path, index=False)
        
        # Save file to Frappe
        with open(file_path, 'rb') as f:
            file_doc = save_file(filename, f.read(), None, None, is_private=1)
        
        return {"file_url": file_doc.file_url}
        
    except Exception as e:
        frappe.log_error(f"Error in export_sales_orders_excel: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=True)
def export_delivery_notes_excel(filters=None):
    """Export delivery notes to Excel"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Authentication required"}
        
        if filters:
            filters = json.loads(filters)
        else:
            filters = {}
        
        # Get all delivery notes (no pagination for export)
        result = get_customer_delivery_notes(filters, page=1, page_length=1000)
        delivery_notes = result.get('delivery_notes', [])
        
        frappe.log_error(f"Delivery notes export - Customer: {customer}, Result: {result}, Notes count: {len(delivery_notes)}")
        
        if not delivery_notes:
            return {"error": "No delivery notes found"}
        
        # Create DataFrame
        df_data = []
        for note in delivery_notes:
            df_data.append({
                'Delivery Note': note['name'],
                'Date': note['posting_date'],
                'Amount': note['grand_total'],
                'Status': note['status']
            })
        
        df = pd.DataFrame(df_data)
        
        # Save to Excel
        filename = f"customer_delivery_notes_{customer}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = f"/tmp/{filename}"
        df.to_excel(file_path, index=False)
        
        # Save file to Frappe
        with open(file_path, 'rb') as f:
            file_doc = save_file(filename, f.read(), None, None, is_private=1)
        
        return {"file_url": file_doc.file_url}
        
    except Exception as e:
        frappe.log_error(f"Error in export_delivery_notes_excel: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=True)
def print_document(doc_type, doc_name):
    """Print document using print format from settings or fallback to standard"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Authentication required"}
        
        # Ignore permissions but validate ownership manually
        frappe.local.flags.ignore_permissions = True
        doc = frappe.get_doc(doc_type, doc_name)

        # Re-enable permission checks after fetching
        frappe.local.flags.ignore_permissions = False

        # Verify customer ownership manually
        if doc_type == "Sales Invoice" and doc.customer != customer:
            return {"error": "Access denied"}
        elif doc_type == "Quotation" and doc.party_name != customer:
            return {"error": "Access denied"}
        elif doc_type == "Sales Order" and doc.customer != customer:
            return {"error": "Access denied"}
        elif doc_type == "Delivery Note" and doc.customer != customer:
            return {"error": "Access denied"}
        elif doc_type == "Payment Entry" and doc.party != customer:
            return {"error": "Access denied"}
        
        # Get print format from settings
        print_format = None
        try:
            settings_doc = frappe.get_doc("Isoft Customer Portal Settings")
            
            # Get print format based on document type
            if doc_type == "Sales Invoice":
                print_format = settings_doc.sales_invoice_print_format
            elif doc_type == "Sales Order":
                print_format = settings_doc.sales_order_print_format
            elif doc_type == "Quotation":
                print_format = settings_doc.quotation_print_format
            elif doc_type == "Payment Entry":
                print_format = settings_doc.payment_entry_print_format
            elif doc_type == "Delivery Note":
                print_format = settings_doc.delivery_note_print_format
            
            # If no print format is set in settings, try to get the default print format
            if not print_format:
                print_format = get_default_print_format(doc_type)
                
        except frappe.DoesNotExistError:
            # Settings document doesn't exist, create it with defaults
            try:
                settings_doc = frappe.new_doc("Isoft Customer Portal Settings")
                settings_doc.insert()
                print_format = get_default_print_format(doc_type)
            except Exception as e:
                frappe.logger().error(f"Failed to create settings document: {str(e)}")
                print_format = get_default_print_format(doc_type)
        except Exception as e:
            frappe.logger().error(f"Error accessing settings: {str(e)}")
            print_format = get_default_print_format(doc_type)
        
        # Ensure we have a valid print format
        if not print_format:
            print_format = "Standard"
        
        return {
            "print_format": print_format,
            "doc_type": doc_type,
            "doc_name": doc_name
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Customer Portal Print Error")
        return {"error": str(e)}

def get_default_print_format(doc_type):
    """Get default print format for document type"""
    try:
        # Try to get the first available print format for this doctype
        print_formats = frappe.get_all("Print Format", 
            filters={"doc_type": doc_type, "disabled": 0}, 
            fields=["name"], 
            limit=1
        )
        
        if print_formats:
            return print_formats[0].name
        
        # If no specific print format found, return Standard
        return "Standard"
        
    except Exception as e:
        frappe.logger().error(f"Error getting default print format for {doc_type}: {str(e)}")
        return "Standard"

@frappe.whitelist(allow_guest=True)
def customer_login(usr, pwd):
    """Custom login for customer portal"""
    try:
        # Use Frappe's authentication system
        from frappe.auth import LoginManager
        login_manager = LoginManager()
        
        # Set the credentials
        frappe.form_dict.usr = usr
        frappe.form_dict.pwd = pwd
        
        # Attempt login
        login_manager.authenticate(user=usr, pwd=pwd)
        
        if login_manager.user:
            # Check if user has Customer role
            # user_roles = frappe.get_roles(login_manager.user)
            # if "Customer" not in user_roles:
            #     return {"success": False, "message": "Access denied. Customer role required."}
            
            # Check if user is enabled
            user_doc = frappe.get_doc("User", login_manager.user)
            if not user_doc.enabled:
                return {"success": False, "message": "Account is disabled."}
            
            # Complete login process
            login_manager.post_login()
            
            return {
                "success": True, 
                "message": "Login successful",
                "user": login_manager.user,
                "full_name": user_doc.full_name
            }
        else:
            return {"success": False, "message": "Invalid credentials"}
            
    except Exception as e:
        frappe.log_error(f"Customer login error: {str(e)}")
        return {"success": False, "message": "Login failed. Please try again."}

@frappe.whitelist(allow_guest=True)
def customer_logout():
    """Custom logout for customer portal"""
    try:
        # Store session info before logout
        original_user = frappe.session.user
        original_sid = frappe.session.sid
        
        # Proper logout using Frappe's session management
        if frappe.session.user != "Guest":
            # Use Frappe's built-in logout mechanism
            frappe.local.login_manager.logout()
            
            # Clear any remaining session data
            if hasattr(frappe.local, 'session'):
                frappe.local.session = None
            if hasattr(frappe.local, 'user'):
                frappe.local.user = None
            
            # Commit any pending database changes
            frappe.db.commit()
        else:
            # User is already Guest, no action needed
            pass
        
        # Return response in the format expected by the JavaScript
        return {
            "message": {
                "success": True,
                "message": "Logout successful"
            }
        }
        
    except Exception as e:
        # Don't log error if session is already cleared
        frappe.logger().error(f"Customer logout error: {str(e)}")
        frappe.logger().error(f"Error type: {type(e).__name__}")
        frappe.logger().error(f"Error traceback: {frappe.get_traceback()}")
        # Return success anyway to ensure user can logout
        return {
            "message": {
                "success": True,
                "message": "Logout completed"
            }
        }

@frappe.whitelist(allow_guest=True)
def export_invoices_pdf(filters=None):
    """Export customer invoices to PDF"""
    try:
        # Check authentication
        if not check_customer_auth():
            return {"error": "Authentication required"}
        
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Customer not found"}
        
        # Parse filters
        if isinstance(filters, str):
            filters = json.loads(filters) if filters else {}
        
        # Get invoices data
        invoices_data = get_customer_invoices(filters, page=1, page_length=1000)
        
        if not invoices_data or not invoices_data.get('invoices'):
            return {"error": "No data to export"}
        
        # Create PDF
        from frappe.utils.pdf import get_pdf
        
        # Create HTML content for PDF
        html_content = f"""
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 40px 20px;
                    color: #1a202c;
                }}
                
                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
                    overflow: hidden;
                }}
                
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                    position: relative;
                }}
                
                .header::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/><circle cx="10" cy="60" r="0.5" fill="white" opacity="0.1"/><circle cx="90" cy="40" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
                    opacity: 0.3;
                }}
                
                .header h1 {{
                    font-size: 2.5rem;
                    font-weight: 700;
                    margin-bottom: 10px;
                    position: relative;
                    z-index: 1;
                }}
                
                .header p {{
                    font-size: 1.1rem;
                    opacity: 0.9;
                    margin: 5px 0;
                    position: relative;
                    z-index: 1;
                }}
                
                .content {{
                    padding: 40px 30px;
                }}
                
                .table-container {{
                    background: white;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 0.9rem;
                }}
                
                th {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    font-weight: 600;
                    padding: 15px 12px;
                    text-align: left;
                    font-size: 0.85rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                
                td {{
                    padding: 12px;
                    border-bottom: 1px solid #e2e8f0;
                    color: #4a5568;
                }}
                
                tr:nth-child(even) {{
                    background-color: #f7fafc;
                }}
                
                tr:hover {{
                    background-color: #edf2f7;
                }}
                
                .amount {{
                    font-weight: 600;
                    color: #2d3748;
                    text-align: right;
                }}
                
                .status {{
                    padding: 4px 8px;
                    border-radius: 6px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    text-transform: uppercase;
                }}
                
                .status.paid {{
                    background: #c6f6d5;
                    color: #22543d;
                }}
                
                .status.pending {{
                    background: #fef5e7;
                    color: #744210;
                }}
                
                .status.overdue {{
                    background: #fed7d7;
                    color: #742a2a;
                }}
                
                .footer {{
                    background: #f7fafc;
                    padding: 20px 30px;
                    text-align: center;
                    border-top: 1px solid #e2e8f0;
                    color: #718096;
                    font-size: 0.85rem;
                }}
                
                @media print {{
                    body {{
                        background: white;
                        padding: 0;
                    }}
                    .container {{
                        box-shadow: none;
                        border-radius: 0;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📄 Customer Invoices Report</h1>
                    <p>Generated on {today()}</p>
                    <p>Customer: {customer}</p>
                </div>
                
                <div class="content">
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Invoice</th>
                                    <th>Date</th>
                                    <th>Due Date</th>
                                    <th>Amount</th>
                                    <th>Outstanding</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        # Add invoice rows
        for invoice in invoices_data['invoices']:
            status_class = invoice.get('status', '').lower().replace(' ', '-')
            html_content += f"""
                                <tr>
                                    <td>{invoice.get('name', '')}</td>
                                    <td>{invoice.get('posting_date', '')}</td>
                                    <td>{invoice.get('due_date', '')}</td>
                                    <td class="amount">{invoice.get('grand_total', 0)}</td>
                                    <td class="amount">{invoice.get('outstanding_amount', 0)}</td>
                                    <td><span class="status {status_class}">{invoice.get('status', '')}</span></td>
                                </tr>
            """
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Generated by Isoft Customer Portal • {today()}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        pdf = get_pdf(html_content)
        
        # Save file
        file_name = f"customer_invoices_{customer}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_doc = save_file(file_name, pdf, None, None, is_private=1)
        
        return {"file_url": file_doc.file_url}
        
    except Exception as e:
        frappe.log_error(f"Error in export_invoices_pdf: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=True)
def export_quotations_pdf(filters=None):
    """Export customer quotations to PDF"""
    try:
        # Check authentication
        if not check_customer_auth():
            return {"error": "Authentication required"}
        
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Customer not found"}
        
        # Parse filters
        if isinstance(filters, str):
            filters = json.loads(filters) if filters else {}
        
        # Get quotations data
        quotations_data = get_customer_quotations(filters, page=1, page_length=1000)
        
        if not quotations_data or not quotations_data.get('quotations'):
            return {"error": "No data to export"}
        
        # Create PDF
        from frappe.utils.pdf import get_pdf
        
        # Create HTML content for PDF
        html_content = f"""
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 40px 20px;
                    color: #1a202c;
                }}
                
                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
                    overflow: hidden;
                }}
                
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                    position: relative;
                }}
                
                .header::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/><circle cx="10" cy="60" r="0.5" fill="white" opacity="0.1"/><circle cx="90" cy="40" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
                    opacity: 0.3;
                }}
                
                .header h1 {{
                    font-size: 2.5rem;
                    font-weight: 700;
                    margin-bottom: 10px;
                    position: relative;
                    z-index: 1;
                }}
                
                .header p {{
                    font-size: 1.1rem;
                    opacity: 0.9;
                    margin: 5px 0;
                    position: relative;
                    z-index: 1;
                }}
                
                .content {{
                    padding: 40px 30px;
                }}
                
                .table-container {{
                    background: white;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 0.9rem;
                }}
                
                th {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    font-weight: 600;
                    padding: 15px 12px;
                    text-align: left;
                    font-size: 0.85rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                
                td {{
                    padding: 12px;
                    border-bottom: 1px solid #e2e8f0;
                    color: #4a5568;
                }}
                
                tr:nth-child(even) {{
                    background-color: #f7fafc;
                }}
                
                tr:hover {{
                    background-color: #edf2f7;
                }}
                
                .amount {{
                    font-weight: 600;
                    color: #2d3748;
                    text-align: right;
                }}
                
                .status {{
                    padding: 4px 8px;
                    border-radius: 6px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    text-transform: uppercase;
                }}
                
                .status.paid {{
                    background: #c6f6d5;
                    color: #22543d;
                }}
                
                .status.pending {{
                    background: #fef5e7;
                    color: #744210;
                }}
                
                .status.overdue {{
                    background: #fed7d7;
                    color: #742a2a;
                }}
                
                .footer {{
                    background: #f7fafc;
                    padding: 20px 30px;
                    text-align: center;
                    border-top: 1px solid #e2e8f0;
                    color: #718096;
                    font-size: 0.85rem;
                }}
                
                @media print {{
                    body {{
                        background: white;
                        padding: 0;
                    }}
                    .container {{
                        box-shadow: none;
                        border-radius: 0;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💼 Customer Quotations Report</h1>
                    <p>Generated on {today()}</p>
                    <p>Customer: {customer}</p>
                </div>
                
                <div class="content">
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Quotation</th>
                                    <th>Date</th>
                                    <th>Valid Till</th>
                                    <th>Amount</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        # Add quotation rows
        for quotation in quotations_data['quotations']:
            status_class = quotation.get('status', '').lower().replace(' ', '-')
            html_content += f"""
                                <tr>
                                    <td>{quotation.get('name', '')}</td>
                                    <td>{quotation.get('transaction_date', '')}</td>
                                    <td>{quotation.get('valid_till', '')}</td>
                                    <td class="amount">{quotation.get('grand_total', 0)}</td>
                                    <td><span class="status {status_class}">{quotation.get('status', '')}</span></td>
                                </tr>
            """
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Generated by Isoft Customer Portal • {today()}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        pdf = get_pdf(html_content)
        
        # Save file
        file_name = f"customer_quotations_{customer}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_doc = save_file(file_name, pdf, None, None, is_private=1)
        
        return {"file_url": file_doc.file_url}
        
    except Exception as e:
        frappe.log_error(f"Error in export_quotations_pdf: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=True)
def export_sales_orders_pdf(filters=None):
    """Export customer sales orders to PDF"""
    try:
        # Check authentication
        if not check_customer_auth():
            return {"error": "Authentication required"}
        
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Customer not found"}
        
        # Parse filters
        if isinstance(filters, str):
            filters = json.loads(filters) if filters else {}
        
        # Get sales orders data
        sales_orders_data = get_customer_sales_orders(filters, page=1, page_length=1000)
        
        if not sales_orders_data or not sales_orders_data.get('sales_orders'):
            return {"error": "No data to export"}
        
        # Create PDF
        from frappe.utils.pdf import get_pdf
        
        # Create HTML content for PDF
        html_content = f"""
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 40px 20px;
                    color: #1a202c;
                }}
                
                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
                    overflow: hidden;
                }}
                
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                    position: relative;
                }}
                
                .header::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/><circle cx="10" cy="60" r="0.5" fill="white" opacity="0.1"/><circle cx="90" cy="40" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
                    opacity: 0.3;
                }}
                
                .header h1 {{
                    font-size: 2.5rem;
                    font-weight: 700;
                    margin-bottom: 10px;
                    position: relative;
                    z-index: 1;
                }}
                
                .header p {{
                    font-size: 1.1rem;
                    opacity: 0.9;
                    margin: 5px 0;
                    position: relative;
                    z-index: 1;
                }}
                
                .content {{
                    padding: 40px 30px;
                }}
                
                .table-container {{
                    background: white;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 0.9rem;
                }}
                
                th {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    font-weight: 600;
                    padding: 15px 12px;
                    text-align: left;
                    font-size: 0.85rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                
                td {{
                    padding: 12px;
                    border-bottom: 1px solid #e2e8f0;
                    color: #4a5568;
                }}
                
                tr:nth-child(even) {{
                    background-color: #f7fafc;
                }}
                
                tr:hover {{
                    background-color: #edf2f7;
                }}
                
                .amount {{
                    font-weight: 600;
                    color: #2d3748;
                    text-align: right;
                }}
                
                .status {{
                    padding: 4px 8px;
                    border-radius: 6px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    text-transform: uppercase;
                }}
                
                .status.paid {{
                    background: #c6f6d5;
                    color: #22543d;
                }}
                
                .status.pending {{
                    background: #fef5e7;
                    color: #744210;
                }}
                
                .status.overdue {{
                    background: #fed7d7;
                    color: #742a2a;
                }}
                
                .footer {{
                    background: #f7fafc;
                    padding: 20px 30px;
                    text-align: center;
                    border-top: 1px solid #e2e8f0;
                    color: #718096;
                    font-size: 0.85rem;
                }}
                
                @media print {{
                    body {{
                        background: white;
                        padding: 0;
                    }}
                    .container {{
                        box-shadow: none;
                        border-radius: 0;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛒 Customer Sales Orders Report</h1>
                    <p>Generated on {today()}</p>
                    <p>Customer: {customer}</p>
                </div>
                
                <div class="content">
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Sales Order</th>
                                    <th>Date</th>
                                    <th>Delivery Date</th>
                                    <th>Amount</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        # Add sales order rows
        for order in sales_orders_data['sales_orders']:
            status_class = order.get('status', '').lower().replace(' ', '-')
            html_content += f"""
                                <tr>
                                    <td>{order.get('name', '')}</td>
                                    <td>{order.get('transaction_date', '')}</td>
                                    <td>{order.get('delivery_date', '')}</td>
                                    <td class="amount">{order.get('grand_total', 0)}</td>
                                    <td><span class="status {status_class}">{order.get('status', '')}</span></td>
                                </tr>
            """
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Generated by Isoft Customer Portal • {today()}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        pdf = get_pdf(html_content)
        
        # Save file
        file_name = f"customer_sales_orders_{customer}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_doc = save_file(file_name, pdf, None, None, is_private=1)
        
        return {"file_url": file_doc.file_url}
        
    except Exception as e:
        frappe.log_error(f"Error in export_sales_orders_pdf: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=True)
def export_delivery_notes_pdf(filters=None):
    """Export customer delivery notes to PDF"""
    try:
        # Check authentication
        if not check_customer_auth():
            return {"error": "Authentication required"}
        
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Customer not found"}
        
        # Parse filters
        if isinstance(filters, str):
            filters = json.loads(filters) if filters else {}
        
        # Get delivery notes data
        delivery_notes_data = get_customer_delivery_notes(filters, page=1, page_length=1000)
        
        frappe.log_error(f"Delivery notes PDF export - Customer: {customer}, Data: {delivery_notes_data}")
        
        if not delivery_notes_data or not delivery_notes_data.get('delivery_notes'):
            return {"error": "No data to export"}
        
        # Create PDF
        from frappe.utils.pdf import get_pdf
        
        # Create HTML content for PDF
        html_content = f"""
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 40px 20px;
                    color: #1a202c;
                }}
                
                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
                    overflow: hidden;
                }}
                
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                    position: relative;
                }}
                
                .header::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/><circle cx="10" cy="60" r="0.5" fill="white" opacity="0.1"/><circle cx="90" cy="40" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
                    opacity: 0.3;
                }}
                
                .header h1 {{
                    font-size: 2.5rem;
                    font-weight: 700;
                    margin-bottom: 10px;
                    position: relative;
                    z-index: 1;
                }}
                
                .header p {{
                    font-size: 1.1rem;
                    opacity: 0.9;
                    margin: 5px 0;
                    position: relative;
                    z-index: 1;
                }}
                
                .content {{
                    padding: 40px 30px;
                }}
                
                .table-container {{
                    background: white;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 0.9rem;
                }}
                
                th {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    font-weight: 600;
                    padding: 15px 12px;
                    text-align: left;
                    font-size: 0.85rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                
                td {{
                    padding: 12px;
                    border-bottom: 1px solid #e2e8f0;
                    color: #4a5568;
                }}
                
                tr:nth-child(even) {{
                    background-color: #f7fafc;
                }}
                
                tr:hover {{
                    background-color: #edf2f7;
                }}
                
                .amount {{
                    font-weight: 600;
                    color: #2d3748;
                    text-align: right;
                }}
                
                .status {{
                    padding: 4px 8px;
                    border-radius: 6px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    text-transform: uppercase;
                }}
                
                .status.paid {{
                    background: #c6f6d5;
                    color: #22543d;
                }}
                
                .status.pending {{
                    background: #fef5e7;
                    color: #744210;
                }}
                
                .status.overdue {{
                    background: #fed7d7;
                    color: #742a2a;
                }}
                
                .footer {{
                    background: #f7fafc;
                    padding: 20px 30px;
                    text-align: center;
                    border-top: 1px solid #e2e8f0;
                    color: #718096;
                    font-size: 0.85rem;
                }}
                
                @media print {{
                    body {{
                        background: white;
                        padding: 0;
                    }}
                    .container {{
                        box-shadow: none;
                        border-radius: 0;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📦 Customer Delivery Notes Report</h1>
                    <p>Generated on {today()}</p>
                    <p>Customer: {customer}</p>
                </div>
                
                <div class="content">
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Delivery Note</th>
                                    <th>Date</th>
                                    <th>Amount</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        # Add delivery note rows
        for note in delivery_notes_data['delivery_notes']:
            status_class = note.get('status', '').lower().replace(' ', '-')
            html_content += f"""
                                <tr>
                                    <td>{note.get('name', '')}</td>
                                    <td>{note.get('posting_date', '')}</td>
                                    <td class="amount">{note.get('grand_total', 0)}</td>
                                    <td><span class="status {status_class}">{note.get('status', '')}</span></td>
                                </tr>
            """
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Generated by Isoft Customer Portal • {today()}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        pdf = get_pdf(html_content)
        
        # Save file
        file_name = f"customer_delivery_notes_{customer}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_doc = save_file(file_name, pdf, None, None, is_private=1)
        
        return {"file_url": file_doc.file_url}
        
    except Exception as e:
        frappe.log_error(f"Error in export_delivery_notes_pdf: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=True)
def export_dashboard_pdf():
    """Export dashboard data to PDF"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {}
        
        # Get dashboard data
        stats = get_dashboard_statistics()
        recent_transactions = get_recent_transactions(20)
        
        # Create HTML content for PDF
        html_content = f"""
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 40px 20px;
                    color: #1a202c;
                }}
                
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
                    overflow: hidden;
                }}
                
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                    position: relative;
                }}
                
                .header::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/><circle cx="10" cy="60" r="0.5" fill="white" opacity="0.1"/><circle cx="90" cy="40" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
                    opacity: 0.3;
                }}
                
                .header h1 {{
                    font-size: 2.5rem;
                    font-weight: 700;
                    margin-bottom: 10px;
                    position: relative;
                    z-index: 1;
                }}
                
                .header p {{
                    font-size: 1.1rem;
                    opacity: 0.9;
                    margin: 5px 0;
                    position: relative;
                    z-index: 1;
                }}
                
                .content {{
                    padding: 40px 30px;
                }}
                
                .section {{
                    margin-bottom: 40px;
                }}
                
                .section h2 {{
                    font-size: 1.5rem;
                    font-weight: 600;
                    color: #2d3748;
                    margin-bottom: 20px;
                    padding-bottom: 10px;
                    border-bottom: 3px solid #667eea;
                    display: flex;
                    align-items: center;
                }}
                
                .section h2::before {{
                    content: '📊';
                    margin-right: 10px;
                    font-size: 1.2rem;
                }}
                
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                
                .stat-card {{
                    background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                    padding: 20px;
                    text-align: center;
                    transition: transform 0.2s ease;
                }}
                
                .stat-card:hover {{
                    transform: translateY(-2px);
                }}
                
                .stat-value {{
                    font-size: 2rem;
                    font-weight: 700;
                    color: #667eea;
                    margin-bottom: 5px;
                }}
                
                .stat-label {{
                    font-size: 0.9rem;
                    color: #718096;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                
                .table-container {{
                    background: white;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 0.9rem;
                }}
                
                th {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    font-weight: 600;
                    padding: 15px 12px;
                    text-align: left;
                    font-size: 0.85rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                
                td {{
                    padding: 12px;
                    border-bottom: 1px solid #e2e8f0;
                    color: #4a5568;
                }}
                
                tr:nth-child(even) {{
                    background-color: #f7fafc;
                }}
                
                tr:hover {{
                    background-color: #edf2f7;
                }}
                
                .amount {{
                    font-weight: 600;
                    color: #2d3748;
                    text-align: right;
                }}
                
                .status {{
                    padding: 4px 8px;
                    border-radius: 6px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    text-transform: uppercase;
                }}
                
                .status.paid {{
                    background: #c6f6d5;
                    color: #22543d;
                }}
                
                .status.pending {{
                    background: #fef5e7;
                    color: #744210;
                }}
                
                .status.overdue {{
                    background: #fed7d7;
                    color: #742a2a;
                }}
                
                .footer {{
                    background: #f7fafc;
                    padding: 20px 30px;
                    text-align: center;
                    border-top: 1px solid #e2e8f0;
                    color: #718096;
                    font-size: 0.85rem;
                }}
                
                @media print {{
                    body {{
                        background: white;
                        padding: 0;
                    }}
                    .container {{
                        box-shadow: none;
                        border-radius: 0;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📈 Customer Dashboard Report</h1>
                    <p>Generated on {today()}</p>
                    <p>Customer: {customer}</p>
                </div>
                
                <div class="content">
                    <div class="section">
                        <h2>Dashboard Statistics</h2>
                        <div class="stats-grid">
                            <div class="stat-card">
                                <div class="stat-value">{stats.get('total_invoices', 0)}</div>
                                <div class="stat-label">Total Invoices</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">{stats.get('total_quotations', 0)}</div>
                                <div class="stat-label">Total Quotations</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">{stats.get('total_deliveries', 0)}</div>
                                <div class="stat-label">Total Deliveries</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">{stats.get('outstanding_amount', 0)}</div>
                                <div class="stat-label">Outstanding Amount</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>Recent Transactions</h2>
                        <div class="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>Type</th>
                                        <th>Reference</th>
                                        <th>Amount</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
        """
        
        # Add transaction rows
        for transaction in recent_transactions:
            status_class = transaction.get('status', '').lower().replace(' ', '-')
            html_content += f"""
                                    <tr>
                                        <td>{transaction.get('date', '')}</td>
                                        <td>{transaction.get('type', '')}</td>
                                        <td>{transaction.get('reference', '')}</td>
                                        <td class="amount">{transaction.get('amount', 0)}</td>
                                        <td><span class="status {status_class}">{transaction.get('status', '')}</span></td>
                                    </tr>
            """
        
        html_content += """
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Generated by Isoft Customer Portal • {today()}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create PDF
        from frappe.utils.pdf import get_pdf
        pdf = get_pdf(html_content)
        
        # Save file
        file_name = f"customer_dashboard_{customer}_{today()}.pdf"
        file_doc = save_file(file_name, pdf, None, None, is_private=1)
        
        return {"file_url": file_doc.file_url}
        
    except Exception as e:
        frappe.log_error(f"Error in export_dashboard_pdf: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=True)
def export_dashboard_excel():
    """Export dashboard data to Excel"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {}
        
        # Get data
        stats = get_dashboard_statistics()
        transactions = get_recent_transactions(50)
        
        # Create DataFrame
        data = {
            'Dashboard Statistics': [
                ['Total Invoices', stats.get('total_invoices', 0)],
                ['Total Quotations', stats.get('total_quotations', 0)],
                ['Total Deliveries', stats.get('total_deliveries', 0)],
                ['Outstanding Amount', stats.get('outstanding_amount', 0)]
            ],
            'Recent Transactions': [
                ['Date', 'Type', 'Reference', 'Amount', 'Status']
            ]
        }
        
        for transaction in transactions:
            data['Recent Transactions'].append([
                transaction.get('date', ''),
                transaction.get('type', ''),
                transaction.get('reference', ''),
                transaction.get('amount', 0),
                transaction.get('status', '')
            ])
        
        # Create Excel file
        filename = f"customer_dashboard_{customer}_{today()}.xlsx"
        file_path = f"/tmp/{filename}"
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Statistics sheet
            df_stats = pd.DataFrame(data['Dashboard Statistics'], columns=['Metric', 'Value'])
            df_stats.to_excel(writer, sheet_name='Statistics', index=False)
            
            # Transactions sheet
            df_transactions = pd.DataFrame(data['Recent Transactions'][1:], columns=data['Recent Transactions'][0])
            df_transactions.to_excel(writer, sheet_name='Transactions', index=False)
        
        # Save file
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        file_doc = save_file(filename, file_data, None, None, is_private=1)
        
        return {
            "file_url": file_doc.file_url,
            "filename": filename
        }
        
    except Exception as e:
        frappe.log_error(f"Error in export_dashboard_excel: {str(e)}")
        return {}

@frappe.whitelist(allow_guest=True)
def get_customer_data_api():
    """API method to get customer data for current user"""
    try:
        # Check authentication
        if not check_customer_auth():
            return None
        
        user = frappe.session.user
        customer = get_customer_from_user()
        
        if not customer:
            return None
        
        # Get customer details
        customer_doc = frappe.get_doc("Customer", customer)
        
        return {
            "user": {
                "name": user,
                "full_name": frappe.get_value("User", user, "full_name"),
                "email": frappe.get_value("User", user, "email")
            },
            "customer": {
                "name": customer,
                "customer_name": customer_doc.customer_name,
                "customer_type": customer_doc.customer_type,
                "customer_group": customer_doc.customer_group,
                "territory": customer_doc.territory
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_customer_data_api: {str(e)}")
        return None

@frappe.whitelist(allow_guest=True)
def check_customer_auth():
    """Check if current user is authenticated as customer"""
    try:
        user = frappe.session.user
        
        if not user or user == 'Guest':
            return {"authenticated": False, "message": "Not authenticated"}
        
        # # Check if user has Customer role
        # user_roles = frappe.get_roles(user)
        # if "Customer" not in user_roles:
        #     return {"authenticated": False, "message": "Customer role required"}
        
        # Get customer information
        customer = get_customer_from_user()
        if not customer:
            return {"authenticated": False, "message": "No customer linked to user"}
        
        return {
            "authenticated": True,
            "user": user,
            "customer": customer
        }
        
    except Exception as e:
        frappe.log_error(f"Customer auth check error: {str(e)}")
        return {"authenticated": False, "message": "Authentication check failed"}

@frappe.whitelist(allow_guest=True)
def test_no_date_filter():
    """Test function to get ledger without date filters"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"error": "No customer found"}
        
        # Test without any date filters
        query_filters = {"party": customer}
        
        # Get total count
        total = frappe.db.count("GL Entry", query_filters)
        
        # Get entries
        entries = frappe.get_all(
            "GL Entry",
            filters=query_filters,
            fields=["name", "posting_date", "voucher_type", "voucher_no", "debit", "credit", "remarks"],
            order_by="posting_date desc, creation desc",
            limit=10
        )
        
        return {
            "customer": customer,
            "total": total,
            "entries": entries
        }
        
    except Exception as e:
        return {"error": str(e)}

@frappe.whitelist(allow_guest=True)
def test_date_formats():
    """Test different date formats and filter combinations"""
    try:
        customer = get_customer_from_user()
        
        if not customer:
            return {"error": "No customer found"}
        
        # Test different date formats
        test_cases = [
            {"from_date": "2024-01-01", "to_date": "2024-12-31"},
            {"from_date": "01/01/2024", "to_date": "12/31/2024"},
            {"from_date": "2024-01-01", "to_date": None},
            {"from_date": None, "to_date": "2024-12-31"},
            {"from_date": "2024-01-01", "to_date": "2024-01-01"},
        ]
        
        results = []
        
        for i, test_case in enumerate(test_cases):
            # Test date validation
            from_date = validate_date_format(test_case.get('from_date'))
            to_date = validate_date_format(test_case.get('to_date'))
            
            # Test filter building
            date_filters = build_date_filter(test_case, "posting_date")
            
            # Test actual query
            query_filters = {"party": customer}
            query_filters.update(date_filters)
            
            count = frappe.db.count("GL Entry", query_filters)
            
            results.append({
                "test_case": test_case,
                "validated_from": from_date,
                "validated_to": to_date,
                "date_filters": date_filters,
                "count": count
            })
        
        return {
            "customer": customer,
            "test_results": results
        }
        
    except Exception as e:
        frappe.log_error(f"Error in test_date_formats: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist()
def get_dashboard_analytics(period=30):
    """Get dashboard analytics data for charts"""
    try:
        customer = get_customer_from_user()
        frappe.log_error(f"Dashboard Analytics - Customer: {customer}, Period: {period}")
        
        if not customer:
            frappe.log_error("Dashboard Analytics - No customer found")
            return {'revenue': [], 'status': {}, 'activities': []}
        
        # Convert period to integer
        period = int(period)
        from_date = frappe.utils.add_days(frappe.utils.today(), -period)
        
        # Revenue trend data with proper date filtering
        revenue_data = frappe.db.sql("""
            SELECT 
                DATE(posting_date) as date,
                SUM(grand_total) as amount
            FROM `tabSales Invoice`
            WHERE customer = %s 
                AND docstatus = 1
                AND posting_date >= %s
            GROUP BY DATE(posting_date)
            ORDER BY posting_date ASC
        """, (customer, from_date), as_dict=True)
        
        frappe.log_error(f"Dashboard Analytics - Revenue data count: {len(revenue_data)}")
        
        # Status breakdown for sales invoices with date filtering
        status_data = frappe.db.sql("""
            SELECT 
                status,
                COUNT(*) as count
            FROM `tabSales Invoice`
            WHERE customer = %s 
                AND docstatus = 1
                AND posting_date >= %s
            GROUP BY status
        """, (customer, from_date), as_dict=True)
        
        status_dict = {item['status']: item['count'] for item in status_data}
        
        frappe.log_error(f"Dashboard Analytics - Status data: {status_dict}")
        
        # Top items by revenue with date filtering
        top_items_data = frappe.db.sql("""
            SELECT 
                item.item_name,
                item.item_code,
                SUM(item.amount) as total_revenue,
                SUM(item.qty) as total_quantity,
                COUNT(DISTINCT si.name) as invoice_count
            FROM `tabSales Invoice Item` item
            INNER JOIN `tabSales Invoice` si ON item.parent = si.name
            WHERE si.customer = %s 
                AND si.docstatus = 1
                AND si.posting_date >= %s
            GROUP BY item.item_code, item.item_name
            ORDER BY total_revenue DESC
            LIMIT 10
        """, (customer, from_date), as_dict=True)
        
        frappe.log_error(f"Dashboard Analytics - Top items count: {len(top_items_data)}")
        
        # Recent activities
        activities = []
        
        # Get recent invoices (primary focus) with date filtering
        recent_invoices = frappe.db.sql("""
            SELECT 
                name,
                posting_date,
                grand_total,
                status,
                'Sales Invoice' as doctype
            FROM `tabSales Invoice`
            WHERE customer = %s 
                AND docstatus = 1
                AND posting_date >= %s
            ORDER BY posting_date DESC
            LIMIT 5
        """, (customer, from_date), as_dict=True)
        
        for inv in recent_invoices:
            activities.append({
                'title': f'Invoice {inv.name}',
                'description': f'Sales invoice {inv.status.lower()}',
                'date': inv.posting_date,
                'status': inv.status,
                'amount': inv.grand_total,
                'type': 'invoice'
            })
        
        # Get recent sales orders (secondary focus)
        recent_orders = frappe.db.sql("""
            SELECT 
                name,
                transaction_date,
                grand_total,
                status,
                'Sales Order' as doctype
            FROM `tabSales Order`
            WHERE customer = %s 
                AND docstatus != 2
                AND transaction_date >= %s
            ORDER BY transaction_date DESC
            LIMIT 2
        """, (customer, from_date), as_dict=True)
        
        for order in recent_orders:
            activities.append({
                'title': f'Order {order.name}',
                'description': f'Sales order {order.status.lower()}',
                'date': order.transaction_date,
                'status': order.status,
                'amount': order.grand_total,
                'type': 'order'
            })
        
        # Sort activities by date
        activities.sort(key=lambda x: x['date'], reverse=True)
        
        return {
            'revenue': revenue_data,
            'status': status_dict,
            'items': top_items_data,
            'activities': activities[:10]  # Limit to 10 activities
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_dashboard_analytics: {str(e)}")
        return {'revenue': [], 'status': {}, 'activities': []}

@frappe.whitelist(allow_guest=True)
def test_dashboard_queries():
    """Test dashboard queries to debug data issues"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {'error': 'No customer found'}
        
        # Test 1: Check all sales invoices for this customer
        all_invoices = frappe.db.sql("""
            SELECT 
                name,
                posting_date,
                grand_total,
                status,
                docstatus
            FROM `tabSales Invoice`
            WHERE customer = %s
            ORDER BY posting_date DESC
            LIMIT 10
        """, (customer,), as_dict=True)
        
        # Test 2: Check invoices in last 30 days
        recent_invoices = frappe.db.sql("""
            SELECT 
                name,
                posting_date,
                grand_total,
                status,
                docstatus
            FROM `tabSales Invoice`
            WHERE customer = %s 
                AND docstatus = 1
                AND posting_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            ORDER BY posting_date DESC
        """, (customer,), as_dict=True)
        
        # Test 3: Check invoices in last 365 days
        year_invoices = frappe.db.sql("""
            SELECT 
                name,
                posting_date,
                grand_total,
                status,
                docstatus
            FROM `tabSales Invoice`
            WHERE customer = %s 
                AND docstatus = 1
                AND posting_date >= DATE_SUB(CURDATE(), INTERVAL 365 DAY)
            ORDER BY posting_date DESC
        """, (customer,), as_dict=True)
        
        return {
            'customer': customer,
            'all_invoices_count': len(all_invoices),
            'all_invoices': all_invoices,
            'recent_invoices_count': len(recent_invoices),
            'recent_invoices': recent_invoices,
            'year_invoices_count': len(year_invoices),
            'year_invoices': year_invoices
        }
        
    except Exception as e:
        frappe.log_error(f"Error in test_dashboard_queries: {str(e)}")
        return {'error': str(e)}

@frappe.whitelist(allow_guest=True)
def get_current_customer_info():
    """Get current customer information for sidebar"""
    try:
        # Check authentication first
        if not check_customer_auth():
            return {'customer_name': 'Guest'}
            
        customer = get_customer_from_user()
        if not customer:
            return {'customer_name': 'Guest'}
        
        customer_doc = frappe.get_doc("Customer", customer)
        
        return {
            'customer_name': customer_doc.customer_name,
            'customer_code': customer_doc.name,
            'customer_group': customer_doc.customer_group,
            'territory': customer_doc.territory
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_current_customer_info: {str(e)}")
        return {'customer_name': 'Customer'}

