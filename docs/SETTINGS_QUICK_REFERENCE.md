# System Settings - Quick Reference

## Initialization

```python
# In main.py - call once at app startup
from services.settings_service import SettingsService
SettingsService.initialize()
```

## Access Settings

```python
from services.settings_service import SettingsService

# Get category objects
app = SettingsService.get_app_settings()
security = SettingsService.get_security_settings()
payment = SettingsService.get_payment_settings()
listing = SettingsService.get_listing_settings()
notification = SettingsService.get_notification_settings()
admin = SettingsService.get_admin_settings()
features = SettingsService.get_feature_flags()

# Get specific setting
value = SettingsService.get_setting('app', 'theme_mode')

# Check feature flag
if SettingsService.is_feature_enabled('enable_map_view'):
    show_map()

# Get all settings
all_settings = SettingsService.get_settings()
```

## Update Settings

```python
# Update single setting
success, msg = SettingsService.update_setting('security', 'password_min_length', 10)
if success:
    print(msg)  # Setting security.password_min_length updated from 8 to 10

# Update multiple
updates = {
    'security': {'password_min_length': 10, 'session_timeout_minutes': 120},
    'payment': {'transaction_fee_percentage': 2.5}
}
success, msg = SettingsService.update_settings(updates)

# Reset all to defaults
success, msg = SettingsService.reset_to_defaults()
```

## Import/Export

```python
# Export to JSON
success, msg = SettingsService.export_settings('backup_settings.json')

# Import from JSON
success, msg = SettingsService.import_settings('backup_settings.json')

# Get change history
history = SettingsService.get_settings_history(limit=20)
for change in history:
    print(f"{change['changed_at']}: {change['changed_by']}")
```

## Settings Categories

### AppSettings
```python
app = SettingsService.get_app_settings()
# app.app_name, app.app_version, app.theme_mode, app.language
# app.timezone, app.debug_mode, app.log_level
```

### SecuritySettings
```python
security = SettingsService.get_security_settings()
# security.password_min_length, security.password_require_uppercase
# security.password_require_numbers, security.password_require_special
# security.password_expiry_days, security.session_timeout_minutes
# security.max_login_attempts, security.lockout_duration_minutes
# security.enable_2fa, security.require_email_verification
# security.require_pm_document_verification
# security.sql_injection_protection, security.csrf_protection
```

### PaymentSettings
```python
payment = SettingsService.get_payment_settings()
# payment.currency_code, payment.currency_symbol
# payment.payment_methods_enabled (list)
# payment.minimum_payment_amount, payment.maximum_payment_amount
# payment.payment_timeout_minutes, payment.enable_refunds
# payment.refund_deadline_days, payment.transaction_fee_percentage
# payment.transaction_fee_fixed, payment.enable_payment_notifications
# payment.automatic_refund_processing
```

### ListingSettings
```python
listing = SettingsService.get_listing_settings()
# listing.listings_per_page, listing.max_images_per_listing
# listing.max_image_size_mb, listing.require_location_verification
# listing.auto_publish_listings, listing.listing_approval_required
# listing.enable_featured_listings, listing.featured_listing_cost
# listing.listing_visibility_radius_km, listing.allow_booking_calendar
# listing.minimum_lease_duration_days, listing.maximum_lease_duration_days
```

### NotificationSettings
```python
notification = SettingsService.get_notification_settings()
# notification.enable_email_notifications
# notification.enable_sms_notifications
# notification.enable_in_app_notifications
# notification.enable_push_notifications
# notification.email_notifications_batch_size
# notification.notification_retention_days
# notification.enable_weekly_digest
# notification.enable_reservation_reminders
# notification.reminder_days_before_reservation
# notification.enable_payment_notifications
# notification.enable_activity_notifications
# notification.email_service_provider
```

### AdminSettings
```python
admin = SettingsService.get_admin_settings()
# admin.items_per_page, admin.enable_activity_logging
# admin.activity_log_retention_days, admin.enable_audit_trail
# admin.enable_export_data, admin.enable_bulk_operations
# admin.require_admin_verification_for_changes
# admin.show_system_metrics, admin.enable_performance_monitoring
# admin.enable_user_analytics, admin.sensitive_data_masking
```

### FeatureFlags
```python
features = SettingsService.get_feature_flags()
# features.enable_advanced_search
# features.enable_map_view
# features.enable_virtual_tours
# features.enable_instant_booking
# features.enable_reviews_and_ratings
# features.enable_tenant_verification
# features.enable_pm_verification
# features.enable_recommended_listings
# features.enable_bulk_messaging
# features.enable_contract_management
# features.enable_maintenance_requests
# features.enable_payment_plans
# features.enable_referral_program
# features.enable_landlord_insurance
```

## Common Patterns

### Password Validation
```python
from services.settings_service import SettingsService

def validate_password(password: str) -> tuple[bool, str]:
    security = SettingsService.get_security_settings()

    if len(password) < security.password_min_length:
        return False, f"Min {security.password_min_length} chars"

    if security.password_require_uppercase and not any(c.isupper() for c in password):
        return False, "Requires uppercase"

    if security.password_require_numbers and not any(c.isdigit() for c in password):
        return False, "Requires number"

    if security.password_require_special:
        special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special for c in password):
            return False, "Requires special"

    return True, "Valid"
```

### Feature-driven UI
```python
import flet as ft
from services.settings_service import SettingsService

def build_listings_page():
    listing = SettingsService.get_listing_settings()
    features = SettingsService.get_feature_flags()

    controls = []

    if features.enable_map_view:
        controls.append(build_map_widget())

    if features.enable_advanced_search:
        controls.append(build_advanced_filter())

    controls.append(build_listings_grid(
        per_page=listing.listings_per_page
    ))

    return ft.Column(controls)
```

### Transaction Fee Calculation
```python
def calculate_total_amount(base_amount: float) -> float:
    payment = SettingsService.get_payment_settings()

    percentage_fee = base_amount * (payment.transaction_fee_percentage / 100)
    fixed_fee = payment.transaction_fee_fixed

    return base_amount + percentage_fee + fixed_fee
```

### Pagination Setup
```python
def setup_pagination():
    admin = SettingsService.get_admin_settings()
    items_per_page = admin.items_per_page

    # Use items_per_page for table pagination
    return items_per_page
```

### Session Management
```python
def setup_session_timeout():
    security = SettingsService.get_security_settings()
    timeout_minutes = security.session_timeout_minutes

    # Set session timeout to timeout_minutes
    schedule_logout_after(timeout_minutes * 60)
```

## Admin View Access

Navigate to admin dashboard and select "Settings" to access the admin settings view.

Features:
- 7 category tabs (App, Security, Payment, Listing, Notification, Admin, Features)
- Form auto-generated from settings types
- Save changes, reset to defaults
- Export/import settings as JSON

## Database

Settings stored in `campuskubo.db`:

```sql
-- Get current settings
SELECT settings_json FROM system_settings WHERE settings_id = 'default';

-- Get change history
SELECT * FROM settings_history ORDER BY changed_at DESC LIMIT 20;

-- Count total changes
SELECT COUNT(*) FROM settings_history;
```

## Troubleshooting

**Settings not updating?**
```python
# Force reload from database
SettingsService.reload_from_database()
```

**Type error on import?**
```python
# Validate settings before import
valid, msg = SettingsService.validate_settings(settings_dict)
if not valid:
    print(msg)  # Shows validation error
```

**Can't find setting?**
```python
# Check valid category names
categories = ['app', 'security', 'payment', 'listing', 'notification', 'admin', 'features']

# Get all settings to browse
all_settings = SettingsService.get_settings_as_dict()
print(all_settings)
```

## Files

- **Model:** `app/models/settings.py` (7 dataclasses + master container)
- **Service:** `app/services/settings_service.py` (centralized access)
- **View:** `app/views/admin_settings_view.py` (admin UI)
- **Database:** `app/storage/db.py` (persistence functions)
- **Guide:** `docs/SYSTEM_SETTINGS_GUIDE.md` (full documentation)
- **Implementation:** `docs/SYSTEM_SETTINGS_IMPLEMENTATION.md` (status and details)

## Version Info

- **Module Version:** 1.0
- **Created:** December 2024
- **Status:** Production Ready

---

**Quick Start:**
1. Call `SettingsService.initialize()` in main.py
2. Access settings anywhere: `SettingsService.get_security_settings()`
3. Manage via admin dashboard under "Settings"
