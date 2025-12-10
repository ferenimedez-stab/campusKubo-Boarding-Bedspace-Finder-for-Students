# Landing Page (Home View) - Backend Logic Analysis

## 📍 **File**: `app/views/home_view.py`
**Route**: `/` (root)
**Authentication**: Public (no login required)

---

## 🏗️ **Architecture Overview**

### **Design Pattern**: MVC (Model-View-Controller)
- **View**: `HomeView` class - UI rendering
- **Model/Data**: `app/storage/db.py` - Database queries
- **Controller**: Route handler in `app/main.py`

### **Data Flow**
```
User visits "/"
  → main.py route_change()
  → HomeView.build()
  → get_properties() [DB query]
  → Featured listings rendered
  → User interactions (search, filters)
  → Session storage + navigation
```

---

## 🔍 **Backend Logic Breakdown**

### **1. Route Initialization** (`app/main.py` line 122)

```python
if page.route == "/":
    page.views.append(HomeView(page).build())
```

**Logic**:
- No authentication check (public access)
- Creates new `HomeView` instance with page context
- Calls `build()` to generate the view
- Appends to `page.views` stack

---

### **2. Data Fetching** (`home_view.py` lines 38-43)

```python
try:
    all_properties = get_properties() or []
    featured_properties = all_properties[:5]  # First 5 only
except Exception:
    featured_properties = []
```

**Backend Call**: `get_properties()` in `app/storage/db.py` line 2310

**Logic**:
1. Queries database for **approved listings only**
2. No search/filter parameters on initial load
3. Defaults to empty list on error (graceful degradation)
4. Takes first 5 properties for "Featured" section

**Error Handling**:
- ✅ Try/except wraps DB call
- ⚠️ Silent failure (no error message to user)
- ✅ Graceful fallback to empty list

---

### **3. Database Query: `get_properties()`**

**Location**: `app/storage/db.py` lines 2310-2402

#### **Base Query**
```sql
SELECT id, pm_id, name, address, location, price, description,
       room_type, total_rooms, available_rooms, available_room_types,
       amenities, availability_status, image_url, image_url_2,
       image_url_3, image_url_4, status, created_at
FROM listings
WHERE status = 'approved'
```

**Security**: ✅ Parameterized query (SQL injection safe)

#### **Filter Logic** (Dynamic WHERE clauses)

**1. Search Query** (lines 2328-2331)
```python
if search_query := (search_query or "").strip():
    pattern = f"%{search_query}%"
    query += " AND (name LIKE ? OR location LIKE ? OR address LIKE ? OR description LIKE ?)"
    params.extend([pattern] * 4)
```
- Searches across: name, location, address, description
- Case-insensitive `LIKE` with wildcards
- ✅ Uses parameterized placeholders (not f-string in SQL)

**2. Price Range** (lines 2333-2338)
```python
if filters.get("price_min") is not None:
    query += " AND price >= ?"
    params.append(filters["price_min"])
if price_max := filters.get("price_max"):
    query += " AND price <= ?"
    params.append(price_max)
```
- Independent min/max filters
- Allows one-sided ranges (e.g., only max price)

**3. Room Type** (lines 2340-2348)
```python
if room_types := filters.get("room_type"):
    if isinstance(room_types, str):
        room_types = [room_types]
    placeholders = ",".join(["?"] * len(room_types))
    query += f" AND (room_type IN ({placeholders})"
    params.extend(room_types)
    for rt in room_types:
        query += " OR available_room_types LIKE ?"
        params.append(f'%"{rt}"%')
    query += ")"
```
- Supports single or multiple room types
- Checks both `room_type` column AND `available_room_types` JSON array
- ✅ Dynamic placeholder generation for IN clause

**4. Amenities** (lines 2350-2355)
```python
if amenities := filters.get("amenities"):
    if isinstance(amenities, str):
        amenities = [amenities]
    for amenity in amenities:
        query += " AND amenities LIKE ?"
        params.append(f'%"{amenity}"%')
```
- Searches within JSON array using `LIKE` pattern
- Multiple amenities = AND logic (all must be present)

**5. Availability Status** (lines 2357-2360)
```python
if availability := filters.get("availability"):
    query += " AND availability_status = ?"
    params.append(availability)
```
- Exact match on status (Available, Reserved, Full)

**6. Location** (lines 2362-2366)
```python
if location := filters.get("location"):
    pattern = f"%{location.strip()}%"
    query += " AND (location LIKE ? OR address LIKE ?)"
    params.extend([pattern, pattern])
```
- Searches both `location` and `address` fields
- Partial match with wildcards

**Sorting** (line 2368)
```sql
ORDER BY created_at DESC
```
- Newest listings first

#### **Post-Processing** (lines 2371-2382)
```python
for prop in result:
    for field in ["amenities", "available_room_types"]:
        if prop.get(field) and isinstance(prop[field], str):
            try:
                prop[field] = json.loads(prop[field])
            except:
                prop[field] = []
```
- Deserializes JSON strings to Python lists
- Graceful fallback to empty list on parse error

**Return Value**: `List[Dict]` - Array of property dictionaries

---

## 🎨 **UI Component Logic**

### **4. Filter Dialogs** (lines 47-249)

Each filter (Price, Room Type, Amenities, Location) follows same pattern:

**Example: Price Filter** (lines 47-94)

```python
def show_price_filter(e):
    price_min = ft.TextField(...)
    price_max = ft.TextField(...)

    def apply_price(e):
        if price_min.value:
            filters["price_min"] = float(price_min.value)
        if price_max.value:
            filters["price_max"] = float(price_max.value)
        dialog.open = False
        self.page.update()
        # Show confirmation snackbar
```

**State Management**:
- `filters` dict defined in local scope (line 35)
- ⚠️ **Issue**: Filters stored in local variable, not persisted
- User applies filter → updates dict → closes dialog
- ⚠️ **Missing**: No re-query or UI refresh after filter application
- ⚠️ **Missing**: Filters not passed to `/browse` route

**Logic Flow**:
1. User clicks filter button → Opens dialog
2. User sets values → `apply_*()` callback
3. Updates `filters` dict
4. Closes dialog + shows snackbar
5. ❌ **No action taken** - featured listings unchanged

---

### **5. Search Functionality** (lines 471-473)

```python
def _perform_search(self, query):
    self.page.session.set("search_query", query)
    self.page.session.set("filters", {})
    self.page.go("/browse")
```

**Logic**:
- Stores search query in session (Flet's session storage)
- Resets filters to empty dict
- Navigates to `/browse` route
- ✅ Proper handoff - browse view reads session data

---

### **6. Featured Listings Rendering** (lines 298-323)

```python
def listing_card(property_data, show_details_button=True):
    listing_payload = dict(property_data)
    listing_payload.setdefault("property_name", property_data.get("name") or property_data.get("address"))
    listing_payload.setdefault("description", property_data.get("description", ""))
    listing_payload.setdefault("price", property_data.get("price", 0))

    image_url = property_data.get("image_url")
    property_id = property_data.get("id")
    availability = property_data.get("availability_status", "Available")
    is_available = str(availability).lower() == "available"

    def view_details(_):
        self.page.session.set("selected_property_id", property_id)
        self.page.go("/property-details")

    return create_home_listing_card(
        listing=listing_payload,
        image_url=image_url,
        is_available=is_available,
        on_click=view_details if show_details_button else None,
        show_cta=show_details_button,
        page=self.page,
    )
```

**Logic**:
1. Normalizes property data (handles missing fields)
2. Extracts display fields (name, description, price, image, status)
3. Determines availability (case-insensitive check)
4. Creates click handler:
   - Stores `property_id` in session
   - Navigates to `/property-details`
5. Delegates rendering to `create_home_listing_card()` component

**Card Grid** (lines 325-328)
```python
featured_row = ft.Row(
    scroll=ft.ScrollMode.AUTO,
    controls=[listing_card(prop) for prop in featured_properties] if featured_properties else [ft.Text("No properties available")]
)
```
- Horizontal scroll container
- List comprehension generates cards
- Fallback message if no properties

---

## 🔐 **Security Analysis**

### ✅ **Strengths**
1. **SQL Injection Prevention**: All queries use parameterized placeholders
2. **Public Route**: No sensitive data exposed (only approved listings)
3. **Error Handling**: Try/except prevents crashes
4. **Status Filtering**: Only `status='approved'` listings shown

### ⚠️ **Vulnerabilities/Issues**

1. **No Input Sanitization on Filters**
   - User input passed directly to DB (mitigated by parameterization)
   - No length limits on search queries
   - No validation on price range (could accept negative values)

2. **Silent Error Handling**
   ```python
   except Exception:
       featured_properties = []
   ```
   - No logging of errors
   - Users see empty list, no explanation
   - **Recommendation**: Log errors + show generic error message

3. **JSON Parse Failures**
   ```python
   try:
       prop[field] = json.loads(prop[field])
   except:
       prop[field] = []
   ```
   - Bare except catches all exceptions
   - **Recommendation**: Catch specific `json.JSONDecodeError`

4. **No Rate Limiting**
   - No protection against rapid repeated queries
   - Could be exploited for DB load

---

## 🐛 **Bugs & Issues**

### **Critical**
1. **Filters Don't Work on Home Page**
   - User applies filter → dialog closes → nothing happens
   - `filters` dict updated but never used
   - Featured listings don't re-fetch
   - **Fix**: Either remove filters from home or re-query after apply

### **Medium**
2. **Filter State Not Persisted**
   - Filters stored in local variable, lost on navigation
   - Not passed to browse route
   - **Fix**: Store in session like search query does

3. **No Validation on Price Input**
   ```python
   filters["price_min"] = float(price_min.value)
   ```
   - Can raise `ValueError` if non-numeric
   - No try/except around conversion
   - **Fix**: Add validation before float()

4. **Hardcoded Limit for Featured**
   ```python
   featured_properties = all_properties[:5]
   ```
   - Always shows 5 or fewer
   - No pagination or "see more"
   - Could be configurable

### **Minor**
5. **Property Name Fallback Logic**
   ```python
   property_data.get("name") or property_data.get("address")
   ```
   - If `name` exists but is empty string, uses name (not address)
   - Should check truthiness: `property_data.get("name") or property_data.get("address") or "Unnamed"`

---

## 🔄 **Data Dependencies**

### **Required Database Tables**
- `listings` - Main property data
  - Columns: id, pm_id, name, address, location, price, description, room_type, amenities, availability_status, image_url, status, created_at
  - Filter: `status = 'approved'`

### **Session Data** (written)
- `search_query` - User's search term (for browse view)
- `selected_property_id` - Clicked property (for detail view)

### **Session Data** (not used but should be)
- `filters` - Set to `{}` when searching, but home filters not stored

---

## 🎯 **User Journey**

### **1. Landing**
```
User opens app → "/" route
  → HomeView.build()
  → get_properties() fetches first 5 approved listings
  → Displays: hero, search bar, filter buttons, featured cards
```

### **2. Search**
```
User types query → presses Enter
  → _perform_search() called
  → Session stores query
  → Navigates to /browse
  → BrowseView reads session.search_query
```

### **3. View Details**
```
User clicks property card
  → view_details() callback
  → Session stores property_id
  → Navigates to /property-details
  → PropertyDetailView reads session.selected_property_id
```

### **4. Filter (Broken)**
```
User clicks "Price" → Dialog opens
User sets min/max → Clicks "Apply"
  → filters dict updated
  → Dialog closes
  → Snackbar: "Filter applied"
  ❌ UI unchanged (filters not used)
```

---

## 📊 **Performance Characteristics**

### **Query Performance**
- **Initial Load**: Single `SELECT` with `WHERE status='approved'`
  - No JOINs
  - Indexed on `created_at` for ORDER BY
  - ✅ Fast for moderate dataset (<10k listings)

### **Scalability Issues**
1. **No Pagination**: Fetches ALL approved listings
   - If 10,000 approved listings → loads all in memory
   - First 5 displayed, rest discarded
   - **Impact**: Unnecessary DB load, memory usage
   - **Fix**: Add `LIMIT 5` to query

2. **JSON Parsing on Every Load**
   - Deserializes amenities/room_types for all results
   - Even though only 5 displayed
   - **Fix**: Parse only displayed items

### **Recommended Optimization**
```python
# Instead of:
all_properties = get_properties()
featured_properties = all_properties[:5]

# Do:
featured_properties = get_properties(limit=5)
```

Then update DB function:
```python
def get_properties(limit=None, offset=0, ...):
    # ... build query ...
    if limit:
        query += f" LIMIT {int(limit)} OFFSET {int(offset)}"
```

---

## ✅ **Recommendations**

### **High Priority**
1. **Fix Filter Functionality**
   - Option A: Remove filters from home (keep only on browse)
   - Option B: Re-fetch listings after filter apply
   - Option C: Store filters in session and navigate to browse

2. **Add Input Validation**
   ```python
   try:
       min_val = float(price_min.value) if price_min.value else None
       if min_val and min_val < 0:
           raise ValueError("Price cannot be negative")
   except ValueError as e:
       show_error_snackbar(str(e))
       return
   ```

3. **Add Query Limit**
   ```python
   featured_properties = get_properties(limit=5)
   ```

### **Medium Priority**
4. **Error Logging**
   ```python
   except Exception as e:
       print(f"[HomeView] Error fetching properties: {e}", file=sys.stderr)
       log_activity(None, "Error", f"Home page property fetch failed: {e}")
       featured_properties = []
   ```

5. **User Feedback on Errors**
   - Show snackbar if property fetch fails
   - "Unable to load listings. Please try again."

6. **Filter State Persistence**
   ```python
   def apply_price(e):
       # ... validation ...
       self.page.session.set("home_filters", filters)
   ```

### **Low Priority**
7. **Configurable Featured Count**
   ```python
   FEATURED_COUNT = int(os.getenv('FEATURED_LISTINGS_COUNT', '5'))
   ```

8. **Add Metrics/Analytics**
   - Track which properties are clicked
   - Monitor search queries
   - A/B test featured listings

---

## 📝 **Summary**

### **Strengths**
- ✅ Clean separation of concerns (view/model)
- ✅ Secure database queries (parameterized)
- ✅ Graceful error handling (no crashes)
- ✅ Good UX (search, filters, navigation)

### **Critical Issues**
- ❌ Filters don't actually filter listings
- ❌ No input validation on user input
- ❌ Fetches all listings but displays 5

### **Code Quality**: B+
**Security**: A- (good but needs error logging)
**Performance**: C+ (inefficient query, no pagination)
**Maintainability**: A (clean, readable code)
**Functionality**: C (broken filters)

---

**Next Steps**: Would you like me to analyze:
1. Browse View (`/browse`) - Full search/filter implementation
2. Property Detail View - Individual listing display
3. Login/Signup flows - Authentication logic
4. Or fix the identified issues in the home view?
