# Merge Instructions: New Features Integration

## Overview
The provided code includes several new features for tenant and room management. This document outlines what has been merged and what still needs to be integrated.

## ✅ Completed Integrations

### 1. Database Functions (in `app/storage/db.py`)
- ✅ Added `create_tenant(owner_id, name, room_number, room_type, status, avatar)` function
- ✅ Added `get_tenants(owner_id)` function
- ✅ Added `update_tenant(tenant_id, **kwargs)` function
- ✅ Added `delete_tenant(tenant_id)` function
- ✅ Created `tenants` table in database schema

## 🔄 Partial Integrations

### 2. Sidebar Component
- ✅ Sidebar component already exists at `app/components/sidebar.py`
- ⚠️ May need updates to match the new navigation structure (Rooms, My Tenants)

## ❌ Pending Integrations

### 3. New Views Required

#### A. Rooms View (`/rooms` and `/rooms/{property_id}`)
**Features:**
- Property selection screen when no property_id provided
- Room management by category (Single, Double deck for 2, Double deck for 4, Studio Type)
- Sample room data with sequential numbering (01-17)
- Edit/Delete room functionality
- Room status management (Occupied, Vacant, etc.)
- Integration with tenant data

**Location:** Create `app/views/rooms_view.py`

**Key Functions:**
```python
def rooms_view(property_id=None):
    # Property selection or room listing
    pass
```

#### B. My Tenants View (`/my-tenants` and `/my-tenants/{property_id}`)
**Features:**
- Property selection screen
- Tenant listing table with:
  - Name with avatar
  - Room number
  - Room type
  - Status (color-coded)
  - Actions (Edit/Delete)
- Sort by (Name A-Z, Name Z-A)
- Filter by (All, Occupied, Pending, Vacant)
- Add new tenant dialog
- Edit tenant dialog
- Delete confirmation

**Location:** Create `app/views/my_tenants_view.py`

**Key Functions:**
```python
def my_tenants_view(property_id=None):
    # Property selection or tenant listing
    pass
```

### 4. Main Application Updates

#### A. Routing (in `app/main.py`)
Add new routes:
```python
elif page.route == "/rooms":
    page.views.append(rooms_view())
elif page.route.startswith("/rooms/"):
    property_id = int(page.route.split("/")[-1])
    page.views.append(rooms_view(property_id=property_id))
elif page.route == "/my-tenants":
    page.views.append(my_tenants_view())
elif page.route.startswith("/my-tenants/"):
    property_id = int(page.route.split("/")[-1])
    page.views.append(my_tenants_view(property_id=property_id))
```

#### B. Imports
Add to `app/main.py`:
```python
from views.rooms_view import RoomsView
from views.my_tenants_view import MyTenantsView
```

### 5. Enhanced Features from Provided Code

#### A. Profile Edit Dialog
- Inline edit dialog for quick profile updates
- Separate edit profile view (`/profile/edit`)
- Profile picture upload
- Document management for PMs

#### B. Sidebar Improvements
- Sliding animation (left: -280 to left: 0)
- Purple gradient background (#3F2E7A, #4A3A8A)
- Active route indicator (orange bar)
- Profile section at top

#### C. Additional Database Features
The provided code includes these database functions that may not exist:
- `assign_sample_listings_to_user(user_id)` - for demo data
- `init_sample_listings()` - initialize sample data
- Enhanced profile management

## 📋 Implementation Steps

### Step 1: Create Rooms View
1. Create `app/views/rooms_view.py`
2. Implement property selection UI
3. Implement room listing by category
4. Add edit/delete dialogs
5. Connect to tenant database functions

### Step 2: Create My Tenants View
1. Create `app/views/my_tenants_view.py`
2. Implement property selection UI
3. Implement tenant table with filtering/sorting
4. Add tenant dialogs (Add, Edit, Delete)
5. Connect to database functions

### Step 3: Update Routing
1. Modify `app/main.py` route_change function
2. Add new route handlers for `/rooms` and `/my-tenants`
3. Add property_id parameter handling

### Step 4: Update Sidebar
1. Review `app/components/sidebar.py`
2. Ensure "Rooms" and "My Tenants" navigation items exist
3. Update active route detection

### Step 5: Test Integration
1. Test database functions (create/update/delete tenants)
2. Test navigation between views
3. Test property selection flow
4. Test room and tenant management

## 🔍 Key Differences from Current System

### Design Patterns
**Provided Code:**
- Single-file application pattern
- Inline view functions
- Direct database calls in views

**Current System:**
- Class-based views
- Modular components
- Service layer architecture

### Recommendations
1. **Adapt to Current Architecture:** Convert inline functions to class-based views
2. **Use Existing Services:** Integrate with existing `listing_service.py`, `user_service.py`
3. **Maintain Consistency:** Follow current naming conventions and patterns
4. **Preserve Features:** Keep the good UX patterns from provided code (animations, filtering, etc.)

## ⚠️ Important Notes

1. **Database Migration:** The `tenants` table has been added to init_db(). Ensure database is reinitialized or migrated.

2. **Profile Photos:** The provided code uses `uploads/profile_photos/profile_{user_id}.png`. Current system may use different path.

3. **Session Management:** Both systems use `page.session` but may have different key names.

4. **Styling:** Provided code uses specific colors and dimensions. Maintain visual consistency.

5. **Room Numbering:** Rooms are numbered 01-17 with specific type ranges:
   - Single: 01-05
   - Double deck for 2: 06-10
   - Double deck for 4: 11-14
   - Studio Type: 15-17

## 🎯 Next Actions

1. **Priority 1:** Create `rooms_view.py` and `my_tenants_view.py`
2. **Priority 2:** Update routing in `main.py`
3. **Priority 3:** Test tenant management flow
4. **Priority 4:** Enhance sidebar navigation
5. **Priority 5:** Add profile edit features

## 📝 Code Snippets for Quick Reference

### Tenant CRUD Pattern
```python
# Create
tenant_id = create_tenant(user_id, "John Doe", "01", "Single", "Occupied", "J")

# Read
tenants = get_tenants(user_id)

# Update
success = update_tenant(tenant_id, status="Vacant")

# Delete
success = delete_tenant(tenant_id)
```

### Sample Room Data Structure
```python
{
    "room_number": "01",
    "room_type": "Single",
    "name": "John Doe",  # or "Vacant"
    "status": "Occupied"  # or "Vacant", "Pending Move-in", etc.
}
```

## 📚 References
- Original code location: User request message
- Database schema: `app/storage/db.py`
- Current routing: `app/main.py`
- View examples: `app/views/pm_dashboard_view.py`
