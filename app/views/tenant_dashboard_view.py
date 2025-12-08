"""
Tenant dashboard view
Updated from main.py tenant_dashboard implementation
"""
import flet as ft


class TenantDashboardView:
    """Tenant dashboard"""

    def __init__(self, page: ft.Page):
        self.page = page

    def show_coming_soon(self, e):
        snack_bar = ft.SnackBar(ft.Text("Coming soon!"))
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()

    def build(self):
        """Build tenant dashboard view - matching model"""
        email = self.page.session.get("email")

        nav_bar = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text("C🏠mpusKubo", size=22, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Text(f"👤 {email}", size=14),
                    ft.IconButton(
                        icon=ft.Icons.LOGOUT,
                        tooltip="Logout",
                        on_click=lambda _: self.page.go("/logout")
                    )
                ])
            ]
        )
        return ft.View("/tenant",
            padding=25,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                nav_bar,
                ft.Container(height=20),
                ft.Text(f"Tenant Dashboard", size=26, weight=ft.FontWeight.BOLD),
                ft.Text(f"Welcome back, {email}!", size=16, color=ft.Colors.BLACK),
                ft.Container(height=20),

                ft.Row(
                    spacing=20,
                    controls=[
                        ft.Container(
                            width=150,
                            height=150,
                            bgcolor="#e0f7fa",
                            border_radius=8,
                            padding=10,
                            content=ft.Column(
                                controls=[
                                    ft.Icon(ft.Icons.SEARCH, size=50, color="#00796b"),
                                    ft.Text("Browse Listings", weight=ft.FontWeight.BOLD),
                                    ft.ElevatedButton(
                                        "Go",
                                        on_click=lambda _: self.page.go("/browse")
                                    )
                                ]
                            )
                        ),
                        ft.Container(
                            width=150,
                            height=150,
                            bgcolor="#e0f7fa",
                            border_radius=8,
                            padding=10,
                            content=ft.Column(
                                controls=[
                                    ft.Icon(ft.Icons.BOOK, size=40, color="#7b1fa2"),
                                    ft.Text("My Reservations", weight=ft.FontWeight.BOLD),
                                    ft.ElevatedButton(
                                        "View",
                                        on_click=self.show_coming_soon
                                    )
                                ]
                            )
                        ),
                    ]
                )
            ]
        )