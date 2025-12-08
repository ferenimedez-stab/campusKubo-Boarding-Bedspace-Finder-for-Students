"""
Notification banner component
"""

import flet as ft


class NotificationBanner:
    """Notification banner for displaying messages (info, success, warning, error)"""

    def __init__(self, message: str, type: str = "info", on_close=None):
        self.message = message
        self.type = type
        self.on_close = on_close

    def view(self):
        # Colors & icons per type
        colors = {
            "info":    {"bg": "#E3F2FD", "icon": ft.Icons.INFO,            "icon_color": "#0078FF"},
            "success": {"bg": "#E8F5E9", "icon": ft.Icons.CHECK_CIRCLE,    "icon_color": "#4CAF50"},
            "warning": {"bg": "#FFF3E0", "icon": ft.Icons.WARNING_AMBER,   "icon_color": "#FF9800"},
            "error":   {"bg": "#FFEBEE", "icon": ft.Icons.ERROR,           "icon_color": "#F44336"},
        }

        style = colors.get(self.type, colors["info"])

        return ft.Container(
            bgcolor=style["bg"],
            padding=15,
            border_radius=10,
            content=ft.Row(
                spacing=10,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    # Icon + Message
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Icon(style["icon"], color=style["icon_color"], size=22),
                            ft.Text(self.message, size=14, weight=ft.FontWeight.W_500, color="#333")
                        ],
                    ),

                    # Close button
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=16,
                        icon_color=ft.Colors.BLACK,
                        tooltip="Dismiss",
                        on_click=self.on_close
                    ) if self.on_close else ft.Container()
                ]
            )
        )
