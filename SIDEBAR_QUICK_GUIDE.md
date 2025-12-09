# Quick Integration Guide: Adding Sidebar Menu to Views

## Step-by-Step Integration

### 1. Import the Utility Function
Add this import at the top of your view file:
```python
from utils.sidebar_utils import create_sidebar_menu_button
```

### 2. Add Menu Button to Header
Replace or update your existing header/navbar to include the menu button:

```python
# Before (example):
header = ft.Row(
    controls=[
        ft.Text("Dashboard", size=24, weight="bold"),
    ]
)

# After:
header = ft.Row(
    controls=[
        create_sidebar_menu_button(self.page),  # ← Add this
        ft.Text("Dashboard", size=24, weight="bold"),
    ],
    spacing=12  # Add spacing between items
)
```

## Views to Update

Here's a checklist of views that should have the sidebar menu button:

### ✅ Already Updated:
- [x] `tenant_dashboard_view.py` - Example implementation complete

### 📝 To Update:
- [ ] `pm_dashboard_view.py` - Property Manager dashboard
- [ ] `admin_dashboard_view.py` - Admin dashboard
- [ ] `browse_view.py` - Browse listings (tenant)
- [ ] `rooms_view.py` - Rooms management (PM)
- [ ] `my_tenants_view.py` - Tenant management (PM)
- [ ] `user_profile_view.py` - User profile
- [ ] `pm_profile_view.py` - PM profile
- [ ] `admin_profile_view.py` - Admin profile
- [ ] `tenant_reservations_view.py` - Tenant reservations
- [ ] `tenant_messages_view.py` - Tenant messages

### ❌ Don't Update (Public Views):
- `home_view.py` - Landing page (no login required)
- `login_view.py` - Login page
- `signup_view.py` - Signup page

## Example Implementations

### Example 1: PM Dashboard View
```python
# app/views/pm_dashboard_view.py

from utils.sidebar_utils import create_sidebar_menu_button

class PMDashboardView:
    def build(self):
        # Add menu button to header
        header = ft.Container(
            bgcolor="#FFFFFF",
            padding=20,
            content=ft.Row(
                controls=[
                    create_sidebar_menu_button(self.page),
                    ft.Text("My Listings", size=24, weight="bold"),
                    # ... rest of header controls
                ],
                spacing=12,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )
        # ... rest of view
```

### Example 2: Browse View
```python
# app/views/browse_view.py

from utils.sidebar_utils import create_sidebar_menu_button

class BrowseView:
    def build(self):
        # Add menu button to top navigation
        nav_bar = ft.Row(
            controls=[
                ft.Row([
                    create_sidebar_menu_button(self.page),
                    ft.Text("C🏠mpusKubo", size=22, weight="bold"),
                ], spacing=12),
                # ... other nav items
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        # ... rest of view
```

### Example 3: Rooms View
```python
# app/views/rooms_view.py

from utils.sidebar_utils import create_sidebar_menu_button

class RoomsView:
    def build(self):
        # Header with menu button
        header = ft.Container(
            padding=24,
            bgcolor="#FFFFFF",
            content=ft.Row(
                controls=[
                    create_sidebar_menu_button(self.page),
                    ft.Text("Rooms Management", size=28, weight="bold"),
                ],
                spacing=12
            )
        )
        # ... rest of view
```

## Common Patterns

### Pattern 1: Simple Header (Most Common)
```python
header = ft.Row([
    create_sidebar_menu_button(self.page),
    ft.Text("Title", size=24, weight="bold"),
], spacing=12)
```

### Pattern 2: Header with Actions
```python
header = ft.Row([
    ft.Row([
        create_sidebar_menu_button(self.page),
        ft.Text("Title", size=24, weight="bold"),
    ], spacing=12),
    ft.Row([
        ft.IconButton(icon=ft.icons.NOTIFICATIONS),
        ft.IconButton(icon=ft.icons.LOGOUT),
    ]),
], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
```

### Pattern 3: Container Header
```python
header = ft.Container(
    padding=20,
    bgcolor="#FFFFFF",
    content=ft.Row([
        create_sidebar_menu_button(self.page),
        ft.Text("Title", size=24, weight="bold"),
    ], spacing=12)
)
```

## Testing Checklist

After adding the menu button to a view:
- [ ] Menu button appears in the header
- [ ] Clicking opens the sidebar with slide-in animation
- [ ] Sidebar shows correct navigation items for user role
- [ ] Active route is highlighted with orange indicator
- [ ] Profile picture/initials display correctly
- [ ] Clicking sidebar items navigates correctly
- [ ] Clicking outside sidebar closes it
- [ ] UI layout is not disrupted

## Alternative: Menu Icon Button

If you prefer a simple menu icon instead of the avatar:
```python
from utils.sidebar_utils import create_menu_icon_button

# Use this instead of create_sidebar_menu_button
menu_icon = create_menu_icon_button(self.page)
```

This creates a hamburger menu icon (☰) instead of the user avatar.

## Tips

1. **Consistent Placement**: Always place the menu button as the first item in your header
2. **Spacing**: Use 12px spacing between menu button and title
3. **Alignment**: Use `ft.MainAxisAlignment.SPACE_BETWEEN` for headers with actions on both sides
4. **Color Scheme**: Keep the existing view colors; the sidebar has its own purple theme
5. **Mobile**: The 36x36px menu button is touch-friendly on mobile devices

## Need Help?

If you encounter issues:
1. Check `SIDEBAR_IMPLEMENTATION.md` for detailed documentation
2. Verify sidebar is initialized in `main.py`
3. Ensure user is logged in (has `user_id` in session)
4. Check console for error messages
