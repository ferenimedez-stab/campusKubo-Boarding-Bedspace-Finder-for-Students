# app/services/admin_service.py
from typing import List, Optional, Dict
from storage.db import (
    get_connection,
    deactivate_user as db_deactivate_user,
    activate_user as db_activate_user,
    delete_user as db_delete_user,
    change_listing_status,
)
from models.user import User, UserRole
from models.listing import Listing

class AdminService:
    """Service for admin-related operations"""

    # ------------------ USER MANAGEMENT ------------------
    def get_all_users(self, role: Optional[UserRole] = None) -> List[User]:
        conn = get_connection()
        cursor = conn.cursor()
        if role:
            cursor.execute("SELECT * FROM users WHERE role=? ORDER BY created_at DESC", (role.value,))
        else:
            cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [User.from_db_row(row) for row in rows]

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return User.from_db_row(row) if row else None

    def deactivate_user(self, user_id: int) -> bool:
        return db_deactivate_user(user_id)

    def activate_user(self, user_id: int) -> bool:
        return db_activate_user(user_id)

    def delete_user(self, user_id: int) -> bool:
        """Permanently remove a user from the database (admin action)."""
        return db_delete_user(user_id)

    def approve_pm(self, user_id: int) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_verified=1 WHERE id=? AND role='pm'", (user_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    def reject_pm(self, user_id: int) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_verified=0 WHERE id=? AND role='pm'", (user_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    # ------------------ LISTING MANAGEMENT ------------------
    def get_all_listings(self, status: Optional[str] = None) -> List[Listing]:
        """Fetch all listings, optionally filtered by status (pending/approved/rejected)"""
        conn = get_connection()
        cursor = conn.cursor()
        if status:
            cursor.execute("SELECT * FROM listings WHERE status=? ORDER BY created_at DESC", (status,))
        else:
            cursor.execute("SELECT * FROM listings ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [Listing.from_db_row(row) for row in rows]

    def approve_listing(self, listing_id: int) -> bool:
        return change_listing_status(listing_id, "approved")

    def reject_listing(self, listing_id: int) -> bool:
        return change_listing_status(listing_id, "rejected")

    # ------------------ DASHBOARD ANALYTICS ------------------
    def get_stats(self) -> Dict[str, int]:
        """Return counts of users, listings, reservations, payments"""
        conn = get_connection()
        cursor = conn.cursor()

        stats = {}
        cursor.execute("SELECT COUNT(*) as count FROM users")

        stats['total_users'] = cursor.fetchone()['count']

        # Role matching: DB may store human-friendly role strings like 'PM One' or 'Tenant Two'
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE lower(role) LIKE '%pm%' OR lower(role) LIKE '%property%'")
        stats['total_pms'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM users WHERE lower(role) LIKE '%tenant%'")
        stats['total_tenants'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM listings")
        stats['total_listings'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM listings WHERE status='approved'")
        stats['approved_listings'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM listings WHERE status='pending'")
        stats['pending_listings'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM reservations")
        stats['total_reservations'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM payments")
        stats['total_payments'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM reports")
        stats['total_reports'] = cursor.fetchone()['count']

        conn.close()
        return stats

    #
    def get_pending_pm_accounts(self) -> List[User]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE (lower(role) LIKE '%pm%' OR lower(role) LIKE '%property%' OR lower(role) LIKE '%manager%') AND is_verified=0 ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [User.from_db_row(row) for row in rows]

    # ------------------ ADDITIONAL HELPERS ------------------
    def get_pending_pm_count(self) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE (lower(role) LIKE '%pm%' OR lower(role) LIKE '%property%' OR lower(role) LIKE '%manager%') AND is_verified=0")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_pending_pm_counts_per_month(self) -> list[tuple[str, int]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT strftime('%Y-%m', created_at) AS month, COUNT(*)
            FROM users
            WHERE (lower(role) LIKE '%pm%' OR lower(role) LIKE '%property%' OR lower(role) LIKE '%manager%') AND is_verified=0
            GROUP BY month ORDER BY month
        """)
        data = cursor.fetchall()
        conn.close()
        return [(row[0], row[1]) for row in data]

    def get_all_users_count(self) -> int:
        return len(self.get_all_users())

    def get_users_count_by_role(self, role: str) -> int:
        # Role can be 'tenant' or 'pm' — perform a DB count using flexible matching
        conn = get_connection()
        cursor = conn.cursor()
        rl = (role or '').lower()
        try:
            if rl == 'pm' or rl == 'property_manager' or rl == 'property':
                cursor.execute("SELECT COUNT(*) FROM users WHERE lower(role) LIKE '%pm%' OR lower(role) LIKE '%property%' OR lower(role) LIKE '%manager%'")
            elif rl == 'tenant':
                cursor.execute("SELECT COUNT(*) FROM users WHERE lower(role) LIKE '%tenant%'")
            else:
                cursor.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def get_all_payments(self):
        """Return recent payments with joined user and listing info."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT p.id, p.user_id, u.email as user_email, p.listing_id, l.address as listing_address,
                       p.amount, p.created_at
                FROM payments p
                LEFT JOIN users u ON p.user_id = u.id
                LEFT JOIN listings l ON p.listing_id = l.id
                ORDER BY p.created_at DESC
            """)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
