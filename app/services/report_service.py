"""
Report Service
Handles admin oversight of submitted reports.
"""

from storage.db import get_connection


class ReportService:

    @staticmethod
    def get_all_reports():
        """
        Fetches all user-submitted reports.
        """
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT r.id, r.message, r.status, r.created_at,
                   u.email as reporter_email,
                   l.address as listing_address
            FROM reports r
            LEFT JOIN users u ON r.user_id = u.id
            LEFT JOIN listings l ON r.listing_id = l.id
            ORDER BY r.created_at DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        reports = []
        for row in rows:
            reports.append({
                "id": row[0],
                "message": row[1],
                "status": row[2],
                "created_at": row[3],
                "reporter_email": row[4],
                "listing_address": row[5],
            })

        return reports

    @staticmethod
    def update_report_status(report_id: int, new_status: str):
        """
        Updates the status of a report (e.g., Pending → Reviewed/Resolved)
        """
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE reports
                SET status = ?
                WHERE id = ?
            """, (new_status, report_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            return False
        finally:
            conn.close()
