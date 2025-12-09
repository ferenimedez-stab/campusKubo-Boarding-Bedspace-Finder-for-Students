"""
Test Profile Dialog Behavior
Verifies that profile dialogs don't cause gray screen issues
"""
import flet as ft
from app.components.profile_section import ProfileSection
from app.state.profile_state import ProfileState


def main(page: ft.Page):
    page.title = "Test Profile Dialog"
    page.padding = 20

    # Create a test profile state
    test_state = ProfileState(
        user_id=1,
        first_name="Test",
        last_name="User",
        email="test@example.com",
        contact_number="1234567890",
        role="student",
        avatar_url="https://ui-avatars.com/api/?name=Test+User&size=110&background=4A90E2&color=fff&bold=true",
        house_no="123",
        street="Test St",
        barangay="Test Barangay",
        city="Test City",
        actual_password="TestPassword123!",
        password_visible=False
    )

    # Create ProfileSection component
    profile_section = ProfileSection(
        page=page,
        state=test_state,
        on_update=lambda: page.update()
    )

    # Create test buttons
    test_buttons = ft.Column([
        ft.Text("Profile Dialog Tests", size=20, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.ElevatedButton(
            "Open Edit Profile Dialog",
            on_click=lambda e: profile_section.show_edit_profile_dialog(),
            icon=ft.Icons.EDIT
        ),
        ft.ElevatedButton(
            "Open Avatar Dialog",
            on_click=lambda e: profile_section.show_avatar_dialog(),
            icon=ft.Icons.PHOTO
        ),
        ft.ElevatedButton(
            "Open Address Dialog",
            on_click=lambda e: profile_section.show_edit_address_dialog(),
            icon=ft.Icons.HOME
        ),
        ft.ElevatedButton(
            "Open Password Dialog",
            on_click=lambda e: profile_section.show_change_password_dialog(),
            icon=ft.Icons.LOCK
        ),
        ft.Divider(),
        ft.Text("Instructions:", weight=ft.FontWeight.BOLD),
        ft.Text("1. Click each button to open dialogs"),
        ft.Text("2. Close dialogs using Cancel or X button"),
        ft.Text("3. Verify page does NOT turn gray"),
        ft.Text("4. Try making changes and saving"),
        ft.Text("5. Check for success/error messages"),
    ])

    page.add(ft.Container(
        content=test_buttons,
        padding=20,
        bgcolor=ft.Colors.BLUE_GREY_50,
        border_radius=10
    ))

    page.update()


if __name__ == "__main__":
    ft.app(target=main)
