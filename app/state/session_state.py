"""
Session state management
"""
from typing import Optional
from models.user import User, UserRole


class SessionState:
    """Manages user session state"""

    def __init__(self, page):
        """Initialize session state"""
        self.page = page

    def login(self, user_id: int, email: str, role: str, full_name: str = None or ""):
        """Store user login information"""
        self.page.session.set("user_id", user_id)
        self.page.session.set("email", email)
        self.page.session.set("role", role)
        self.page.session.set("full_name", full_name)
        self.page.session.set("is_logged_in", True)

    def logout(self):
        """Clear session data"""
        self.page.session.clear()

    def is_logged_in(self) -> bool:
        """Check if user is logged in"""
        return self.page.session.get("is_logged_in") == True

    def get_user_id(self) -> Optional[int]:
        """Get current user ID"""
        return self.page.session.get("user_id")

    def get_email(self) -> Optional[str]:
        """Get current user email"""
        return self.page.session.get("email")

    def get_role(self) -> Optional[str]:
        """Get current user role"""
        return self.page.session.get("role")

    def get_full_name(self) -> Optional[str]:
        """Get current user full name"""
        return self.page.session.get("full_name")

    def is_tenant(self) -> bool:
        """Check if current user is tenant"""
        return self.get_role() == "tenant"

    def is_property_manager(self) -> bool:
        """Check if current user is property manager"""
        return self.get_role() == "pm"

    def is_admin(self) -> bool:
        """Check if current user is admin"""
        return self.get_role() == "admin"

    def require_auth(self) -> bool:
        """Redirect to login if not authenticated"""
        if not self.is_logged_in():
            self.page.go("/login")
            return False
        return True