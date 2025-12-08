"""
Signup view 
"""
import flet as ft
from storage.db import create_user, validate_password, validate_email
from config.colors import COLORS
from utils.navigation import go_home


class SignupView:
    """Signup page view"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.selected_role = ft.Text("Tenant", visible=False)
        self.colors = COLORS

    def change_role(self, role):
        self.selected_role.value = role
        self.tenant_button.bgcolor = self.colors["primary"] if role == "Tenant" else self.colors["background"]
        self.tenant_button.color = self.colors["card_bg"] if role == "Tenant" else self.colors["text_dark"]
        self.pm_button.bgcolor = self.colors["primary"] if role == "Property Manager" else self.colors["background"]
        self.pm_button.color = self.colors["card_bg"] if role == "Property Manager" else self.colors["text_dark"]
        self.page.update()

    def build(self):
        """Build signup view - matching model"""
        self.page.title = "CampusKubo - Sign Up"

        self.tenant_button = ft.ElevatedButton(
            "🏠 Tenant",
            width=150,
            bgcolor=self.colors["primary"],
            color=self.colors["card_bg"],
            on_click=lambda _: self.change_role("Tenant")
        )

        self.pm_button = ft.ElevatedButton(
            "🏢 Property Manager",
            width=160,
            bgcolor=self.colors["background"],
            color=self.colors["text_dark"],
            bgcolor="#e4e4e4",
            color="black",
            on_click=lambda _: self.change_role("Property Manager")
        )

        # Form fields with real-time validation hints
        full_name = ft.TextField(
            label="Full Name",
            width=330,
            hint_text="e.g., Juan Dela Cruz",
            prefix_icon=ft.Icons.PERSON,
            bgcolor=self.colors["background"],
            border_color=self.colors["border"],
            focused_border_color=self.colors["primary"],
            color=self.colors["text_dark"]
        )

        email = ft.TextField(
            label="Email Address",
            width=330,
            hint_text="e.g., juan@example.com",
            prefix_icon=ft.Icons.EMAIL,
            keyboard_type=ft.KeyboardType.EMAIL,
            bgcolor=self.colors["background"],
            border_color=self.colors["border"],
            focused_border_color=self.colors["primary"],
            color=self.colors["text_dark"]
        )

        # Password requirements display
        req_length = ft.Row([
            ft.Icon(ft.Icons.CIRCLE, size=12, color=self.colors["border"]),
            ft.Text("At least 8 characters", size=11, color=self.colors["text_light"])
        ], spacing=5)

        req_uppercase = ft.Row([
            ft.Icon(ft.Icons.CIRCLE, size=12, color=self.colors["border"]),
            ft.Text("One uppercase letter", size=11, color=self.colors["text_light"])
        ], spacing=5)

        req_number = ft.Row([
            ft.Icon(ft.Icons.CIRCLE, size=12, color=self.colors["border"]),
            ft.Text("One number", size=11, color=self.colors["text_light"])
        ], spacing=5)

        req_special = ft.Row([
            ft.Icon(ft.Icons.CIRCLE, size=12, color=self.colors["border"]),
            ft.Text("One special character (!@#$%^&*)", size=11, color=self.colors["text_light"])
            ft.Icon(ft.Icons.CIRCLE, size=12, color=ft.Colors.GREY),
            ft.Text("At least 8 characters", size=11, color=ft.Colors.GREY)
        ], spacing=5)

        password_requirements = ft.Column(
            visible=False,
            spacing=5,
            controls=[
                ft.Text("Password requirements:", size=12, color=self.colors["text_dark"], weight=ft.FontWeight.BOLD),
                req_length,
                req_uppercase,
                req_number,
                req_special,
            ]
        )
        def validate_password_live(e):
            """Real-time password validation with visual feedback"""
            pwd = password.value or ""
            password_requirements.visible = True
            # Check each requirement
            has_length = len(pwd) >= 8
            has_uppercase = any(c.isupper() for c in pwd)
            has_number = any(c.isdigit() for c in pwd)
            has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in pwd)

            # Update length requirement
            req_length.controls[0] = ft.Icon(ft.Icons.CHECK_CIRCLE if has_length else ft.Icons.CIRCLE, size=12, color=self.colors["success"] if has_length else self.colors["border"])
            req_length.controls[1] = ft.Text("At least 8 characters", size=11, color=self.colors["success"] if has_length else self.colors["text_light"])

            # Update uppercase requirement
            req_uppercase.controls[0] = ft.Icon(ft.Icons.CHECK_CIRCLE if has_uppercase else ft.Icons.CIRCLE, size=12, color=self.colors["success"] if has_uppercase else self.colors["border"])
            req_uppercase.controls[1] = ft.Text("One uppercase letter", size=11, color=self.colors["success"] if has_uppercase else self.colors["text_light"])

            # Update number requirement
            req_number.controls[0] = ft.Icon(ft.Icons.CHECK_CIRCLE if has_number else ft.Icons.CIRCLE, size=12, color=self.colors["success"] if has_number else self.colors["border"])
            req_number.controls[1] = ft.Text("One number", size=11, color=self.colors["success"] if has_number else self.colors["text_light"])

            # Update special character requirement
            req_special.controls[0] = ft.Icon(ft.Icons.CHECK_CIRCLE if has_special else ft.Icons.CIRCLE, size=12, color=self.colors["success"] if has_special else self.colors["border"])
            req_special.controls[1] = ft.Text("One special character (!@#$%^&*)", size=11, color=self.colors["success"] if has_special else self.colors["text_light"])

            password_requirements.update()

        password = ft.TextField(
            label="Password",
            width=330,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK,
            on_change=validate_password_live,
            bgcolor=self.colors["background"],
            border_color=self.colors["border"],
            focused_border_color=self.colors["primary"],
            color=self.colors["text_dark"]
        )

        confirm_pw = ft.TextField(
            label="Confirm Password",
            width=330,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            bgcolor=self.colors["background"],
            border_color=self.colors["border"],
            focused_border_color=self.colors["primary"],
            color=self.colors["text_dark"]
        )

        agree = ft.Checkbox(
            value=False,
            fill_color=self.colors["primary"],
            check_color=self.colors["card_bg"]
        )
        terms_text = ft.Text(
            "I agree to the Terms and Conditions and Privacy Policies",
            size=12,
            color=self.colors["text_dark"]
        )

        msg = ft.Text(" ", size=12, text_align=ft.TextAlign.CENTER)
        loading = ft.ProgressRing(visible=False, width=20, height=20, color=self.colors["primary"])

        def do_signup(e):
            # Clear previous messages
            msg.value = ""
            msg.color = self.colors["error"]
            loading.visible = True
            self.page.update()

            # Validate all fields are filled
            if not full_name.value or not full_name.value.strip():
                msg.value = "❌ Full name is required"
                loading.visible = False
                msg.update()
                loading.update()
                return

            if not email.value or not email.value.strip():
                msg.value = "❌ Email address is required"
                loading.visible = False
                msg.update()
                loading.update()
                return

            if not password.value:
                msg.value = "❌ Password is required"
                loading.visible = False
                msg.update()
                loading.update()
                return

            # Check if passwords match
            if password.value != confirm_pw.value:
                msg.value = "❌ Passwords do not match"
                loading.visible = False
                msg.update()
                loading.update()
                return

            # Check terms agreement
            if not agree.value:
                msg.value = "❌ You must agree to the Terms and Conditions"
                loading.visible = False
                msg.update()
                loading.update()
                return

            is_valid, validation_msg = validate_password(password.value)
            if not is_valid:
                msg.value = f"❌ {validation_msg}"
                loading.visible = False
                msg.update()
                loading.update()
                return

            is_valid, validation_msg = validate_email(email.value)
            if not is_valid:
                msg.value = f"❌ {validation_msg}"
                loading.visible = False
                msg.update()
                loading.update()
                return

            # Create user (validation happens in create_user function)
            success, message = create_user(
                full_name.value,
                email.value,
                password.value,
                "tenant" if self.selected_role.value == "Tenant" else "pm"
            )

            loading.visible = False

            if success:
                msg.value = f"✅ {message}! A confirmation email has been sent to {email.value}. You may now log in."
                msg.color = self.colors["success"]

                # Clear form after successful registration
                full_name.value = ""
                email.value = ""
                password.value = ""
                confirm_pw.value = ""
                agree.value = False
            else:
                msg.value = f"❌ {message}"
                msg.color = self.colors["error"]

            msg.update()
            loading.update()

        # Role selection info box
        role_info = ft.Container(
            padding=10,
            bgcolor=self.colors["background"],
            border_radius=6,
            border=ft.border.all(1, self.colors["border"]),
            content=ft.Column(
                spacing=5,
                controls=[
                    ft.Text("Choose your role:", size=12, weight=ft.FontWeight.BOLD, color=self.colors["text_dark"]),
                    ft.Text("🏠 Tenant - Search and book accommodations", size=11, color=self.colors["text_light"]),
                    ft.Text("🏢 Property Manager - List and manage properties", size=11, color=self.colors["text_light"]),
                ]
            )
        )

        return ft.View(
            "/signup",
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
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

                            # Header
                            ft.Text("Create Account", size=26, weight=ft.FontWeight.BOLD, color=self.colors["text_dark"]),
                            ft.Text("Join CampusKubo today!", size=14, weight=ft.FontWeight.BOLD, color=self.colors["text_light"]),

                            ft.Container(height=5),

                            # Role selection
                            role_info,
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[self.tenant_button, self.pm_button]
                            ),

                            ft.Container(height=5),

                            # Form fields
                            full_name,
                            email,
                            password,
                            password_requirements,
                            confirm_pw,

                            # Terms checkbox
                            ft.Row(
                                controls=[agree, terms_text],
                                alignment=ft.MainAxisAlignment.START,
                                width=330
                            ),

                            # Messages and loading
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[loading, msg]
                            ),

                            # Submit button
                            ft.ElevatedButton(
                                "Create Account",
                                width=330,
                                height=45,
                                on_click=do_signup,
                                bgcolor=self.colors["primary"],
                                color=self.colors["card_bg"]
                            ),

                            # Login link
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Text("Already have an account?", size=13, color=self.colors["text_dark"]),
                                    ft.TextButton(
                                        "Login",
                                        on_click=lambda _: self.page.go("/login"),
                                        style=ft.ButtonStyle(color=self.colors["primary"])
                                    ),
                                ]
                            )
                        ]
                    )
                )
            ]
        )