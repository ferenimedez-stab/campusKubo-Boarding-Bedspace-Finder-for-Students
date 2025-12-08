"""
Property details view
Updated from main.py property_details_view implementation
"""
import flet as ft
from storage.db import get_property_by_id


class PropertyDetailView:
    """Property details view"""

    def __init__(self, page: ft.Page):
        self.page = page

    def build(self):
        """Build property details view - matching model"""
        property_id = self.page.session.get("selected_property_id")

        if not property_id:
            snack_bar = ft.SnackBar(ft.Text("Property not found. Please select a property first."))
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.page.go("/browse")
            return

        property_data = get_property_by_id(property_id)

        if not property_data:
            snack_bar = ft.SnackBar(ft.Text("Property not found. Please select a valid property."))
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.page.go("/browse")
            return

        def handle_action_button(e):
            # Check if user is logged in
            user_role = self.page.session.get("role")
            if not user_role:
                # Show dialog prompting sign-up/login
                show_auth_dialog()
            else:
                # Proceed with reservation
                snack_bar = ft.SnackBar(ft.Text("Reservation feature coming soon!"))
                self.page.overlay.append(snack_bar)
                snack_bar.open = True
                self.page.update()

        def show_auth_dialog():
            def close_dialog():
                dialog.open = False
                self.page.update()

            def close_and_navigate(route):
                dialog.open = False
                self.page.update()
                self.page.go(route)

            dialog = ft.AlertDialog(
                title=ft.Row([
                    ft.Icon(ft.Icons.LOCK_PERSON, color="#f57c00", size=30),
                    ft.Text("Account Required", weight=ft.FontWeight.BOLD)
                ], spacing=10),
                content=ft.Container(
                    width=300,
                    content=ft.Column(
                        tight=True,
                        spacing=10,
                        controls=[
                            ft.Text(
                                "To reserve this property, you need to create an account or sign in.",
                                size=14
                            ),
                            ft.Divider(height=1),
                            ft.Text("✨ Benefits of signing up:", size=13, weight=ft.FontWeight.BOLD),
                            ft.Text("• Reserve properties instantly", size=12),
                            ft.Text("• Contact property owners", size=12),
                            ft.Text("• Save favorite listings", size=12),
                            ft.Text("• Track your reservations", size=12),
                        ]
                    )
                ),
                actions=[
                    ft.ElevatedButton(
                        "Create Account",
                        icon=ft.Icons.PERSON_ADD,
                        bgcolor="#4caf50",
                        color="white",
                        on_click=lambda _: close_and_navigate("/signup")
                    ),
                    ft.OutlinedButton(
                        "Sign In",
                        icon=ft.Icons.LOGIN,
                        on_click=lambda _: close_and_navigate("/login")
                    ),
                    ft.TextButton("Maybe Later", on_click=lambda _: close_dialog()),
                ],
                actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()

        nav_bar = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: self.page.go("/browse")),
                    ft.Text("C🏠mpusKubo", size=22, weight=ft.FontWeight.BOLD),
                ]),
                ft.Row([
                    ft.TextButton("Login", on_click=lambda _: self.page.go("/login")),
                    ft.TextButton("Register", on_click=lambda _: self.page.go("/signup")),
                    ft.IconButton(icon=ft.Icons.NOTIFICATIONS, tooltip="Notifications")
                ])
            ]
        )

        # Determine button state based on login status
        user_role = self.page.session.get("role")
        is_available = property_data.get("availability_status", "Available") == "Available"

        action_button = ft.ElevatedButton(
            "Reserve Now" if is_available else "Contact Owner",
            width=300,
            height=50,
            disabled=not is_available and not user_role,
            on_click=handle_action_button
        )

        amenities_str = property_data.get("amenities", "")
        amenities_list = [a.strip() for a in amenities_str.split(",")] if amenities_str else []

        return ft.View(
            "/property-details",
            padding=25,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                nav_bar,
                ft.Container(height=20),

                ft.Container(
                    bgcolor="#f5f5f5",
                    padding=10,
                    border_radius=6,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                expand=True,
                                spacing=10,
                                controls=[
                                    ft.Text(property_data.get("name", "Property"), size=32, weight=ft.FontWeight.BOLD),
                                    ft.Row([
                                        ft.Icon(ft.Icons.LOCATION_ON, size=20, color="#0078ff"),
                                        ft.Text(property_data.get("address", "N/A"), size=16, color="black")
                                    ], spacing=5),
                                    ft.Row([
                                        ft.Icon(ft.Icons.PLACE, size=20, color="black"),
                                        ft.Text(property_data.get("location", "N/A"), size=16, color="black")
                                    ], spacing=5)
                                ]
                            ),
                            ft.Container(
                                bgcolor="#f0f7ff",
                                padding=15,
                                border_radius=8,
                                content=ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=10,
                                    controls=[
                                        ft.Text("Monthly Rent", size=14, color="black"),
                                        ft.Text(f"₱{property_data.get('price', 0):,.0f}", size=24, weight=ft.FontWeight.BOLD, color="#0078ff")
                                    ]
                                )
                            )
                        ]
                    )

                ),
                ft.Container(height=20),
                # Image gallery placeholder
                ft.Container(
                    bgcolor="#ffffff",
                    padding=20,
                    border_radius=10,
                    content=ft.Column(
                        spacing=15,
                        controls=[
                            ft.Text("Photos", size=20, weight=ft.FontWeight.BOLD, color="black"),
                            ft.Container(
                                width=None,
                                height=400,
                                bgcolor="#dfdfdf",
                                border_radius=10,
                                content=ft.Column(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Icon(ft.Icons.IMAGE, size=80, color=ft.Colors.BLACK),
                                        ft.Text("Property images will be displayed here", color="black")
                                    ]
                                )
                            ),
                        ]
                    )
                ),

                ft.Container(height=20),

                # Description Section
                ft.Container(
                    bgcolor="#ffffff",
                    padding=20,
                    border_radius=10,
                    content=ft.Column(
                        spacing=15,
                        controls=[
                            ft.Text("Description", size=20, weight=ft.FontWeight.BOLD, color="black"),
                            ft.Text(
                                property_data.get("description", "No description available"),
                                size=15,
                                color="#444",
                                text_align=ft.TextAlign.JUSTIFY
                            ),
                        ]
                    )
                ),

                ft.Container(height=20),

                # Property Details Section
                ft.Container(
                    bgcolor="#ffffff",
                    padding=20,
                    border_radius=10,
                    content=ft.Column(
                        spacing=15,
                        controls=[
                            ft.Text("Property Details", size=20, weight=ft.FontWeight.BOLD, color="#333"),
                            ft.Row(
                                wrap=True,
                                spacing=30,
                                controls=[
                                    ft.Container(
                                        bgcolor="#f9f9f9",
                                        padding=15,
                                        border_radius=8,
                                        content=ft.Column([
                                            ft.Icon(ft.Icons.MEETING_ROOM, size=30, color="#0078ff"),
                                            ft.Text("Room Type", size=12, color=ft.Colors.BLACK),
                                            ft.Text(property_data.get("room_type", "N/A"), size=16, weight=ft.FontWeight.BOLD, color="#333")
                                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
                                    ),
                                    ft.Container(
                                        bgcolor="#f9f9f9",
                                        padding=15,
                                        border_radius=8,
                                        content=ft.Column([
                                            ft.Icon(
                                                ft.Icons.CHECK_CIRCLE if is_available else ft.Icons.CANCEL,
                                                size=30,
                                                color="#4caf50" if is_available else "#f44336"
                                            ),
                                            ft.Text("Availability", size=12, color=ft.Colors.BLACK),
                                            ft.Text(
                                                property_data.get("availability_status", "N/A"),
                                                size=16,
                                                weight=ft.FontWeight.BOLD,
                                                color="#4caf50" if is_available else "#f44336"
                                            )
                                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
                                    ),
                                    ft.Container(
                                        bgcolor="#f9f9f9",
                                        padding=15,
                                        border_radius=8,
                                        content=ft.Column([
                                            ft.Icon(ft.Icons.BED, size=30, color="#0078ff"),
                                            ft.Text("Available Rooms", size=12, color=ft.Colors.BLACK),
                                            ft.Text(
                                                f"{property_data.get('available_rooms', 0)}/{property_data.get('total_rooms', 0)}",
                                                size=16,
                                                weight=ft.FontWeight.BOLD,
                                                color="#333"
                                            )
                                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
                                    ),
                                ]
                            ),
                        ]
                    )
                ),

                ft.Container(height=20),

                # Amenities Section
                ft.Container(
                    bgcolor="#ffffff",
                    padding=20,
                    border_radius=10,
                    content=ft.Column(
                        spacing=15,
                        controls=[
                            ft.Text("Amenities & Features", size=20, weight=ft.FontWeight.BOLD, color="#333"),
                            ft.Column(
                                spacing=10,
                                controls=[
                                    ft.Row([
                                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=20, color="#4caf50"),
                                        ft.Text(amenity, size=15, color="#444")
                                    ], spacing=10) for amenity in amenities_list
                                ]
                            ) if amenities_list else ft.Text("No amenities listed", size=14, color=ft.Colors.BLACK)
                        ]
                    )
                ),

                ft.Container(height=30),

                # Action Button
                ft.Container(
                    bgcolor="#ffffff",
                    padding=20,
                    border_radius=10,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=10,
                                controls=[
                                    action_button,
                                    ft.Text(
                                        "Sign in to make a reservation" if not user_role else "",
                                        size=12,
                                        color="black",
                                        italic=True
                                    ) if is_available else ft.Text(
                                        "This property is currently not available",
                                        size=12,
                                        color="#f44336",
                                        italic=True
                                    )
                                ]
                            )
                        ]
                    )
                ),

                ft.Container(height=20),
            ]
        )