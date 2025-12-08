"""
Reservation service
"""
from storage.db import (
    create_reservation,
    get_connection,
    get_reservation as db_get_reservation,
)
from typing import Tuple, Optional, List, Dict, Any


class ReservationService:
    """Handles reservation operations"""

    @staticmethod
    def create_new_reservation(
        listing_id: int,
        tenant_id: int,
        start_date: str,
        end_date: str
    ) -> Tuple[bool, str]:
        """
        Create new reservation
        Returns (success: bool, message: str)
        """
        # Basic validation
        if not start_date or not end_date:
            return False, "Start and end dates are required"

        # Create reservation
        reservation_id = create_reservation(
            listing_id, tenant_id, start_date, end_date
        )

        if reservation_id:
            return True, "Reservation created successfully"
        else:
            return False, "Failed to create reservation"

    @staticmethod
    def create_reservation_full(
        user_id: int,
        prop_id: int,
        check_in: str,
        check_out: str,
        guests: str,
        total: float,
        fee: float,
        method: str,
        manager: str,
    ) -> Optional[int]:
        """
        Adapter for richer reservation creation signature used in UI flows.
        Note: current schema stores only dates/status; payment/fee are not persisted.
        Returns reservation id or None on failure.
        """
        return create_reservation(prop_id, user_id, check_in, check_out)

    @staticmethod
    def get_user_reservations(user_id: int) -> list:
        """Get all reservations for a user with error handling."""
        if user_id <= 0:
            print(f"[get_user_reservations] Invalid user_id: {user_id}")
            return []

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT r.*, l.address, l.price
                FROM reservations r
                JOIN listings l ON r.listing_id = l.id
                WHERE r.tenant_id = ?
                ORDER BY r.created_at DESC
            """, (user_id,))

            reservations = cursor.fetchall()
            return reservations
        except Exception as e:
            print(f"[get_user_reservations] error for user {user_id}: {e}")
            return []
        finally:
            conn.close()

    def get_reservation_by_id(self, reservation_id: int) -> Optional[dict]:
        """Get reservation details by ID with error handling."""
        if reservation_id <= 0:
            print(f"[get_reservation_by_id] Invalid reservation_id: {reservation_id}")
            return None

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM reservations WHERE id=?", (reservation_id,))
            row = cursor.fetchone()
            if row:
                # Use dict access with Row object
                return {
                    "id": row["id"],
                    "listing_id": row["listing_id"],
                    "tenant_id": row["tenant_id"],
                    "start_date": row["start_date"],
                    "end_date": row["end_date"],
                    "status": row["status"],
                    "created_at": row["created_at"],
                }
            return None
        except Exception as e:
            print(f"[get_reservation_by_id] error for reservation {reservation_id}: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_reservation(reservation_id: int) -> Optional[Dict[str, Any]]:
        """Adapter wrapper for reservation lookup including listing info."""
        return db_get_reservation(reservation_id)

    @staticmethod
    def get_property_reservations(property_id: int) -> List[Dict[str, Any]]:
        """Return reservations for a property (listing)."""
        if property_id <= 0:
            return []
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT * FROM reservations
                WHERE listing_id = ?
                ORDER BY start_date ASC
                """,
                (property_id,),
            )
            rows = cursor.fetchall()
            return [dict(r) for r in rows] if rows else []
        except Exception as e:
            print(f"[get_property_reservations] error for property {property_id}: {e}")
            return []
        finally:
            conn.close()

    def get_all_reservations(self) -> list[dict]:
        """Get all reservations"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reservations ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        reservations = []
        for row in rows:
            reservations.append({
                "id": row[0],
                "listing_id": row[1],
                "tenant_id": row[2],
                "start_date": row[3],
                "end_date": row[4],
                "status": row[5],
                "created_at": row[6],
            })
        return reservations

    def update_reservation_status(self, reservation_id: int, new_status: str) -> bool:
        """Update reservation status (admin action) with validation."""
        if reservation_id <= 0:
            print(f"[update_reservation_status] Invalid reservation_id: {reservation_id}")
            return False
        if not new_status or not new_status.strip():
            print("[update_reservation_status] Status is required")
            return False

        valid_statuses = ["pending", "approved", "confirmed", "cancelled", "rejected"]
        if new_status not in valid_statuses:
            print(f"[update_reservation_status] Invalid status: {new_status}. Valid: {valid_statuses}")
            return False

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE reservations SET status = ? WHERE id = ?", (new_status, reservation_id))
            conn.commit()
            if cursor.rowcount > 0:
                return True
            print(f"[update_reservation_status] Reservation not found: {reservation_id}")
            return False
        except Exception as e:
            conn.rollback()
            print(f"[update_reservation_status] error for reservation {reservation_id}: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def delete_reservation(reservation_id: int) -> bool:
        """Permanently delete a reservation."""
        if reservation_id <= 0:
            return False
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM reservations WHERE id = ?", (reservation_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"[delete_reservation] error for reservation {reservation_id}: {e}")
            return False
        finally:
            conn.close()

    def get_all_reservations_count(self) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM reservations")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_reservations_per_month(self) -> list[tuple[str, int]]:
        """Return [(month_name, count)]"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT strftime('%Y-%m', created_at) AS month, COUNT(*)
            FROM reservations GROUP BY month ORDER BY month
        """)
        data = cursor.fetchall()
        conn.close()
        return [(row[0], row[1]) for row in data]