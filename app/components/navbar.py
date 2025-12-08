"""
Navigation bar component
"""

import flet as ft


class NavBar:
    """Top navigation bar component"""

    def __init__(self, page: ft.Page, show_auth_buttons: bool = True):
        self.page = page
        self.show_auth_buttons = show_auth_buttons

    def view(self):
        # Logo and title as a simple text with icon character to match the skeleton
        logo_section = ft.Text(
            " C🏠mpusKubo",
            size=22,
            weight=ft.FontWeight.BOLD,
            color="#1A1A1A"
        )

        # Auth buttons (Login/Register + notifications)
        auth_buttons = (
            ft.Row(
                spacing=12,
                controls=[
                    ft.TextButton("Login", on_click=lambda _: self.page.go("/login")),
                    ft.TextButton("Register", on_click=lambda _: self.page.go("/signup")),
                    ft.IconButton(icon=ft.Icons.NOTIFICATIONS, tooltip="Notifications", icon_color=ft.Colors.BLUE_900)
                ]
            ) if self.show_auth_buttons else ft.Container()
        )

        return ft.Container(
            bgcolor="#FFFFFF",
            padding=ft.padding.symmetric(horizontal=40, vertical=15),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color="#00000008",
                offset=ft.Offset(0, 2)
            ),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    logo_section,
                    auth_buttons
                ]
            )
        )


class DashboardNavBar:
    """Dashboard navigation bar with user info"""

    def __init__(
        self,
        page: ft.Page,
        title: str,
        user_email: str,
        show_add_button: bool = False,
        on_add_click=None,
        on_logout=None
    ):
        self.page = page
        self.title = title
        self.user_email = user_email
        self.show_add_button = show_add_button
        self.on_add_click = on_add_click
        self.on_logout = on_logout

    def view(self):
        # Logo section
        logo_section = ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.HOME, size=28, color="#0078FF"),
                            ft.Column(
                                spacing=0,
                                controls=[
                                    ft.Text("CampusKubo", size=22, weight=ft.FontWeight.BOLD),
                                    ft.Text(self.user_email, size=13, color=ft.Colors.BLACK)
                                ]
                            )
                        ]
                    )


        # Action buttons
        action_buttons = []

        if self.show_add_button:
            action_buttons.append(
                ft.ElevatedButton(
                    "Add New Listing",
                    icon=ft.Icons.ADD_CIRCLE,
                    bgcolor="#0078FF",
                    color="white",
                    on_click=self.on_add_click
                )
            )

        # ADMIN PROFILE BUTTON
        profile_button = ft.IconButton(
            icon=ft.Icons.ACCOUNT_CIRCLE,
            tooltip="Profile",
            on_click=lambda _: self.page.go("/admin_profile")
        )

        logout_button = ft.OutlinedButton(
                "Logout",
                icon=ft.Icons.LOGOUT,
                on_click=self.on_logout
            )

        action_buttons.append(profile_button)
        action_buttons.append(logout_button)

        return ft.Container(
            bgcolor="#FFFFFF",
            padding=ft.padding.symmetric(horizontal=40, vertical=20),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color="#00000008",
                offset=ft.Offset(0, 2)
            ),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    logo_section,
                    ft.Row(spacing=10, controls=action_buttons)
                ]
            )
        )
