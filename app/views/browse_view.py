# app/views/browse_view.py
"""
Browse/Search view - displays all approved listings with filtering.
Accessible to guests, tenants, and PMs. No login required.
"""
import flet as ft
from typing import Any
from storage.db import get_properties
from components.signup_banner import SignupBanner
from utils.navigation import go_home


class BrowseView:
    """Browse all available listings with filters"""

    def __init__(self, page: ft.Page):
        self.page = page

    def build(self) -> ft.View:
        """Build browse view - matching model"""
        self.page.title = "CampusKubo Browse Listings"
        filters: dict[str, Any] = self.page.session.get("filters") or {}
        search_query = self.page.session.get("search_query") or ""

        # Get properties from database
        properties = get_properties(search_query, filters)

        back_button = ft.Container(
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_color="#0078ff",
                        icon_size=24,
                        tooltip="Back to Home",
                        on_click=lambda _: go_home(self.page)
                    ),
                    ft.Text("Back to Home", size=14)
                ]
            )
        )

        search_input = ft.TextField(
            hint_text="Search by Keyword or Location...",
            width=650,
            value=search_query,
            prefix_icon=ft.Icons.SEARCH,
            on_submit=lambda e: self._perform_search(e.control.value)
        )

        # Filter controls
        price_min = ft.TextField(
            label="Min Price",
            hint_text="₱1000",
            width=100,
            text_size=12,
            keyboard_type=ft.KeyboardType.NUMBER,
            dense=True
        )

        price_max = ft.TextField(
            label="Max Price",
            hint_text="₱5000",
            width=100,
            text_size=12,
            keyboard_type=ft.KeyboardType.NUMBER,
            dense=True
        )

        room_type_dropdown = ft.Dropdown(
            label="Room Type",
            hint_text="Select Type",
            width=210,
            text_size=12,
            dense=True,
            options=[
                ft.dropdown.Option("Single"),
                ft.dropdown.Option("Double"),
                ft.dropdown.Option("Shared"),
                ft.dropdown.Option("Studio"),
            ]
        )

        amenities_dropdown = ft.Dropdown(
            label="Amenities",
            hint_text="Select amenity",
            width=210,
            text_size=12,
            dense=True,
            options=[
                ft.dropdown.Option("WiFi"),
                ft.dropdown.Option("Air Conditioning"),
                ft.dropdown.Option("Kitchen"),
            ]
        )

        availability_dropdown = ft.Dropdown(
            label="Availability",
            hint_text="Select status",
            width=210,
            text_size=12,
            dense=True,
            options=[
                ft.dropdown.Option("All"),
                ft.dropdown.Option("Available"),
                ft.dropdown.Option("Reserved"),
                ft.dropdown.Option("Full"),
            ],
            value="All"
        )

        location_input = ft.TextField(
            label="Location",
            hint_text="e.g., Near Campus",
            width=210,
            text_size=12,
            dense=True
        )

        def apply_filters(e):
            filters = {
                "price_min": float(price_min.value) if price_min.value else None,
                "price_max": float(price_max.value) if price_max.value else None,
                "room_type": room_type_dropdown.value if room_type_dropdown.value else None,
                "amenities": amenities_dropdown.value if amenities_dropdown.value else None,
                "availability": availability_dropdown.value if availability_dropdown.value and availability_dropdown.value != "All" else None,
                "location": location_input.value if location_input.value else None
            }
            self.page.session.set("filters", filters)
            self.page.go("/browse")

        def clear_filters(e):
            self.page.session.set("filters", {})
            self.page.session.set("search_query", "")
            self.page.go("/browse")

        sidebar = ft.Container(
            width=230,
            padding=15,
            bgcolor="#ffffff",
            border_radius=10,
            content=ft.Column(
                spacing=8,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Text("Filters", size=24, weight=ft.FontWeight.BOLD, color="Black"),
                    ft.Divider(height=1, color="#ddd"),

                    # Price Range Section
                    ft.Container(
                        padding=5,
                        content=ft.Column(
                            spacing=5,
                            controls=[
                                ft.Text("💰 Price Range", weight=ft.FontWeight.BOLD, size=13, color="Green"),
                                ft.Row([price_min, price_max], spacing=8),
                            ]
                        )
                    ),
                    ft.Divider(height=1, color="#e0e0e0"),

                    # Room Type Section
                    ft.Container(
                        padding=5,
                        content=ft.Column(
                            spacing=5,
                            controls=[
                                ft.Text("🛏 Room Type", weight=ft.FontWeight.BOLD, size=13, color="yellow"),
                                room_type_dropdown,
                            ]
                        )
                    ),
                    ft.Divider(height=1, color="#e0e0e0"),

                    # Amenities Section
                    ft.Container(
                        padding=5,
                        content=ft.Column(
                            spacing=5,
                            controls=[
                                ft.Text("🏠 Amenities", weight=ft.FontWeight.BOLD, size=13, color="Magenta"),
                                amenities_dropdown,
                            ]
                        )
                    ),
                    ft.Divider(height=1, color="#e0e0e0"),

                    # Availability Section
                    ft.Container(
                        padding=5,
                        content=ft.Column(
                            spacing=5,
                            controls=[
                                ft.Text("📅 Availability", weight=ft.FontWeight.BOLD, size=13, color="Cyan"),
                                availability_dropdown,
                            ]
                        )
                    ),
                    ft.Divider(height=1, color="#e0e0e0"),

                    # Location Section
                    ft.Container(
                        padding=5,
                        content=ft.Column(
                            spacing=5,
                            controls=[
                                ft.Text("📍 Location", weight=ft.FontWeight.BOLD, size=13, color="orange"),
                                location_input,
                            ]
                        )
                    ),

                    ft.Container(height=10),

                    ft.ElevatedButton(
                        "Apply Filters",
                        width=200,
                        height=45,
                        bgcolor="#0078ff",
                        color="white",
                        on_click=apply_filters
                    ),
                    ft.OutlinedButton(
                        "Clear Filters",
                        width=200,
                        height=45,
                        on_click=clear_filters
                    )
                ]
            )
        )

        # Property listing card
        def property_card(property_data):
            name = property_data.get("name", "Property")
            price = property_data.get("price", 0)
            price = f"₱{price:,.0f}/mo"
            location = property_data.get("location", "N/A")
            availability = property_data.get("availability_status", "Available")
            property_id = property_data.get("id")
            image_url = property_data.get("image_url")

            def view_details(e):
                self.page.session.set("selected_property_id", property_id)
                self.page.go("/property-details")

            return ft.Container(
                bgcolor="#FFFFFF",
                width=280,
                padding=15,
                margin=10,
                border_radius=8,
                shadow=ft.BoxShadow(
                    blur_radius=15,
                    spread_radius=1,
                    color=ft.Colors.with_opacity(0.1, "#000000")
                ),
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Container(
                            width=250,
                            height=150,
                            bgcolor="#dfdfdf",
                            border_radius=8,
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                            content=ft.Image(
                                src=image_url,
                                width=250,
                                height=150,
                                fit=ft.ImageFit.COVER,
                            ) if image_url else ft.Icon(ft.Icons.HOME, size=60, color="#999")
                        ),
                        ft.Container(
                            padding=5,
                            content=ft.Column(
                                spacing=5,
                                controls=[
                                    ft.Text(name, weight=ft.FontWeight.BOLD, size=16, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                    ft.Row([
                                        ft.Icon(ft.Icons.LOCATION_ON, size=16, color=ft.Colors.BLACK),
                                        ft.Text(location, size=14, color=ft.Colors.BLACK, max_lines=1)
                                    ], spacing=4),
                                    ft.Text(price, size=18, color="#0078ff", weight=ft.FontWeight.BOLD),
                                    ft.Container(
                                        padding=ft.padding.symmetric(vertical=2, horizontal=6),
                                        bgcolor="#e0e0e0" if availability == "Available" else "#ffcccc",
                                        border_radius=6,
                                        content=ft.Text(
                                            availability,
                                            size=12,
                                            color="#4caf50" if availability == "Available" else "#f44336",
                                            weight=ft.FontWeight.BOLD,
                                        )
                                    ),
                                    ft.Container(
                                        padding=ft.padding.symmetric(vertical=4, horizontal=8),
                                        bgcolor="#e3f2fd",
                                        border_radius=4,
                                        content=ft.Row(
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            spacing=5,
                                            controls=[
                                                ft.Icon(ft.Icons.INFO_OUTLINE, size=14, color="#1976d2"),
                                                ft.Text("Sign in to reserve", size=11, color="#1565c0", italic=True)
                                            ]
                                        )
                                    )
                                ]
                            )
                        )
                    ]
                ),
                on_click=view_details,
                ink=True,
                tooltip="Click to view details"
            )

        property_grid = ft.Container(
            expand=True,
            padding=15,
            bgcolor="#ffffff",
            border_radius=10,
            content=ft.Column(
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Text(
                        f"Search Results for '{search_query}'" if search_query else "All Available Properties",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color="Black"
                    ),
                    ft.Text(
                        f"Showing {len(properties)} properties",
                        size=14,
                        color=ft.Colors.BLACK
                    ),
                    ft.Divider(height=1, color="#e0e0e0"),

                    ft.Container(
                        content=ft.Row(
                            wrap=True,
                            spacing=15,
                            run_spacing=15,
                            alignment=ft.MainAxisAlignment.START,
                            controls=[property_card(prop) for prop in properties]
                        ) if properties else ft.Container(
                            padding=50,
                            alignment=ft.alignment.center,
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=15,
                                controls=[
                                    ft.Icon(ft.Icons.SEARCH_OFF, size=80, color="#ccc"),
                                    ft.Text("No properties found", size=20, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
                                    ft.Text("Try adjusting your search or filters", size=14, color="black"),
                                    ft.ElevatedButton(
                                        "Clear Filters",
                                        on_click=clear_filters,
                                        bgcolor="#0078ff",
                                        color="white"
                                    )
                                ]
                            )
                        )
                    )
                ]
            )
        )

        signup_banner = SignupBanner(
            page=self.page,
            on_create_click=lambda: self.page.go("/signup"),
            on_signin_click=lambda: self.page.go("/login")
        ).build()

        main_layout = ft.Row(
            spacing=20,
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand=True,
            controls=[
                sidebar,
                property_grid
            ]
        )

        return ft.View(
            "/browse",
            padding=25,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                back_button,
                ft.Container(height=10),
                ft.Text("Browse Listings", size=28, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                search_input,
                ft.Container(height=20),
                main_layout,
                signup_banner
            ]
        )

    def _perform_search(self, query):
        self.page.session.set("search_query", query)
        self.page.go("/browse")
