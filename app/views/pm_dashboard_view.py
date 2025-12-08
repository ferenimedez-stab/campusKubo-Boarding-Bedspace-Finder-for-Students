"""Property Manager dashboard view - integrated design"""
import os
import flet as ft
from services.listing_service import ListingService
from storage.db import get_listing_images, delete_listing
from components.listing_card import ListingCard


class PMDashboardView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.listing_service = ListingService()

    def build(self):
        page = self.page
        user_id = page.session.get("user_id")
        if not user_id:
            page.go("/login")
            return None

        listings_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

        # Avatar for the property manager using their initials
        pm_full_name = page.session.get("full_name") or page.session.get("email") or "User"
        pm_initials = "".join([part[0].upper() for part in pm_full_name.split()[:2] if part]) or "U"
        pm_avatar = ft.Container(
            content=ft.CircleAvatar(
                content=ft.Text(pm_initials, color="white", weight=ft.FontWeight.BOLD),
                bgcolor="#0078FF",
                radius=18,
            ),
            on_click=lambda e: page.go("/pm/profile"),
        )

        # Simple notifications button (placeholder for future logic)
        def open_notifications(e):
            snack = ft.SnackBar(
                content=ft.Text("Notifications feature coming soon."),
                bgcolor="#333333",
                action="OK",
                action_color="#FFFFFF",
            )
            setattr(page, 'snack_bar', snack)
            try:
                getattr(page, 'snack_bar').open = True
            except Exception:
                try:
                    page.open(getattr(page, 'snack_bar'))
                except Exception:
                    pass
            page.update()

        notifications_button = ft.IconButton(
            icon=ft.Icons.NOTIFICATIONS_OUTLINED,
            tooltip="Notifications",
            icon_color="#0078FF",
            on_click=open_notifications,
        )

        def load_listings():
            listings_container.controls.clear()
            # Get all listings for this PM
            listings = self.listing_service.get_all_listings(owner_id=user_id)

            if not listings:
                # Show empty state
                listings_container.controls.append(
                    ft.Container(
                        padding=40,
                        width=800,
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15,
                            controls=[
                                ft.Icon(ft.Icons.ADD_HOME, size=64, color=ft.Colors.BLACK),
                                ft.Text("No listings yet", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                                ft.Text(
                                    "Use the \"Add New Listing\" button above to create your first property.",
                                    size=14,
                                    color=ft.Colors.BLACK,
                                ),
                            ]
                        )
                    )
                )
            else:
                for listing in listings:
                    # Get images and availability for each listing
                    images = get_listing_images(listing.id)
                    is_available = self.listing_service.check_availability(listing.id)

                    card = self._create_listing_card(
                        listing, images, is_available, user_id
                    )
                    listings_container.controls.append(card)

        def show_delete_confirmation(listing_id, listing_name):
            """Show confirmation dialog before deleting a listing."""

            def on_confirm(e):
                dlg.open = False
                page.update()
                perform_delete(listing_id)

            def on_cancel(e):
                dlg.open = False
                page.update()

            # Create dialog
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.WARNING, color="#F44336", size=28),
                        ft.Text("Confirm Deletion", size=20, weight=ft.FontWeight.BOLD, color="#1A1A1A"),
                    ],
                    spacing=10,
                ),
                content=ft.Column(
                    spacing=15,
                    tight=True,
                    controls=[
                        ft.Text(
                            f'Are you sure you want to delete "{listing_name}"?',
                            size=14,
                            color="#333333",
                        ),
                        ft.Text(
                            "This action cannot be undone. All associated data, including images, will be permanently deleted.",
                            size=12,
                            color=ft.Colors.BLACK,
                        ),
                    ],
                ),
                actions=[
                    ft.TextButton(
                        "Cancel",
                        on_click=on_cancel,
                        style=ft.ButtonStyle(
                            color=ft.Colors.BLACK,
                        ),
                    ),
                    ft.ElevatedButton(
                        "Delete",
                        on_click=on_confirm,
                        style=ft.ButtonStyle(
                            color="white",
                            bgcolor="#F44336",
                        ),
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            setattr(page, 'dialog', dlg)
            dlg.open = True
            page.update()

        def perform_delete(listing_id):
            """Actually delete the listing after confirmation."""
            if not listing_id or not user_id:
                snack = ft.SnackBar(
                    content=ft.Text("Error: Invalid listing or user"),
                    bgcolor="#F44336",
                )
                setattr(page, 'snack_bar', snack)
                try:
                    getattr(page, 'snack_bar').open = True
                except Exception:
                    try:
                        page.open(getattr(page, 'snack_bar'))
                    except Exception:
                        pass
                page.update()
                return

            try:
                success, message = self.listing_service.delete_listing_by_id(
                    listing_id, user_id
                )

                if success:
                    snack = ft.SnackBar(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.CHECK_CIRCLE, color="white"),
                                ft.Text("Listing deleted successfully", color="white"),
                            ],
                            spacing=10,
                        ),
                        bgcolor="#4CAF50",
                        action="OK",
                        action_color="white",
                    )
                    setattr(page, 'snack_bar', snack)
                    try:
                        getattr(page, 'snack_bar').open = True
                    except Exception:
                        try:
                            page.open(getattr(page, 'snack_bar'))
                        except Exception:
                            pass
                    # Refresh dashboard
                    page.go("/pm")
                    page.update()
                else:
                    snack = ft.SnackBar(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.ERROR, color="white"),
                                ft.Text(message or "Failed to delete listing", color="white"),
                            ],
                            spacing=10,
                        ),
                        bgcolor="#F44336",
                        action="OK",
                        action_color="white",
                    )
                    setattr(page, 'snack_bar', snack)
                    try:
                        getattr(page, 'snack_bar').open = True
                    except Exception:
                        try:
                            page.open(getattr(page, 'snack_bar'))
                        except Exception:
                            pass
                    page.update()
            except Exception as ex:
                snack = ft.SnackBar(
                    content=ft.Text(f"Error deleting listing: {str(ex)}"),
                    bgcolor="#F44336",
                )
                setattr(page, 'snack_bar', snack)
                try:
                    getattr(page, 'snack_bar').open = True
                except Exception:
                    try:
                        page.open(getattr(page, 'snack_bar'))
                    except Exception:
                        pass
                page.update()

        def create_listing_card_handler(listing, images, is_available, owner_id):
            """Create a PM listing card using ListingCard component"""
            listing_id = listing.id
            main_image = images[0] if images else ""

            # Create handlers with proper closures
            def delete_handler(e):
                show_delete_confirmation(listing_id, listing.address)

            def edit_handler(e):
                page.go(f"/pm/edit/{listing_id}")

            # Use ListingCard component with horizontal layout
            card = ListingCard(
                listing=listing,
                image_url=main_image,
                is_available=is_available,
                show_actions=True,
                on_edit=edit_handler,
                on_delete=delete_handler,
                layout="horizontal",
            )
            return card.build_card()

        # Store for use in load_listings
        self._create_listing_card = create_listing_card_handler

        load_listings()

        return ft.View(
            "/pm",
            padding=0,
            scroll=ft.ScrollMode.AUTO,
            bgcolor="#F5F7FA",
            controls=[
                ft.Container(
                    bgcolor="#FFFFFF",
                    padding=ft.padding.symmetric(horizontal=40, vertical=20),
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=10,
                        color="#00000008",
                        offset=ft.Offset(0, 2),
                    ),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(
                                spacing=12,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    pm_avatar,
                                    ft.Text(
                                        f"Welcome back, {pm_full_name}!",
                                        size=26,
                                        weight=ft.FontWeight.BOLD,
                                        color="#1A1A1A",
                                    ),
                                ],
                            ),
                            ft.Row(
                                spacing=10,
                                controls=[
                                    notifications_button,
                                    ft.ElevatedButton(
                                        "Add New Listing",
                                        icon=ft.Icons.ADD_CIRCLE,
                                        style=ft.ButtonStyle(
                                            color="white",
                                            bgcolor="#0078FF",
                                        ),
                                        on_click=lambda _: page.go("/pm/add"),
                                    ),
                                    ft.OutlinedButton(
                                        "Logout",
                                        icon=ft.Icons.LOGOUT,
                                        on_click=lambda _: page.go("/logout"),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
                ft.Container(
                    padding=40,
                    content=ft.Column(
                        spacing=20,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.HOME, size=24, color="#0078FF"),
                                    ft.Text(
                                        "My Listings",
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                        color="#1A1A1A",
                                    ),
                                ],
                                spacing=10,
                            ),
                            listings_container,
                        ],
                    ),
                ),
            ],
        )