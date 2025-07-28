# Isoft Customer Portal

A comprehensive customer portal application for ERPNext that provides customers with real-time access to their business data and transactions.

## Features

### 🏠 Dashboard
- **Real-time Statistics**: View total invoices, quotations, sales orders, delivery notes, and outstanding amounts
- **Recent Transactions**: See latest transactions with status indicators
- **Auto-refresh**: Data updates automatically every 5 minutes
- **Export Options**: Download dashboard data as Excel or PDF

### 📊 Ledger
- **Complete Transaction History**: View all financial transactions
- **Advanced Filtering**: Filter by date range, voucher type, and amount
- **Pagination**: Navigate through large datasets efficiently
- **Summary Statistics**: View total debits, credits, and net balance
- **Export Functionality**: Export filtered data to Excel or PDF

### 📄 Invoices
- **Invoice Management**: View all customer invoices with details
- **Status Tracking**: Monitor invoice status (Draft, Submitted, Paid, Overdue, etc.)
- **Outstanding Amounts**: Track outstanding balances
- **Due Date Monitoring**: View payment due dates
- **Export Reports**: Generate Excel and PDF reports

### 📋 Quotations
- **Quotation Tracking**: View all customer quotations
- **Validity Monitoring**: Track quotation validity periods
- **Status Management**: Monitor quotation status (Draft, Open, Replied, etc.)
- **Export Options**: Download quotation data

### 🛒 Sales Orders
- **Order Management**: View all sales orders
- **Delivery Tracking**: Monitor delivery status and progress
- **Completion Status**: Track order completion percentages
- **Export Reports**: Generate comprehensive reports

### 🚚 Delivery Notes
- **Delivery Tracking**: View all delivery notes
- **Billing Status**: Monitor billing completion
- **Delivery Types**: Track different delivery types
- **Export Functionality**: Download delivery data

## Installation

1. **Install the App**:
   ```bash
   bench get-app isoft_customer_portal
   bench install-app isoft_customer_portal
   ```

2. **Setup Customer Role**:
   The app automatically creates a "Customer" role during installation.

3. **Assign Customer Role**:
   - Go to User Management
   - Edit customer users
   - Add "Customer" role to their profile

4. **Access the Portal**:
   - Customers can access the portal at: `/customer-dashboard`
   - The portal is role-based and only accessible to users with "Customer" role

## Security Features

### 🔐 Role-Based Access Control
- **Customer Role**: Restricted access to customer-specific data only
- **Permission System**: Customers can only view their own documents
- **No Desk Access**: Customers cannot access the ERPNext desk interface

### 🛡️ Data Protection
- **Document-Level Permissions**: Customers can only see their own invoices, quotations, etc.
- **Field-Level Security**: Sensitive information is protected
- **Audit Trail**: All access is logged for security

## API Endpoints

### Dashboard
- `get_dashboard_statistics()`: Get dashboard statistics
- `get_recent_transactions(limit)`: Get recent transactions
- `export_dashboard_excel()`: Export dashboard to Excel
- `export_dashboard_pdf()`: Export dashboard to PDF

### Ledger
- `get_customer_ledger(filters, page, page_length)`: Get ledger entries
- `export_ledger_excel(filters)`: Export ledger to Excel
- `export_ledger_pdf(filters)`: Export ledger to PDF

### Invoices
- `get_customer_invoices(filters, page, page_length)`: Get invoice list
- `export_invoices_excel(filters)`: Export invoices to Excel
- `export_invoices_pdf(filters)`: Export invoices to PDF

### Quotations
- `get_customer_quotations(filters, page, page_length)`: Get quotation list
- `export_quotations_excel(filters)`: Export quotations to Excel
- `export_quotations_pdf(filters)`: Export quotations to PDF

### Sales Orders
- `get_customer_sales_orders(filters, page, page_length)`: Get sales orders
- `export_sales_orders_excel(filters)`: Export sales orders to Excel
- `export_sales_orders_pdf(filters)`: Export sales orders to PDF

### Delivery Notes
- `get_customer_delivery_notes(filters, page, page_length)`: Get delivery notes
- `export_delivery_notes_excel(filters)`: Export delivery notes to Excel
- `export_delivery_notes_pdf(filters)`: Export delivery notes to PDF

## Customization

### Styling
- CSS files are located in: `public/css/isoft_customer_portal.css`
- Customize colors, layouts, and responsive design

### JavaScript
- JS files are located in: `public/js/`
- Each page has its own JavaScript file for functionality

### Templates
- HTML templates are located in: `www/`
- Customize page layouts and content

## Configuration

### Home Page
- Set in `hooks.py`: `home_page = "customer-dashboard"`
- Customers are automatically redirected to dashboard

### Role Home Page
- Configured in `hooks.py`: `role_home_page = {"Customer": "customer-dashboard"}`

### Permissions
- Permission rules are defined in `permissions.py`
- Supports multiple document types with customer-specific access

## Support

For support and questions:
- **Email**: abbasschokor225@gmail.com
- **Publisher**: Abbass Chokor
- **License**: MIT

## Version History

- **v1.0.0**: Initial release with dashboard, ledger, invoices, quotations, sales orders, and delivery notes
- **Features**: Real-time data, export functionality, role-based security, responsive design

## License

This project is licensed under the MIT License - see the license.txt file for details.