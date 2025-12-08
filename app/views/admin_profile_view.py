# app/views/admin_profile_view.py

import flet as ft
from state.session_state import SessionState
from components.navbar import DashboardNavBar
from components.footer import Footer
from services.admin_service import AdminService

class AdminProfileView:
    """Admin Profile Page"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.session = SessionState(page)
        self.admin_service = AdminService()

    def build(self):
        # Auth
        if not self.session.require_auth():
            return None

        if not self.session.is_admin():
            self.page.go("/")
            return None

        # Fetch user info
        user_id = self.session.get_user_id()
        if not user_id:
            self.page.go("/login")
            return None

        try:
            profile = self.admin_service.get_user_by_id(user_id)
        except Exception as e:
            print(f"[handle_save] Failed to save admin profile: {e}")
            profile = None

        if not profile:
            return ft.View(
                "/admin_profile",
                controls=[ft.Text("Error loading profile", color="red")]
            )

        back_button = ft.TextButton(
                        "← Back to Dashboard",
                        on_click=lambda _: self.page.go("/admin")
                    )
        # Navbar
        navbar = DashboardNavBar(
            page=self.page,
            title="Admin Profile",
            user_email=self.session.get_email() or "",
            show_add_button=False,
            on_logout=lambda _: self._logout()
        ).view()

        footer = Footer().view()

        # UI
        return ft.View(
            "/admin_profile",
            scroll=ft.ScrollMode.AUTO,
            controls=[
                navbar,
                ft.Container(
                    padding=40,
                    content=ft.Column(
                        spacing=20,
                        controls=[back_button,
                            ft.Text("Admin Profile", size=28, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                padding=20,
                                bgcolor="white",
                                border_radius=12,
                                content=ft.Column(
                                    spacing=15,
                                    controls=[
                                        ft.Text(f"Full Name: {profile.full_name}"),
                                        ft.Text(f"Email: {profile.email}"),
                                        ft.Text(f"Role: {profile.role.name}"),
                                        ft.Divider(),
                                        ft.ElevatedButton(
                                            "Log Out",
                                            on_click=lambda _: self._logout(),
                                            bgcolor="red",
                                            color="white"
                                        )
                                    ]
                                )
                            ),
                        ]
                    )
                ),
                footer
            ]
        )

    def _logout(self):
        self.session.logout()
        self.page.go("/")
