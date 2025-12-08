"""
Home/Landing page view
"""
import flet as ft
from typing import Any
from storage.db import get_properties
from components.signup_banner import SignupBanner


class HomeView:
    """Home page view"""

    def __init__(self, page: ft.Page):
        self.page = page

    def build(self) -> ft.View:
        """Build home view - matching model"""
        search_input = ft.TextField(
            hint_text="Search by Keyword or Location...",
            width=650,
            prefix_icon=ft.Icons.SEARCH,
            on_submit=lambda e: self._perform_search(e.control.value)
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
            featured_properties = get_properties() or []
        except Exception:
            featured_properties = []

        def show_price_filter(e):
            price_min = ft.TextField(
                label="Min Price",
                hint_text="e.g., ₱1000",
                keyboard_type=ft.KeyboardType.NUMBER,
                width=150
            )
            price_max = ft.TextField(
                label="Max Price",
                hint_text="e.g., ₱5000",
                keyboard_type=ft.KeyboardType.NUMBER,
                width=150
            )

            def apply_price(e):
                if price_min.value:
                    filters["price_min"] = float(price_min.value)
                if price_max.value:
                    filters["price_max"] = float(price_max.value)
                dialog.open = False
                self.page.update()
                snack_bar = ft.SnackBar(ft.Text("Price filter applied."))
                self.page.overlay.append(snack_bar)
                snack_bar.open = True
                self.page.update()

            dialog = ft.AlertDialog(
                title=ft.Text("💰 Set Price Range"),
                content=ft.Column([
                    ft.Row([price_min, price_max], spacing=10),
                ], tight=True),
                actions=[
                    ft.TextButton("Apply", on_click=apply_price),
                    ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(dialog))
                ]
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
                snack_bar = ft.SnackBar(ft.Text(f"Room type '{selected.current.value}' selected."))
                self.page.overlay.append(snack_bar)
                snack_bar.open = True
                self.page.update()

            dialog = ft.AlertDialog(
                title=ft.Text("🛏 Select Room Type"),
                content=ft.Dropdown(
                    ref=selected,
                    options=[ft.dropdown.Option(rt) for rt in room_types],
                    width=200
                ),
                actions=[
                    ft.TextButton("Apply", on_click=apply_room_type),
                    ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(dialog))
                ]
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
                snack_bar = ft.SnackBar(ft.Text(f"Amenity '{selected.current.value}' selected."))
                self.page.overlay.append(snack_bar)
                snack_bar.open = True
                self.page.update()

            dialog = ft.AlertDialog(
                title=ft.Text("🏠 Select Amenities"),
                content=ft.Dropdown(
                    ref=selected,
                    options=[ft.dropdown.Option(am) for am in amenities_list],
                    width=200
                ),
                actions=[
                    ft.TextButton("Apply", on_click=apply_amenities),
                    ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(dialog))
                ]
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
                snack_bar = ft.SnackBar(ft.Text("Availability filter applied!"))
                self.page.overlay.append(snack_bar)
                snack_bar.open = True
                self.page.update()

            dialog = ft.AlertDialog(
                title=ft.Text("📅 Select Availability"),
                content=ft.Dropdown(
                    ref=selected,
                    label="Status",
                    value="All",
                    options=[ft.dropdown.Option(status) for status in statuses],
                    width=250
                ),
                actions=[
                    ft.TextButton("Apply", on_click=apply_availability),
                    ft.ElevatedButton("Cancel", on_click=lambda _: self._close_dialog(dialog)),
                ]
            )
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()

        def show_location_filter(e):
            location_input = ft.TextField(
                label="Location",
                hint_text="e.g., Quezon City",
                width=250
            )

            def apply_location(e):
                if location_input.value:
                    filters["location"] = location_input.value
                dialog.open = False
                self.page.update()
                snack_bar = ft.SnackBar(ft.Text(f"Location '{location_input.value}' applied!"))
                self.page.overlay.append(snack_bar)
                snack_bar.open = True
                self.page.update()

            dialog = ft.AlertDialog(
                title=ft.Text("📍 Enter Location"),
                content=location_input,
                actions=[
                    ft.TextButton("Cancel", on_click=lambda _: self._close_dialog(dialog)),
                    ft.ElevatedButton("Apply", on_click=apply_location),
                ]
            )
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()

        filters_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            controls=[
                ft.OutlinedButton("💰 Price Range", on_click=show_price_filter),
                ft.OutlinedButton("🏠 Amenities", on_click=show_amenities_filter),
                ft.OutlinedButton("🛏 Room Type", on_click=show_room_type_filter),
                ft.OutlinedButton("📅 Availability", on_click=show_availability_filter),
                ft.OutlinedButton("📍 Location", on_click=show_location_filter),
            ]
        )

        # Featured Listings Cards
        def listing_card(property_data, show_details_button=True):
            name = property_data.get("name", "Boarding House")
            price = property_data.get("price", 0)
            price = f"₱{price:,.0f}/mo"
            rating = "★★★★★"
            image_url = property_data.get("image_url")
            property_id = property_data.get("id")

            def view_details(e):
                self.page.session.set("selected_property_id", property_id)
                self.page.go("/property-details")

            card_controls = [
                ft.Container(
                    width=180,
                    height=120,
                    bgcolor="#dfdfdf",
                    border_radius=6,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    content=ft.Image(
                        src=image_url,
                        width=180,
                        height=120,
                        fit=ft.ImageFit.COVER,
                    ) if image_url else ft.Icon(ft.Icons.HOME, size=60, color=ft.Colors.BLACK),
                ),
                ft.Text(rating, size=14, weight=ft.FontWeight.BOLD),
                ft.Text(name, weight=ft.FontWeight.BOLD, size=14),
                ft.Text(price, color="black", size=13)
            ]

            if show_details_button:
                card_controls.append(
                    ft.ElevatedButton(
                        "View Details",
                        width=140,
                        height=35,
                        on_click=view_details
                    )
                )

            return ft.Container(
                bgcolor="#ffffff",
                width=200,
                padding=10,
                border_radius=8,
                shadow=ft.BoxShadow(blur_radius=8, spread_radius=1, color="#cccccc"),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=card_controls
                )
            )

        featured_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            controls=[listing_card(prop) for prop in featured_properties] if featured_properties else [ft.Text("No properties available", size=16, color="Black")]
        )

        nav_bar = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(" C🏠mpusKubo", size=22, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.TextButton("Login", on_click=lambda _: self.page.go("/login")),
                    ft.TextButton("Register", on_click=lambda _: self.page.go("/signup")),
                    ft.IconButton(icon=ft.Icons.NOTIFICATIONS, tooltip="Notifications")
                ])
            ]
        )

        return ft.View(
            "/",
            padding=25,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                nav_bar,
                ft.Container(height=15),
                search_input,
                filters_row,
                ft.Container(height=15),
                ft.Text("Find your next HOME away to Home", size=32, weight=ft.FontWeight.BOLD),
                ft.Container(height=15),
                ft.Text("Browse available listing below", size=16, color="#555"),
                ft.Container(height=20),
                featured_row,
                ft.Container(height=30),
                ft.Container(
                    padding=20,
                    bgcolor="#f5f5f5",
                    border_radius=8,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text("🔍 Want to explore more listings?", size=24, weight=ft.FontWeight.BOLD),
                            ft.Text("Browse all available properties without creating an account.", size=14),
                            ft.ElevatedButton(
                                "Browse Listings as Guest",
                                icon=ft.Icons.SEARCH,
                                on_click=lambda _: self.page.go("/browse")
                            )
                        ]
                    )
                )
            ]
        )

    def _perform_search(self, query):
        self.page.session.set("search_query", query)
        self.page.session.set("filters", {})
        self.page.go("/browse")

    def _close_dialog(self, dialog):
        dialog.open = False
        self.page.update()