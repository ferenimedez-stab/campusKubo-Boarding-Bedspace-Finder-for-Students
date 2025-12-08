# app/views/admin_users_view.py

import flet as ft
from services.admin_service import AdminService
from components.admin_utils import format_id, format_name, format_datetime
from state.session_state import SessionState
from components.navbar import DashboardNavBar
from components.footer import Footer
from components.table_card import TableCard
from models.user import UserRole
from storage.db import get_connection, get_recent_activity
from datetime import datetime

class AdminUsersView:

    def __init__(self, page: ft.Page):
        self.page = page
        self.session = SessionState(page)
        self.admin_service = AdminService()
        # UI state: search and role filter
        self.search_field = ft.TextField(hint_text="Search users by name or email", expand=True, on_change=self._on_filters_changed)
        self.role_filter = ft.Dropdown(
            label="Role",
            options=[
                ft.dropdown.Option("All"),
                ft.dropdown.Option("Tenants"),
                ft.dropdown.Option("PMs"),
                ft.dropdown.Option("Admins")
            ],
            value="All",
            on_change=self._on_filters_changed,
            width=200
        )

        # Container to hold the table so we can refresh it in-place
        self.table_container = ft.Container()
        # pagination
        self.page_index = 0
        self.page_size = 8
        # Tabs state
        self.active_tab = "all"

        # Status and date filters
        self.status_filter2 = ft.Dropdown(
            label="Status",
            options=[ft.dropdown.Option("All"), ft.dropdown.Option("Active"), ft.dropdown.Option("Deactivated")],
            value="All",
            on_change=self._on_filters_changed,
            width=180
        )

        # Use text fields for date input to support a wider range of Flet versions
        self.date_from = ft.TextField(hint_text="From (YYYY-MM-DD)", width=160)
        self.date_to = ft.TextField(hint_text="To (YYYY-MM-DD)", width=160)

    def build(self):

        if not self.session.require_auth(): return None
        if not self.session.is_admin(): self.page.go("/"); return None

        # Initial render of users table
        self._render_table()

        navbar = DashboardNavBar(
            page=self.page,
            title="User Management",
            user_email=self.session.get_email() or "",
        ).view()

        # Build header row with search and filters
        filters_row = ft.Row(controls=[self.search_field, self.role_filter, self.status_filter2, self.date_from, self.date_to], spacing=12)

        # Tabs
        tabs_control = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="All Users"),
                ft.Tab(text="Tenants"),
                ft.Tab(text="Admins"),
                ft.Tab(text="Property Managers"),
                ft.Tab(text="Deactivated Users"),
                ft.Tab(text="Activity Logs"),
            ],
            on_change=self._on_tab_change
        )

        return ft.View(
            "/admin_users",
            scroll=ft.ScrollMode.AUTO,
            controls=[
                navbar,
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Row(controls=[
                            ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: self.page.go('/admin')),
                            ft.Text("All Registered Users", size=26, weight= ft.FontWeight.BOLD)
                        ], alignment=ft.MainAxisAlignment.START),
                        ft.Divider(),
                        tabs_control,
                        filters_row,
                        ft.Divider(),
                        # Charts area
                        ft.Row(controls=[self._build_registration_chart_container(), self._build_active_inactive_card()], spacing=16),
                        ft.Divider(),
                        ft.Container(height=420, content=ft.ListView(expand=True, spacing=8, padding=ft.padding.all(0), controls=[self.table_container])),
                        ft.Divider(),
                        self._build_pagination()
                    ])
                )
            ]
        )

    def _set_active(self, user_id: int, active: bool):
        from services.admin_service import AdminService
        svc = AdminService()
        ok = svc.activate_user(user_id) if active else svc.deactivate_user(user_id)
        if ok:
            self.page.open(ft.SnackBar(ft.Text('User status updated')))
        else:
            self.page.open(ft.SnackBar(ft.Text('Failed to update user')))
        self.page.go('/admin_users')

    def _confirm_delete(self, user_id: int):
        dlg = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text("Are you sure you want to permanently delete this user? This action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(dlg)),
                ft.ElevatedButton("Delete", bgcolor="#D32F2F", color="white", on_click=lambda e, uid=user_id: self._perform_delete(uid, dlg))
            ]
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def _close_dialog(self, dlg: ft.AlertDialog):
        dlg.open = False
        self.page.update()

    def _perform_delete(self, user_id: int, dlg: ft.AlertDialog):
        dlg.open = False
        svc = AdminService()
        ok = svc.delete_user(user_id)
        if ok:
            self.page.open(ft.SnackBar(ft.Text('User deleted')))
        else:
            self.page.open(ft.SnackBar(ft.Text('Failed to delete user')))
        # refresh
        self._render_table()
        self.page.update()

    # --------------------
    # Filtering / rendering
    # --------------------
    def _on_filters_changed(self, e):
        # Re-render table with new filters
        self._render_table()
        self.page.update()

    def _render_table(self):
        # Build SQL-backed filters (role, status, date range)
        role_tab = self.active_tab  # 'all', 'tenants', 'pms', 'deactivated', 'activity'

        # role filter from dropdown still applies in combination
        role_val = (self.role_filter.value or "All").lower()
        role_enum = None
        if role_val == 'tenants':
            role_enum = UserRole.TENANT
        elif role_val == 'pms':
            role_enum = UserRole.PROPERTY_MANAGER
        elif role_val == 'admins':
            role_enum = UserRole.ADMIN

        # status filter from second dropdown
        status_val = (self.status_filter2.value or "All").lower()
        status_active = None
        if status_val == 'active':
            status_active = 1
        elif status_val == 'deactivated':
            status_active = 0

        # date filters
        df = getattr(self.date_from, 'value', None)
        dt = getattr(self.date_to, 'value', None)

        users = self._fetch_users(role=role_enum, active=status_active, date_from=df, date_to=dt, tab=role_tab)

        # Apply search filter client-side
        q = (self.search_field.value or "").strip().lower()
        if q:
            users = [u for u in users if (getattr(u, 'full_name', '') or '').lower().find(q) != -1 or (getattr(u, 'email', '') or '').lower().find(q) != -1]

        # Pagination slice
        total = len(users)
        start = self.page_index * self.page_size
        end = start + self.page_size
        page_items = users[start:end]

        rows = []
        for u in page_items:
            uid = getattr(u, 'id', None)
            if uid is None:
                continue  # Skip rows without valid user IDs

            name = getattr(u, 'full_name', '')
            email = getattr(u, 'email', '')
            role = getattr(u, 'role', '') if not isinstance(getattr(u, 'role', ''), UserRole) else getattr(u, 'role').value
            activate_btn = ft.ElevatedButton("Activate", on_click=lambda e, _id=uid: self._set_active(_id, True))
            deactivate_btn = ft.OutlinedButton("Deactivate", on_click=lambda e, _id=uid: self._set_active(_id, False))
            delete_btn = ft.IconButton(ft.Icons.DELETE, tooltip="Delete user", on_click=lambda e, _id=uid: self._confirm_delete(_id))
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(format_id('U', uid))),
                ft.DataCell(ft.Text(format_name(name))),
                ft.DataCell(ft.Text(email)),
                ft.DataCell(ft.Text((role or '').title())),
                ft.DataCell(ft.Row([activate_btn, deactivate_btn, delete_btn], spacing=6))
            ]))

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Name")),
                ft.DataColumn(ft.Text("Email")),
                ft.DataColumn(ft.Text("Role")),
                ft.DataColumn(ft.Text("Actions")),
            ],
            rows=rows,
            border=ft.border.all(1, "#E0E0E0"),
            heading_row_color="#F5F5F5",
            column_spacing=12,
            expand=True
        )

        # Use reusable TableContainer component to wrap the DataTable
        tc = TableCard(title="Users", table=table, actions=[], width=1200, expand=True)
        self.table_container.content = tc.build()

    def _build_pagination(self):
        # compute total items according to current filters (use same logic as _render_table)
        role_val = (self.role_filter.value or "All").lower()
        role_enum = None
        if role_val == 'tenants':
            role_enum = UserRole.TENANT
        elif role_val == 'pms':
            role_enum = UserRole.PROPERTY_MANAGER
        elif role_val == 'admins':
            role_enum = UserRole.ADMIN

        status_val = (self.status_filter2.value or "All").lower()
        status_active = None
        if status_val == 'active':
            status_active = 1
        elif status_val == 'deactivated':
            status_active = 0

        df = getattr(self.date_from, 'value', None) or (self.date_from.value if hasattr(self.date_from, 'value') else None)
        dt = getattr(self.date_to, 'value', None) or (self.date_to.value if hasattr(self.date_to, 'value') else None)

        users = self._fetch_users(role=role_enum, active=status_active, date_from=df, date_to=dt, tab=self.active_tab)
        q = (self.search_field.value or "").strip().lower()
        if q:
            users = [u for u in users if (getattr(u, 'full_name', '') or '').lower().find(q) != -1 or (getattr(u, 'email', '') or '').lower().find(q) != -1]
        total_items = len(users)

        # Compute total pages and clamp current page index
        total_pages = max(1, (total_items + self.page_size - 1) // self.page_size)
        if self.page_index >= total_pages:
            self.page_index = max(0, total_pages - 1)

        prev_disabled = self.page_index <= 0
        next_disabled = self.page_index >= (total_pages - 1)

        return ft.Row(controls=[
            ft.ElevatedButton("Prev", disabled=prev_disabled, on_click=lambda e: self._change_page(-1)),
            ft.Text(f"Page {self.page_index + 1} of {total_pages}"),
            ft.ElevatedButton("Next", disabled=next_disabled, on_click=lambda e: self._change_page(1)),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=12)

    def _change_page(self, delta: int):
        self.page_index = max(0, self.page_index + delta)
        self._render_table()
        self.page.update()

    # --------------------
    # Data access helpers
    # --------------------
    def _fetch_users(self, role: UserRole = None, active: int = None, date_from: datetime = None, date_to: datetime = None, tab: str = 'all'):
        """Query users table with optional filters and return list[User]."""
        conn = get_connection()
        cur = conn.cursor()
        q = "SELECT * FROM users WHERE 1=1"
        params = []
        # Tab-based overrides
        if tab == 'deactivated':
            q += " AND is_active = 0"
        # Role filtering: use flexible LIKE matching so 'Tenant One' or similar values are matched
        if tab == 'tenants':
            q += " AND (lower(role) LIKE '%tenant%')"
        elif tab == 'pms':
            q += " AND (lower(role) LIKE '%pm%' OR lower(role) LIKE '%property%')"
        elif tab == 'admins':
            q += " AND (lower(role) LIKE '%admin%')"
        elif role:
            # role is a UserRole enum; do flexible matching as well
            rv = role.value.lower()
            if rv == 'pm' or rv == 'property_manager':
                q += " AND (lower(role) LIKE '%pm%' OR lower(role) LIKE '%property%')"
            else:
                q += " AND lower(role) LIKE ?"
                params.append(f"%{rv}%")
        if active is not None:
            q += " AND is_active = ?"
            params.append(active)
        if date_from:
            q += " AND date(created_at) >= date(?)"
            if isinstance(date_from, str):
                df_str = date_from.strip()
            elif hasattr(date_from, 'isoformat'):
                df_str = date_from.isoformat()
            else:
                df_str = str(date_from)
            params.append(df_str)
        if date_to:
            q += " AND date(created_at) <= date(?)"
            if isinstance(date_to, str):
                dt_str = date_to.strip()
            elif hasattr(date_to, 'isoformat'):
                dt_str = date_to.isoformat()
            else:
                dt_str = str(date_to)
            params.append(dt_str)

        q += " ORDER BY created_at DESC"
        try:
            cur.execute(q, tuple(params))
            rows = cur.fetchall()
            from models.user import User
            users = [User.from_db_row(r) for r in rows]
            return users
        finally:
            conn.close()

    # --------------------
    # Tabs and charts
    # --------------------
    def _on_tab_change(self, e):
        idx = e.control.selected_index
        mapping = {0: 'all', 1: 'tenants', 2: 'admins', 3: 'pms', 4: 'deactivated', 5: 'activity'}
        self.active_tab = mapping.get(idx, 'all')
        # If switching to activity logs, render activity instead
        if self.active_tab == 'activity':
            self._render_activity_logs()
        else:
            # update role dropdown to reflect tab selection
            if self.active_tab == 'tenants':
                self.role_filter.value = 'Tenants'
            elif self.active_tab == 'admins':
                self.role_filter.value = 'Admins'
            elif self.active_tab == 'pms':
                self.role_filter.value = 'PMs'
            elif self.active_tab == 'deactivated':
                self.status_filter2.value = 'Deactivated'
            else:
                self.role_filter.value = 'All'
                self.status_filter2.value = 'All'
            self._render_table()
        self.page.update()

    def _render_activity_logs(self):
        # Use storage helper to get recent activity
        logs = get_recent_activity(50)
        rows = []
        for r in logs:
            rid = r['id']
            user = (r['user_full_name'] if 'user_full_name' in r.keys() and r['user_full_name'] else (r['user_email'] if 'user_email' in r.keys() and r['user_email'] else 'System'))
            action = (r['action'] if 'action' in r.keys() else '')
            details = (r['details'] if 'details' in r.keys() else '') or ''
            created = (format_datetime(r['created_at']) if 'created_at' in r.keys() and r['created_at'] else '')
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(rid))),
                ft.DataCell(ft.Text(user)),
                ft.DataCell(ft.Text(action)),
                ft.DataCell(ft.Text(details)),
                ft.DataCell(ft.Text(created)),
            ]))

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("User")),
                ft.DataColumn(ft.Text("Action")),
                ft.DataColumn(ft.Text("Details")),
                ft.DataColumn(ft.Text("When")),
            ],
            rows=rows,
            border=ft.border.all(1, "#E0E0E0"),
            heading_row_color="#F5F5F5",
            column_spacing=12,
            expand=True
        )
        self.table_container.content = ft.Container(content=table, width=1200, expand=True)

    def _build_registration_chart_container(self):
        # Build a small LineChart with registrations per month (last 6 months)
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as cnt FROM users GROUP BY month ORDER BY month DESC LIMIT 6")
            data = cur.fetchall()
        finally:
            conn.close()

        # If no data, use sample
        if not data:
            sample = [("2025-06", 5), ("2025-07", 8), ("2025-08", 10), ("2025-09", 7), ("2025-10", 12), ("2025-11", 9)]
            data = sample

        data = list(reversed(data))
        points = []
        labels = []
        for i, row in enumerate(data, start=1):
            m = row[0]
            v = int(row[1])
            labels.append((i, m[5:]))
            points.append(ft.LineChartDataPoint(x=i, y=v, tooltip=str(v)))

        bottom_axis = ft.ChartAxis(labels=[ft.ChartAxisLabel(value=i, label=ft.Text(lbl, size=10)) for i, lbl in labels], labels_size=10)
        max_y = max([int(r[1]) for r in data]) if data else 1
        chart = ft.LineChart(
            data_series=[ft.LineChartData(data_points=points, curved=True, color="#2196F3", stroke_width=2)],
            left_axis=ft.ChartAxis(labels=[ft.ChartAxisLabel(value=v, label=ft.Text(str(v), size=10)) for v in range(0, max_y + 1, max(1, max_y//4))]),
            bottom_axis=bottom_axis,
            height=160,
            expand=True,
        )

        card = ft.Container(bgcolor="white", padding=12, border_radius=8, expand=True, content=ft.Column(controls=[ft.Text("User Registrations", weight=ft.FontWeight.BOLD), chart]))
        return card

    def _build_active_inactive_card(self):
        # Query active vs inactive counts
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT SUM(CASE WHEN is_active=1 THEN 1 ELSE 0 END) as active, SUM(CASE WHEN is_active=0 THEN 1 ELSE 0 END) as inactive FROM users")
            row = cur.fetchone()
        finally:
            conn.close()

        active = (row[0] or 0) if row else 0
        inactive = (row[1] or 0) if row else 0

        # Simple bar representation using BarChart
        groups = [
            ft.BarChartGroup(x=0, bar_rods=[ft.BarChartRod(to_y=active, width=30, color="#4CAF50")]),
            ft.BarChartGroup(x=1, bar_rods=[ft.BarChartRod(to_y=inactive, width=30, color="#F44336")]),
        ]
        chart = ft.BarChart(bar_groups=groups, groups_space=30, height=140, expand=True, bottom_axis=ft.ChartAxis(labels=[ft.ChartAxisLabel(value=0, label=ft.Text("Active")), ft.ChartAxisLabel(value=1, label=ft.Text("Inactive"))]))
        card = ft.Container(bgcolor="white", padding=12, border_radius=8, width=320, content=ft.Column(controls=[ft.Text("Active vs Inactive Users", weight=ft.FontWeight.BOLD), chart, ft.Text(f"Active: {active}  Inactive: {inactive}")]))
        return card
