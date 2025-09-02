# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

def create_customer_user_permission_on_login():
    """Create user permission for customer after login when session is established"""
    
    try:
        user = frappe.session.user
        
        # Skip for standard users
        if user in ["Administrator", "Guest"]:
            return
        
        # Ignore user permissions during this operation to avoid circular permission checks
        frappe.flags.ignore_permissions = True
        
        # Check if user exists and get user document
        if not frappe.db.exists("User", user):
            frappe.logger().warning(f"User {user} does not exist in database")
            return
        
        user_doc = frappe.get_doc("User", user)
        
        # Check if user has Isoft Customer Portal user type
        if user_doc.user_type != "Isoft Customer Portal":
            return
        
        # Check if user has Customer Portal role
        user_roles = frappe.get_roles(user)
        
        if "Customer Portal" not in user_roles:
            # Auto-add the role if missing
            user_doc.add_roles("Customer Portal")
            user_doc.save()
            frappe.db.commit()
        
        # Find customer linked to this user
        customer = get_customer_from_user(user)
        
        if not customer:
            frappe.logger().warning(f"No customer found linked to user {user}")
            return
        
        # Create user permissions for Customer access
        create_user_permission_if_not_exists(user, "Customer", customer)
        
        # Create user permissions for sales documents
        create_sales_document_permissions(user, customer)
        
        # Also create permissions for Contact if the user is linked via Contact
        contact = frappe.db.get_value("Contact", {"user": user}, "name")
        if contact:
            create_user_permission_if_not_exists(user, "Contact", contact)
        
        frappe.logger().info(f"Successfully created/verified user permissions for customer portal user {user}")
        
    except Exception as e:
        error_msg = f"Error creating customer user permission for {frappe.session.user}: {str(e)}"
        frappe.logger().error(error_msg)
        frappe.log_error(error_msg, "Customer Portal Login Hook Error")
            
    finally:
        # Reset the ignore permissions flag
        frappe.flags.ignore_permissions = False

def create_sales_document_permissions(user, customer):
    """Create user permissions for sales documents for the customer portal user"""
    frappe.logger().info(f"Creating sales document permissions for user {user} and customer {customer}")
    
    # List of document types and their customer field mapping
    sales_doctypes = {
        "Sales Invoice": "customer",
        "Quotation": "party_name", 
        "Payment Entry": "party", 
        "Sales Order": "customer",
        "Delivery Note": "customer"
    }
    
    for doctype, customer_field in sales_doctypes.items():
        try:
            # Get all documents of this type for the customer
            documents = get_customer_documents(doctype, customer_field, customer)
            frappe.logger().info(f"Found {len(documents)} {doctype} documents for customer {customer}")
            
            # Check which documents don't have user permissions yet
            documents_without_permissions = get_documents_without_user_permissions(user, doctype, documents)
            frappe.logger().info(f"Creating permissions for {len(documents_without_permissions)} {doctype} documents without existing permissions")
            
            # Create user permissions for documents that don't have them
            for doc_name in documents_without_permissions:
                create_user_permission_if_not_exists(user, doctype, doc_name)
                
        except Exception as e:
            frappe.logger().error(f"Error creating permissions for {doctype}: {str(e)}")
            continue

def get_customer_documents(doctype, customer_field, customer):
    """Get all documents of a specific type for a customer"""
    try:
        # Handle Payment Entry special case (party_type + party)
        if doctype == "Payment Entry":
            documents = frappe.get_all(doctype, 
                                     filters={
                                         "party_type": "Customer",
                                         "party": customer
                                     }, 
                                     fields=["name"])
        else:
            # Standard case with customer field
            documents = frappe.get_all(doctype, 
                                     filters={customer_field: customer}, 
                                     fields=["name"])
        
        return [doc.name for doc in documents]
        
    except Exception as e:
        frappe.logger().error(f"Error getting {doctype} documents for customer {customer}: {str(e)}")
        return []

def get_documents_without_user_permissions(user, doctype, documents):
    """Get list of documents that don't have user permissions for the user"""
    if not documents:
        return []
    
    try:
        # Get existing user permissions for this user and doctype
        existing_permissions = frappe.get_all("User Permission", 
                                            filters={
                                                "user": user,
                                                "allow": doctype
                                            }, 
                                            fields=["for_value"])
        
        existing_doc_names = [perm.for_value for perm in existing_permissions]
        
        # Return documents that don't have permissions yet
        documents_without_permissions = [doc for doc in documents if doc not in existing_doc_names]
        
        return documents_without_permissions
        
    except Exception as e:
        frappe.logger().error(f"Error checking existing permissions for {doctype}: {str(e)}")
        return documents  # Return all documents if check fails

@frappe.whitelist()
def create_missing_user_permissions_for_customer(customer, user=None):
    """
    Manually create user permissions for existing documents for a specific customer
    Can be called via API or from console
    """
    if not user:
        user = frappe.session.user
    
    frappe.logger().info(f"Creating missing user permissions for customer {customer} and user {user}")
    
    try:
        # Verify user is a customer portal user
        user_doc = frappe.get_doc("User", user)
        if user_doc.user_type != "Isoft Customer Portal":
            return {
                "success": False,
                "message": f"User {user} is not a Customer Portal user"
            }
        
        # Verify user is linked to this customer
        linked_customer = get_customer_from_user(user)
        if linked_customer != customer:
            return {
                "success": False,
                "message": f"User {user} is not linked to customer {customer}. Linked to: {linked_customer}"
            }
        
        # Create permissions for existing documents
        frappe.flags.ignore_permissions = True
        
        # Create customer permission first
        create_user_permission_if_not_exists(user, "Customer", customer)
        
        # Create sales document permissions
        create_sales_document_permissions(user, customer)
        
        # Create contact permission if applicable
        contact = frappe.db.get_value("Contact", {"user": user}, "name")
        if contact:
            create_user_permission_if_not_exists(user, "Contact", contact)
        
        # Get final count of permissions
        final_permissions = frappe.get_all("User Permission", 
                                         filters={"user": user}, 
                                         fields=["allow", "for_value"])
        
        frappe.db.commit()
        
        return {
            "success": True,
            "message": f"Created user permissions for customer {customer}",
            "total_permissions": len(final_permissions),
            "permissions": final_permissions
        }
        
    except Exception as e:
        frappe.logger().error(f"Error creating missing permissions: {str(e)}")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }
    finally:
        frappe.flags.ignore_permissions = False

def create_user_permission_if_not_exists(user, doctype, for_value, apply_to_specific_doctype=None):
    """Create user permission if it doesn't exist"""
    
    # Check if permission already exists
    existing_permission = frappe.db.exists("User Permission", {
        "user": user,
        "allow": doctype,
        "for_value": for_value
    })
    
    if existing_permission:
        frappe.logger().info(f"User permission already exists: {user} -> {doctype} -> {for_value}")
        return existing_permission
    
    try:
        # Ensure all values are strings and properly formatted
        user = str(user).strip()
        doctype = str(doctype).strip()
        for_value = str(for_value).strip()
        
        # Use direct SQL insert for more control (fallback method)
        try:
            # Method 1: Try with frappe.get_doc() but with better error handling
            user_permission = frappe.new_doc("User Permission")
            user_permission.user = user
            user_permission.allow = doctype
            user_permission.for_value = for_value
            
            if apply_to_specific_doctype:
                user_permission.apply_to_all_doctypes = 0
            else:
                user_permission.apply_to_all_doctypes = 1
            
            # Insert the document
            user_permission.insert(ignore_permissions=True)
            
            # Add applicable_for after successful insert if needed
            if apply_to_specific_doctype:
                user_permission.append("applicable_for", {
                    "applicable_for": str(apply_to_specific_doctype).strip()
                })
                user_permission.save(ignore_permissions=True)
            
            permission_id = user_permission.name
            
        except Exception as doc_error:
            # Method 2: Direct SQL insert (more reliable for simple cases)
            permission_id = frappe.generate_hash(length=10)
            
            # Insert main User Permission record
            frappe.db.sql("""
                INSERT INTO `tabUser Permission` 
                (name, creation, modified, modified_by, owner, docstatus, idx, user, allow, for_value, apply_to_all_doctypes)
                VALUES (%(name)s, NOW(), NOW(), %(user)s, %(user)s, 0, 1, %(user)s, %(allow)s, %(for_value)s, %(apply_all)s)
            """, {
                "name": permission_id,
                "user": user,
                "allow": doctype,
                "for_value": for_value,
                "apply_all": 0 if apply_to_specific_doctype else 1
            })
            
            # Insert applicable_for record if needed
            if apply_to_specific_doctype:
                frappe.db.sql("""
                    INSERT INTO `tabUser Permission Applicable For`
                    (name, creation, modified, modified_by, owner, docstatus, idx, parent, parenttype, parentfield, applicable_for)
                    VALUES (%(name)s, NOW(), NOW(), %(user)s, %(user)s, 0, 1, %(parent)s, 'User Permission', 'applicable_for', %(applicable_for)s)
                """, {
                    "name": frappe.generate_hash(length=10),
                    "user": user,
                    "parent": permission_id,
                    "applicable_for": apply_to_specific_doctype
                })
        
        # Commit the transaction
        frappe.db.commit()
        
        # Verify it was created
        created_permission = frappe.db.exists("User Permission", {
            "user": user,
            "allow": doctype,
            "for_value": for_value
        })
        
        if created_permission:
            frappe.logger().info(f"Created user permission: {user} -> {doctype} -> {for_value} (ID: {created_permission})")
            return created_permission
        else:
            frappe.logger().error(f"User permission not found after creation: {user} -> {doctype} -> {for_value}")
            return None
            
    except Exception as e:
        error_msg = f"Error creating user permission {user} -> {doctype} -> {for_value}: {str(e)}"
        frappe.logger().error(error_msg)
        frappe.log_error(error_msg, "User Permission Creation Error")
        return None

def has_customer_permission(doc, ptype, user):
    """Check if user has permission to access customer documents"""
    if not user:
        return False
    
    # Allow system managers and administrators
    if frappe.has_permission(doc.doctype, ptype, user=user):
        return True
    
    # Only apply custom permissions for Isoft Customer Portal users
    try:
        user_doc = frappe.get_doc("User", user)
        if user_doc.user_type != "Isoft Customer Portal":
            return False  # Let standard Frappe permissions handle other user types
    except Exception:
        return False
    
    # Check if user is linked to a customer
    customer = get_customer_from_user(user)
    if not customer:
        return False
    
    # For customer documents, check if the customer matches
    if hasattr(doc, 'customer') and doc.customer == customer:
        return True
    
    if hasattr(doc, 'party_name') and doc.party_name == customer:
        return True
    
    return False

def get_customer_from_user(user=None):
    """Get customer linked to user"""
    if not user:
        user = frappe.session.user
    
    # Check if user is directly linked to a customer via email_id field
    customer = frappe.db.get_value("Customer", {"email_id": user}, "name")
    if customer:
        return customer
    
    # Check if user is linked to a customer via Contact
    contact = frappe.db.get_value("Contact", {"user": user}, "name")
    if contact:
        # Get customer from contact links
        customer_links = frappe.get_all("Dynamic Link", {
            "parent": contact,
            "parenttype": "Contact",
            "link_doctype": "Customer"
        }, ["link_name"])
        
        if customer_links:
            return customer_links[0].link_name
    
    return None

def validate_customer_access():
    """Validate customer access for current user - only for Isoft Customer Portal users"""
    user = frappe.session.user
    
    # Skip for standard users
    if user in ["Administrator", "Guest"]:
        return None
    
    # Only validate for Isoft Customer Portal users
    try:
        user_doc = frappe.get_doc("User", user)
        if user_doc.user_type != "Isoft Customer Portal":
            return None  # Not a customer portal user
    except Exception:
        return None
    
    customer = get_customer_from_user(user)
    return customer

def get_user_type_info():
    """Get user type information for current user"""
    user = frappe.session.user
    
    if user in ["Administrator", "Guest"]:
        return None
    
    try:
        user_doc = frappe.get_doc("User", user)
        if user_doc.user_type == "Isoft Customer Portal":
            customer = get_customer_from_user(user)
            return {
                "user_type": "Isoft Customer Portal",
                "customer": customer,
                "has_customer_access": bool(customer)
            }
    except Exception:
        pass
    
    return None

@frappe.whitelist(allow_guest=True)
def check_customer_auth():
    """Check if current user is authenticated as customer - only for Isoft Customer Portal users"""
    try:
        user = frappe.session.user
        
        if not user or user == 'Guest':
            return {"authenticated": False, "message": "Not authenticated"}
        
        # Check if user has Isoft Customer Portal user type
        try:
            user_doc = frappe.get_doc("User", user)
            if user_doc.user_type != "Isoft Customer Portal":
                return {"authenticated": False, "message": "Not an Isoft Customer Portal user"}
        except Exception:
            return {"authenticated": False, "message": "User type check failed"}
        
        # Check if user has Customer Portal role
        user_roles = frappe.get_roles(user)
        if "Customer Portal" not in user_roles:
            return {"authenticated": False, "message": "Customer Portal role required"}
        
        # Get customer information
        customer = get_customer_from_user()
        if not customer:
            return {"authenticated": False, "message": "No customer linked to user"}
        
        return {
            "authenticated": True,
            "user": user,
            "customer": customer,
            "user_type": "Isoft Customer Portal"
        }
        
    except Exception as e:
        frappe.log_error(f"Customer auth check error: {str(e)}")
        return {"authenticated": False, "message": "Authentication check failed"}