"""
ListingCard component for CampusKubo
Handles display of Listing objects for tenants and PMs
"""
import flet as ft
import os
from typing import Optional, Callable, Literal
from models.listing import Listing  # adjust import if your Listing class is elsewhere


class ListingCard:
    """Reusable ListingCard component for Flet, works with Listing objects"""

    def __init__(
        self,
        listing: Listing,
        image_url: str = "",
        is_available: bool = True,
        on_click: Optional[Callable] = None,
        show_actions: bool = False,
        on_edit: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        layout: Literal["vertical", "horizontal"] = "vertical",
    ):
        self.listing = listing
        self.image_url = image_url
        self.is_available = is_available
        self.on_click = on_click
        self.show_actions = show_actions
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.layout = layout

    def build_card(self):
        """Build the main card content"""

        # Return layout based on preference
        if self.layout == "horizontal":
            return self._build_horizontal_card()
        else:
            return self._build_vertical_card()

    def _build_vertical_card(self):
        availability_badge = ft.Container(
            content=ft.Row(
                spacing=4,
                controls=[
                    ft.Icon(
                        ft.Icons.CHECK_CIRCLE if self.is_available else ft.Icons.CANCEL,
                        size=12,
                        color="white",
                    ),
                    ft.Text(
                        "Available" if self.is_available else "Occupied",
                        size=11,
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
            ),
            bgcolor="#4CAF50" if self.is_available else "#F44336",
            padding=ft.padding.symmetric(horizontal=10, vertical=6),
            border_radius=20,
        )

        # Image section
        # Card width and image size: kept consistent to allow side-by-side layout
        CARD_WIDTH = 300
        IMAGE_HEIGHT = 180
        image_section = ft.Container(
            width=CARD_WIDTH - 20,
            height=IMAGE_HEIGHT,
            bgcolor="#E8E8E8",
            border_radius=ft.border_radius.only(top_left=12, top_right=12),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=ft.Stack(
                controls=[
                    ft.Image(
                        src=self.image_url,
                        width=CARD_WIDTH - 20,
                        height=IMAGE_HEIGHT,
                        fit=ft.ImageFit.COVER,
                    )
                    if self.image_url and os.path.exists(self.image_url)
                    else ft.Container(
                        content=ft.Icon(ft.Icons.HOME, size=60, color="#999"),
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(
                        content=availability_badge,
                        alignment=ft.alignment.top_right,
                        margin=10,
                    ),
                ]
            ),
            on_click=self.on_click,  # make the whole image clickable
        )

        # Content section
        address = getattr(self.listing, "address", "")
        price = getattr(self.listing, "price", 0)

        # Safely parse price to a float for formatting; fallback to original if unable
        try:
            numeric_price = float(str(price).replace(',', '').replace('₱', '').strip())
            display_price = f"₱{numeric_price:,.0f}"
        except (ValueError, TypeError):
            display_price = str(price) if price not in (None, '') else "₱0"

        content_controls = [
            ft.Row(
                controls=[
                    ft.Icon(ft.Icons.STAR, size=16, color="#FFB800"),
                    ft.Text("4.8", size=13, weight=ft.FontWeight.BOLD, color="#333"),
                    ft.Text("(24 reviews)", size=11, color="#666"),
                ],
                spacing=4,
            ),
            ft.Text(
                address[:30] + "..." if len(address) > 30 else address,
                weight=ft.FontWeight.BOLD,
                size=15,
                color="#1A1A1A",
            ),
            ft.Row(
                controls=[
                    ft.Text(
                        display_price,
                        color="#0078FF",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text("/mo", color="#666", size=12),
                ],
                spacing=2,
            ),
        ]

        # Management buttons
        if self.show_actions:
            content_controls.append(
                ft.Row(
                    spacing=5,
                    controls=[
                        ft.ElevatedButton(
                            "Edit",
                            icon=ft.Icons.EDIT,
                            on_click=self.on_edit,
                        ),
                        ft.OutlinedButton(
                            "Delete",
                            icon=ft.Icons.DELETE,
                            on_click=self.on_delete,
                        ),
                    ],
                )
            )

        # Always include a 'View Details' CTA below the content
        content_controls.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.OutlinedButton(
                        "View Details",
                        on_click=self.on_click,
                        width=120,
                        height=36,
                        style=ft.ButtonStyle(
                            color="#0078FF",
                            shape=ft.RoundedRectangleBorder(radius=20),
                        )
                    )
                ]
            )
        )

        content_section = ft.Container(
            padding=15,
            content=ft.Column(spacing=8, controls=content_controls),
        )

        # Main card container with background, radius, and shadow
        return ft.Container(
            width=CARD_WIDTH,
            padding=0,
            bgcolor="#FFFFFF",
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=20,
                color="#00000010",
                offset=ft.Offset(0, 6),
            ),
            content=ft.Column(
                spacing=0,
                controls=[image_section, content_section],
            )
        )

    def _build_horizontal_card(self):
        """Build horizontal card layout - image on left, content on right (for PM dashboard)"""
        availability_badge = ft.Container(
            content=ft.Row(
                spacing=4,
                controls=[
                    ft.Icon(
                        ft.Icons.CHECK_CIRCLE if self.is_available else ft.Icons.CANCEL,
                        size=14,
                        color="white",
                    ),
                    ft.Text(
                        "Available" if self.is_available else "Occupied",
                        size=12,
                        color="white",
                        weight="bold",
                    ),
                ],
            ),
            bgcolor="#4CAF50" if self.is_available else "#F44336",
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            border_radius=20,
        )

        # Image section
        IMAGE_WIDTH = 250
        IMAGE_HEIGHT = 200
        address = getattr(self.listing, "address", "")
        price = getattr(self.listing, "price", 0)
        description = getattr(self.listing, "description", "")

        # Safely parse price
        try:
            numeric_price = float(str(price).replace(',', '').replace('₱', '').strip())
            display_price = f"₱{numeric_price:,.2f}/month"
        except (ValueError, TypeError):
            display_price = f"₱{price}" if price else "₱0"

        image_section = ft.Container(
            width=IMAGE_WIDTH,
            height=IMAGE_HEIGHT,
            bgcolor="#E8E8E8",
            border_radius=ft.border_radius.only(top_left=12, bottom_left=12),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=ft.Stack(
                controls=[
                    ft.Image(
                        src=self.image_url,
                        width=IMAGE_WIDTH,
                        height=IMAGE_HEIGHT,
                        fit=ft.ImageFit.COVER,
                    )
                    if self.image_url and os.path.exists(self.image_url)
                    else ft.Container(
                        content=ft.Icon(ft.Icons.HOME, size=60, color="#999"),
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(
                        content=availability_badge,
                        alignment=ft.alignment.top_right,
                        margin=10,
                    ),
                ]
            ),
        )

        # Content section
        content_controls = [
            ft.Row(
                controls=[
                    ft.Text(
                        address,
                        size=20,
                        weight="bold",
                        color="#1A1A1A",
                        expand=True,
                    ),
                ]
            ),
            ft.Row(
                controls=[
                    ft.Icon(ft.Icons.ATTACH_MONEY, size=20, color="#0078FF"),
                    ft.Text(display_price, size=18, color="#0078FF", weight="bold"),
                ],
                spacing=5,
            ),
            ft.Container(
                content=ft.Text(
                    description[:120] + "..." if len(description) > 120 else description,
                    size=13,
                    color="#666",
                ),
                height=40,
            ),
        ]

        # Action buttons
        if self.show_actions:
            content_controls.append(
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.ElevatedButton(
                            "Edit",
                            icon=ft.Icons.EDIT,
                            style=ft.ButtonStyle(
                                color="white",
                                bgcolor="#0078FF",
                            ),
                            on_click=self.on_edit,
                        ),
                        ft.OutlinedButton(
                            "Delete",
                            icon=ft.Icons.DELETE_OUTLINED,
                            style=ft.ButtonStyle(
                                color="#F44336",
                            ),
                            on_click=self.on_delete,
                        ),
                    ],
                )
            )

        content_section = ft.Container(
            expand=True,
            padding=20,
            content=ft.Column(spacing=12, controls=content_controls),
        )

        # Main horizontal card
        return ft.Container(
            bgcolor="#FFFFFF",
            padding=0,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color="#00000015",
                offset=ft.Offset(0, 4),
            ),
            content=ft.Row(spacing=0, controls=[image_section, content_section]),
        )

