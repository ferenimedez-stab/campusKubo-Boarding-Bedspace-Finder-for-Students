# CampusKubo - Model Integration Guide

## Overview

A complete model-based implementation of CampusKubo has been created that matches the provided UI design. The system now has two parallel implementations:

1. **Modular Architecture** (`main.py`) - Current production system with reusable components
2. **Single-File Model** (`main_model.py`) - New implementation matching the provided design

## What Was Created

### Database Functions (Updated `storage/db.py`)

Added model-compatible adapter functions that wrap existing database functionality:

```python
# Model-compatible functions
validate_password(password: str) -> tuple[bool, str]
validate_email(email: str) -> tuple[bool, str]
property_data()  # Seed initial data
get_properties(search_query: str, filters: dict) -> List[Dict]
get_property_by_id(id: int) -> Optional[Dict]
create_user(full_name, email, password, role) -> tuple[bool, str]
```

**Key Changes:**
- Updated `create_user()` signature to match model: `(full_name, email, password, role)`
- Returns tuple `(success: bool, message: str)` for better user feedback
- Added comprehensive password and email validation
- Existing functions remain backward compatible with current system

### New Main File (`app/main_model.py`)

A complete single-file application (1500+ lines) that implements the provided model:

#### Features Implemented:
1. **Home/Landing View**
   - Hero search bar
   - Featured property listings grid
   - Interactive filter dialogs (price, room type, amenities, location, availability)
   - Call-to-action for guest browsing
   - Navigation bar with Login/Register buttons

2. **Browse Listings View**
   - Sidebar with advanced filters
   - Property grid with cards
   - Search functionality
   - Filter application and clearing
   - SignupBanner component integration
   - Responsive layout

3. **Property Details View**
   - Full property information display
   - Image gallery placeholder
   - Amenities list
   - Property specs (room type, availability, room count)
   - Action buttons (Reserve/Contact Owner)
   - Authentication dialog for unauthenticated users

4. **Login View**
   - Email and password inputs
   - Error messaging
   - Guest continue option
   - Sign-up link

5. **Signup View**
   - Role selection (Tenant/Property Manager)
   - Form validation
   - Real-time password requirements feedback
   - Terms agreement checkbox
   - Loading indicator
   - Success/error messaging

6. **Dashboards**
   - Tenant Dashboard (browse, reservations)
   - Property Manager Dashboard (add property, view listings, manage reservations)

7. **Routing & Session Management**
   - Protected routes for authenticated users
   - Session state for search queries and filters
   - Role-based access control

## Database Function Compatibility

### Model Expected Interface
```python
from db import (
    get_properties,           # Get filtered listings
    get_property_by_id,       # Get single property
    init_db,                  # Initialize database
    create_user,              # Register new user
    validate_user,            # Authenticate user
    validate_password,        # Check password strength
    validate_email,           # Validate email format
    property_data             # Seed sample data
)
```

### Implementation Status
- ✅ All model functions implemented
- ✅ Backward compatible with existing code
- ✅ Proper type hints and validation
- ✅ Error handling with meaningful messages

## Using the Model Implementation

### Option 1: Replace Main Entry Point
Replace `app/main.py` imports to use the model version:

```bash
# Rename files
mv app/main.py app/main_old.py
mv app/main_model.py app/main.py

# Run application
python -m flet app.main
```

### Option 2: Keep Both Versions
Run both implementations side-by-side:

```bash
# Original modular version
python -m flet app.main

# New model version
python -m flet app.main_model
```

### Option 3: Hybrid Approach
Import specific components from the model version into the existing system as needed.

## Key Differences: Model vs. Modular

### Model Version (`main_model.py`)
- Single-file implementation
- All views defined inline
- Self-contained and simple
- Perfect for learning/prototyping
- ~1500 lines of code

### Modular Version (`main.py`)
- Distributed across multiple files
- Reusable components
- Better for team development
- Easier to maintain and test
- Better separation of concerns

## Database Schema Support

The implementation works with the existing database schema:

```sql
-- users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE,
    password TEXT,  -- SHA256 hashed
    role TEXT,      -- 'tenant', 'property_manager', 'admin'
    full_name TEXT,
    is_verified INTEGER,
    is_active INTEGER,
    created_at TEXT
);

-- listings table
CREATE TABLE listings (
    id INTEGER PRIMARY KEY,
    pm_id INTEGER,
    name TEXT,
    address TEXT,
    location TEXT,
    price REAL,
    description TEXT,
    room_type TEXT,
    total_rooms INTEGER,
    available_rooms INTEGER,
    amenities TEXT,
    status TEXT,  -- 'pending', 'approved', 'rejected'
    created_at TEXT
);

-- Additional tables (reservations, activity logs, etc.)
-- See storage/db.py for full schema
```

## Validation & Security

### Password Requirements
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 number
- At least 1 special character (!@#$%^&*)

### Email Validation
- Valid format check
- Duplicate prevention
- Case-insensitive storage

### Database Security
- SHA256 password hashing
- No plaintext password storage
- SQL parameterization (prevent injection)
- Foreign key constraints
- Transaction rollback on errors

## Testing the Implementation

### Test Signup Flow
1. Navigate to `/signup`
2. Select role (Tenant or Property Manager)
3. Enter valid details
4. Verify password requirements feedback
5. Create account

### Test Login Flow
1. Navigate to `/login`
2. Enter registered email and password
3. Verify redirection to appropriate dashboard
4. Check session state

### Test Browse Flow
1. Visit home page `/`
2. Use filters or search
3. View property details
4. Try to reserve (should prompt login if not authenticated)

### Test Property Details
1. Navigate to browse view
2. Click on property card
3. Verify all details display correctly
4. Check amenities list renders properly

## Integration Notes

### With Existing Components
The model uses these existing components from the modular system:
- `ListingCard` - Property card component
- `SignupBanner` - Signup promotion banner
- `Listing` model - Property data structure

### Database Layer
- Uses existing `storage/db.py` functions
- Adapter functions handle signature differences
- No changes to core database logic

### Session Management
- Uses Flet's `page.session` for state
- Stores: search_query, filters, role, email, selected_property_id
- Session cleared on logout

## Future Enhancements

### Ready for Implementation:
1. **Email Notifications**
   - Confirmation emails
   - Password reset links
   - Reservation updates

2. **Image Uploads**
   - Property image gallery
   - User profile pictures
   - Image validation

3. **Messaging System**
   - Tenant-to-PM communication
   - In-app notifications
   - Message history

4. **Advanced Filtering**
   - Distance-based search
   - Map integration
   - Saved searches

5. **Payment Integration**
   - Reservation deposits
   - Monthly payments
   - Transaction history

## File Structure

```
app/
├── main.py              # Original modular entry point
├── main_model.py        # NEW: Single-file model implementation
├── storage/
│   └── db.py           # UPDATED: Added adapter functions
├── components/
│   ├── listing_card.py
│   ├── signup_banner.py
│   └── ...
├── services/
│   ├── auth_service.py
│   ├── listing_service.py
│   └── ...
├── models/
│   ├── listing.py
│   ├── user.py
│   └── ...
└── views/
    ├── home_view.py
    ├── browse_view.py
    └── ...
```

## Troubleshooting

### Import Errors
**Problem:** `ModuleNotFoundError: No module named 'storage'`

**Solution:** Run from the app directory or ensure PYTHONPATH includes the app folder
```bash
cd app
python -m flet main_model
```

### Database Errors
**Problem:** `database is locked`

**Solution:** Ensure only one instance is running, or use WAL mode (already enabled)

### Session Issues
**Problem:** Session data lost during navigation

**Solution:** Session persists across routes in Flet. Check that `page.session.set()` is called before `page.go()`

## Performance Considerations

- Single-file model: Loads all views on startup
- Modular version: Lazy loads views on demand
- Database queries are optimized with proper indexing
- Caching for property lists is available

## Support & Maintenance

### For Model Version Issues
- Check Flet framework compatibility
- Ensure Python 3.7+
- Verify all imports are available

### For Database Issues
- Check `storage/db.py` for detailed logs
- Verify database file exists in `storage/campuskubo.db`
- Clear database and reinitialize if corrupted: `rm campuskubo.db && python app/storage/db.py`

## Conclusion

The model implementation provides a complete, working version of CampusKubo that matches the provided design. It can be used as-is for development, or serves as a reference for integrating features back into the modular system.

Both implementations are now available and can be maintained in parallel as needed.
