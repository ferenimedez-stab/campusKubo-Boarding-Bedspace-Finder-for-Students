# CampusKubo Feature Testing Guide

## Quick Start

### Running the Application
```cmd
cd app
python main.py
```

The app will launch in Flet viewer. Navigate to `http://localhost:8000` in browser (if applicable to your Flet setup).

---

## Feature Testing Paths

### 1️⃣ Guest Browsing with Advanced Filters

**Path:** Home → Browse Listings → Search & Filter → Property Detail

**Steps:**
1. Start app (will go to `/` route)
2. Look for "Browse Listings" link or button
3. Navigate to `/browse` (manually or via link)
4. **Search Test:**
   - Enter search query (e.g., "dorm", "bedspace")
   - See results update
   - Clear search to show all

5. **Price Filter Test:**
   - Enter `price_min: 5000`
   - Enter `price_max: 15000`
   - Click "Apply Filters"
   - Verify results show only listings in price range

6. **Location Filter Test:**
   - Enter location (e.g., "Quezon City", "Makati")
   - Click "Apply Filters"
   - Verify results match location

7. **Click Property Card:**
   - Select a listing card
   - Should navigate to `/listing/{id}` (ListingDetailExtendedView)
   - See property details, amenities, price

### 2️⃣ Guest Authentication Flow

**Path:** Property Detail (as Guest) → Reserve → Auth Dialog → Signup

**Steps:**
1. View property detail page as unauthenticated user
2. Click "Reserve Now" button
3. **Auth Dialog appears with:**
   - "Create Account" button
   - "Already have an account? Sign in" link
   - Benefits list

4. **Click "Create Account":**
   - Navigate to `/signup`
   - Should see enhanced signup form

5. **Watch Real-Time Validation:**
   - Type in Full Name field (should accept letters/spaces only)
   - Type email → border changes green/red based on format
   - Type password → see strength indicator below password field
   - Watch checkmarks appear as requirements are met:
     ✓ At least 8 characters
     ✓ One uppercase letter
     ✓ One number
     ✓ One special character
   - Type in Confirm Password
   - See green checkmark when passwords match

6. **Complete Signup:**
   - Toggle role (Tenant / Property Manager)
   - Check "I agree to Terms"
   - Click "Create Account"
   - Should see success message
   - Redirected to `/login`

### 3️⃣ Enhanced Signup Validation

**Path:** Direct to `/signup` → Fill Form with Validation

**Steps:**
1. Navigate to `/signup`
2. **Full Name Validation:**
   - Type "John Doe" → accepted
   - Type "John123" → border turns red (invalid)
   - Clear and type "Jane Smith" → green border

3. **Email Validation:**
   - Type "user@example.com" → green border
   - Type "invalid-email" → red border
   - Type "test@mail.co.uk" → green border

4. **Password Strength Display:**
   - Type "pass" → all requirements red/gray
   - Type "Password" → uppercase ✓, others still red
   - Type "Password1" → uppercase ✓, digit ✓, length ✓, special ✗
   - Type "Password1!" → all ✓ green

5. **Confirm Password Match:**
   - Password: "Password1!"
   - Confirm: "Password2!" → red border
   - Confirm: "Password1!" → green border

### 4️⃣ Database Search Function

**Path:** Direct Python test of search_listings_advanced()

**Manual Test:**
```python
# In Python console or test file
from storage.db import search_listings_advanced

# Test 1: All listings
results = search_listings_advanced()
print(f"Found {len(results)} listings")

# Test 2: With search query
results = search_listings_advanced(search_query="dorm")
print(f"Found {len(results)} dorm listings")

# Test 3: With price filter
results = search_listings_advanced(
    filters={'price_min': 5000, 'price_max': 15000}
)
print(f"Found {len(results)} in price range ₱5,000-₱15,000")

# Test 4: With location filter
results = search_listings_advanced(
    filters={'location': 'Quezon City'}
)
print(f"Found {len(results)} in Quezon City")

# Test 5: Combined
results = search_listings_advanced(
    search_query="bedspace",
    filters={
        'price_min': 8000,
        'price_max': 20000,
        'location': 'Makati'
    }
)
print(f"Found {len(results)} matching all criteria")
```

### 5️⃣ Backward Compatibility Check

**Path:** Verify existing features still work

**Tests:**
1. **Admin Dashboard:**
   - Login with admin account
   - Navigate to `/admin` → should work
   - View users, listings, reservations, reports

2. **Tenant Dashboard:**
   - Login with tenant account
   - Navigate to `/tenant` → should work
   - Browse tenant reservations

3. **Property Manager Dashboard:**
   - Login with PM account
   - Navigate to `/pm` → should work
   - Add/edit/manage listings

4. **Old Listing Detail (if exists):**
   - Note: `/listing/{id}` now uses ListingDetailExtendedView
   - Old ListingDetailView still in codebase for reference
   - Can restore by changing main.py route if needed

---

## Troubleshooting

### Issue: `/browse` route not found
- **Solution:** Make sure latest main.py has BrowseView import and route
- Check: `grep "BrowseView" app/main.py`

### Issue: Auth dialog doesn't appear
- **Solution:** Check SessionState.get_email() returns None for guests
- Verify: listing has `status='approved'` in database
- Check: on_action_click() method in ListingDetailExtendedView

### Issue: Password strength indicator not showing
- **Solution:** Ensure password_requirements.py is imported correctly
- Check: signup_form.py has PasswordRequirements import
- Verify: _on_password_change callback is wired to password field

### Issue: Search results empty
- **Solution:** Check database has approved listings
- Run: `python -c "from storage.db import search_listings_advanced; print(len(search_listings_advanced()))"`
- Verify: Listings have status='approved'

### Issue: Type errors when running
- **Solution:** Make sure Flet enums are used (not strings)
  - ❌ `scroll="auto"`
  - ✅ `scroll=ft.ScrollMode.AUTO`
- Check all files have been updated with proper enums

---

## Routes Map

| Route | View | Auth Required | Purpose |
|-------|------|---------------|---------|
| `/` | HomeView | No | Home/landing page |
| `/login` | LoginView | No | User login |
| `/signup` | SignupView | No | User registration (enhanced) |
| `/browse` | BrowseView | No | Guest listing browser (NEW) |
| `/listing/{id}` | ListingDetailExtendedView | No | Property detail (ENHANCED) |
| `/tenant` | Tenant Dashboard | Yes | Tenant view |
| `/profile` | UserProfileView | Yes | User profile |
| `/pm` | PMDashboardView | Yes | PM dashboard |
| `/pm/profile` | PMProfileView | Yes | PM profile |
| `/pm/add` | Add Listing View | Yes | Create listing |
| `/pm/edit/{id}` | Edit Listing View | Yes | Edit listing |
| `/admin` | AdminDashboardView | Yes (Admin) | Admin dashboard |
| `/admin_users` | AdminUsersView | Yes (Admin) | User management |
| `/admin_listings` | AdminListingsView | Yes (Admin) | Listing approval |
| `/admin_reservations` | AdminReservationsView | Yes (Admin) | Reservation mgmt |
| `/admin_payments` | AdminPaymentsView | Yes (Admin) | Payment tracking |
| `/admin_reports` | AdminReportsView | Yes (Admin) | Reports |
| `/admin_pm_verification` | AdminPMVerificationView | Yes (Admin) | PM verification |
| `/logout` | LogoutView | Yes | User logout |

---

## Expected Behaviors

### ✅ Guest Browsing
- Can search for listings without login
- Filters work: price_min, price_max, location
- Click property → sees full details
- Click "Reserve" → auth dialog appears

### ✅ Signup Validation
- Real-time form validation
- Password strength shown with icons
- Email format validation
- Name format validation
- Confirm password match check

### ✅ Property Detail
- Shows address, price, description
- Lists amenities from database
- Shows "Reserve Now" button
- Auth prompt for guests

### ✅ Admin/PM Features
- All existing routes work unchanged
- Admin can still approve listings
- PM can still manage listings
- Session management preserved

---

## Performance Notes

- **Search:** search_listings_advanced() uses indexed price/location columns
- **Filtering:** Works on already-fetched results from browse_view
- **Validation:** Real-time, client-side only (no network calls)
- **Database:** No new tables added (backward compatible)

---

## Success Criteria

✅ Guest can browse properties without authentication
✅ Advanced filters work (price, location, search)
✅ Property detail page shows all information
✅ Auth dialog appears for guest actions
✅ Signup form validates in real-time
✅ Password strength indicator works
✅ Admin/PM/Tenant features unchanged
✅ No type errors or lint warnings
✅ Zero database migrations needed

---

**All systems ready for testing! 🚀**
