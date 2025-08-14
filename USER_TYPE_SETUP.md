# Isoft Customer Portal User Type Setup

This document explains how to set up and use the new "Isoft Customer Portal" user type for the isoft_customer_portal app.

## Overview

The "Isoft Customer Portal" user type provides customers with **READ-ONLY access** to sales-related documents and customer information through the customer portal. It includes:

- **Read-only access** to all sales documents (Sales Invoice, Quotation, Sales Order, Delivery Note, Payment Entry)
- **Read-only access** to customer profile information (Customer, Address, Contact)
- **Select access** to reference documents for dropdowns and lookups
- **Module access** to Selling, Stock, Accounts, and CRM modules

## Automatic Setup

The user type is automatically created when the `isoft_customer_portal` app is installed or updated. The setup includes:

1. Creating the "Customer Portal" role
2. Creating the "Isoft Customer Portal" user type with all necessary permissions
3. Setting up website pages for the customer portal
4. Assigning the user type to existing customers

## Manual Setup

If you need to manually set up or update the user type, you can use the provided script:

### Option 1: Run from Frappe Bench Console

```bash
# Navigate to your bench directory
cd /path/to/your/bench

# Start the Frappe console
bench console

# Run the setup script
exec(open('apps/isoft_customer_portal/isoft_customer_portal/setup_user_type.py').read())
```

### Option 2: Run as a Custom Command

```bash
# Create a custom command in your bench
bench --site your-site.com execute isoft_customer_portal.setup_user_type.setup_isoft_customer_portal_user_type
```

## User Type Configuration

### Basic Settings

- **Name**: Isoft Customer Portal
- **Role**: Customer Portal
- **Apply User Permission On**: Contact *(Changed from Customer to Contact since Contact contains the email ID)*
- **User ID Field**: user *(Changed from "user_id" to "user" - the actual field name in Contact document)*

### Document Permissions

#### User Doctypes (READ-ONLY access for all documents)

| Document Type | Read | Write | Create | Submit | Cancel | Amend | Delete |
|---------------|------|-------|--------|--------|--------|-------|--------|
| Sales Invoice | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Quotation | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Sales Order | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Delivery Note | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Payment Entry | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Customer | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Address | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Contact | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

**Note**: All documents are set to **READ-ONLY** access. Customers can view their information but cannot modify, create, or delete any documents.

#### Select Doctypes (Reference access)

Customers can view and select from these documents in dropdowns and lookups:

- Company, Currency, Customer Group, Territory
- Payment Terms Template, Mode of Payment
- Sales Partner, Sales Person
- Item Group, Brand, Warehouse
- Cost Center, Project
- Tax Category, Tax Rule
- Letter Head, Print Heading, Terms and Conditions

### Module Access

Customers have access to these modules:
- **Selling**: For sales-related documents
- **Stock**: For delivery and warehouse information
- **Accounts**: For payment and financial information
- **CRM**: For customer relationship management

## Authentication

The customer portal now validates users against the "Isoft Customer Portal" user type. Users must have:

1. The "Customer Portal" role
2. The "Isoft Customer Portal" user type assigned
3. A valid customer account linked to their user profile via Contact document

## User Permission Logic

### Why Contact Instead of Customer?

The user type applies permissions on **Contact** documents because:

1. **Email Authentication**: Contact documents contain the email ID used for user login
2. **User Linking**: Users are linked to the system via Contact documents
3. **Permission Inheritance**: Through Contact → Dynamic Link → Customer relationship
4. **Data Access**: Users can access customer data where their Contact is linked to the Customer

### Why "user" Field Instead of "user_id"?

The **User ID Field** is set to "user" because:

1. **Field Name**: In the Contact document, the field that links to User is named "user"
2. **Standard Frappe**: This is the standard field name used in Frappe for linking to User documents
3. **Database Consistency**: Matches the actual database field name in the Contact doctype

### Permission Flow:
```
User Login → Contact Document (user field) → Dynamic Link → Customer → Sales Documents
```

## Updating Existing Installations

If you have an existing installation, the app will automatically:

1. Update the existing user type with new permissions
2. Add any missing document types or modules
3. Ensure all customers have the correct role and user type
4. **Convert all existing permissions to READ-ONLY**
5. **Change apply_user_permission_on from Customer to Contact**
6. **Change user_id_field from "user_id" to "user"**

## Security Features

- **Complete Read-Only Access**: Customers can only view documents, no modifications allowed
- **Data Protection**: No risk of customers accidentally modifying or deleting important information
- **Audit Trail**: All access is logged and auditable
- **Customer Isolation**: Customers can only access their own documents
- **Contact-Based Permissions**: User access is controlled via Contact document relationships
- **Proper Field Mapping**: Uses correct "user" field name for Contact → User linking

## Use Cases

This read-only setup is ideal for:

- **Viewing Only**: Customers who need to see their invoices, orders, and account information
- **Reporting**: Access to historical data for personal records
- **Reference**: Looking up past transactions and account details
- **Compliance**: Maintaining data integrity by preventing unauthorized changes

## Troubleshooting

### Common Issues

1. **User Type Not Created**: Check the Frappe error logs for any installation errors
2. **Permissions Not Working**: Ensure the user has both the role and user type assigned
3. **Customer Not Found**: Verify the customer is linked to the user via Contact document
4. **Cannot Edit Documents**: This is expected behavior - all documents are read-only
5. **Permission Errors**: Check that Contact documents are properly linked to Customer documents
6. **Field Mapping Issues**: Ensure the user_id_field is set to "user" (not "user_id")

### Manual Verification

You can verify the setup by checking:

```python
# In Frappe console
import frappe

# Check if user type exists
user_type = frappe.get_doc("User Type", "Isoft Customer Portal")
print(f"User Type: {user_type.name}")
print(f"Role: {user_type.role}")
print(f"Apply Permission On: {user_type.apply_user_permission_on}")  # Should be "Contact"
print(f"User ID Field: {user_type.user_id_field}")  # Should be "user"

# Check user doctypes - all should be read-only
for dt in user_type.user_doctypes:
    print(f"Document Type: {dt.document_type}, Read: {dt.read}, Write: {dt.write}, Create: {dt.create}, Delete: {dt.delete}")

# Check select doctypes
for dt in user_type.select_doctypes:
    print(f"Select Document Type: {dt.document_type}")

# Check modules
for m in user_type.user_type_modules:
    print(f"Module: {m.module}")
```

### Logs

Check the Frappe error logs for any issues:

```bash
bench --site your-site.com tail-logs
```

## Support

If you encounter issues with the user type setup, please:

1. Check the Frappe error logs
2. Verify the user type configuration
3. Ensure all required doctypes exist in your system
4. Contact support with specific error messages

## Important Notes

- **All documents are READ-ONLY**: This is by design for security and data integrity
- **No write permissions**: Customers cannot modify any information
- **No create permissions**: Customers cannot create new documents
- **No delete permissions**: Customers cannot delete any documents
- **Select access only**: Reference documents are for dropdown/lookup purposes only
- **Contact-based permissions**: User access is controlled via Contact document relationships
- **Permission inheritance**: Customer data access flows through Contact → Customer relationship
- **Correct field mapping**: User ID Field is "user" (the actual field name in Contact document)
