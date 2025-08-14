# Logout Process Debugging Guide

This guide helps you debug the logout functionality in the Isoft Customer Portal.

## Overview

The logout process involves multiple components:
1. **Client-side logout trigger** (JavaScript)
2. **Server-side logout API** (Python)
3. **Session cleanup** (Database)
4. **Client-side cleanup** (Browser storage)
5. **Redirect to logout page**

## Debugging Steps

### 1. Check Server Logs

Monitor the Frappe logs for logout-related messages:

```bash
# Check Frappe logs
tail -f sites/[your-site]/logs/frappe.log

# Check error logs
tail -f sites/[your-site]/logs/frappe-error.log
```

Look for these debug messages:
- `=== CUSTOMER LOGOUT API STARTED ===`
- `=== CUSTOMER LOGOUT ROUTE STARTED ===`
- Session information and cleanup steps

### 2. Check Browser Console

Open browser developer tools (F12) and check the Console tab for:
- `=== CLIENT-SIDE LOGOUT STARTED ===`
- API call responses
- Session cleanup messages
- Storage clearing messages

### 3. Test Logout API Directly

You can test the logout API directly using curl:

```bash
# Test logout API
curl -X POST "http://your-site/api/method/isoft_customer_portal.api.customer_logout" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json"
```

### 4. Run Debug Scripts

Use the provided debug scripts:

```bash
# Run debug script
bench --site [your-site] console
```

Then in the console:
```python
exec(open('apps/isoft_customer_portal/isoft_customer_portal/debug_logout.py').read())
```

### 5. Check Session Database

Query the sessions table to see if sessions are being cleared:

```sql
-- Check current sessions
SELECT user, sid, lastupdate, device 
FROM `tabSessions` 
WHERE user = 'your-username';

-- Check for orphaned sessions
SELECT user, sid, lastupdate 
FROM `tabSessions` 
WHERE lastupdate < DATE_SUB(NOW(), INTERVAL 1 DAY);
```

### 6. Test Authentication After Logout

After logout, verify the user is no longer authenticated:

```python
# In Frappe console
frappe.call('isoft_customer_portal.api.check_customer_auth')
```

Should return: `{'message': {'authenticated': False}}`

## Common Issues and Solutions

### Issue 1: Session Not Clearing
**Symptoms**: User remains logged in after logout
**Debug Steps**:
1. Check if `frappe.local.login_manager.logout()` is being called
2. Verify session is deleted from database
3. Check if cookies are being cleared

**Solution**: Ensure proper session cleanup in the API

### Issue 2: Client-side Data Not Clearing
**Symptoms**: User data persists in browser
**Debug Steps**:
1. Check browser console for storage clearing messages
2. Verify localStorage and sessionStorage are cleared
3. Check if Frappe session data is cleared

**Solution**: Ensure all client-side cleanup is executed

### Issue 3: Redirect Not Working
**Symptoms**: User stays on current page after logout
**Debug Steps**:
1. Check if logout API returns success
2. Verify redirect URL is correct
3. Check for JavaScript errors

**Solution**: Ensure proper redirect handling

### Issue 4: Authentication Still Valid After Logout
**Symptoms**: User can still access protected pages
**Debug Steps**:
1. Check if session is properly cleared
2. Verify authentication check is working
3. Check if cookies are cleared

**Solution**: Ensure complete session termination

## Debugging Checklist

- [ ] Server logs show logout process started
- [ ] API call returns success
- [ ] Session is cleared from database
- [ ] Client-side storage is cleared
- [ ] User is redirected to logout page
- [ ] Authentication check returns false after logout
- [ ] User cannot access protected pages after logout

## Testing the Logout Process

1. **Login as a customer**
2. **Navigate to any protected page**
3. **Click logout button**
4. **Check browser console for debug messages**
5. **Verify redirect to logout page**
6. **Try to access protected page again (should redirect to login)**
7. **Check server logs for complete process**

## Manual Testing Commands

```python
# Test logout API
frappe.call('isoft_customer_portal.api.customer_logout')

# Check authentication
frappe.call('isoft_customer_portal.api.check_customer_auth')

# Check session status
frappe.session.user
frappe.session.sid

# Check database sessions
frappe.db.sql("SELECT * FROM `tabSessions` WHERE user = %s", frappe.session.user)
```

## Performance Monitoring

Monitor these metrics during logout:
- API response time
- Database session cleanup time
- Client-side cleanup time
- Total logout process time

## Troubleshooting Tips

1. **Clear browser cache** if testing locally
2. **Check network tab** for failed API calls
3. **Verify session cookies** are being cleared
4. **Test with different browsers** to rule out browser-specific issues
5. **Check for JavaScript errors** that might prevent logout

## Log Files to Monitor

- `frappe.log` - General application logs
- `frappe-error.log` - Error logs
- Browser console - Client-side debugging
- Network tab - API call monitoring

## Support

If issues persist, check:
1. Frappe version compatibility
2. Browser compatibility
3. Network connectivity
4. Server configuration
5. Database connectivity 