"""
campusKubo - Main Application Entry Point
A Flet-based boarding house finder for students
"""

import flet as ft


def main(page: ft.Page):
    """Main application entry point"""

    # Page configuration
    page.title = "campusKubo - Boarding & Bedspace Finder"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window.width = 1200
    page.window.height = 800

    # Temporary welcome screen
    def show_welcome():
        welcome_text = ft.Text(
            "Welcome to campusKubo!",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700,
        )

        subtitle = ft.Text(
            "Your trusted platform for finding student accommodations",
            size=16,
            color=ft.Colors.GREY_700,
        )

        # Placeholder buttons
        snack = ft.SnackBar(
            content=ft.Text("Feature coming soon!"),
            action="OK",
        )

        tenant_btn = ft.ElevatedButton(
            "I'm looking for accommodation",
            icon=ft.Icons.SEARCH,
            on_click=lambda _: page.add(snack),
        )

        manager_btn = ft.OutlinedButton(
            "I'm a property manager",
            icon=ft.Icons.BUSINESS,
            on_click=lambda _: page.add(snack),
        )

        # Layout
        content = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        ft.Icons.HOME_ROUNDED,
                        size=120,
                        color=ft.Colors.BLUE_400,
                    ),
                    welcome_text,
                    subtitle,
                    ft.Container(height=20),
                    tenant_btn,
                    manager_btn,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )

        page.add(content)

    # Show welcome screen
    show_welcome()


if __name__ == "__main__":
    # Run the app
    ft.app(target=main)