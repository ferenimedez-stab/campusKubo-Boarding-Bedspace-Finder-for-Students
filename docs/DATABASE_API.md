# CampusKubo Database API Reference

## Model-Compatible Functions (NEW)

These functions match the interface expected by `main_model.py`:

### User Management

#### `create_user(full_name: str, email: str, password: str, role: str) -> Tuple[bool, str]`
Creates a new user account with validation.

**Parameters:**
- `full_name`: User's full name
- `email`: Unique email address
- `password`: Password (must meet requirements)
- `role`: "tenant" or "property_manager"

**Returns:** `(success: bool, message: str)`

**Example:**
```python
success, msg = create_user("Juan Dela Cruz", "juan@example.com", "Secure123!", "tenant")
if success:
    print("Account created:", msg)
else:
    print("Error:", msg)
```

**Validation:**
- Email must be valid format and not already registered
- Password must be 8+ chars, 1+ uppercase, 1+ number, 1+ special char
- Full name cannot be empty

---

#### `validate_user(email: str, password: str) -> Optional[Dict]`
Authenticate user credentials.

**Parameters:**
- `email`: User's email
- `password`: User's password (plain text, will be hashed)

**Returns:** `Dict with {id, role, email, full_name}` or `None`

**Example:**
```python
user = validate_user("juan@example.com", "Secure123!")
if user:
    print(f"Logged in as: {user['full_name']}")
    role = user['role']  # 'tenant' or 'property_manager'
else:
    print("Invalid credentials")
```

---

### Property Management

#### `get_properties(search_query: str = "", filters: dict = None) -> List[Dict]`
Search and filter properties.

**Parameters:**
- `search_query`: Search by name/location/description
- `filters`: Dict with optional keys:
  - `price_min`: Minimum price
  - `price_max`: Maximum price
  - `room_type`: Room type (Single/Double/Shared/Studio)
  - `amenities`: Specific amenity
  - `location`: Location string
  - `availability`: Status filter

**Returns:** List of property dictionaries

**Example:**
```python
# Get all properties
all_props = get_properties()

# Search with query
results = get_properties("near campus")

# Filter by price
cheap = get_properties("", {"price_max": 3000})

# Multiple filters
filters = {
    "price_min": 2000,
    "price_max": 5000,
    "room_type": "Double",
    "location": "Quezon City"
}
filtered = get_properties("", filters)
```

---

#### `get_property_by_id(property_id: int) -> Optional[Dict]`
Get a single property by ID.

**Parameters:**
- `property_id`: Property ID

**Returns:** Property dictionary or `None` if not found

**Example:**
```python
prop = get_property_by_id(42)
if prop:
    print(f"Property: {prop['name']}")
    print(f"Price: ₱{prop['price']}/month")
else:
    print("Property not found")
```

**Returned Fields:**
```python
{
    'id': int,
    'pm_id': int,                    # Property manager ID
    'name': str,
    'address': str,
    'location': str,
    'price': float,
    'description': str,
    'room_type': str,                # Single/Double/Shared/Studio
    'total_rooms': int,
    'available_rooms': int,
    'amenities': str,                # Comma-separated
    'status': str,                   # pending/approved/rejected
    'availability_status': str,      # Available/Reserved/Full
    'image_url': str or None,
    'created_at': str
}
```

---

### Validation Functions

#### `validate_password(password: str) -> Tuple[bool, str]`
Check if password meets security requirements.

**Parameters:**
- `password`: Password to validate

**Returns:** `(is_valid: bool, message: str)`

**Requirements:**
- ✅ 8+ characters
- ✅ 1+ uppercase letter
- ✅ 1+ number
- ✅ 1+ special character (!@#$%^&*()_+-=[]{}|;:,.<>?)

**Example:**
```python
valid, msg = validate_password("MyPass123!")
if valid:
    print("Password OK")
else:
    print("Error:", msg)  # "Password must contain at least one uppercase letter"
```

---

#### `validate_email(email: str) -> Tuple[bool, str]`
Check if email is valid and not registered.

**Parameters:**
- `email`: Email to validate

**Returns:** `(is_valid: bool, message: str)`

**Checks:**
- ✅ Valid email format
- ✅ Not already registered
- ✅ Not empty

**Example:**
```python
valid, msg = validate_email("newuser@example.com")
if valid:
    print("Email available")
else:
    print("Error:", msg)  # "Email already registered" or "Invalid email format"
```

---

### Database Initialization

#### `init_db()`
Initialize the database, creating tables if needed.

**Example:**
```python
init_db()  # Safe to call multiple times
```

#### `property_data()`
Seed sample properties if database is empty.

**Example:**
```python
property_data()  # Adds sample listings only if none exist
```

---

## Legacy Functions (Still Available)

These functions are used by the modular system and continue to work:

### User Functions
- `get_user_info(user_id: int)` → Dict or None
- `get_user_by_email(email: str)` → Dict or None
- `create_admin(email: str, password: str, full_name: str)` → bool
- `update_user_full_name(user_id: int, full_name: str)` → bool
- `update_user_password(user_id: int, new_password: str)` → bool
- `delete_user(user_id: int)` → bool

### Property Functions
- `create_listing(pm_id, address, price, description, ...) → bool`
- `get_listings(pm_id=None)` → List[sqlite3.Row]
- `get_listing_by_id(listing_id: int)` → Row or None
- `get_listings_by_status(status: str)` → List[Row]
- `get_listings_by_pm(pm_id: int)` → List[Row]
- `get_listings_by_tenant(tenant_id: int)` → List[Row]
- `update_listing(listing_id, **kwargs)` → bool
- `delete_listing(listing_id: int)` → bool

### Reservation Functions
- `create_reservation(tenant_id, listing_id, start_date, end_date)` → bool
- `get_reservations(tenant_id=None, listing_id=None)` → List[Row]
- `update_reservation_status(reservation_id, status)` → bool
- `cancel_reservation(reservation_id)` → bool

### Activity Logging
- `log_activity(user_id, action, details)` → bool
- `get_activity_log(user_id=None, limit=100)` → List[Row]

### Search
- `search_listings_advanced(search_query, filters)` → List[Row]

---

## Database Schema

### Users Table
```sql
users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,          -- SHA256 hashed
    role TEXT NOT NULL,              -- tenant, property_manager, admin
    full_name TEXT,
    is_verified INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TEXT
)
```

### Listings Table
```sql
listings (
    id INTEGER PRIMARY KEY,
    pm_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    location TEXT,
    price REAL NOT NULL,
    description TEXT,
    room_type TEXT,                  -- Single, Double, Shared, Studio
    total_rooms INTEGER,
    available_rooms INTEGER,
    amenities TEXT,                  -- Comma-separated
    image_url TEXT,
    status TEXT DEFAULT 'pending',   -- pending, approved, rejected
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (pm_id) REFERENCES users(id)
)
```

### Reservations Table
```sql
reservations (
    id INTEGER PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    listing_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT,
    status TEXT DEFAULT 'pending',   -- pending, confirmed, cancelled
    created_at TEXT,
    FOREIGN KEY (tenant_id) REFERENCES users(id),
    FOREIGN KEY (listing_id) REFERENCES listings(id)
)
```

### Activity Logs Table
```sql
activity_logs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    details TEXT,
    timestamp TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

---

## Usage Examples

### Example 1: Complete Signup Flow
```python
from storage.db import create_user, validate_password, validate_email

# Validate inputs
pwd_valid, pwd_msg = validate_password("MyPass123!")
email_valid, email_msg = validate_email("juan@example.com")

if pwd_valid and email_valid:
    # Create account
    success, msg = create_user(
        full_name="Juan Dela Cruz",
        email="juan@example.com",
        password="MyPass123!",
        role="tenant"
    )
    if success:
        print("✅ Account created!")
    else:
        print(f"❌ {msg}")
else:
    if not pwd_valid:
        print(f"❌ Password: {pwd_msg}")
    if not email_valid:
        print(f"❌ Email: {email_msg}")
```

### Example 2: Search and Filter
```python
from storage.db import get_properties, get_property_by_id

# Search all properties
all_listings = get_properties()
print(f"Found {len(all_listings)} properties")

# Search with keyword
near_campus = get_properties("near campus")

# Filter by price
affordable = get_properties("", {
    "price_min": 2000,
    "price_max": 4000
})

# Get specific property
prop = get_property_by_id(5)
if prop:
    print(f"{prop['name']} - ₱{prop['price']}/month")
```

### Example 3: Login and Dashboard
```python
from storage.db import validate_user

email = "juan@example.com"
password = "MyPass123!"

user = validate_user(email, password)
if user:
    print(f"Welcome {user['full_name']}!")

    # Role-based logic
    if user['role'] == 'tenant':
        # Show tenant dashboard
        show_browse_listings()
    elif user['role'] == 'property_manager':
        # Show PM dashboard
        show_manage_properties()
else:
    print("Invalid email or password")
```

---

## Error Handling

All functions handle errors gracefully:

```python
try:
    user = validate_user("test@example.com", "password")
    if user:
        # User authenticated
    else:
        # User not found or password wrong
except Exception as e:
    print(f"Database error: {e}")
```

Errors are logged to stderr but don't crash the application.

---

## Best Practices

1. **Always validate input** before database operations
2. **Use try-except** for database calls
3. **Store passwords hashed only** - never store plaintext
4. **Use session state** for authenticated user info
5. **Parameterize queries** - all built-in functions do this
6. **Call init_db()** at application startup
7. **Check return values** for success/failure

---

## Performance Tips

- Use filters to narrow results: `get_properties("", {"price_max": 5000})`
- Limit activity log queries: `get_activity_log(limit=50)`
- Cache property lists if they don't change frequently
- Use pagination for large result sets (implement in application layer)

---

**Version:** 1.0 (Updated for Model Integration)
**Last Updated:** December 2024
**Database:** SQLite with WAL mode enabled
