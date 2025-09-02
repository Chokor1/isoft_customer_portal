frappe.ui.form.on('User', {
    before_save: function(frm) {
        // Check if user_type is being changed to 'Isoft Customer Portal'
        if (frm.doc.user_type === 'Isoft Customer Portal') {
            // Check if this is a new assignment or user type change
            const old_user_type = frm.doc.__onload && frm.doc.__onload.user_type_before_save;
            const is_user_type_change = old_user_type !== frm.doc.user_type;
            
            if (is_user_type_change && !frm.doc.__user_permission_confirmed) {
                // Prevent save until confirmation
                frappe.validated = false;
                
                // Show confirmation dialog
                frappe.confirm(
                    `<p>You are setting this user's type to <strong>"Isoft Customer Portal"</strong>.</p>
                     <p><strong>The following user permissions will be automatically created when this user is linked to a customer:</strong></p>
                     <ul>
                         <li>Customer (access to their assigned customer)</li>
                         <li>Sales Invoice (for their customer only)</li>
                         <li>Quotation (for their customer only)</li>
                         <li>Payment Entry (for their customer only)</li>
                         <li>Sales Order (for their customer only)</li>
                         <li>Delivery Note (for their customer only)</li>
                     </ul>
                     <p>This will restrict the user to see only documents related to their assigned customer.</p>
                     <p><strong>Do you want to continue?</strong></p>`,
                    () => {
                        // User confirmed - set flag and save
                        frm.doc.__user_permission_confirmed = true;
                        frm.save();
                    },
                    () => {
                        // User cancelled - show message
                        frappe.msgprint({
                            title: __('Save Cancelled'),
                            message: __('User type change cancelled.'),
                            indicator: 'orange'
                        });
                    },
                    __('Confirm Customer Portal User Type'),
                    __('Yes, Continue'),
                    __('Cancel')
                );
                
                return false;
            }
        }
    },

    refresh: function(frm) {
        // Store the original user_type value for comparison
        frm.doc.__onload = frm.doc.__onload || {};
        frm.doc.__onload.user_type_before_save = frm.doc.user_type;
        // Reset confirmation flag
        frm.doc.__user_permission_confirmed = false;
    }
});

