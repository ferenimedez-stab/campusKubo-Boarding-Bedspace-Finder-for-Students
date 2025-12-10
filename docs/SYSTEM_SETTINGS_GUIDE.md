# System Settings Module - Complete Guide

## Overview

The System Settings Module provides centralized configuration management for the CampusKubo application. It enables administrators to manage application behavior, security policies, payment settings, and feature toggles without modifying code.

### Key Features

✅ **Centralized Configuration** - All settings in one place
✅ **Category-based Organization** - 7 setting categories for different concerns
✅ **Database Persistence** - Settings automatically saved and retrieved from database
✅ **In-memory Caching** - Fast access with optional reload
✅ **Change History** - Track all settings modifications
✅ **Import/Export** - Backup and restore configurations via JSON
✅ **Multi-level Validation** - Type safety and constraint validation
✅ **Feature Flags** - Gradual feature rollout and A/B testing

---

## Architecture

### Component Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│                 ADMIN UI LAYER                          │
│  (admin_settings_view.py)                               │
│  - Settings form builder                                │
│  - Category navigation                                  │
│  - Change tracking                                      │
│  - Import/Export UI                                     │
└────────────────┬────────────────────────────────────────┘
                 │ Uses
                 ↓
┌─────────────────────────────────────────────────────────┐
│            SETTINGS SERVICE                              │
│  (services/settings_service.py)                          │
│  - Centralized settings access                          │
│  - Caching layer                                        │
│  - Persistence coordination                             │
│  - Category accessors                                   │
│  - Feature flag queries                                 │
└────────────────┬────────────────────────────────────────┘
                 │ Uses
                 ↓
┌─────────────────────────────────────────────────────────┐
│            DATA MODELS                                   │
│  (models/settings.py)                                   │
│  - SystemSettings (master container)                    │
│  - AppSettings                                          │
│  - SecuritySettings                                     │
│  - PaymentSettings                                      │
│  - ListingSettings                                      │
│  - NotificationSettings                                 │
│  - AdminSettings                                        │
│  - FeatureFlags                                         │
└────────────────┬────────────────────────────────────────┘
                 │ Uses
                 ↓
┌─────────────────────────────────────────────────────────┐
│          DATABASE FUNCTIONS                              │
│  (storage/db.py)                                        │
│  - get_settings()                                       │
│  - save_settings()                                      │
│  - reset_settings()                                     │
│  - get_all_settings_history()                           │
│  - update_setting_field()                               │
└────────────────┬────────────────────────────────────────┘
                 │ Persists to
                 ↓
┌─────────────────────────────────────────────────────────┐
│         SQLITE DATABASE (campuskubo.db)                 │
│                                                         │
│  system_settings TABLE                                  │
│  ├─ id                                                  │
│  ├─ settings_id (unique key)                            │
│  ├─ settings_json (full config)                         │
│  ├─ created_at                                          │
│  └─ updated_at                                          │
│                                                         │
│  settings_history TABLE                                 │
│  ├─ id                                                  │
│  ├─ settings_id (FK)                                    │
│  ├─ changed_fields                                      │
│  ├─ old_values / new_values                             │
│  ├─ changed_by (admin username)                         │
│  └─ changed_at                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Settings Categories

### 1. App Settings (`AppSettings`)

Core application configuration.

```python
app:
  app_name: "CampusKubo"              # Application name
  app_version: "1.0.0"                # Version string
  theme_mode: "LIGHT"                 # LIGHT, DARK, AUTO
  language: "en"                      # Language code
  timezone: "Asia/Manila"             # Timezone
  debug_mode: false                   # Enable debug logging
  log_level: "INFO"                   # Logging level
```

**Usage:**
```python
from services.settings_service import SettingsService

settings = SettingsService.get_app_settings()
print(settings.app_name)  # CampusKubo
print(settings.theme_mode)  # LIGHT
```

### 2. Security Settings (`SecuritySettings`)

Password policies and authentication settings.

```python
security:
  password_min_length: 8              # Minimum length
  password_require_uppercase: true    # Requires A-Z
  password_require_numbers: true      # Requires 0-9
  password_require_special: true      # Requires !@#$%...
  password_expiry_days: null          # null = no expiry
  session_timeout_minutes: 60         # Session duration
  max_login_attempts: 5               # Failed attempts
  lockout_duration_minutes: 15        # Lockout period
  enable_2fa: false                   # Two-factor auth
  require_email_verification: true    # Email confirmation
  require_pm_document_verification: true
  sql_injection_protection: true      # Parameterized queries
  csrf_protection: true               # CSRF tokens
```

**Usage:**
```python
security = SettingsService.get_security_settings()
if len(password) < security.password_min_length:
    raise ValueError("Password too short")
```

### 3. Payment Settings (`PaymentSettings`)

Financial configuration and payment processing.

```python
payment:
  currency_code: "PHP"                # Currency
  currency_symbol: "₱"                # Display symbol
  payment_methods_enabled:            # Available methods
    - "cash"
    - "card"
    - "online_banking"
  minimum_payment_amount: 1000.0
  maximum_payment_amount: 1000000.0
  payment_timeout_minutes: 30
  enable_refunds: true
  refund_deadline_days: null          # null = unlimited
  transaction_fee_percentage: 0.0     # Percentage fee
  transaction_fee_fixed: 0.0          # Fixed fee amount
  enable_payment_notifications: true
  automatic_refund_processing: false
```

**Usage:**
```python
payment = SettingsService.get_payment_settings()
final_amount = amount + (amount * payment.transaction_fee_percentage / 100)
```

### 4. Listing Settings (`ListingSettings`)

Property and listing management configuration.

```python
listing:
  listings_per_page: 12
  max_images_per_listing: 10
  max_image_size_mb: 5.0
  require_location_verification: true
  auto_publish_listings: false
  listing_approval_required: true
  enable_featured_listings: true
  featured_listing_cost: 500.0        # In currency
  listing_visibility_radius_km: 50.0
  allow_booking_calendar: true
  minimum_lease_duration_days: 30
  maximum_lease_duration_days: null   # null = unlimited
```

**Usage:**
```python
listing = SettingsService.get_listing_settings()
if len(images) > listing.max_images_per_listing:
    raise ValueError("Too many images")
```

### 5. Notification Settings (`NotificationSettings`)

Communication and notification configuration.

```python
notification:
  enable_email_notifications: true
  enable_sms_notifications: false
  enable_in_app_notifications: true
  enable_push_notifications: false
  email_notifications_batch_size: 100
  notification_retention_days: 90
  enable_weekly_digest: true
  enable_reservation_reminders: true
  reminder_days_before_reservation: 1
  enable_payment_notifications: true
  enable_activity_notifications: true
  email_service_provider: "smtp"      # smtp, sendgrid, aws_ses
```

**Usage:**
```python
notif = SettingsService.get_notification_settings()
if notif.enable_email_notifications:
    send_email(user, message)
```

### 6. Admin Settings (`AdminSettings`)

Admin dashboard and management configuration.

```python
admin:
  items_per_page: 10                  # Table pagination
  enable_activity_logging: true
  activity_log_retention_days: 365
  enable_audit_trail: true
  enable_export_data: true
  enable_bulk_operations: true
  require_admin_verification_for_changes: false
  show_system_metrics: true
  enable_performance_monitoring: true
  enable_user_analytics: true
  sensitive_data_masking: true        # Hide PII
```

**Usage:**
```python
admin = SettingsService.get_admin_settings()
pagination_size = admin.items_per_page
```

### 7. Feature Flags (`FeatureFlags`)

Feature toggles for gradual rollout.

```python
features:
  enable_advanced_search: true
  enable_map_view: true
  enable_virtual_tours: false
  enable_instant_booking: false
  enable_reviews_and_ratings: true
  enable_tenant_verification: true
  enable_pm_verification: true
  enable_recommended_listings: true
  enable_bulk_messaging: false
  enable_contract_management: false
  enable_maintenance_requests: false
  enable_payment_plans: false
  enable_referral_program: false
  enable_landlord_insurance: false
```

**Usage:**
```python
features = SettingsService.get_feature_flags()
if features.enable_map_view:
    show_map_widget()
```

---

## Usage Examples

### Basic Settings Access

```python
from services.settings_service import SettingsService

# Initialize (typically done in app startup)
SettingsService.initialize()

# Get all settings
settings = SettingsService.get_settings()

# Get a specific category
security = SettingsService.get_security_settings()
print(security.password_min_length)  # 8

# Get a specific setting
theme = SettingsService.get_setting('app', 'theme_mode')
print(theme)  # LIGHT

# Check if feature enabled
if SettingsService.is_feature_enabled('enable_map_view'):
    show_map()
```

### Updating Settings

```python
# Update single setting
success, msg = SettingsService.update_setting(
    category='app',
    key='theme_mode',
    value='DARK'
)
if success:
    print(msg)  # Setting app.theme_mode updated from LIGHT to DARK

# Update multiple settings
updates = {
    'security': {
        'password_min_length': 10,
        'session_timeout_minutes': 120
    },
    'payment': {
        'transaction_fee_percentage': 2.5
    }
}
success, msg = SettingsService.update_settings(updates)
```

### Feature Flag Usage

```python
# Check if feature is enabled
if SettingsService.is_feature_enabled('enable_virtual_tours'):
    render_virtual_tour_ui()
else:
    show_coming_soon_message()

# Toggle feature for testing
SettingsService.update_setting('features', 'enable_virtual_tours', True)
```

### Settings History

```python
# Get change history
history = SettingsService.get_settings_history(limit=20)
for change in history:
    print(f"{change['changed_at']}: {change['changed_by']} - {change['changed_fields']}")
```

### Import/Export

```python
# Export settings for backup
success, msg = SettingsService.export_settings('backup_settings.json')
if success:
    print(msg)  # Settings exported to backup_settings.json

# Import settings from file
success, msg = SettingsService.import_settings('backup_settings.json')
if success:
    print(msg)  # Settings imported from backup_settings.json
```

---

## Admin UI

### Settings View Features

**Category Navigation:**
- App Settings
- Security
- Payments
- Listings
- Notifications
- Admin
- Features

**Form Fields:**
- Auto-generated based on setting type
- Booleans → Checkboxes
- Numbers → Number fields
- Strings → Text fields
- Lists → JSON text area

**Actions:**
- Save Changes
- Reset to Defaults
- Export Settings (JSON)
- Import Settings (JSON)

### Access URL

```
/admin/settings
```

---

## Database Schema

### system_settings Table

```sql
CREATE TABLE system_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    settings_id TEXT UNIQUE DEFAULT 'default',
    settings_json TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

**Sample Record:**
```json
{
  "settings_id": "default",
  "settings_json": "{...all settings as JSON...}",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### settings_history Table

```sql
CREATE TABLE settings_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    settings_id TEXT NOT NULL,
    changed_fields TEXT,
    old_values TEXT,
    new_values TEXT,
    changed_by TEXT,
    changed_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(settings_id) REFERENCES system_settings(settings_id)
);
```

**Sample Record:**
```sql
INSERT INTO settings_history VALUES (
    1,
    'default',
    'password_min_length,session_timeout_minutes',
    '{"password_min_length": 8, "session_timeout_minutes": 60}',
    '{"password_min_length": 10, "session_timeout_minutes": 120}',
    'admin@campuskubo.com',
    '2024-01-15T10:35:00'
);
```

---

## Configuration Files

### Environment Variables

Can override settings via environment variables:

```bash
# .env
CAMPUSKUBO_DEBUG_MODE=true
CAMPUSKUBO_THEME_MODE=DARK
CAMPUSKUBO_LANGUAGE=tl
CAMPUSKUBO_CURRENCY_CODE=PHP
CAMPUSKUBO_PASSWORD_MIN_LENGTH=10
```

### Settings JSON Structure

```json
{
  "settings_id": "default",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "version": 1,
  "app": {
    "app_name": "CampusKubo",
    "app_version": "1.0.0",
    "theme_mode": "LIGHT",
    "language": "en",
    "timezone": "Asia/Manila",
    "debug_mode": false,
    "log_level": "INFO"
  },
  "security": { ... },
  "payment": { ... },
  "listing": { ... },
  "notification": { ... },
  "admin": { ... },
  "features": { ... }
}
```

---

## Best Practices

### 1. Initialization

Always initialize at app startup:

```python
# In main.py
def main(page: ft.Page):
    SettingsService.initialize()
    # ... rest of app initialization
```

### 2. Caching

Settings are cached in memory for performance:

```python
# Fast - uses cache
theme1 = SettingsService.get_setting('app', 'theme_mode')

# Reload from database if needed
SettingsService.reload_from_database()
theme2 = SettingsService.get_setting('app', 'theme_mode')
```

### 3. Change Tracking

Always assign admin when making changes:

```python
# Database function tracks who made change
save_settings(settings_dict, changed_by='admin@campuskubo.com')
```

### 4. Validation

Validate before updating:

```python
valid, msg = SettingsService.validate_settings(settings_dict)
if not valid:
    handle_error(msg)
```

### 5. Feature Flags

Use feature flags for gradual rollout:

```python
# New feature - disabled by default
if SettingsService.is_feature_enabled('enable_virtual_tours'):
    # Show new feature
else:
    # Show old feature or nothing

# Enable for 10% of users
if user.id % 10 == 0:  # Simple bucketing
    enable_for_this_user = True
```

---

## Migration Guide

### From Hard-coded Config to Settings Module

**Before:**
```python
# config.py (hard-coded)
PASSWORD_MIN_LENGTH = 8
SESSION_TIMEOUT = 60
CURRENCY = "PHP"

# Usage
if len(password) < PASSWORD_MIN_LENGTH:
    raise ValueError()
```

**After:**
```python
# Dynamic and database-backed
security = SettingsService.get_security_settings()
if len(password) < security.password_min_length:
    raise ValueError()

# Change at runtime, no code deployment needed
SettingsService.update_setting('security', 'password_min_length', 10)
```

---

## Performance Considerations

### Caching Strategy

- Settings loaded once on app startup
- Cached in memory for O(1) access
- Reload on demand or via RefreshService

### Query Optimization

- Settings stored as single JSON document (fast retrieval)
- History kept for audit trail (not frequently queried)
- Consider archiving old history monthly

### Database Indexes

```sql
CREATE INDEX idx_settings_id ON system_settings(settings_id);
CREATE INDEX idx_history_settings_id ON settings_history(settings_id);
CREATE INDEX idx_history_changed_at ON settings_history(changed_at DESC);
```

---

## Security Considerations

### Access Control

- ✅ Settings view restricted to admin only
- ✅ Settings changes logged in audit trail
- ✅ Change history immutable
- ✅ Sensitive data fields for future masking

### Data Protection

- ✅ Settings stored with updated_at timestamp
- ✅ All changes tracked with changed_by field
- ✅ Export/Import for backup and disaster recovery
- ✅ Parameterized database queries prevent injection

### Validation

- ✅ Type validation at model level
- ✅ Range validation at service level
- ✅ Constraint validation at input level

---

## Common Patterns

### Pattern 1: Password Policy Enforcement

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
            return False, "Requires special character"

    return True, "Valid"
```

### Pattern 2: Feature Flag Rollout

```python
def should_show_feature(user_id: int, feature_name: str) -> bool:
    # Global feature toggle
    if not SettingsService.is_feature_enabled(feature_name):
        return False

    # Gradual rollout to % of users
    rollout_percentage = 10  # 10%
    return (user_id % 100) < rollout_percentage
```

### Pattern 3: Settings-driven UI

```python
def build_admin_dashboard():
    admin_settings = SettingsService.get_admin_settings()
    features = SettingsService.get_feature_flags()

    columns = []

    if admin_settings.show_system_metrics:
        columns.append(build_metrics_panel())

    if admin_settings.enable_activity_logging:
        columns.append(build_activity_log())

    if features.enable_reviews_and_ratings:
        columns.append(build_ratings_panel())

    return ft.Column(columns)
```

---

## Troubleshooting

### Settings Not Persisting

**Problem:** Settings changes don't persist across restarts

**Solution:**
1. Check `campuskubo.db` exists in `app/storage/`
2. Verify `system_settings` table exists: `SELECT * FROM system_settings;`
3. Check database write permissions
4. Review logs for save errors

### Cache Stale Data

**Problem:** Changes made by another instance not visible

**Solution:**
```python
# Force reload from database
SettingsService.reload_from_database()
settings = SettingsService.get_settings()
```

### Type Conversion Errors

**Problem:** Settings import/export fails with type errors

**Solution:**
1. Validate JSON structure: `SettingsService.validate_settings(data)`
2. Check data types match model definitions
3. Review import file for valid JSON syntax

---

## Future Enhancements

### Planned Features

- [ ] Per-user settings override (user preferences)
- [ ] Settings versioning with rollback capability
- [ ] Real-time sync across multiple app instances
- [ ] A/B testing framework with settings-driven experiments
- [ ] Settings audit log with email notifications
- [ ] Configuration templates for different deployment scenarios
- [ ] Performance monitoring tied to settings changes
- [ ] Gradual rollout automation with rollback triggers

### Integration Points

- **Auth Service** - Password policy enforcement
- **Email Service** - Notification settings usage
- **Payment Service** - Currency, fee, timeout settings
- **Listing Service** - Listing behavior settings
- **Admin Service** - Dashboard configuration
- **Feature Flags** - Beta feature management

---

**Document Version:** 1.0
**Last Updated:** December 2024
**Status:** Complete Implementation
