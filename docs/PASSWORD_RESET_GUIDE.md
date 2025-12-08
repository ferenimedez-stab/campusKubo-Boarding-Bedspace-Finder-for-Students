# Password Reset: Quick Implementation Guide

## 🎯 User Flow

### For Users (Forgot Password)
```
1. Go to login page → Click "Forgot Password?"
2. Enter email address
3. Check email for reset link
4. Click reset link (valid for 15 minutes)
5. Enter new password
6. Done! Log in with new password
```

### For Developers (Integration)

#### 1. Frontend: Add "Forgot Password" Link
```html
<!-- On login page -->
<a href="/forgot-password">Forgot your password?</a>
```

#### 2. Frontend: Request Reset Page (GET /forgot-password)
```python
# views/forgot_password_view.py
def build(self) -> ft.View:
    email_input = ft.TextField(label="Email Address")

    def handle_submit(e):
        email = email_input.value
        success, message, token = AuthService.request_password_reset(email)

        if success:
            # TODO: Send email with token
            # send_password_reset_email(email, token)
            show_message("Check your email for reset link")
        else:
            show_error(message)
```

#### 3. Frontend: Reset Password Page (GET /reset?token=xyz)
```python
# views/reset_password_view.py
def build(self) -> ft.View:
    token = self.page.route_parameters.get("token", "")
    password_input = ft.TextField(label="New Password", password=True)

    def handle_submit(e):
        new_password = password_input.value
        success, message = AuthService.reset_password_with_token(token, new_password)

        if success:
            show_message(message)
            self.page.go("/login")
        else:
            show_error(message)
```

#### 4. Backend: Send Email (TODO)
```python
# You need to implement email sending
import smtplib
from email.mime.text import MIMEText

def send_password_reset_email(email: str, token: str):
    """
    Send password reset email to user.
    """
    reset_link = f"https://yourapp.com/reset?token={token}"

    subject = "Reset Your CampusKubo Password"
    html_body = f"""
    <h2>Password Reset Request</h2>
    <p>Click the link below to reset your password:</p>
    <a href="{reset_link}" style="background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
        Reset Password
    </a>
    <p><strong>Note:</strong> This link expires in 15 minutes</p>
    <p>If you didn't request this, ignore this email.</p>
    """

    # TODO: Configure and send via SMTP, SendGrid, AWS SES, etc.
```

---

## 🔒 Security Functions Reference

### Request Password Reset
```python
from services.auth_service import AuthService

success, message, token = AuthService.request_password_reset(email)

# Returns:
# success: bool (True if user exists and token created)
# message: str (user-friendly message)
# token: str (secure random token to send via email) or None

# Example:
success, msg, token = AuthService.request_password_reset("user@example.com")
if success:
    send_email(
        to="user@example.com",
        subject="Reset Your Password",
        body=f"Click here: https://app.com/reset?token={token}"
    )
```

### Reset Password With Token
```python
from services.auth_service import AuthService

success, message = AuthService.reset_password_with_token(token, new_password)

# Returns:
# success: bool (True if password updated)
# message: str (error or success message)

# Example:
success, msg = AuthService.reset_password_with_token(
    token="abc123xyz...",
    new_password="NewSecurePass123!"
)
if success:
    redirect_to_login()
else:
    show_error(msg)  # "Invalid or expired reset link"
```

### Database Functions
```python
from storage.db import (
    create_password_reset_token,      # Create token (internal use)
    verify_password_reset_token,      # Check if token is valid
    use_password_reset_token,         # Mark token as used
    cleanup_expired_reset_tokens      # Delete old tokens (maintenance)
)
```

---

## 🛠️ Setup Checklist

### Required (Core Security)
- [x] Database schema with password_reset_tokens table
- [x] AuthService methods for reset flow
- [x] DB functions for token management
- [x] Password validation requirements

### Recommended (Production Ready)
- [ ] Email service integration
- [ ] "Forgot Password" view UI
- [ ] "Reset Password" view UI
- [ ] Email templates with branding
- [ ] Rate limiting on password reset requests
- [ ] HTTPS configuration (production)
- [ ] Scheduled token cleanup job
- [ ] Admin password reset tools

### Optional (Enhanced UX)
- [ ] SMS confirmation as alternative to email
- [ ] Password reset via security questions
- [ ] 2FA verification during reset
- [ ] Notification emails after successful reset
- [ ] Login attempt alerts

---

## 📊 Token Lifecycle

```
[Created]
   ↓
   Token stored in DB with expires_at = now + 15 minutes
   User receives email with reset link containing token
   ↓
[Valid Period (0-15 min)]
   ↓
   User clicks link and enters new password
   System calls verify_password_reset_token(token)
   ✓ Token is valid, user_id returned
   Password is updated with hashed value
   System calls use_password_reset_token(token) → marked as used=1
   ↓
[Expired or Used]
   ↓
   ✗ Token can no longer be used for password reset
   ✓ Can be deleted by cleanup_expired_reset_tokens()
```

---

## 🚨 Security Best Practices

### DO ✅
- Use HTTPS in production
- Send tokens via email only
- Expire tokens after 15-30 minutes
- Invalidate old tokens when new reset requested
- Hash/encrypt tokens in database
- Log reset attempts for audit trail
- Require password validation (strength checks)
- Show generic message ("Check your email if account exists")

### DON'T ❌
- Send passwords via email (send reset link instead)
- Store plaintext passwords
- Display user feedback about whether email exists
- Use weak tokens (use secrets module)
- Send reset links in URLs without token validation
- Allow same token to work multiple times
- Log or print plaintext passwords
- Expose token in error messages

---

## 🔗 Related Files

- `app/storage/db.py` - Database functions for tokens
- `app/services/auth_service.py` - AuthService reset methods
- `SECURITY_PASSWORD_POLICY.md` - Detailed security documentation

---

**Status:** ✅ IMPLEMENTED
**Last Updated:** December 6, 2025
