# Admin Create/Edit Features - Quick Reference

## How to Test the Features

### Testing Admin Users
1. Start the app and navigate to Admin Dashboard → Users tab
2. Click "Add User" button
3. Fill in form:
   - Full Name: "John Doe"
   - Email: "john@example.com"
   - Phone: "+63-912-345-6789" (optional)
   - Role: Select from dropdown (admin, pm, tenant, system_admin)
   - Password: "Test123!Pass"
   - Active: Toggle on/off
4. Click "Save"
5. Verify snackbar message and table refresh
6. Click edit icon on a user row to test edit mode
7. Form should pre-fill with existing data
8. Modify and save to update

### Testing Admin Listings
1. Navigate to Admin Dashboard → Listings tab
2. Click "Add Listing" button
3. Fill in form:
   - Address: "123 Main St, City"
   - Price: "15000"
   - PM Owner: Select from dropdown (auto-populated with all PMs)
   - Description: "Spacious 2-bedroom apartment near campus"
   - Lodging Details: "Furnished, WiFi included"
   - Status: Select from dropdown (pending, approved, active, rejected, archived)
4. Click "Save"
5. Verify snackbar message and listings refresh
6. Click "Edit" button on a listing card to test edit mode
7. Form should pre-fill with existing listing data
8. Modify and save to update

### Testing Admin Reservations
1. Navigate to Admin Dashboard → Reservations tab
2. Click "Add Reservation" button
3. Fill in form:
   - Listing: Select from dropdown (auto-populated with available listings)
   - Tenant: Select from dropdown (auto-populated with all tenant users)
   - Start Date: "2024-03-01" (YYYY-MM-DD format)
   - End Date: "2024-06-30" (YYYY-MM-DD format)
   - Status: Select from dropdown (pending, approved, active, completed, cancelled)
4. Click "Save"
5. Verify snackbar message and table refresh
6. Click edit icon on a reservation row to test edit mode
7. Form should pre-fill with existing reservation data
8. Modify and save to update

## Key Implementation Details

### Admin Users View File Location
- `app/views/admin_users_view.py`
- Form fields initialized in `__init__`
- Modal methods: `_open_user_form()`, `_close_user_form()`, `_submit_user_form()`

### Admin Listings View File Location
- `app/views/admin_listings_view.py`
- Form fields initialized in `__init__`
- Modal methods: `_open_listing_form()`, `_close_listing_form()`, `_submit_listing_form()`
- Edit button integrated into `build_listing_card()` method

### Admin Reservations View File Location
- `app/views/admin_reservations_view.py`
- Form fields initialized in `__init__`
- Modal methods: `_open_reservation_form()`, `_close_reservation_form()`, `_submit_reservation_form()`
- Edit button added to reservation table rows

## Service Layer Methods

### AdminService Methods
```python
# Users
admin_service.create_user_account(full_name, email, role, password, is_active=True)
admin_service.update_user_account(user_id, full_name, email, role, is_active=True, phone=None)
admin_service.reset_user_password(user_id, new_password)
admin_service.get_all_users_by_role(role_string)  # 'admin', 'pm', 'tenant', 'system_admin'

# Listings
admin_service.create_listing_admin(address, price, description, lodging_details, status, pm_id)
admin_service.update_listing_admin(listing_id, address, price, description, lodging_details, status, pm_id=None)

# Reservations
admin_service.create_reservation_admin(listing_id, tenant_id, start_date, end_date, status='pending')
admin_service.update_reservation_admin(reservation_id, listing_id, tenant_id, start_date, end_date, status)
```

## Common Validation Rules

### Users Form
- All fields required except phone
- Email must be unique (checked by backend)
- Password must meet requirements (as per app policy)
- Phone format is free-text (stored as-is)

### Listings Form
- Address required and non-empty
- Price required, must be numeric and > 0
- PM Owner required (dropdown selection)
- Description optional but recommended
- Lodging Details optional
- Status must be selected

### Reservations Form
- Listing required (dropdown selection)
- Tenant required (dropdown selection)
- Start Date required, format: YYYY-MM-DD
- End Date required, format: YYYY-MM-DD
- Status required (dropdown selection)

## Database Schema Updates

### Users Table (existing)
New fields added:
- `phone` (TEXT, optional)
- `is_active` (INTEGER, default 1)

### Listings Table (existing)
No schema changes needed, existing structure supports all operations

### Reservations Table (existing)
No schema changes needed, existing structure supports all operations

## UI Components Used

### Form Fields
- `ft.TextField` - For text input (address, price, name, email, phone, dates, description)
- `ft.Dropdown` - For selections (role, PM owner, tenant, listing, status)
- `ft.Switch` - For boolean toggle (is_active in users)

### Dialogs and Layout
- `ft.AlertDialog` - For modal form dialogs
- `ft.Container` - For layout and spacing
- `ft.Column` - For vertical stacking of form fields
- `ft.Row` - For horizontal layout (buttons, tabs)

### Feedback
- `ft.SnackBar` - For user feedback messages (success/error)
- `ft.Text` - For labels and messages

## Return Values and Error Handling

### Success
- Returns: `(True, "Success message")`
- Table automatically refreshes via RefreshService
- Snackbar displays success message
- Form closes automatically

### Failure
- Returns: `(False, "Error message")`
- Snackbar displays error message
- Form remains open for user to fix issues
- No table refresh

## Auto-Refresh Pattern

All create/edit operations:
1. Call service method
2. Get (success, message) or (success, message, id) tuple
3. Show snackbar with message
4. If success: close form and refresh table
5. If failure: show error and keep form open

This pattern is implemented identically across users, listings, and reservations views.

## Testing Edge Cases

### Users
- [ ] Duplicate email handling
- [ ] Invalid password format
- [ ] Very long names/emails
- [ ] Special characters in phone
- [ ] Toggle active/inactive status multiple times

### Listings
- [ ] Very high/low prices
- [ ] Very long addresses and descriptions
- [ ] Missing optional fields (description, lodging)
- [ ] Status transitions (pending → approved → active)
- [ ] Price with decimals

### Reservations
- [ ] End date before start date
- [ ] Invalid date format (should show error)
- [ ] Overlapping reservations (may need validation)
- [ ] Status transitions (pending → approved → active → completed)
- [ ] Tenant with active reservations (may need validation)

## Integration with Existing Features

### RefreshService
- All mutations trigger `notify_refresh()`
- Registered views auto-update without explicit refresh calls
- Cross-view consistency maintained

### Session Management
- All views check `SessionState.is_admin()` before allowing admin operations
- Authentication required before accessing admin features

### Navigation
- Admin features accessible from admin dashboard
- Back buttons return to admin dashboard
- URL routes: `/admin_users`, `/admin_listings`, `/admin_reservations`
