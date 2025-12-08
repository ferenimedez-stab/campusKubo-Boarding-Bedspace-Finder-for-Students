# app/views/admin_listings_view.py

import flet as ft
from services.listing_service import ListingService
from services.admin_service import AdminService
from components.navbar import DashboardNavBar
from state.session_state import SessionState
from collections import defaultdict


class AdminListingsView:

    def __init__(self, page: ft.Page):
        self.page = page
        self.session = SessionState(page)
        self.listing_service = ListingService()
        self.admin_service = AdminService()

        # UI State
        self.search_field = ft.TextField(
            hint_text="Search by address or description",
            expand=True,
            on_change=self.on_filters_changed
        )

        # Tab state
        self.current_tab = "active"  # active, pending, rejected, archived

        # Filter state
        self.price_min = ft.TextField(
            label="Min Price",
            value="",
            width=120,
            on_change=self.on_filters_changed
        )
        self.price_max = ft.TextField(
            label="Max Price",
            value="",
            width=120,
            on_change=self.on_filters_changed
        )

        self.location_filter = ft.TextField(
            label="Location",
            value="",
            width=150,
            on_change=self.on_filters_changed
        )

        self.pm_filter = ft.Dropdown(
            label="PM Owner",
            options=[ft.dropdown.Option("All")],
            value="All",
            on_change=self.on_filters_changed,
            width=180
        )

        self.listings_column = ft.Column(expand=True)
        self.tab_content = ft.Column(expand=True)


    # ----------------------------------------------------
    # Build view
    # ----------------------------------------------------
    def build(self):
        if not self.session.require_auth():
            return None
        if not self.session.is_admin():
            self.page.go("/")
            return None

        self._populate_pm_filter()
        self.refresh_listings()

        return ft.View(
            "/admin_listings",
            scroll=ft.ScrollMode.AUTO,
            controls=[
                DashboardNavBar(self.page, "Listing Management",
                                self.session.get_email() or "").view(),

                ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Row(controls=[
                            ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: self.page.go('/admin')),
                            ft.Text("Listing Management", size=26, weight=ft.FontWeight.BOLD)
                        ], alignment=ft.MainAxisAlignment.START),

                        # Tabs for status filtering
                        ft.Tabs(
                            selected_index=self._get_tab_index(),
                            on_change=self._on_tab_change,
                            tabs=[
                                ft.Tab(
                                    text="Active",
                                    content=self.tab_content
                                ),
                                ft.Tab(
                                    text="Pending Approval",
                                    content=self.tab_content
                                ),
                                ft.Tab(
                                    text="Rejected",
                                    content=self.tab_content
                                ),
                                ft.Tab(
                                    text="Archived",
                                    content=self.tab_content
                                )
                            ]
                        ),

                        ft.Divider(),

                        # Search bar
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.SEARCH),
                                self.search_field
                            ],
                            alignment=ft.MainAxisAlignment.START
                        ),

                        # Filters row
                        ft.Row(
                            controls=[
                                self.price_min,
                                self.price_max,
                                self.location_filter,
                                self.pm_filter
                            ],
                            wrap=True,
                            spacing=10
                        ),

                        ft.Divider(),

                        # Analytics section (optional)
                        ft.ExpansionTile(
                            title=ft.Text("Analytics", weight=ft.FontWeight.BOLD),
                            controls=[
                                ft.Container(
                                    height=300,
                                    content=ft.Column([
                                        ft.Text("Listings per Location", size=14, weight=ft.FontWeight.BOLD),
                                        self._build_location_chart()
                                    ], expand=True)
                                )
                            ]
                        ),

                        ft.Divider(),
                    ], expand=True)
                )
            ]
        )

    def _switch_tab(self, tab_name: str):
        """Switch to a different tab and refresh listings."""
        self.current_tab = tab_name
        self.refresh_listings()

    def _get_tab_index(self):
        """Get the current tab index for ft.Tabs."""
        tab_map = {"active": 0, "pending": 1, "rejected": 2, "archived": 3}
        return tab_map.get(self.current_tab, 0)

    def _on_tab_change(self, e):
        """Handle tab change event."""
        tab_names = ["active", "pending", "rejected", "archived"]
        if e.control.selected_index < len(tab_names):
            self._switch_tab(tab_names[e.control.selected_index])

    def _populate_pm_filter(self):
        """Populate PM filter dropdown with all PM owners."""
        all_listings = self.listing_service.get_all_listings()
        pm_set = set()
        for listing in all_listings:
            if hasattr(listing, 'pm_id') and listing.pm_id:
                pm_set.add(str(listing.pm_id))

        options = [ft.dropdown.Option("All")]
        for pm_id in sorted(pm_set):
            options.append(ft.dropdown.Option(f"PM {pm_id}"))

        self.pm_filter.options = options
        self.pm_filter.value = "All"

    def _build_location_chart(self):
        """Build a pie chart showing listings per location."""
        all_listings = self.listing_service.get_all_listings()
        location_count = defaultdict(int)

        for listing in all_listings:
            addr = getattr(listing, 'address', 'Unknown')
            # Group by city/area (first part of address)
            area = addr.split(',')[0] if ',' in addr else addr
            location_count[area] += 1

        if not location_count:
            return ft.Text("No data available", size=12, color=ft.Colors.GREY)

        # Create pie chart data
        total_listings = sum(location_count.values())
        colors = [ft.Colors.BLUE, ft.Colors.GREEN, ft.Colors.ORANGE, ft.Colors.RED,
                 ft.Colors.PURPLE, ft.Colors.YELLOW, ft.Colors.PINK, ft.Colors.CYAN]

        # Sort by count descending and take top 8
        sorted_locations = sorted(location_count.items(), key=lambda x: x[1], reverse=True)[:8]

        pie_sections = []
        legend_items = []

        for i, (location, count) in enumerate(sorted_locations):
            # Calculate percentage
            percentage = (count / total_listings) * 100

            # Create pie section (using containers to simulate pie slices)
            color = colors[i % len(colors)]

            # Simple pie slice representation using containers
            pie_sections.append(
                ft.Container(
                    width=percentage * 3,  # Scale width by percentage
                    height=30,
                    bgcolor=color,
                    border_radius=ft.border_radius.only(
                        top_left=15 if i == 0 else 0,
                        bottom_left=15 if i == 0 else 0,
                        top_right=15 if i == len(sorted_locations)-1 else 0,
                        bottom_right=15 if i == len(sorted_locations)-1 else 0
                    ),
                    content=ft.Text(f"{percentage:.1f}%", size=10, color=ft.Colors.WHITE,
                                  text_align=ft.TextAlign.CENTER)
                )
            )

            # Legend item
            legend_items.append(
                ft.Row([
                    ft.Container(width=15, height=15, bgcolor=color, border_radius=2),
                    ft.Text(f"{location}: {count} ({percentage:.1f}%)", size=11)
                ], spacing=8)
            )

        return ft.Column([
            ft.Text("Listings by Location", size=14, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            # Pie chart representation
            ft.Container(
                content=ft.Row(pie_sections, spacing=0),
                height=40,
                alignment=ft.alignment.center
            ),
            ft.Container(height=15),
            # Legend
            ft.Column(legend_items, spacing=5)
        ], spacing=5)

    # ----------------------------------------------------
    # Refresh data
    # ----------------------------------------------------
    def refresh_listings(self):
        """Loads all listings, applies filters based on current tab, and rebuilds grid."""
        all_listings = self.listing_service.get_all_listings()

        # Filter by tab (status)
        status_map = {
            "active": ["active"],
            "pending": ["pending"],
            "rejected": ["rejected"],
            "archived": ["archived"]
        }
        target_statuses = status_map.get(self.current_tab, [])
        filtered = [l for l in all_listings if getattr(l, 'status', '').lower() in [s.lower() for s in target_statuses]]

        # Apply search
        query = self.search_field.value or ""
        if query:
            filtered = self.listing_service.search_listings(query, filtered)

        # Apply price filter
        try:
            min_price = float(self.price_min.value) if self.price_min.value else None
            max_price = float(self.price_max.value) if self.price_max.value else None
            if min_price is not None:
                filtered = [l for l in filtered if float(getattr(l, 'price', 0)) >= min_price]
            if max_price is not None:
                filtered = [l for l in filtered if float(getattr(l, 'price', 0)) <= max_price]
        except (ValueError, TypeError):
            pass

        # Apply location filter
        location = self.location_filter.value or ""
        if location:
            filtered = [l for l in filtered if location.lower() in getattr(l, 'address', '').lower()]

        # Apply PM filter
        pm = self.pm_filter.value or ""
        if pm and pm != "All":
            pm_id = pm.replace("PM ", "")
            try:
                pm_id_num = int(pm_id)
                filtered = [l for l in filtered if getattr(l, 'pm_id', None) == pm_id_num]
            except (ValueError, TypeError):
                pass

        # Build grid layout
        cards = [self.build_listing_card(listing) for listing in filtered]

        if not cards:
            self.tab_content.controls = [
                ft.Container(
                    alignment=ft.alignment.center,
                    padding=40,
                    content=ft.Text("No listings found", size=14, color=ft.Colors.GREY)
                )
            ]
        else:
            # Create a grid layout using Row wrapping
            grid_rows = []
            for i in range(0, len(cards), 2):
                grid_rows.append(
                    ft.Row([cards[i], cards[i+1]] if i+1 < len(cards) else [cards[i]], spacing=15)
                )

            self.tab_content.controls = [ft.Column(grid_rows, spacing=15, expand=True)]

        self.page.update()

    # ----------------------------------------------------
    # Triggered when search or filter changes
    # ----------------------------------------------------
    def on_filters_changed(self, _):
        self.refresh_listings()

    # ----------------------------------------------------
    # Build each listing card (for grid)
    # ----------------------------------------------------
    def build_listing_card(self, listing):
        """Creates a compact card for each listing in grid view."""
        images = getattr(listing, "images", [])
        address = getattr(listing, "address", "No Address")
        pm_email = getattr(listing, "pm_email", "N/A")
        price = getattr(listing, "price", 0)
        status = getattr(listing, "status", "Unknown")
        description = getattr(listing, "description", "")

        # Safely format price
        try:
            price_val = float(price)
            price_text = f"\u20b1{price_val:,.2f}"
        except (TypeError, ValueError):
            try:
                price_val = float(str(price).replace(',', '').strip())
                price_text = f"\u20b1{price_val:,.2f}"
            except Exception:
                price_text = f"\u20b1{price}"

        # Status color
        status_lower = str(status).lower()
        if status_lower == "active":
            status_color = ft.Colors.GREEN
        elif status_lower == "pending":
            status_color = ft.Colors.ORANGE
        elif status_lower == "rejected":
            status_color = ft.Colors.RED
        else:
            status_color = ft.Colors.GREY

        # Action buttons
        def _confirm_listing_action(action: str, lid: int):
            title = "Confirm"
            msg = f"Are you sure you want to {action} this listing?"
            dlg = ft.AlertDialog(
                title=ft.Text(title),
                content=ft.Text(msg),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: self._close_dialog()),
                    ft.ElevatedButton(action.capitalize(), on_click=lambda e, a=action, id=lid: self._perform_listing_action(a, id))
                ]
            )
            setattr(self.page, "dialog", dlg)
            dlg.open = True
            self.page.update()

        # Thumbnail image
        image_widget = ft.Container(
            height=150,
            bgcolor=ft.Colors.GREY_200,
            border_radius=8,
            content=ft.Icon(ft.Icons.IMAGE, size=50, color=ft.Colors.GREY)
        )
        if images and len(images) > 0:
            try:
                image_widget = ft.Image(src=images[0], width=250, height=150, fit=ft.ImageFit.COVER)
            except Exception:
                pass

        return ft.Container(
            expand=True,
            padding=12,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_300),
            content=ft.Column([
                # Image or placeholder
                image_widget,

                ft.SizedBox(height=8),

                # Address
                ft.Text(address, size=14, weight=ft.FontWeight.BOLD, max_lines=2),

                # Description snippet
                ft.Text(description[:80] + "..." if len(description) > 80 else description,
                       size=11, color=ft.Colors.GREY_700, max_lines=2),

                ft.SizedBox(height=8),

                # Price and Status
                ft.Row([
                    ft.Text(price_text, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
                    ft.Chip(label=ft.Text(status, size=10), color=status_color)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.SizedBox(height=10),

                # Action buttons
                ft.Row([
                    ft.ElevatedButton(
                        "View",
                        width=80,
                        height=36,
                        on_click=lambda e: self.page.go(f"/admin_listing/{listing.id}")
                    ),
                    ft.OutlinedButton(
                        "Edit",
                        width=80,
                        height=36,
                        on_click=lambda e: self.page.go(f"/admin_listing/{listing.id}")
                    ) if status_lower in ["active", "pending"] else ft.Container(),
                    (ft.ElevatedButton(
                        "Approve",
                        width=70,
                        height=36,
                        bgcolor=ft.Colors.GREEN,
                        color=ft.Colors.WHITE,
                        on_click=lambda e, lid=listing.id: _confirm_listing_action('approve', lid)
                    ) if status_lower == "pending" else
                    ft.ElevatedButton(
                        "Delete",
                        width=70,
                        height=36,
                        bgcolor=ft.Colors.RED,
                        color=ft.Colors.WHITE,
                        on_click=lambda e: self.delete_listing(listing.id)
                    ))
                ], spacing=5)
            ], spacing=5)
        )

    # ----------------------------------------------------
    # Deletion handler
    # ----------------------------------------------------
    def delete_listing(self, listing_id):
        # Use admin-level deletion
        ok, msg = self.listing_service.delete_listing_by_admin(listing_id)
        snack_bar = ft.SnackBar(ft.Text(msg))
        self.page.open(snack_bar)
        self.refresh_listings()
    def _close_dialog(self):
        dlg = getattr(self.page, "dialog", None)
        if dlg:
            dlg.open = False
            self.page.update()
            # clear the dialog attribute to keep the page object consistent
            setattr(self.page, "dialog", None)
            self.page.update()

    def _perform_listing_action(self, action: str, listing_id: int):
        self._close_dialog()
        if action == 'approve':
            ok = self.admin_service.approve_listing(listing_id)
            msg = 'Listing approved' if ok else 'Failed to approve listing'
        else:
            ok = self.admin_service.reject_listing(listing_id)
            msg = 'Listing rejected' if ok else 'Failed to reject listing'

        self.page.open(ft.SnackBar(ft.Text(msg)))
        self.refresh_listings()
