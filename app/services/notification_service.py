"""
Notification service (in-memory stub)
"""
from datetime import datetime
from typing import List, Dict


class NotificationService:
    """Handles notifications (in-memory)."""

    def __init__(self):
        self.notifications: List[Dict] = []
        self.next_id = 1

    def add_notification(self, user_id: int, notif_type: str, message: str, category: str = "activity") -> Dict:
        notif = {
            "notification_id": self.next_id,
            "user_id": user_id,
            "notification_type": notif_type,
            "message": message,
            "category": category,
            "is_read": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.notifications.append(notif)
        self.next_id += 1
        return notif

    def get_user_notifications(self, user_id: int) -> List[Dict]:
        return [n for n in self.notifications if n.get("user_id") == user_id]

    def get_unread_count(self, user_id: int) -> int:
        return len([n for n in self.notifications if n.get("user_id") == user_id and not n.get("is_read")])

    def mark_notification_read(self, notif_id: int) -> bool:
        for n in self.notifications:
            if n.get("notification_id") == notif_id:
                n["is_read"] = True
                return True
        return False

    def mark_all_notifications_read(self, user_id: int) -> int:
        count = 0
        for n in self.notifications:
            if n.get("user_id") == user_id and not n.get("is_read"):
                n["is_read"] = True
                count += 1
        return count