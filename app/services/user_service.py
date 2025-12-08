"""
User service - business logic for user operations
"""
from storage.db import (
    get_connection,
    update_user_profile as db_update_user_profile,
    update_user_password as db_update_user_password,
)
from storage.db import get_user_by_id as db_get_user_by_id
from models.user import User, UserRole
from typing import Optional, List, Dict, Any


class UserService:
    """Handles user-related operations"""

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID"""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, email, full_name, role FROM users WHERE id = ?",
            (user_id,)
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return User.from_db_row(row)

        return None

    @staticmethod
    def get_user_full(user_id: int) -> Optional[Dict[str, Any]]:
        """Return the full DB row for a user as a dict (includes phone and other columns)."""
        return db_get_user_by_id(user_id)

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        conn = get_connection()
        cursor = conn.cursor()

        email_clean = email.strip().lower()
        cursor.execute(
            "SELECT id, email, full_name, role FROM users WHERE email = ?",
            (email_clean,)
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return User.from_db_row(row)

        return None

    @staticmethod
    def get_all_users(role: Optional[str] = None) -> List[User]:
        """Get all users, optionally filtered by role"""
        conn = get_connection()
        cursor = conn.cursor()

        if role:
            cursor.execute(
                "SELECT id, email, full_name, role FROM users WHERE role = ?",
                (role,)
            )
        else:
            cursor.execute("SELECT id, email, full_name, role FROM users")

        rows = cursor.fetchall()
        conn.close()

        return [User.from_db_row(row) for row in rows]

    @staticmethod
    def update_user_profile(user_id: int, full_name: str) -> bool:
        """Update user profile information"""
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE users SET full_name = ? WHERE id = ?",
                (full_name, user_id)
            )
            conn.commit()
            success = cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating user profile: {e}")
            success = False
        finally:
            conn.close()

        return success

    # ------------------------------------------------------------------
    # Adapter-style helpers to align with richer profile flows
    # ------------------------------------------------------------------
    @staticmethod
    def update_user_profile_full(user_id: int, first: str, last: str, gender: str, email: str, phone: str, avatar: str) -> bool:
        """
        Update user profile with extended signature; gender/avatar are not persisted in current schema.
        """
        full_name = f"{first} {last}".strip()
        return db_update_user_profile(user_id, full_name)

    @staticmethod
    def update_user_password(user_id: int, new_password: str) -> bool:
        """Update password through db adapter."""
        return db_update_user_password(user_id, new_password)

    @staticmethod
    def get_user_address(user_id: int) -> Optional[Dict[str, Any]]:
        """Address data not modeled in current schema."""
        return None

    @staticmethod
    def update_user_address(user_id: int, house: str, street: str, brgy: str, city: str) -> bool:
        """Stub: address persistence is not available in current schema."""
        return False

    @staticmethod
    def get_user_settings(user_id: int) -> Optional[Dict[str, Any]]:
        """Settings not modeled; return None."""
        return None

    @staticmethod
    def update_user_settings(user_id: int, new_settings: Dict[str, Any]) -> bool:
        """Stub for compatibility; returns False to indicate no persistence."""
        return False

    @staticmethod
    def get_saved_listings(user_id: int) -> List[Dict[str, Any]]:
        """Saved listings feature not backed by current schema; return empty list."""
        return []