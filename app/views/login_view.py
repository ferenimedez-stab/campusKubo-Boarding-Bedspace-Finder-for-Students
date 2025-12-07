# views/login_view.py
"""
Login view
Updated from main.py with complete authentication logic
"""
import flet as ft
from storage.db import validate_user


class LoginView:
    """Login page view"""

    def __init__(self, page: ft.Page):
        self.page = page

    def build(self):
        """Build login view - matching model"""
        self.page.title = "CampusKubo - Login"
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER

        email = ft.TextField(label="Email Address", width=330)
        password = ft.TextField(label="Password", width=330, password=True, can_reveal_password=True)
        msg = ft.Text("", size=16, color="red", weight=ft.FontWeight.BOLD)

        def do_login(e):
            email_val = email.value or ""
            password_val = password.value or ""
            print(f"Login attempt: email={email_val}, password provided={bool(password_val)}")
            user = validate_user(email_val, password_val)
            print(f"User validated: {user}")
            if user:
                # Set all session data properly
                self.page.session.set("user_id", user.get('id'))
                self.page.session.set("email", user.get('email'))
                self.page.session.set("role", user.get('role'))
                self.page.session.set("full_name", user.get('full_name', ''))
                self.page.session.set("is_logged_in", True)

                user_role = user.get('role')
                print(f"Login successful - ID: {user.get('id')}, Role: {user_role}, Email: {user.get('email')}")

                # Map DB role to routes used in the app
                if user_role in ("pm", "property_manager"):
                    self.page.go("/pm")
                elif user_role == "tenant":
                    self.page.go("/tenant")
                elif user_role == "admin":
                    self.page.go("/admin")
                else:
                    self.page.go("/")
            else:
                print("Login failed")
                msg.value = "Incorrect email or password. Please try again."
                self.page.update()

        return ft.View("/login",
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=400,
                    padding=20,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=15,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.START,
                                controls=[
                                    ft.TextButton(
                                        content=ft.Row(
                                            controls=[
                                                ft.Icon(ft.Icons.ARROW_BACK),
                                                ft.Text("Back to Home")
                                            ]
                                        ),
                                        on_click=lambda _: self.page.go("/")
                                    ),
                                ]
                            ),
                            ft.Text("Sign In", size=26, weight=ft.FontWeight.BOLD),
                            email,
                            password,
                            msg,
                            ft.ElevatedButton("Log In", width=330, on_click=do_login),
                            ft.TextButton("Don't have an account? Sign Up", on_click=lambda _: self.page.go("/signup")),
                            ft.TextButton("Continue as Guest → Browse Listings", on_click=lambda _: self.page.go("/browse"))
                        ]
                    )
                )
            ]
        )
