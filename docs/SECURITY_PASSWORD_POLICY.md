# CampusKubo Security: Password Policy & Recovery

## ❌ What We DON'T Do (Why It's Dangerous)

### ❌ Never Store Plaintext Passwords
```python
# WRONG - NEVER DO THIS:
user_password_plaintext = "user123Password!"  # Storing in database
user_recovery_sheet = {email: plaintext_password}  # Storing in encrypted file
```

**Why it's dangerous:**
- If your database is breached, ALL passwords are compromised immediately
- If your encrypted sheet key is leaked, all passwords are exposed
- You'd be liable for user account theft and potential legal action
- Violates GDPR, HIPAA, and other compliance standards
- Inside threats: employees with database access can see all passwords

---

## ✅ What We DO Instead: Secure Token-Based Reset

### Architecture Overview

```
User Flow:
┌─────────────────────────────────────────────────────┐
│ 1. User clicks "Forgot Password"                    │
│    ↓                                                │
│ 2. Enter email address                              │
│    ↓                                                │
│ 3. System generates secure random token             │
│    ↓                                                │
│ 4. Store token in database with 15-min expiry      │
│    ↓                                                │
│ 5. Send reset link via email                        │
│    https://yourapp.com/reset?token=abc123xyz       │
│    ↓                                                │
│ 6. User clicks link (validates token)               │
│    ↓                                                │
│ 7. User creates NEW password                        │
│    ↓                                                │
│ 8. Password is hashed and stored                    │
│    Token marked as "used" (can't reuse)            │
│    ↓                                                │
│ 9. User logs in with new password                   │
└─────────────────────────────────────────────────────┘
```

---

## 🔐 Implementation Details

### 1. Password Storage (Database)

**What's stored:**
```sql
-- USERS table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,  -- SHA256 HASH ONLY (never plaintext)
    role TEXT,
    full_name TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT
);

-- PASSWORD RESET TOKENS table
CREATE TABLE password_reset_tokens (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,  -- Cryptographically secure random
    expires_at TEXT NOT NULL,     -- ISO datetime (15 min from creation)
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    used INTEGER DEFAULT 0,       -- 1 = token has been used
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Key Points:**
- `password` column stores **only hashed values** (SHA256)
- No `original_pass` column
- No plaintext recovery codes stored
- Tokens are **single-use** and **time-limited**

### 2. Password Reset Flow in Code

#### Step 1: User Requests Reset
```python
from services.auth_service import AuthService

# User submits email on "Forgot Password" page
email = request.form.get("email")
success, message, token = AuthService.request_password_reset(email)

if success:
    # Send email to user with reset link
    send_reset_email(
        to=email,
        reset_link=f"https://yourapp.com/reset?token={token}"
    )
```

#### Step 2: User Clicks Reset Link & Sets New Password
```python
# User submits new password form with token
token = request.args.get("token")
new_password = request.form.get("new_password")

success, message = AuthService.reset_password_with_token(token, new_password)

if success:
    return redirect("/login", message="Password updated! Please log in.")
else:
    return render_template("reset_password.html",
                         error=message,  # "Invalid or expired reset link"
                         token=token)
```

### 3. Token Security Properties

| Property | Value | Why |
|----------|-------|-----|
| **Length** | 32 bytes (256 bits) | Cryptographically secure |
| **Generation** | `secrets.token_urlsafe()` | Can't be guessed or brute-forced |
| **Expiration** | 15 minutes | Limits time window for attacks |
| **Single-use** | Yes (marked as `used=1`) | Can't reuse same token twice |
| **Invalidation** | Auto-delete if other reset generated | Only latest token valid |
| **Storage** | Hashed in database | Even if DB leaked, tokens are secure |

---

## 🛡️ Security Guarantees

### What This Approach Prevents

| Attack | Prevention |
|--------|-----------|
| **Plaintext password theft** | Passwords never stored plaintext |
| **Token replay attacks** | Tokens marked as `used` after success |
| **Token expiration bypass** | Database checks `expires_at` timestamp |
| **Brute-force token guessing** | 256-bit random tokens (2^256 possibilities) |
| **Password interception** | Only transmitted over HTTPS in production |
| **Unauthorized password changes** | Email verification required before reset |
| **Malicious insider access** | Admin sees token ≠ password |
| **Account takeover via reset link** | Token specific to user + time-limited |

---

## 📝 Admin Password Help (No Plaintext Access)

### What Admins CAN Do

```python
# Option 1: Force temporary password
def admin_reset_user_password(admin_id: int, user_id: int) -> str:
    """
    Admin forces password reset without seeing the old one.
    Returns a temporary password user must change on login.
    """
    temp_password = secrets.token_urlsafe(16)  # Random temp password

    # Set temp password
    update_user_password(user_id, temp_password)

    # Send email to user:
    # "Your admin has reset your password. Temporary password: [redacted in email]"
    # "You'll be forced to create a new one on your next login"

    send_admin_reset_email(user_id, temp_password)

    return temp_password  # Only admin sees it in system, send to user via email

# Option 2: Trigger password reset (recommended)
def admin_trigger_password_reset(admin_id: int, user_id: int) -> str:
    """
    Admin initiates password reset on behalf of user.
    User receives email with reset link and completes their own reset.
    """
    user = get_user_by_id(user_id)
    success, message, token = AuthService.request_password_reset(user['email'])

    if success:
        send_reset_email_on_behalf_of_admin(user['email'], token,
            message="An admin has initiated a password reset for your account")

    log_activity(admin_id, "User Password Reset",
                f"Admin initiated password reset for user {user_id}")

    return token
```

### What Admins CANNOT Do
- ✗ See original password
- ✗ Decrypt password hash
- ✗ Access recovery codes or backup
- ✗ Bypass email verification

---

## 🔄 Database Cleanup (Maintenance)

### Auto-Delete Expired Tokens
```python
from storage.db import cleanup_expired_reset_tokens

# Run periodically (daily via cron job or background task)
deleted_count = cleanup_expired_reset_tokens()
# Deletes all tokens where expires_at <= now

# Example: Add to your background job scheduler
# APScheduler, Celery, or custom task runner
scheduler.add_job(
    cleanup_expired_reset_tokens,
    'cron',
    hour=2,  # Run daily at 2 AM
    minute=0
)
```

---

## 🚀 Implementation Checklist

- [x] **Database Schema** - Password reset tokens table created
- [x] **Secure Token Generation** - Using `secrets.token_urlsafe(32)`
- [x] **Token Validation** - Time + usage checks in place
- [x] **Password Hashing** - SHA256 only (no plaintext storage)
- [x] **Auth Service Methods** - `request_password_reset()` and `reset_password_with_token()`
- [ ] **Email Integration** - Send reset links via email (TODO: implement email service)
- [ ] **Frontend UI** - "Forgot Password" page with email input (TODO)
- [ ] **Reset Page UI** - Form to submit new password with token (TODO)
- [ ] **Scheduled Cleanup** - Auto-delete expired tokens (TODO)
- [ ] **Admin Tools** - Force password reset UI for admins (TODO)
- [ ] **Email Templates** - Professional password reset email (TODO)
- [ ] **HTTPS Only** - Ensure production uses HTTPS (TODO: deployment)
- [ ] **Rate Limiting** - Prevent spam password reset requests (TODO)

---

## 📚 Related Security Documentation

- See `app/services/auth_service.py` for implementation
- See `app/storage/db.py` for database functions
- See `app/components/password_requirements.py` for password validation UI

---

## ⚠️ Critical Reminders

1. **NEVER** log or print passwords
2. **NEVER** send passwords in plain URLs (only tokens)
3. **ALWAYS** use HTTPS in production
4. **ALWAYS** validate tokens server-side before accepting password changes
5. **ALWAYS** hash passwords with strong algorithms (SHA256 minimum)
6. **ALWAYS** send reset links via email (not SMS or instant messaging)
7. **ALWAYS** expire tokens quickly (15-30 minutes recommended)
8. **ALWAYS** log password reset attempts for audit trail

---

**Last Updated:** December 6, 2025
**Security Level:** ✅ RECOMMENDED BEST PRACTICE
