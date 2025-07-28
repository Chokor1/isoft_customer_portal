import frappe
from frappe import _
from frappe.utils import getdate, today, add_days, formatdate
from frappe.utils.file_manager import save_file
import json
import pandas as pd
from datetime import datetime, timedelta

@frappe.whitelist()
def get_dashboard_statistics():
    """Get dashboard statistics for the current customer"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {}
        
        # Get statistics
        stats = {
            'total_invoices': get_total_invoices(customer),
            'total_quotations': get_total_quotations(customer),
            'total_deliveries': get_total_deliveries(customer),
            'total_sales_orders': get_total_sales_orders(customer),
            'outstanding_amount': get_outstanding_amount(customer)
        }
        
        return stats
    except Exception as e:
        frappe.log_error(f"Error in get_dashboard_statistics: {str(e)}")
        return {}

@frappe.whitelist()
def get_recent_transactions(limit=10):
    """Get recent transactions for the current customer"""
    try:
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
        
        # Sort by date and limit
        transactions.sort(key=lambda x: x['date'], reverse=True)
        return transactions[:limit]
        
    except Exception as e:
        frappe.log_error(f"Error in get_recent_transactions: {str(e)}")
        return []

@frappe.whitelist()
def get_customer_ledger(filters=None, page=1, page_length=20):
    """Get customer ledger entries"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"entries": [], "total": 0, "summary": {}}
        
        if filters:
            filters = json.loads(filters)
        else:
            filters = {}
        
        # Build query filters
        query_filters = {"party": customer}
        
        if filters.get('from_date'):
            query_filters["posting_date"] = [">=", filters.get('from_date')]
        if filters.get('to_date'):
            if "posting_date" in query_filters:
                query_filters["posting_date"].append("<=", filters.get('to_date'))
            else:
                query_filters["posting_date"] = ["<=", filters.get('to_date')]
        
        # Get total count
        total = frappe.db.count("GL Entry", query_filters)
        
        # Get entries with pagination
        entries = frappe.get_all(
            "GL Entry",
            filters=query_filters,
            fields=["name", "posting_date", "voucher_type", "voucher_no", "debit", "credit", "debit_in_account_currency", "credit_in_account_currency", "account_currency", "remarks"],
            order_by="posting_date desc, creation desc",
            start=(page - 1) * page_length,
            page_length=page_length
        )
        
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

@frappe.whitelist()
def get_customer_invoices(filters=None, page=1, page_length=20):
    """Get customer invoices"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"invoices": [], "total": 0, "summary": {}}
        
        if filters:
            filters = json.loads(filters)
        else:
            filters = {}
        
        # Build query filters
        query_filters = {"customer": customer, "docstatus": ["!=", 2]}
        
        if filters.get('from_date'):
            query_filters["posting_date"] = [">=", filters.get('from_date')]
        if filters.get('to_date'):
            if "posting_date" in query_filters:
                query_filters["posting_date"].append("<=", filters.get('to_date'))
            else:
                query_filters["posting_date"] = ["<=", filters.get('to_date')]
        if filters.get('status'):
            query_filters["status"] = filters.get('status')
        
        # Get total count
        total = frappe.db.count("Sales Invoice", query_filters)
        
        # Get invoices with pagination
        invoices = frappe.get_all(
            "Sales Invoice",
            filters=query_filters,
            fields=["name", "posting_date", "due_date", "grand_total", "outstanding_amount", "status", "currency"],
            order_by="posting_date desc",
            start=(page - 1) * page_length,
            page_length=page_length
        )
        
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

@frappe.whitelist()
def get_customer_quotations(filters=None, page=1, page_length=20):
    """Get customer quotations"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"quotations": [], "total": 0, "summary": {}}
        
        if filters:
            filters = json.loads(filters)
        else:
            filters = {}
        
        # Build query filters
        query_filters = {"party_name": customer, "docstatus": ["!=", 2]}
        
        if filters.get('from_date'):
            query_filters["transaction_date"] = [">=", filters.get('from_date')]
        if filters.get('to_date'):
            if "transaction_date" in query_filters:
                query_filters["transaction_date"].append("<=", filters.get('to_date'))
            else:
                query_filters["transaction_date"] = ["<=", filters.get('to_date')]
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

@frappe.whitelist()
def get_customer_delivery_notes(filters=None, page=1, page_length=20):
    """Get customer delivery notes"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"delivery_notes": [], "total": 0, "summary": {}}
        
        if filters:
            filters = json.loads(filters)
        else:
            filters = {}
        
        # Build query filters
        query_filters = {"customer": customer, "docstatus": ["!=", 2]}
        
        if filters.get('from_date'):
            query_filters["posting_date"] = [">=", filters.get('from_date')]
        if filters.get('to_date'):
            if "posting_date" in query_filters:
                query_filters["posting_date"].append("<=", filters.get('to_date'))
            else:
                query_filters["posting_date"] = ["<=", filters.get('to_date')]
        if filters.get('status'):
            query_filters["status"] = filters.get('status')
        
        # Get total count
        total = frappe.db.count("Delivery Note", query_filters)
        
        # Get delivery notes with pagination
        delivery_notes = frappe.get_all(
            "Delivery Note",
            filters=query_filters,
            fields=["name", "posting_date", "grand_total", "status", "currency"],
            order_by="posting_date desc",
            start=(page - 1) * page_length,
            page_length=page_length
        )
        
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

@frappe.whitelist()
def get_customer_sales_orders(filters=None, page=1, page_length=20):
    """Get customer sales orders"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"sales_orders": [], "total": 0, "summary": {}}
        
        if filters:
            filters = json.loads(filters)
        else:
            filters = {}
        
        # Build query filters
        query_filters = {"customer": customer, "docstatus": ["!=", 2]}
        
        if filters.get('from_date'):
            query_filters["transaction_date"] = [">=", filters.get('from_date')]
        if filters.get('to_date'):
            if "transaction_date" in query_filters:
                query_filters["transaction_date"].append("<=", filters.get('to_date'))
            else:
                query_filters["transaction_date"] = ["<=", filters.get('to_date')]
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

def get_customer_from_user():
    """Get customer linked to current user"""
    try:
        user = frappe.get_user()
        if not user:
            return None
        
        # Check if user has Customer role
        if "Customer" not in [role.role for role in user.roles]:
            return None
        
        # Get customer linked to user
        customer = frappe.db.get_value("Customer", {"user": user.name})
        if not customer:
            # Try to get customer by email
            customer = frappe.db.get_value("Customer", {"email_id": user.email})
        
        return customer
    except Exception as e:
        frappe.log_error(f"Error in get_customer_from_user: {str(e)}")
        return None

def get_total_invoices(customer):
    """Get total number of invoices for customer"""
    return frappe.db.count("Sales Invoice", {"customer": customer, "docstatus": ["!=", 2]})

def get_total_quotations(customer):
    """Get total number of quotations for customer"""
    return frappe.db.count("Quotation", {"party_name": customer, "docstatus": ["!=", 2]})

def get_total_deliveries(customer):
    """Get total number of delivery notes for customer"""
    return frappe.db.count("Delivery Note", {"customer": customer, "docstatus": ["!=", 2]})

def get_total_sales_orders(customer):
    """Get total number of sales orders for customer"""
    return frappe.db.count("Sales Order", {"customer": customer, "docstatus": ["!=", 2]})

def get_outstanding_amount(customer):
    """Get outstanding amount for customer"""
    try:
        result = frappe.db.sql("""
            SELECT SUM(outstanding_amount)
            FROM `tabSales Invoice`
            WHERE customer = %s AND docstatus = 1 AND outstanding_amount > 0
        """, customer, as_dict=True)
        
        return result[0]['SUM(outstanding_amount)'] or 0
    except Exception as e:
        frappe.log_error(f"Error in get_outstanding_amount: {str(e)}")
        return 0

def get_ledger_summary(customer, filters):
    """Get ledger summary for customer"""
    try:
        query_filters = {"party": customer}
        
        if filters.get('from_date'):
            query_filters["posting_date"] = [">=", filters.get('from_date')]
        if filters.get('to_date'):
            if "posting_date" in query_filters:
                query_filters["posting_date"].append("<=", filters.get('to_date'))
            else:
                query_filters["posting_date"] = ["<=", filters.get('to_date')]
        
        # Get total debit and credit
        result = frappe.db.sql("""
            SELECT 
                SUM(debit) as total_debit,
                SUM(credit) as total_credit,
                SUM(debit_in_account_currency) as total_debit_in_account_currency,
                SUM(credit_in_account_currency) as total_credit_in_account_currency
            FROM `tabGL Entry`
            WHERE party = %s
        """, customer, as_dict=True)
        
        if result:
            return {
                'total_debit': result[0]['total_debit'] or 0,
                'total_credit': result[0]['total_credit'] or 0,
                'balance': (result[0]['total_debit'] or 0) - (result[0]['total_credit'] or 0)
            }
        
        return {'total_debit': 0, 'total_credit': 0, 'balance': 0}
        
    except Exception as e:
        frappe.log_error(f"Error in get_ledger_summary: {str(e)}")
        return {'total_debit': 0, 'total_credit': 0, 'balance': 0}

def get_invoices_summary(customer, filters):
    """Get invoices summary for customer"""
    try:
        query_filters = {"customer": customer, "docstatus": ["!=", 2]}
        
        if filters.get('from_date'):
            query_filters["posting_date"] = [">=", filters.get('from_date')]
        if filters.get('to_date'):
            if "posting_date" in query_filters:
                query_filters["posting_date"].append("<=", filters.get('to_date'))
            else:
                query_filters["posting_date"] = ["<=", filters.get('to_date')]
        
        # Get total amount and outstanding
        result = frappe.db.sql("""
            SELECT 
                SUM(grand_total) as total_amount,
                SUM(outstanding_amount) as total_outstanding
            FROM `tabSales Invoice`
            WHERE customer = %s AND docstatus != 2
        """, customer, as_dict=True)
        
        if result:
            return {
                'total_amount': result[0]['total_amount'] or 0,
                'total_outstanding': result[0]['total_outstanding'] or 0
            }
        
        return {'total_amount': 0, 'total_outstanding': 0}
        
    except Exception as e:
        frappe.log_error(f"Error in get_invoices_summary: {str(e)}")
        return {'total_amount': 0, 'total_outstanding': 0}

def get_quotations_summary(customer, filters):
    """Get quotations summary for customer"""
    try:
        query_filters = {"party_name": customer, "docstatus": ["!=", 2]}
        
        if filters.get('from_date'):
            query_filters["transaction_date"] = [">=", filters.get('from_date')]
        if filters.get('to_date'):
            if "transaction_date" in query_filters:
                query_filters["transaction_date"].append("<=", filters.get('to_date'))
            else:
                query_filters["transaction_date"] = ["<=", filters.get('to_date')]
        
        # Get total amount
        result = frappe.db.sql("""
            SELECT SUM(grand_total) as total_amount
            FROM `tabQuotation`
            WHERE party_name = %s AND docstatus != 2
        """, customer, as_dict=True)
        
        if result:
            return {
                'total_amount': result[0]['total_amount'] or 0
            }
        
        return {'total_amount': 0}
        
    except Exception as e:
        frappe.log_error(f"Error in get_quotations_summary: {str(e)}")
        return {'total_amount': 0}

def get_delivery_notes_summary(customer, filters):
    """Get delivery notes summary for customer"""
    try:
        query_filters = {"customer": customer, "docstatus": ["!=", 2]}
        
        if filters.get('from_date'):
            query_filters["posting_date"] = [">=", filters.get('from_date')]
        if filters.get('to_date'):
            if "posting_date" in query_filters:
                query_filters["posting_date"].append("<=", filters.get('to_date'))
            else:
                query_filters["posting_date"] = ["<=", filters.get('to_date')]
        
        # Get total amount
        result = frappe.db.sql("""
            SELECT SUM(grand_total) as total_amount
            FROM `tabDelivery Note`
            WHERE customer = %s AND docstatus != 2
        """, customer, as_dict=True)
        
        if result:
            return {
                'total_amount': result[0]['total_amount'] or 0
            }
        
        return {'total_amount': 0}
        
    except Exception as e:
        frappe.log_error(f"Error in get_delivery_notes_summary: {str(e)}")
        return {'total_amount': 0}

def get_sales_orders_summary(customer, filters):
    """Get sales orders summary for customer"""
    try:
        query_filters = {"customer": customer, "docstatus": ["!=", 2]}
        
        if filters.get('from_date'):
            query_filters["transaction_date"] = [">=", filters.get('from_date')]
        if filters.get('to_date'):
            if "transaction_date" in query_filters:
                query_filters["transaction_date"].append("<=", filters.get('to_date'))
            else:
                query_filters["transaction_date"] = ["<=", filters.get('to_date')]
        
        # Get total amount
        result = frappe.db.sql("""
            SELECT SUM(grand_total) as total_amount
            FROM `tabSales Order`
            WHERE customer = %s AND docstatus != 2
        """, customer, as_dict=True)
        
        if result:
            return {
                'total_amount': result[0]['total_amount'] or 0
            }
        
        return {'total_amount': 0}
        
    except Exception as e:
        frappe.log_error(f"Error in get_sales_orders_summary: {str(e)}")
        return {'total_amount': 0}

@frappe.whitelist()
def export_dashboard_excel():
    """Export dashboard data to Excel"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Customer not found"}
        
        # Get all data
        invoices = frappe.get_all(
            "Sales Invoice",
            filters={"customer": customer, "docstatus": ["!=", 2]},
            fields=["name", "posting_date", "due_date", "grand_total", "outstanding_amount", "status"]
        )
        
        quotations = frappe.get_all(
            "Quotation",
            filters={"party_name": customer, "docstatus": ["!=", 2]},
            fields=["name", "transaction_date", "valid_till", "grand_total", "status"]
        )
        
        sales_orders = frappe.get_all(
            "Sales Order",
            filters={"customer": customer, "docstatus": ["!=", 2]},
            fields=["name", "transaction_date", "delivery_date", "grand_total", "status"]
        )
        
        delivery_notes = frappe.get_all(
            "Delivery Note",
            filters={"customer": customer, "docstatus": ["!=", 2]},
            fields=["name", "posting_date", "grand_total", "status"]
        )
        
        # Create Excel file
        with pd.ExcelWriter('customer_portal_data.xlsx', engine='openpyxl') as writer:
            # Invoices sheet
            if invoices:
                df_invoices = pd.DataFrame(invoices)
                df_invoices.to_excel(writer, sheet_name='Invoices', index=False)
            
            # Quotations sheet
            if quotations:
                df_quotations = pd.DataFrame(quotations)
                df_quotations.to_excel(writer, sheet_name='Quotations', index=False)
            
            # Sales Orders sheet
            if sales_orders:
                df_sales_orders = pd.DataFrame(sales_orders)
                df_sales_orders.to_excel(writer, sheet_name='Sales Orders', index=False)
            
            # Delivery Notes sheet
            if delivery_notes:
                df_delivery_notes = pd.DataFrame(delivery_notes)
                df_delivery_notes.to_excel(writer, sheet_name='Delivery Notes', index=False)
        
        # Save file to Frappe
        with open('customer_portal_data.xlsx', 'rb') as f:
            file_content = f.read()
        
        file_doc = save_file(
            'customer_portal_data.xlsx',
            file_content,
            'Customer Portal Data',
            'Customer Portal',
            is_private=1
        )
        
        return {"file_url": file_doc.file_url}
        
    except Exception as e:
        frappe.log_error(f"Error in export_dashboard_excel: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist()
def export_dashboard_pdf():
    """Export dashboard data to PDF"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Customer not found"}
        
        # Get dashboard data
        stats = get_dashboard_statistics()
        recent_transactions = get_recent_transactions(20)
        
        # Create HTML content
        html_content = f"""
        <html>
        <head>
            <title>Customer Portal Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .stats {{ display: flex; justify-content: space-around; margin-bottom: 30px; }}
                .stat-item {{ text-align: center; }}
                .transactions {{ margin-top: 30px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Customer Portal Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="stats">
                <div class="stat-item">
                    <h3>{stats.get('total_invoices', 0)}</h3>
                    <p>Total Invoices</p>
                </div>
                <div class="stat-item">
                    <h3>{stats.get('total_quotations', 0)}</h3>
                    <p>Total Quotations</p>
                </div>
                <div class="stat-item">
                    <h3>{stats.get('total_deliveries', 0)}</h3>
                    <p>Total Deliveries</p>
                </div>
                <div class="stat-item">
                    <h3>{stats.get('total_sales_orders', 0)}</h3>
                    <p>Total Sales Orders</p>
                </div>
            </div>
            
            <div class="transactions">
                <h2>Recent Transactions</h2>
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
        
        for transaction in recent_transactions:
            html_content += f"""
                        <tr>
                            <td>{transaction['date']}</td>
                            <td>{transaction['type']}</td>
                            <td>{transaction['reference']}</td>
                            <td>{transaction['amount']}</td>
                            <td>{transaction['status']}</td>
                        </tr>
            """
        
        html_content += """
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        
        # Generate PDF
        from frappe.utils.pdf import get_pdf
        pdf_content = get_pdf(html_content)
        
        # Save file to Frappe
        file_doc = save_file(
            'customer_portal_report.pdf',
            pdf_content,
            'Customer Portal Report',
            'Customer Portal',
            is_private=1
        )
        
        return {"file_url": file_doc.file_url}
        
    except Exception as e:
        frappe.log_error(f"Error in export_dashboard_pdf: {str(e)}")
        return {"error": str(e)} 

@frappe.whitelist()
def export_ledger_excel(filters=None):
    """Export ledger data to Excel"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Customer not found"}
        
        # Get ledger data
        ledger_data = get_customer_ledger(filters, 1, 10000)  # Get all data
        
        if ledger_data and ledger_data.get('entries'):
            df = pd.DataFrame(ledger_data['entries'])
            df.to_excel('customer_ledger.xlsx', index=False)
            
            with open('customer_ledger.xlsx', 'rb') as f:
                file_content = f.read()
            
            file_doc = save_file(
                'customer_ledger.xlsx',
                file_content,
                'Customer Ledger',
                'Customer Portal',
                is_private=1
            )
            
            return {"file_url": file_doc.file_url}
        
        return {"error": "No data to export"}
        
    except Exception as e:
        frappe.log_error(f"Error in export_ledger_excel: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist()
def export_ledger_pdf(filters=None):
    """Export ledger data to PDF"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Customer not found"}
        
        # Get ledger data
        ledger_data = get_customer_ledger(filters, 1, 10000)
        
        if not ledger_data or not ledger_data.get('entries'):
            return {"error": "No data to export"}
        
        # Create HTML content
        html_content = f"""
        <html>
        <head>
            <title>Customer Ledger Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .text-right {{ text-align: right; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Customer Ledger Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Voucher Type</th>
                        <th>Voucher No</th>
                        <th>Against</th>
                        <th>Debit</th>
                        <th>Credit</th>
                        <th>Balance</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for entry in ledger_data['entries']:
            html_content += f"""
                    <tr>
                        <td>{entry.get('posting_date', '')}</td>
                        <td>{entry.get('voucher_type', '')}</td>
                        <td>{entry.get('voucher_no', '')}</td>
                        <td>{entry.get('against', '')}</td>
                        <td class="text-right">{entry.get('debit', 0)}</td>
                        <td class="text-right">{entry.get('credit', 0)}</td>
                        <td class="text-right">{entry.get('balance', 0)}</td>
                    </tr>
            """
        
        html_content += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        # Generate PDF
        from frappe.utils.pdf import get_pdf
        pdf_content = get_pdf(html_content)
        
        # Save file to Frappe
        file_doc = save_file(
            'customer_ledger.pdf',
            pdf_content,
            'Customer Ledger Report',
            'Customer Portal',
            is_private=1
        )
        
        return {"file_url": file_doc.file_url}
        
    except Exception as e:
        frappe.log_error(f"Error in export_ledger_pdf: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist()
def export_invoices_excel(filters=None):
    """Export invoices data to Excel"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Customer not found"}
        
        # Get invoices data
        invoices_data = get_customer_invoices(filters, 1, 10000)
        
        if invoices_data and invoices_data.get('invoices'):
            df = pd.DataFrame(invoices_data['invoices'])
            df.to_excel('customer_invoices.xlsx', index=False)
            
            with open('customer_invoices.xlsx', 'rb') as f:
                file_content = f.read()
            
            file_doc = save_file(
                'customer_invoices.xlsx',
                file_content,
                'Customer Invoices',
                'Customer Portal',
                is_private=1
            )
            
            return {"file_url": file_doc.file_url}
        
        return {"error": "No data to export"}
        
    except Exception as e:
        frappe.log_error(f"Error in export_invoices_excel: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist()
def export_invoices_pdf(filters=None):
    """Export invoices data to PDF"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Customer not found"}
        
        # Get invoices data
        invoices_data = get_customer_invoices(filters, 1, 10000)
        
        if not invoices_data or not invoices_data.get('invoices'):
            return {"error": "No data to export"}
        
        # Create HTML content
        html_content = f"""
        <html>
        <head>
            <title>Customer Invoices Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .text-right {{ text-align: right; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Customer Invoices Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Invoice No</th>
                        <th>Date</th>
                        <th>Customer</th>
                        <th>Amount</th>
                        <th>Outstanding</th>
                        <th>Status</th>
                        <th>Due Date</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for invoice in invoices_data['invoices']:
            html_content += f"""
                    <tr>
                        <td>{invoice.get('name', '')}</td>
                        <td>{invoice.get('posting_date', '')}</td>
                        <td>{invoice.get('customer_name', '')}</td>
                        <td class="text-right">{invoice.get('grand_total', 0)}</td>
                        <td class="text-right">{invoice.get('outstanding_amount', 0)}</td>
                        <td>{invoice.get('status', '')}</td>
                        <td>{invoice.get('due_date', '')}</td>
                    </tr>
            """
        
        html_content += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        # Generate PDF
        from frappe.utils.pdf import get_pdf
        pdf_content = get_pdf(html_content)
        
        # Save file to Frappe
        file_doc = save_file(
            'customer_invoices.pdf',
            pdf_content,
            'Customer Invoices Report',
            'Customer Portal',
            is_private=1
        )
        
        return {"file_url": file_doc.file_url}
        
    except Exception as e:
        frappe.log_error(f"Error in export_invoices_pdf: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist()
def export_quotations_excel(filters=None):
    """Export quotations data to Excel"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Customer not found"}
        
        # Get quotations data
        quotations_data = get_customer_quotations(filters, 1, 10000)
        
        if quotations_data and quotations_data.get('quotations'):
            df = pd.DataFrame(quotations_data['quotations'])
            df.to_excel('customer_quotations.xlsx', index=False)
            
            with open('customer_quotations.xlsx', 'rb') as f:
                file_content = f.read()
            
            file_doc = save_file(
                'customer_quotations.xlsx',
                file_content,
                'Customer Quotations',
                'Customer Portal',
                is_private=1
            )
            
            return {"file_url": file_doc.file_url}
        
        return {"error": "No data to export"}
        
    except Exception as e:
        frappe.log_error(f"Error in export_quotations_excel: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist()
def export_quotations_pdf(filters=None):
    """Export quotations data to PDF"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Customer not found"}
        
        # Get quotations data
        quotations_data = get_customer_quotations(filters, 1, 10000)
        
        if not quotations_data or not quotations_data.get('quotations'):
            return {"error": "No data to export"}
        
        # Create HTML content
        html_content = f"""
        <html>
        <head>
            <title>Customer Quotations Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .text-right {{ text-align: right; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Customer Quotations Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Quotation No</th>
                        <th>Date</th>
                        <th>Customer</th>
                        <th>Amount</th>
                        <th>Status</th>
                        <th>Valid Till</th>
                        <th>Valid Days</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for quotation in quotations_data['quotations']:
            html_content += f"""
                    <tr>
                        <td>{quotation.get('name', '')}</td>
                        <td>{quotation.get('transaction_date', '')}</td>
                        <td>{quotation.get('party_name', '')}</td>
                        <td class="text-right">{quotation.get('grand_total', 0)}</td>
                        <td>{quotation.get('status', '')}</td>
                        <td>{quotation.get('valid_till', '')}</td>
                        <td>{quotation.get('valid_days', '')}</td>
                    </tr>
            """
        
        html_content += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        # Generate PDF
        from frappe.utils.pdf import get_pdf
        pdf_content = get_pdf(html_content)
        
        # Save file to Frappe
        file_doc = save_file(
            'customer_quotations.pdf',
            pdf_content,
            'Customer Quotations Report',
            'Customer Portal',
            is_private=1
        )
        
        return {"file_url": file_doc.file_url}
        
    except Exception as e:
        frappe.log_error(f"Error in export_quotations_pdf: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist()
def export_sales_orders_excel(filters=None):
    """Export sales orders data to Excel"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Customer not found"}
        
        # Get sales orders data
        sales_orders_data = get_customer_sales_orders(filters, 1, 10000)
        
        if sales_orders_data and sales_orders_data.get('sales_orders'):
            df = pd.DataFrame(sales_orders_data['sales_orders'])
            df.to_excel('customer_sales_orders.xlsx', index=False)
            
            with open('customer_sales_orders.xlsx', 'rb') as f:
                file_content = f.read()
            
            file_doc = save_file(
                'customer_sales_orders.xlsx',
                file_content,
                'Customer Sales Orders',
                'Customer Portal',
                is_private=1
            )
            
            return {"file_url": file_doc.file_url}
        
        return {"error": "No data to export"}
        
    except Exception as e:
        frappe.log_error(f"Error in export_sales_orders_excel: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist()
def export_sales_orders_pdf(filters=None):
    """Export sales orders data to PDF"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Customer not found"}
        
        # Get sales orders data
        sales_orders_data = get_customer_sales_orders(filters, 1, 10000)
        
        if not sales_orders_data or not sales_orders_data.get('sales_orders'):
            return {"error": "No data to export"}
        
        # Create HTML content
        html_content = f"""
        <html>
        <head>
            <title>Customer Sales Orders Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .text-right {{ text-align: right; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Customer Sales Orders Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Sales Order No</th>
                        <th>Date</th>
                        <th>Customer</th>
                        <th>Amount</th>
                        <th>Status</th>
                        <th>Delivery Status</th>
                        <th>Delivery Date</th>
                        <th>% Delivered</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for sales_order in sales_orders_data['sales_orders']:
            html_content += f"""
                    <tr>
                        <td>{sales_order.get('name', '')}</td>
                        <td>{sales_order.get('transaction_date', '')}</td>
                        <td>{sales_order.get('customer_name', '')}</td>
                        <td class="text-right">{sales_order.get('grand_total', 0)}</td>
                        <td>{sales_order.get('status', '')}</td>
                        <td>{sales_order.get('delivery_status', '')}</td>
                        <td>{sales_order.get('delivery_date', '')}</td>
                        <td>{sales_order.get('per_delivered', 0)}%</td>
                    </tr>
            """
        
        html_content += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        # Generate PDF
        from frappe.utils.pdf import get_pdf
        pdf_content = get_pdf(html_content)
        
        # Save file to Frappe
        file_doc = save_file(
            'customer_sales_orders.pdf',
            pdf_content,
            'Customer Sales Orders Report',
            'Customer Portal',
            is_private=1
        )
        
        return {"file_url": file_doc.file_url}
        
    except Exception as e:
        frappe.log_error(f"Error in export_sales_orders_pdf: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist()
def export_delivery_notes_excel(filters=None):
    """Export delivery notes data to Excel"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Customer not found"}
        
        # Get delivery notes data
        delivery_notes_data = get_customer_delivery_notes(filters, 1, 10000)
        
        if delivery_notes_data and delivery_notes_data.get('delivery_notes'):
            df = pd.DataFrame(delivery_notes_data['delivery_notes'])
            df.to_excel('customer_delivery_notes.xlsx', index=False)
            
            with open('customer_delivery_notes.xlsx', 'rb') as f:
                file_content = f.read()
            
            file_doc = save_file(
                'customer_delivery_notes.xlsx',
                file_content,
                'Customer Delivery Notes',
                'Customer Portal',
                is_private=1
            )
            
            return {"file_url": file_doc.file_url}
        
        return {"error": "No data to export"}
        
    except Exception as e:
        frappe.log_error(f"Error in export_delivery_notes_excel: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist()
def export_delivery_notes_pdf(filters=None):
    """Export delivery notes data to PDF"""
    try:
        customer = get_customer_from_user()
        if not customer:
            return {"error": "Customer not found"}
        
        # Get delivery notes data
        delivery_notes_data = get_customer_delivery_notes(filters, 1, 10000)
        
        if not delivery_notes_data or not delivery_notes_data.get('delivery_notes'):
            return {"error": "No data to export"}
        
        # Create HTML content
        html_content = f"""
        <html>
        <head>
            <title>Customer Delivery Notes Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .text-right {{ text-align: right; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Customer Delivery Notes Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Delivery Note No</th>
                        <th>Date</th>
                        <th>Customer</th>
                        <th>Amount</th>
                        <th>Status</th>
                        <th>Delivery Type</th>
                        <th>Delivery Date</th>
                        <th>% Billed</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for delivery_note in delivery_notes_data['delivery_notes']:
            html_content += f"""
                    <tr>
                        <td>{delivery_note.get('name', '')}</td>
                        <td>{delivery_note.get('posting_date', '')}</td>
                        <td>{delivery_note.get('customer_name', '')}</td>
                        <td class="text-right">{delivery_note.get('grand_total', 0)}</td>
                        <td>{delivery_note.get('status', '')}</td>
                        <td>{delivery_note.get('delivery_type', '')}</td>
                        <td>{delivery_note.get('delivery_date', '')}</td>
                        <td>{delivery_note.get('per_billed', 0)}%</td>
                    </tr>
            """
        
        html_content += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        # Generate PDF
        from frappe.utils.pdf import get_pdf
        pdf_content = get_pdf(html_content)
        
        # Save file to Frappe
        file_doc = save_file(
            'customer_delivery_notes.pdf',
            pdf_content,
            'Customer Delivery Notes Report',
            'Customer Portal',
            is_private=1
        )
        
        return {"file_url": file_doc.file_url}
        
    except Exception as e:
        frappe.log_error(f"Error in export_delivery_notes_pdf: {str(e)}")
        return {"error": str(e)} 