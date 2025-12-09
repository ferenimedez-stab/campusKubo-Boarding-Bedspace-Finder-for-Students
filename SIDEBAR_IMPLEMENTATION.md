# Sidebar Navigation Menu Implementation

## Overview
The sidebar navigation menu has been implemented following the reference design with a slide-in animation and dark purple theme (#3F2E7A). The sidebar is accessible from any view where users are authenticated.

## Files Created/Modified

### New Files:
1. **`app/components/sidebar_menu.py`** - Main sidebar component with animation
2. **`app/utils/sidebar_utils.py`** - Utility functions for creating menu buttons

### Modified Files:
1. **`app/main.py`** - Added sidebar initialization
2. **`app/views/tenant_dashboard_view.py`** - Example integration (menu button added)

## How It Works

### 1. Sidebar Component (`sidebar_menu.py`)
The `SidebarMenu` class handles:
- Creating sidebar content based on user role (Tenant/PM/Admin)
- Profile picture display with fallback to initials
- Navigation items with active state indicators
- Slide-in/slide-out animation (300ms ease-out)
- Dark purple theme (#3F2E7A)
- Orange active indicator bar (#FF6B35)

### 2. Integration in Main App
In `main.py`, the sidebar is initialized once:
```python
# Initialize sidebar menu
sidebar = SidebarMenu(page)

# Store sidebar reference in page session for views to access
page.session.set("sidebar", sidebar)
```

### 3. Adding Menu Button to Views

#### Method 1: Using Avatar Button (Recommended)
Import the utility function and add it to your view's header:

```python
from utils.sidebar_utils import create_sidebar_menu_button

# In your build() method:
header = ft.Row(
    controls=[
        create_sidebar_menu_button(self.page),  # Menu avatar button
        ft.Text("Your View Title", size=24, weight="bold"),
    ],
    spacing=12
)
```

#### Method 2: Using Simple Menu Icon
```python
from utils.sidebar_utils import create_menu_icon_button

menu_button = create_menu_icon_button(self.page)
```

## Navigation Items by Role

### Tenant
- Dashboard → `/tenant`
- Browse → `/browse`
- Reservations → `/tenant/reservations`
- Messages → `/tenant/messages`
- Settings → `/tenant/profile`
- Logout

### Property Manager
- Dashboard → `/pm`
- My Listings → `/pm`
- My Tenants → `/my-tenants`
- Rooms → `/rooms`
- Analytics → `/pm/analytics`
- Settings → `/pm/profile`
- Logout

### Administrator
- Dashboard → `/admin`
- Users → `/admin_users`
- PM Verification → `/admin_pm_verification`
- Listings → `/admin_listings`
- Reservations → `/admin_reservations`
- Payments → `/admin_payments`
- Reports → `/admin_reports`
- Settings → `/admin_profile`
- Logout

## Features

### ✅ Slide-in Animation
- Sidebar slides in from the left (-280px → 0px)
- Smooth 300ms ease-out transition
- Backdrop overlay with semi-transparent black (#00000040)

### ✅ Active Route Indicator
- Orange vertical bar (#FF6B35) on the left side of active item
- Bold text for active navigation item
- Automatically detects current route

### ✅ Profile Section
- Displays user avatar (profile picture or initials)
- Shows full name and role label
- Lighter purple background (#4A3A8A)

### ✅ Responsive Profile Picture
- Checks `app/assets/uploads/profile_photos/profile_{user_id}.png`
- Falls back to initials in a circle avatar if no picture found

### ✅ Click Outside to Close
- Clicking the backdrop automatically closes the sidebar
- Clicking a navigation item also closes the sidebar

## Usage Example

Here's how to add the sidebar menu button to any existing view:

```python
"""
Example View with Sidebar Integration
"""
import flet as ft
from utils.sidebar_utils import create_sidebar_menu_button

class MyView:
    def __init__(self, page: ft.Page):
        self.page = page

    def build(self):
        # Create header with menu button
        header = ft.Container(
            padding=20,
            bgcolor="#FFFFFF",
            content=ft.Row(
                controls=[
                    create_sidebar_menu_button(self.page),  # Sidebar menu button
                    ft.Text("My View", size=24, weight="bold"),
                ],
                spacing=12
            )
        )

        # Your view content
        content = ft.Column(
            controls=[
                header,
                # ... rest of your view content
            ]
        )

        return ft.View(
            "/my-view",
            controls=[content]
        )
```

## Styling Details

### Colors
- **Sidebar Background**: `#3F2E7A` (Dark Purple)
- **Profile Section**: `#4A3A8A` (Lighter Purple)
- **Active Indicator**: `#FF6B35` (Orange)
- **Text**: White
- **Backdrop**: `#00000040` (40% Black)

### Dimensions
- **Width**: 280px
- **Active Indicator**: 4px width, 32px height
- **Avatar**: 50x50px (in sidebar), 36x36px (menu button)
- **Animation**: 300ms ease-out

### Typography
- **User Name**: 18px, bold, white
- **Role Label**: 13px, 0.9 opacity, white
- **Navigation Items**: 14px (bold if active, normal otherwise)

## Troubleshooting

### Issue: Menu button doesn't appear
**Solution**: Ensure the sidebar is initialized in `main.py` and stored in `page.session`

### Issue: Sidebar doesn't open
**Solution**: Check that user is logged in (`user_id` in session)

### Issue: Profile picture not showing
**Solution**: Verify the image exists at `app/assets/uploads/profile_photos/profile_{user_id}.png`

### Issue: Active route not highlighted
**Solution**: Ensure the route in `nav_items` matches the current `page.route`

## Next Steps

To add the sidebar to other views:
1. Import `create_sidebar_menu_button` from `utils.sidebar_utils`
2. Add the menu button to your view's header/navbar
3. Test by running the app and clicking the menu button

The sidebar is now ready to use throughout the application without altering the existing UI layout!
