# app/views/admin_dashboard_view.py
"""
Admin Dashboard - Main View
Includes: Header, KPI Cards, Charts, Map Section
"""

import flet as ft
from components.admin_stats_card import AdminStatsCard
from components.chart_card import ChartCard
from components.navbar import DashboardNavBar
from components.footer import Footer
from services.admin_service import AdminService
from services.listing_service import ListingService
from services.reservation_service import ReservationService
from services.activity_service import ActivityService
from state.session_state import SessionState
from models.user import UserRole

# Import admin subviews
from .admin_users_view import AdminUsersView
from .admin_pm_verification_view import AdminPMVerificationView
from .admin_listings_view import AdminListingsView
from .admin_reservations_view import AdminReservationsView
from .admin_payments_view import AdminPaymentsView
from .admin_reports_view import AdminReportsView
from .admin_profile_view import AdminProfileView
import datetime
import re
import calendar


class AdminDashboardView:
    """Admin dashboard view with KPI cards, charts, and map"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.session = SessionState(page)
        self.admin_service = AdminService()
        self.listing_service = ListingService()
        self.reservation_service = ReservationService()
        self.activity_service = ActivityService()

    def build(self):
        print("AdminDashboardView.build() called")
        print(f"Session data: logged_in={self.page.session.get('is_logged_in')}, role={self.page.session.get('role')}, email={self.page.session.get('email')}")

        # --- AUTH ---
        if not self.session.require_auth():
            print("Auth check failed - redirecting to login")
            return None
        if not self.session.is_admin():
            print(f"Not admin - user role is: {self.page.session.get('role')}")
            self.page.go("/")
            return None

        print("Auth passed - building admin dashboard")

        # --- FETCH ANALYTICS ---
        stats = self.admin_service.get_stats()
        total_tenants = stats.get('total_tenants', 0) or 0
        total_pms = stats.get('total_pms', 0) or 0
        total_users = int(total_tenants) + int(total_pms)
        pending_pms = self.admin_service.get_pending_pm_count()
        total_listings = stats.get('total_listings', 0) or 0
        approved_listings = stats.get('approved_listings', 0) or 0
        pending_listings = stats.get('pending_listings', 0) or 0
        total_reservations = stats.get('total_reservations', 0) or 0
        total_reports = stats.get('total_reports', 0) or 0
        total_payments = stats.get('total_payments', 0) or 0

        # --- NAVBAR + FOOTER ---
        navbar = DashboardNavBar(
            page=self.page,
            title="Admin Dashboard",
            user_email=self.session.get_email() or "Admin",
            show_add_button=False,
            on_logout=lambda _: self._logout()
        ).view()

        footer = Footer().view()

        # --- CLICK HANDLERS FOR KPI CARDS ---
        def go_users(_):
            self.page.go("/admin_users")

        def go_listings(_):
            self.page.go("/admin_listings")

        def go_reservations(_):
            self.page.go("/admin_reservations")

        def go_pm_verification(_):
            self.page.go("/admin_pm_verification")

        def go_reports(_):
            self.page.go("/admin_reports")

        def go_payments(_):
            self.page.go("/admin_payments")

        # =====================================================
        # 1. HEADER SECTION
        # =====================================================
        header_section = ft.Container(
            content=ft.Column(
                spacing=5,
                controls=[
                    ft.Text("Overview", size=28, weight=ft.FontWeight.BOLD, color="#1a1a2e"),
                    ft.Text("Summary of platform activity", size=14, color=ft.Colors.BLACK),
                ]
            )
        )

        # =====================================================
        # 2. KPI CLICKABLE CARDS SECTION
        # =====================================================
        # Use the reusable AdminStatsCard component for KPI cards
        kpi_cards = ft.Row(
            wrap=True,
            spacing=20,
            run_spacing=20,
            controls=[
                AdminStatsCard(title="Total Users", value=total_users, icon=ft.Icon(ft.Icons.PERSON, size=24, color="#2196F3"), trend_value=12, trend_up=True, color="#2196F3", on_click=go_users).build(),
                AdminStatsCard(title="Active Listings", value=approved_listings, icon=ft.Icon(ft.Icons.HOME_WORK, size=24, color="#4CAF50"), trend_value=8, trend_up=True, color="#4CAF50", on_click=go_listings).build(),
                AdminStatsCard(title="Reservations", value=total_reservations, icon=ft.Icon(ft.Icons.BOOKMARK, size=24, color="#FF9800"), trend_value=5, trend_up=True, color="#FF9800", on_click=go_reservations).build(),
                AdminStatsCard(title="Pending PMs", value=pending_pms, icon=ft.Icon(ft.Icons.VERIFIED_USER, size=24, color="#9C27B0"), trend_value=3, trend_up=False, color="#9C27B0", on_click=go_pm_verification).build(),
                AdminStatsCard(title="Reports", value=total_reports, icon=ft.Icon(ft.Icons.REPORT, size=24, color="#F44336"), trend_value=2, trend_up=False, color="#F44336", on_click=go_reports).build(),
            ]
        )

        # =====================================================
        # 3. CHARTS SECTION
        # =====================================================

        # Helper functions for charts
        def _short_label(label):
            if not label:
                return ""
            try:
                s = str(label)
                if re.match(r"^\d{4}-\d{2}$", s):
                    dt = datetime.datetime.strptime(s, "%Y-%m")
                    return dt.strftime("%b")
                return str(label).split('-')[-1]
            except Exception:
                return str(label)

        def _make_left_axis(max_y):
            try:
                max_y = int(max_y)
            except Exception:
                max_y = 1
            ticks = [0]
            if max_y <= 4:
                ticks = list(range(0, max_y + 1))
            else:
                step = max(1, int(max_y / 4))
                ticks = [0, step, step * 2, step * 3, max_y]
            labels = [ft.ChartAxisLabel(value=v, label=ft.Text(str(v), size=10)) for v in ticks]
            return ft.ChartAxis(labels=labels, labels_size=10)

        # --- Chart 1: User Distribution Pie Chart ---
        tenants = total_tenants
        pms = total_pms
        admins = max(0, stats.get('total_users', 0) - tenants - pms)
        total_for_pie = tenants + pms + admins

        if total_for_pie == 0:
            pie_sections = [
                ft.PieChartSection(value=1, color=ft.Colors.GREY_300, title="No users", radius=90, title_style=ft.TextStyle(size=12, color=ft.Colors.WHITE))
            ]
        else:
            def _pct(n):
                return int(round((n / total_for_pie) * 100)) if total_for_pie > 0 else 0

            pie_sections = [
                ft.PieChartSection(
                    value=tenants if tenants > 0 else 0.1,
                    color="#4CAF50",
                    title=f"Tenants\n{_pct(tenants)}%",
                    title_style=ft.TextStyle(size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    radius=90,
                ),
                ft.PieChartSection(
                    value=pms if pms > 0 else 0.1,
                    color="#FF9800",
                    title=f"PMs\n{_pct(pms)}%",
                    title_style=ft.TextStyle(size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    radius=90,
                ),
                ft.PieChartSection(
                    value=admins if admins > 0 else 0.1,
                    color="#2196F3",
                    title=f"Admin\n{_pct(admins)}%",
                    title_style=ft.TextStyle(size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    radius=90,
                ),
            ]

        user_pie_chart = ft.PieChart(
            sections=pie_sections,
            sections_space=2,
            center_space_radius=40,
            height=200,
            expand=True,
        )

        # Legend for pie chart
        pie_legend = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15,
            controls=[
                ft.Row([ft.Container(width=12, height=12, bgcolor="#4CAF50", border_radius=2), ft.Text("Tenants", size=11)]),
                ft.Row([ft.Container(width=12, height=12, bgcolor="#FF9800", border_radius=2), ft.Text("PMs", size=11)]),
                ft.Row([ft.Container(width=12, height=12, bgcolor="#2196F3", border_radius=2), ft.Text("Admins", size=11)]),
            ]
        )

        user_distribution_card = ChartCard(
            title="User Distribution",
            subtitle="Breakdown by user role",
            chart=user_pie_chart,
            legend=pie_legend,
            icon=ft.Icon(ft.Icons.PIE_CHART, size=20, color=ft.Colors.BLACK),
            width=320,
        ).build()

        # --- Chart 2: Reservation Trend Line Chart ---
        res_monthly = self.reservation_service.get_reservations_per_month() or []
        if not res_monthly:
            res_monthly = [("Jan", 5), ("Feb", 8), ("Mar", 12), ("Apr", 10), ("May", 15), ("Jun", 18)]

        data_points = []
        res_labels = []
        for i, (label, value) in enumerate(res_monthly, start=1):
            lbl = _short_label(label)
            res_labels.append((i, lbl))
            data_points.append(ft.LineChartDataPoint(x=i, y=value or 0, tooltip=str(value or 0)))

        res_bottom_axis = ft.ChartAxis(
            labels=[ft.ChartAxisLabel(value=i, label=ft.Container(ft.Text(lbl, size=10), margin=ft.margin.only(top=5))) for i, lbl in res_labels],
            labels_size=10,
        )

        res_max = max([int(v or 0) for _, v in res_monthly]) if res_monthly else 1
        res_max_y = max(int(res_max * 1.25), 1)

        reservation_line_chart = ft.LineChart(
            data_series=[
                ft.LineChartData(
                    data_points=data_points,
                    curved=True,
                    color="#2196F3",
                    stroke_width=3,
                    point=True,
                    stroke_cap_round=True,
                    below_line_gradient=ft.LinearGradient(
                        begin=ft.alignment.top_center,
                        end=ft.alignment.bottom_center,
                        colors=["#2196F340", "#2196F305"],
                    ),
                )
            ],
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE)),
            horizontal_grid_lines=ft.ChartGridLines(interval=1, color=ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE), width=1),
            left_axis=_make_left_axis(res_max_y),
            bottom_axis=res_bottom_axis,
            height=200,
            tooltip_bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.BLUE_GREY),
            min_y=0,
            max_y=res_max_y,
            min_x=0,
            max_x=max(1, len(res_monthly)),
            expand=True,
        )

        reservation_trend_card = ChartCard(
            title="Reservation Trend",
            subtitle="Monthly bookings",
            chart=reservation_line_chart,
            icon=ft.Icon(ft.Icons.SHOW_CHART, size=20, color=ft.Colors.BLACK),
            footer=ft.Row(
                alignment=ft.MainAxisAlignment.END,
                spacing=8,
                controls=[
                    ft.Container(
                        bgcolor="#E3F2FD",
                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                        border_radius=15,
                        content=ft.Text("Monthly", size=11, color="#1976D2"),
                    )
                ]
            ),
        ).build()

        # --- Revenue/Expense Bar Chart ---
        months_data = [
            ("Oct", 116.21, 45.40),
            ("Nov", 282.98, 71.47),
            ("Dec", 221.35, 32.04),
            ("Jan", 214.04, 17.88),
            ("Feb", 214.37, 23.40),
            ("Mar", 131.10, 1.48),
        ]

        bar_groups = []
        bar_labels = []
        for i, (month, revenue, expense) in enumerate(months_data):
            bar_labels.append((i, month))
            bar_groups.append(
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[
                        ft.BarChartRod(to_y=revenue, width=20, color="#4CAF50", border_radius=ft.border_radius.only(top_left=4, top_right=4)),
                        ft.BarChartRod(to_y=expense, width=20, color="#F44336", border_radius=ft.border_radius.only(top_left=4, top_right=4)),
                    ],
                )
            )

        revenue_expense_chart = ft.BarChart(
            bar_groups=bar_groups,
            groups_space=25,
            bottom_axis=ft.ChartAxis(
                labels=[ft.ChartAxisLabel(value=i, label=ft.Text(lbl, size=10)) for i, lbl in bar_labels],
                labels_size=10,
            ),
            left_axis=_make_left_axis(300),
            height=200,
            border=ft.border.all(1, ft.Colors.GREY_300),
            horizontal_grid_lines=ft.ChartGridLines(color=ft.Colors.GREY_200, width=1, dash_pattern=[3, 3]),
            max_y=300,
            expand=True,
        )

        revenue_legend = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
            controls=[
                ft.Row([ft.Container(width=12, height=12, bgcolor="#4CAF50", border_radius=2), ft.Text("Revenue", size=11)]),
                ft.Row([ft.Container(width=12, height=12, bgcolor="#F44336", border_radius=2), ft.Text("Expenses", size=11)]),
            ]
        )

        revenue_expense_card = ChartCard(
            title="Revenue vs Expense Trend",
            subtitle="Monthly comparison",
            chart=revenue_expense_chart,
            icon=ft.Icon(ft.Icons.BAR_CHART, size=20, color=ft.Colors.BLACK),
            legend=revenue_legend,
        ).build()

        charts_row = ft.Row(
            spacing=20,
            controls=[
                user_distribution_card,
                ft.Column(
                    expand=True,
                    spacing=20,
                    controls=[
                        reservation_trend_card,
                    ]
                ),
            ]
        )

        # =====================================================
        # 4. MAP SECTION - Lodging Hotspots
        # =====================================================
        sample_locations = [
            {"name": "Manila", "x": 45, "y": 55, "count": 12, "status": "active"},
            {"name": "Quezon City", "x": 48, "y": 50, "count": 8, "status": "active"},
            {"name": "Makati", "x": 46, "y": 58, "count": 15, "status": "active"},
            {"name": "Pasig", "x": 50, "y": 54, "count": 6, "status": "pending"},
            {"name": "Taguig", "x": 48, "y": 60, "count": 10, "status": "active"},
            {"name": "Cebu", "x": 65, "y": 65, "count": 5, "status": "active"},
        ]

        def get_marker_color(status):
            if status == "active":
                return "#2196F3"
            elif status == "pending":
                return "#FF9800"
            else:
                return "#9E9E9E"

        map_markers = []
        for loc in sample_locations:
            color = get_marker_color(loc["status"])
            size = min(40, 15 + loc["count"] * 2)
            map_markers.append(
                ft.Container(
                    left=loc["x"] * 5,
                    top=loc["y"] * 3,
                    width=size,
                    height=size,
                    bgcolor=color,
                    border_radius=size/2,
                    border=ft.border.all(2, "white"),
                    shadow=ft.BoxShadow(blur_radius=5, color="#00000030"),
                    alignment=ft.alignment.center,
                    tooltip=f"{loc['name']}: {loc['count']} listings",
                    content=ft.Text(str(loc["count"]), size=10, color="white", weight=ft.FontWeight.BOLD),
                )
            )

        map_legend = ft.Row(
            alignment=ft.MainAxisAlignment.START,
            spacing=20,
            controls=[
                ft.Row([ft.Container(width=14, height=14, bgcolor="#2196F3", border_radius=7, border=ft.border.all(1, "white")), ft.Text("Active", size=12)]),
                ft.Row([ft.Container(width=14, height=14, bgcolor="#FF9800", border_radius=7, border=ft.border.all(1, "white")), ft.Text("Pending", size=12)]),
                ft.Row([ft.Container(width=14, height=14, bgcolor="#9E9E9E", border_radius=7, border=ft.border.all(1, "white")), ft.Text("Archived", size=12)]),
            ]
        )

        map_section = ft.Container(
            bgcolor="white",
            padding=20,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=15, spread_radius=1, color="#00000010"),
            content=ft.Column(
                spacing=15,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text("Listings Hotspot Map", size=18, weight=ft.FontWeight.BOLD),
                                    ft.Text("Geographic distribution of listings", size=12, color=ft.Colors.BLACK),
                                ]
                            ),
                            ft.Row([
                                ft.IconButton(icon=ft.Icons.FULLSCREEN, icon_size=20, tooltip="Expand Map"),
                                ft.IconButton(icon=ft.Icons.REFRESH, icon_size=20, tooltip="Refresh Data"),
                            ])
                        ]
                    ),
                    ft.Divider(height=1, color="#E0E0E0"),
                    ft.Container(
                        height=280,
                        border_radius=8,
                        bgcolor="#E8F4FD",
                        border=ft.border.all(1, "#B0D4F1"),
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        content=ft.Stack(
                            controls=[
                                ft.Container(
                                    expand=True,
                                    gradient=ft.LinearGradient(
                                        begin=ft.alignment.top_center,
                                        end=ft.alignment.bottom_center,
                                        colors=["#E3F2FD", "#BBDEFB", "#90CAF9"],
                                    ),
                                    content=ft.Column(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Icon(ft.Icons.MAP, size=60, color="#1976D2"),
                                            ft.Text("Philippines Map View", size=14, color="#1976D2"),
                                            ft.Text("Showing listing hotspots across regions", size=11, color=ft.Colors.BLACK),
                                        ]
                                    )
                                ),
                                *map_markers,
                            ]
                        )
                    ),
                    map_legend,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        controls=[
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=2,
                                controls=[
                                    ft.Text(str(approved_listings), size=20, weight=ft.FontWeight.BOLD, color="#2196F3"),
                                    ft.Text("Active", size=11, color=ft.Colors.BLACK),
                                ]
                            ),
                            ft.Container(width=1, height=40, bgcolor="#E0E0E0"),
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=2,
                                controls=[
                                    ft.Text(str(pending_listings), size=20, weight=ft.FontWeight.BOLD, color="#FF9800"),
                                    ft.Text("Pending", size=11, color=ft.Colors.BLACK),
                                ]
                            ),
                            ft.Container(width=1, height=40, bgcolor="#E0E0E0"),
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=2,
                                controls=[
                                    ft.Text("6", size=20, weight=ft.FontWeight.BOLD, color="#4CAF50"),
                                    ft.Text("Regions", size=11, color=ft.Colors.BLACK),
                                ]
                            ),
                        ]
                    ),
                ]
            )
        )

        # =====================================================
        # 5. RECENT ACTIVITY SECTION
        # =====================================================
        recent_activity = self.activity_service.get_recent_activities(limit=8)

        def _log_text(log):
            try:
                msg = None
                if isinstance(log, dict):
                    msg = log.get('message') or log.get('details') or log.get('action')
                else:
                    for key in ('message', 'details', 'action'):
                        try:
                            v = log[key]
                            if v:
                                msg = v
                                break
                        except Exception:
                            continue
                return str(msg) if msg else ""
            except Exception:
                return str(log) if log else ""

        def _activity_click_handler(msg):
            m = (msg or "").lower()
            if "report" in m:
                route = "/admin_reports"
            elif "pm" in m or "property manager" in m or "pending" in m:
                route = "/admin_pm_verification"
            elif "listing" in m:
                route = "/admin_listings"
            elif "reservation" in m:
                route = "/admin_reservations"
            else:
                route = "/admin_users"
            return lambda _: self.page.go(route)

        def _get_activity_icon(msg):
            m = (msg or "").lower()
            if "report" in m:
                return ft.Icons.REPORT, "#F44336"
            elif "pm" in m or "property manager" in m:
                return ft.Icons.VERIFIED_USER, "#9C27B0"
            elif "listing" in m:
                return ft.Icons.HOME_WORK, "#4CAF50"
            elif "reservation" in m:
                return ft.Icons.BOOKMARK, "#FF9800"
            elif "user" in m or "register" in m:
                return ft.Icons.PERSON_ADD, "#2196F3"
            else:
                return ft.Icons.NOTIFICATIONS, "#607D8B"

        activity_controls = []
        for log in recent_activity:
            txt = _log_text(log)
            if not txt:
                continue
            handler = _activity_click_handler(txt)
            icon, color = _get_activity_icon(txt)

            activity_controls.append(
                ft.Container(
                    content=ft.Row(
                        spacing=10,
                        controls=[
                            ft.Container(
                                width=32,
                                height=32,
                                bgcolor=f"{color}15",
                                border_radius=16,
                                alignment=ft.alignment.center,
                                content=ft.Icon(icon, size=16, color=color),
                            ),
                            ft.Text(txt, size=13, expand=True, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Icon(ft.Icons.CHEVRON_RIGHT, size=16, color=ft.Colors.BLACK),
                        ]
                    ),
                    padding=ft.padding.symmetric(vertical=8, horizontal=12),
                    border_radius=8,
                    on_click=handler,
                )
            )

        if not activity_controls:
            activity_controls.append(
                ft.Container(
                    padding=30,
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                        controls=[
                            ft.Icon(ft.Icons.HISTORY, size=40, color=ft.Colors.BLACK),
                            ft.Text("No recent activity", size=14, color=ft.Colors.BLACK),
                        ]
                    )
                )
            )

        activity_section = ft.Container(
            bgcolor="white",
            padding=20,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=15, spread_radius=1, color="#00000010"),
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Recent Activity", size=18, weight=ft.FontWeight.BOLD),
                            ft.TextButton("View All", on_click=lambda _: self.page.go("/admin_reports")),
                        ]
                    ),
                    ft.Divider(height=1, color="#E0E0E0"),
                    ft.Column(spacing=5, controls=activity_controls),
                ]
            )
        )

        # =====================================================
        # MAIN VIEW LAYOUT
        # =====================================================
        print("Building ft.View for admin dashboard")
        view = ft.View(
            "/admin",
            bgcolor="#F5F7FA",
            scroll=ft.ScrollMode.AUTO,
            controls=[
                navbar,
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=40, vertical=30),
                    content=ft.Column(
                        spacing=25,
                        controls=[
                            header_section,
                            kpi_cards,
                            charts_row,
                            ft.Row(
                                spacing=20,
                                vertical_alignment=ft.CrossAxisAlignment.START,
                                controls=[
                                    ft.Container(expand=2, content=map_section),
                                    ft.Container(expand=1, content=activity_section),
                                ]
                            ),
                            revenue_expense_card,
                        ]
                    )
                ),
                footer
            ]
        )
        print(f"Admin dashboard view created successfully: {view is not None}")
        return view

    def _logout(self):
        self.session.logout()
        self.page.go("/")
