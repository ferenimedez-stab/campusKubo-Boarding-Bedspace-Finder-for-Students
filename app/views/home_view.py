"""
Home/Landing page view
"""
import flet as ft
from typing import Any
from storage.db import get_properties
from components.signup_banner import SignupBanner
from components.listing_card import create_home_listing_card
from config.colors import COLORS

class HomeView:
    """Home page view"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.colors = COLORS

    def build(self) -> ft.View:
        """Build home view - matching model"""
        search_input = ft.TextField(
            hint_text="Search by Keyword or Location...",
            width=650,
            prefix_icon=ft.Icons.SEARCH,
            on_submit=lambda e: self._perform_search(e.control.value),
            bgcolor=self.colors["card_bg"],
            border_color=self.colors["border"],
            focused_border_color=self.colors["primary"],
            color=self.colors["text_dark"]
        )

        filters: dict[str, Any] = {
            "price_min": None,
            "price_max": None,
            "room_type": None,
            "amenities": None,
            "location": None
        }

        # Fetch properties for featured section
        try:
            all_properties = get_properties() or []
            featured_properties = all_properties[:5]
        except Exception:
            featured_properties = []

        def show_price_filter(e):
            price_min = ft.TextField(
                label="Min Price",
                hint_text="e.g., ₱1000",
                keyboard_type=ft.KeyboardType.NUMBER,
                width=180,
                bgcolor=self.colors["background"],
                border_color=self.colors["border"],
                color=self.colors["text_dark"]
            )
            price_max = ft.TextField(
                label="Max Price",
                hint_text="e.g., ₱50000",
                keyboard_type=ft.KeyboardType.NUMBER,
                width=180,
                bgcolor=self.colors["background"],
                border_color=self.colors["border"],
                color=self.colors["text_dark"]
            )

            def apply_price(e):
                if price_min.value:
                    filters["price_min"] = float(price_min.value)
                if price_max.value:
                    filters["price_max"] = float(price_max.value)
                dialog.open = False
                self.page.update()
                snack_bar = ft.SnackBar(
                    ft.Text("Price filter applied.", color=self.colors["card_bg"]),
                    bgcolor=self.colors["accent"]
                )
                self.page.overlay.append(snack_bar)
                snack_bar.open = True
                self.page.update()

            dialog = ft.AlertDialog(
                title=ft.Text("💰 Set Price Range", color=self.colors["text_dark"], size=18),
                content=ft.Container(
                    width=400,
                    padding=10,
                    content=ft.Column([
                        ft.Row([price_min, price_max], spacing=10),
                    ], tight=True),
                ),
                actions=[
                    ft.TextButton("Apply", on_click=apply_price, style=ft.ButtonStyle(color=self.colors["primary"])),
                    ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(dialog), style=ft.ButtonStyle(color=self.colors["text_light"]))
                ],
                bgcolor=self.colors["card_bg"]
            )
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()

        def show_room_type_filter(e):
            room_types = ["Single", "Double", "Shared", "Studio"]
            selected = ft.Ref()

            def apply_room_type(e):
                if selected.current and selected.current.value:
                    filters["room_type"] = selected.current.value
                dialog.open = False
                self.page.update()
                snack_bar = ft.SnackBar(
                    ft.Text(f"Room type '{selected.current.value}' selected.", color=self.colors["card_bg"]),
                    bgcolor=self.colors["accent"]
                )
                self.page.overlay.append(snack_bar)
                snack_bar.open = True
                self.page.update()

            dialog = ft.AlertDialog(
                title=ft.Text("🛏 Select Room Type", color=self.colors["text_dark"]),
                content=ft.Dropdown(
                    ref=selected,
                    options=[ft.dropdown.Option(rt) for rt in room_types],
                    width=200,
                    bgcolor=self.colors["background"],
                    border_color=self.colors["border"],
                    color=self.colors["text_dark"]
                ),
                actions=[
                    ft.TextButton("Apply", on_click=apply_room_type, style=ft.ButtonStyle(color=self.colors["primary"])),
                    ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(dialog), style=ft.ButtonStyle(color=self.colors["text_light"]))
                ],
                bgcolor=self.colors["card_bg"]
            )
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()

        def show_amenities_filter(e):
            amenities_list = ["WiFi", "Air Conditioning", "Kitchen", "Laundry", "Parking", "Security"]
            selected = ft.Ref()

            def apply_amenities(e):
                if selected.current and selected.current.value:
                    filters["amenities"] = selected.current.value
                dialog.open = False
                self.page.update()
                snack_bar = ft.SnackBar(
                    ft.Text(f"Amenity '{selected.current.value}' selected.", color=self.colors["card_bg"]),
                    bgcolor=self.colors["accent"]
                )
                self.page.overlay.append(snack_bar)
                snack_bar.open = True
                self.page.update()

            dialog = ft.AlertDialog(
                title=ft.Text("🏠 Select Amenities", color=self.colors["text_dark"]),
                content=ft.Dropdown(
                    ref=selected,
                    options=[ft.dropdown.Option(am) for am in amenities_list],
                    width=200,
                    bgcolor=self.colors["background"],
                    border_color=self.colors["border"],
                    color=self.colors["text_dark"]
                ),
                actions=[
                    ft.TextButton("Apply", on_click=apply_amenities, style=ft.ButtonStyle(color=self.colors["primary"])),
                    ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(dialog), style=ft.ButtonStyle(color=self.colors["text_light"]))
                ],
                bgcolor=self.colors["card_bg"]
            )
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()

        def show_availability_filter(e):
            statuses = ["All", "Available", "Reserved", "Full"]
            selected = ft.Ref()

            def apply_availability(e):
                if selected.current and selected.current.value and selected.current.value != "All":
                    filters["availability"] = selected.current.value
                else:
                    filters["availability"] = None
                dialog.open = False
                self.page.update()
                snack_bar = ft.SnackBar(
                    ft.Text("Availability filter applied!", color=self.colors["card_bg"]),
                    bgcolor=self.colors["accent"]
                )
                self.page.overlay.append(snack_bar)
                snack_bar.open = True
                self.page.update()

            dialog = ft.AlertDialog(
                title=ft.Text("📅 Select Availability", color=self.colors["text_dark"]),
                content=ft.Dropdown(
                    ref=selected,
                    label="Status",
                    value="All",
                    options=[ft.dropdown.Option(status) for status in statuses],
                    width=250,
                    bgcolor=self.colors["background"],
                    border_color=self.colors["border"],
                    color=self.colors["text_dark"]
                ),
                actions=[
                    ft.TextButton("Apply", on_click=apply_availability, style=ft.ButtonStyle(color=self.colors["primary"])),
                    ft.ElevatedButton("Cancel", on_click=lambda _: self._close_dialog(dialog), bgcolor=self.colors["text_light"], color=self.colors["card_bg"]),
                ],
                bgcolor=self.colors["card_bg"]
            )
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()

        def show_location_filter(e):
            location_input = ft.TextField(
                label="Location",
                hint_text="e.g., Quezon City",
                width=250,
                bgcolor=self.colors["background"],
                border_color=self.colors["border"],
                color=self.colors["text_dark"]
            )

            def apply_location(e):
                if location_input.value:
                    filters["location"] = location_input.value
                dialog.open = False
                self.page.update()
                snack_bar = ft.SnackBar(
                    ft.Text(f"Location '{location_input.value}' applied!", color=self.colors["card_bg"]),
                    bgcolor=self.colors["accent"]
                )
                self.page.overlay.append(snack_bar)
                snack_bar.open = True
                self.page.update()

            dialog = ft.AlertDialog(
                title=ft.Text("📍 Enter Location", color=self.colors["text_dark"]),
                content=location_input,
                actions=[
                    ft.TextButton("Cancel", on_click=lambda _: self._close_dialog(dialog), style=ft.ButtonStyle(color=self.colors["text_light"])),
                    ft.ElevatedButton("Apply", on_click=apply_location, bgcolor=self.colors["primary"], color=self.colors["card_bg"]),
                ],
                bgcolor=self.colors["card_bg"]
            )
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()

        filters_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            controls=[
                ft.OutlinedButton(
                    "💰 Price Range",
                    on_click=show_price_filter,
                    style=ft.ButtonStyle(
                        color=self.colors["text_dark"],
                        side=ft.BorderSide(color=self.colors["border"], width=1)
                    )
                ),
                ft.OutlinedButton(
                    "🏠 Amenities",
                    on_click=show_amenities_filter,
                    style=ft.ButtonStyle(
                        color=self.colors["text_dark"],
                        side=ft.BorderSide(color=self.colors["border"], width=1)
                    )
                ),
                ft.OutlinedButton(
                    "🛏 Room Type",
                    on_click=show_room_type_filter,
                    style=ft.ButtonStyle(
                        color=self.colors["text_dark"],
                        side=ft.BorderSide(color=self.colors["border"], width=1)
                    )
                ),
                ft.OutlinedButton(
                    "📅 Availability",
                    on_click=show_availability_filter,
                    style=ft.ButtonStyle(
                        color=self.colors["text_dark"],
                        side=ft.BorderSide(color=self.colors["border"], width=1)
                    )
                ),
                ft.OutlinedButton(
                    "📍 Location",
                    on_click=show_location_filter,
                    style=ft.ButtonStyle(
                        color=self.colors["text_dark"],
                        side=ft.BorderSide(color=self.colors["border"], width=1)
                    )
                ),
            ]
        )

        # Featured Listings Cards
        def listing_card(property_data, show_details_button=True):
            listing_payload = dict(property_data)
            listing_payload.setdefault("property_name", property_data.get("name") or property_data.get("address"))
            listing_payload.setdefault("description", property_data.get("description", ""))
            listing_payload.setdefault("price", property_data.get("price", 0))

            image_url = property_data.get("image_url")
            property_id = property_data.get("id")
            availability = property_data.get("availability_status", "Available")
            is_available = str(availability).lower() == "available"

            def view_details(_):
                self.page.session.set("selected_property_id", property_id)
                self.page.go("/property-details")

            return create_home_listing_card(
                listing=listing_payload,
                image_url=image_url,
                is_available=is_available,
                on_click=view_details if show_details_button else None,
                show_cta=show_details_button,
                page=self.page,
            )

        featured_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            controls=[listing_card(prop) for prop in featured_properties] if featured_properties else [ft.Text("No properties available", size=16, color=self.colors["text_light"])]
        )

        from components.logo import Logo

        nav_bar = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                Logo(size=22, color=self.colors["primary"]),
                ft.Row([
                    ft.TextButton(
                        "Login",
                        on_click=lambda _: self.page.go("/login"),
                        style=ft.ButtonStyle(color=self.colors["text_dark"])
                    ),
                    ft.TextButton(
                        "Register",
                        on_click=lambda _: self.page.go("/signup"),
                        style=ft.ButtonStyle(color=self.colors["text_dark"])
                    )
                ])
            ]
        )

        # About Section
        about_section = ft.Container(
            padding=30,
            bgcolor=self.colors["card_bg"],
            border_radius=12,
            border=ft.border.all(1, self.colors["border"]),
            shadow=ft.BoxShadow(blur_radius=10, spread_radius=2, color="#D4C4B080"),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                controls=[
                    ft.Text(
                        "About CampusKubo",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=self.colors["primary"]
                    ),
                    ft.Container(
                        width=60,
                        height=3,
                        bgcolor=self.colors["accent"],
                        border_radius=2
                    ),
                    ft.Text(
                        "Your trusted platform for finding comfortable and affordable student accommodation near campus.",
                        size=16,
                        color=self.colors["text_dark"],
                        text_align=ft.TextAlign.CENTER,
                        max_lines=3
                    ),
                    ft.Container(height=10),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=40,
                        controls=[
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=5,
                                controls=[
                                    ft.Icon(ft.Icons.HOME_WORK, size=40, color=self.colors["primary"]),
                                    ft.Text("Verified Listings", weight=ft.FontWeight.BOLD, color=self.colors["text_dark"]),
                                    ft.Text("Quality-checked properties", size=12, color=self.colors["text_light"])
                                ]
                            ),
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=5,
                                controls=[
                                    ft.Icon(ft.Icons.SHIELD, size=40, color=self.colors["secondary"]),
                                    ft.Text("Safe & Secure", weight=ft.FontWeight.BOLD, color=self.colors["text_dark"]),
                                    ft.Text("Protected transactions", size=12, color=self.colors["text_light"])
                                ]
                            ),
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=5,
                                controls=[
                                    ft.Icon(ft.Icons.SUPPORT_AGENT, size=40, color=self.colors["accent"]),
                                    ft.Text("24/7 Support", weight=ft.FontWeight.BOLD, color=self.colors["text_dark"]),
                                    ft.Text("Always here to help", size=12, color=self.colors["text_light"])
                                ]
                            )
                        ]
                    )
                ]
            )
        )

        return ft.View(
            "/",
            padding=25,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            bgcolor=self.colors["background"],
            controls=[
                nav_bar,
                ft.Container(height=15),
                search_input,
                filters_row,
                ft.Container(height=15),
                ft.Text(
                    "Find your next HOME away to Home",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=self.colors["text_dark"]
                ),
                ft.Container(height=15),
                ft.Container(height=20),
                featured_row,
                ft.Container(height=30),
                ft.Container(
                    padding=20,
                    bgcolor=self.colors["card_bg"],
                    border_radius=8,
                    border=ft.border.all(1, self.colors["border"]),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                "🔍 Want to explore more listings?",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=self.colors["text_dark"]
                            ),
                            ft.Text(
                                "Browse all available properties without creating an account.",
                                size=14,
                                color=self.colors["text_light"]
                            ),
                            ft.ElevatedButton(
                                "Browse Listings as Guest",
                                icon=ft.Icons.SEARCH,
                                on_click=lambda _: self.page.go("/browse"),
                                bgcolor=self.colors["accent"],
                                color=self.colors["card_bg"]
                            )
                        ]
                    )
                ),
                ft.Container(height=30),
                about_section,
            ]
        )

    def _perform_search(self, query):
        self.page.session.set("search_query", query)
        self.page.session.set("filters", {})
        self.page.go("/browse")

    def _close_dialog(self, dialog):
        dialog.open = False
        self.page.update()