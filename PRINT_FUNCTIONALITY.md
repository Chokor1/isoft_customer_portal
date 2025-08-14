# Customer Portal Print Functionality

This document explains how the print functionality works in the Isoft Customer Portal and how to configure print formats.

## Overview

The customer portal provides a unified printing system that:
- Uses print formats configured in `Isoft Customer Portal Settings`
- Falls back to default print formats if none are configured
- Ensures customers can only print their own documents
- Provides a consistent printing experience across all document types

## How It Works

### 1. Print Button Click
When a customer clicks the print button on any document, it calls:
```javascript
isoft_customer_portal.printDocument('Document Type', 'Document Name')
```

### 2. API Call
The JavaScript function calls the `print_document` API method which:
- Validates customer authentication
- Checks document ownership
- Retrieves the appropriate print format from settings
- Returns the print format information

### 3. Print Format Resolution
The system follows this priority order:
1. **Settings Configuration**: Print format specified in `Isoft Customer Portal Settings`
2. **Default Format**: First available print format for the document type
3. **Fallback**: "Standard" format if no others are available

### 4. Print Window
A new window opens with the print view URL containing:
- Document type and name
- Selected print format
- Print trigger
- Language settings

## Configuration

### Print Format Settings

The `Isoft Customer Portal Settings` doctype contains these fields:

| Field | Document Type | Description |
|-------|---------------|-------------|
| `sales_invoice_print_format` | Sales Invoice | Print format for invoices |
| `quotation_print_format` | Quotation | Print format for quotations |
| `sales_order_print_format` | Sales Order | Print format for sales orders |
| `delivery_note_print_format` | Delivery Note | Print format for delivery notes |
| `payment_entry_print_format` | Payment Entry | Print format for payment entries |

### Setting Up Print Formats

1. **Create Print Formats**:
   - Go to Setup → Print → Print Format
   - Create new print formats for each document type
   - Ensure they are enabled and properly configured

2. **Configure Settings**:
   - Go to Isoft Customer Portal → Isoft Customer Portal Settings
   - Set the appropriate print format for each document type
   - Save the settings

3. **Test Printing**:
   - Go to the customer portal
   - Try printing different document types
   - Verify the correct format is used

## API Method

### `print_document(doc_type, doc_name)`

**Parameters:**
- `doc_type`: The document type (e.g., "Sales Invoice")
- `doc_name`: The document name/ID

**Returns:**
```json
{
    "print_format": "Custom Invoice Format",
    "doc_type": "Sales Invoice",
    "doc_name": "ACC-SINV-2024-00001"
}
```

**Error Response:**
```json
{
    "error": "Error message"
}
```

## JavaScript Functions

### Main Print Function
```javascript
printDocument(doctype, docName)
```

**Note**: The print function is now completely self-contained in the portal header template and doesn't depend on external JavaScript files. This ensures it's always available when the page loads.

### Portal Header Function
```javascript
// Self-contained print function in portal header
printDocument(doctype, docName)
```

**Note**: The old `printDocumentWithCustomURLDebug` function has been completely removed. All print functionality now uses the unified `printDocument` function that's built into the portal header.

## Print URL Structure

The generated print URL follows this pattern:
```
/printview?doctype=Sales%20Invoice&name=ACC-SINV-2024-00001&trigger_print=1&format=Custom%20Invoice%20Format&no_letterhead=0&_lang=en
```

**Parameters:**
- `doctype`: Document type (URL encoded)
- `name`: Document name/ID
- `trigger_print`: Set to 1 to automatically trigger print dialog
- `format`: Print format name
- `no_letterhead`: Set to 0 to include letterhead
- `_lang`: Language code (if available)

## Security Features

- **Authentication Required**: Only authenticated customers can print
- **Document Ownership**: Customers can only print their own documents
- **Permission Validation**: Manual validation of customer access
- **Audit Trail**: All print attempts are logged

## Error Handling

### Common Errors

1. **Authentication Required**: User not logged in
2. **Access Denied**: Document doesn't belong to customer
3. **Failed to get print format**: Settings or print format issues
4. **Pop-up Blocked**: Browser blocking new windows

### Error Recovery

- **Settings Missing**: Automatically creates default settings
- **Print Format Missing**: Falls back to available formats
- **Network Issues**: Shows retry message to user

## Troubleshooting

### Print Format Not Working

1. **Check Settings**: Verify print formats are set in Isoft Customer Portal Settings
2. **Print Format Status**: Ensure print formats are enabled
3. **Permissions**: Check if print formats are accessible
4. **Browser Console**: Look for JavaScript errors
5. **Function Availability**: The printDocument function is built into the portal header and should always be available

### Print Window Not Opening

1. **Pop-up Blocker**: Check browser pop-up settings
2. **JavaScript Errors**: Check browser console for errors
3. **API Response**: Verify API returns correct print format
4. **URL Generation**: Check if print URL is properly formed
5. **Frappe Framework**: Ensure Frappe framework is loaded (print function checks for this)

### Wrong Print Format

1. **Settings Configuration**: Verify correct format is set for document type
2. **Print Format Names**: Ensure format names match exactly
3. **Cache Issues**: Clear browser cache and reload
4. **Settings Document**: Check if settings document exists and is accessible
5. **Function Call**: Ensure using `printDocument(doctype, name)` not old functions

## Migration from Old Functions

### What Was Removed

The following old print functions have been completely removed:

- ❌ `printDocumentWithCustomURLDebug(doctype, name, format)`
- ❌ `printDocumentWithCustomURL(doctype, name, format)`
- ❌ `printDocumentWithSettings(doctype, name)`

### What to Use Instead

All print functionality now uses the unified system:

```javascript
// ✅ CORRECT: Use the main function
isoft_customer_portal.printDocument('Sales Invoice', 'ACC-SINV-2024-00001');

// ✅ CORRECT: Use the portal header wrapper
printDocument('Sales Invoice', 'ACC-SINV-2024-00001');
```

### Temporary Fallback (For Cached References)

**Note**: A temporary fallback function has been added to handle any cached references to the old functions. This function will:

1. **Show deprecation warnings** in the browser console
2. **Redirect calls** to the new unified print system
3. **Provide debugging information** to help identify where old calls are coming from
4. **Be removed in future versions**

The fallback function will show console warnings like:
```
⚠️ DEPRECATED: printDocumentWithCustomURLDebug is deprecated and will be removed.
📍 Called from: [stack trace]
🔄 Redirecting to new print system...
💡 Update your code to use: isoft_customer_portal.printDocument(doctype, name)
```

### Migration Steps

1. **Update Print Buttons**: Change all onclick handlers to use `isoft_customer_portal.printDocument`
2. **Remove Old Functions**: Delete any custom print functions that duplicate functionality
3. **Test Functionality**: Verify printing works with the new system
4. **Update Documentation**: Remove references to old function names

### Code Examples

#### Before (Old Way)
```html
<!-- ❌ OLD: Don't use this -->
<button onclick="printDocumentWithCustomURLDebug('Sales Invoice', '${invoice.name}')">
    Print
</button>
```

#### After (New Way)
```html
<!-- ✅ NEW: Use this -->
<button onclick="isoft_customer_portal.printDocument('Sales Invoice', '${invoice.name}')">
    Print
</button>
```

## Best Practices

1. **Print Format Naming**: Use descriptive names for print formats
2. **Testing**: Test print functionality with different document types
3. **Fallbacks**: Always provide fallback print formats
4. **User Feedback**: Show loading and success messages
5. **Error Messages**: Provide clear error messages for troubleshooting

## Examples

### Basic Print Call
```javascript
// Print a sales invoice
printDocument('Sales Invoice', 'ACC-SINV-2024-00001');
```

### Print Button HTML
```html
<button class="btn btn-sm btn-outline-primary print-btn" 
        onclick="event.stopPropagation(); printDocument('Sales Invoice', '${invoice.name}')" 
        title="Print Invoice">
    <i class="fas fa-print"></i>
</button>
```

### Custom Print Format
```javascript
// Custom print function with specific format
function printWithCustomFormat(docType, docName, format) {
    let baseUrl = window.location.origin;
    let printUrl = baseUrl + '/printview?' +
        'doctype=' + encodeURIComponent(docType) +
        '&name=' + encodeURIComponent(docName) +
        '&trigger_print=1' +
        '&format=' + encodeURIComponent(format) +
        '&no_letterhead=0';
    
    window.open(printUrl, '_blank');
}
```

## Support

If you encounter issues with the print functionality:

1. Check the Frappe error logs
2. Verify print format configurations
3. Test with different document types
4. Check browser console for JavaScript errors
5. Contact support with specific error messages
