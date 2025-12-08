# views/login_view.py
"""
Login view 
"""
import flet as ft
from storage.db import validate_user
from config.colors import COLORS
from utils.navigation import go_home


class LoginView:
    """Login page view"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.colors = COLORS

    def build(self):
        """Build login view - matching model"""
        self.page.title = "CampusKubo - Login"
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER

        email = ft.TextField(
            label="Email Address", 
            width=330,
            bgcolor=self.colors["background"],
            border_color=self.colors["border"],
            focused_border_color=self.colors["primary"],
            color=self.colors["text_dark"]
        )
        password = ft.TextField(
            label="Password", 
            width=330, 
            password=True, 
            can_reveal_password=True,
            bgcolor=self.colors["background"],
            border_color=self.colors["border"],
            focused_border_color=self.colors["primary"],
            color=self.colors["text_dark"]
        )
        msg = ft.Text("", size=16, color=self.colors["error"], weight=ft.FontWeight.BOLD)

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

        def show_forgot_password(e):
            reset_email = ft.TextField(
                label="Enter your email address",
                hint_text="email@example.com",
                width=350,
                bgcolor=self.colors["background"],
                border_color=self.colors["border"],
                color=self.colors["text_dark"]
            )
            
            def send_reset_link(e):
                if reset_email.value:
                    # TODO: Implement actual password reset logic here
                    # This would typically send an email with a reset link
                    dialog.open = False
                    self.page.update()
                    
                    success_snack = ft.SnackBar(
                        ft.Text(
                            f"Password reset link sent to {reset_email.value}",
                            color=self.colors["card_bg"]
                        ),
                        bgcolor=self.colors["accent"]
                    )
                    self.page.overlay.append(success_snack)
                    success_snack.open = True
                    self.page.update()
                else:
                    error_text.value = "Please enter your email address"
                    error_text.visible = True
                    self.page.update()
            
            error_text = ft.Text(
                "",
                size=12,
                color=self.colors["error"],
                visible=False
            )
            
            dialog = ft.AlertDialog(
                title=ft.Text(
                    "🔑 Reset Password",
                    color=self.colors["text_dark"],
                    size=18
                ),
                content=ft.Container(
                    width=400,
                    padding=10,
                    content=ft.Column([
                        ft.Text(
                            "Enter your email address and we'll send you a link to reset your password.",
                            size=14,
                            color=self.colors["text_light"]
                        ),
                        ft.Container(height=10),
                        reset_email,
                        error_text
                    ], tight=True)
                ),
                actions=[
                    ft.TextButton(
                        "Cancel",
                        on_click=lambda e: self._close_dialog(dialog),
                        style=ft.ButtonStyle(color=self.colors["text_light"])
                    ),
                    ft.ElevatedButton(
                        "Send Reset Link",
                        on_click=send_reset_link,
                        bgcolor=self.colors["primary"],
                        color=self.colors["card_bg"]
                    )
                ],
                bgcolor=self.colors["card_bg"]
            )
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()

        return ft.View("/login",
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            bgcolor=self.colors["background"],
            controls=[
                ft.Container(
                    width=400,
                    padding=20,
                    bgcolor=self.colors["card_bg"],
                    border_radius=12,
                    border=ft.border.all(1, self.colors["border"]),
                    shadow=ft.BoxShadow(
                        blur_radius=15,
                        spread_radius=2,
                        color=ft.Colors.with_opacity(0.1, self.colors["text_light"])
                    ),
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
                                                ft.Icon(ft.Icons.ARROW_BACK, color=self.colors["primary"]),
                                                ft.Text("Back to Home", color=self.colors["text_dark"])
                                            ]
                                        ),
                                            on_click=lambda _: go_home(self.page)
                                    ),
                                ]
                            ),
                            ft.Text(
                                "Sign In",
                                size=26,
                                weight=ft.FontWeight.BOLD,
                                color=self.colors["text_dark"]
                            ),
                            email,
                            password,
                            ft.Row(
                                alignment=ft.MainAxisAlignment.END,
                                controls=[
                                    ft.TextButton(
                                        "Forgot Password?",
                                        on_click=show_forgot_password,
                                        style=ft.ButtonStyle(color=self.colors["primary"])
                                    )
                                ]
                            ),
                            msg,
                            ft.ElevatedButton(
                                "Log In",
                                width=330,
                                on_click=do_login,
                                bgcolor=self.colors["primary"],
                                color=self.colors["card_bg"]
                            ),
                            ft.TextButton(
                                "Don't have an account? Sign Up",
                                on_click=lambda _: self.page.go("/signup"),
                                style=ft.ButtonStyle(color=self.colors["text_dark"])
                            ),
                            ft.Container(
                                padding=10,
                                bgcolor=self.colors["background"],
                                border_radius=6,
                                content=ft.TextButton(
                                    "Continue as Guest → Browse Listings",
                                    on_click=lambda _: self.page.go("/browse"),
                                    style=ft.ButtonStyle(color=self.colors["text_light"])
                                )
                            )
                        ]
                    )
                )
            ]
        )
    
    def _close_dialog(self, dialog):
        dialog.open = False
        self.page.update()