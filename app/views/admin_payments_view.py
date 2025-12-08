import flet as ft
from services.admin_service import AdminService
from components.admin_utils import format_id, format_name, format_datetime
from components.navbar import DashboardNavBar
from components.table_card import TableCard
from state.session_state import SessionState


class AdminPaymentsView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.session = SessionState(page)
        self.admin_service = AdminService()
        self.page_index = 0
        self.page_size = 8
        self.table_container = ft.Container()

    def build(self):
        if not self.session.require_auth():
            return None
        if not self.session.is_admin():
            self.page.go("/")
            return None

        # initial render
        self._render_table()

        navbar = DashboardNavBar(self.page, "Payments", self.session.get_email() or "").view()

        return ft.View(
            "/admin_payments",
            scroll=ft.ScrollMode.AUTO,
            controls=[
                navbar,
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Row(controls=[
                            ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: self.page.go('/admin')),
                            ft.Text("Payments", size=26, weight=ft.FontWeight.BOLD)
                        ], alignment=ft.MainAxisAlignment.START),
                        ft.Divider(),
                                        ft.Container(height=440, content=self.table_container),
                        ft.Divider(),
                        self._build_pagination()
                    ])
                )
            ]
        )

    def _render_table(self):
        payments = self.admin_service.get_all_payments()

        total = len(payments)
        start = self.page_index * self.page_size
        end = start + self.page_size
        page_items = payments[start:end]

        rows = []
        for p in page_items:
            pid_raw = p.get('id')
            try:
                pid = int(pid_raw) if pid_raw is not None else 0
            except (TypeError, ValueError):
                pid = 0
            user_email = p.get('user_email') or '—'
            listing_addr = p.get('listing_address') or '—'
            amount_raw = p.get('amount') or 0
            try:
                amount_val = float(amount_raw)
            except Exception:
                # if amount is not numeric, fallback to 0 and log for debugging
                print(f"[admin_payments_view] Non-numeric amount for payment id={pid_raw}: {amount_raw}")
                amount_val = 0.0
            created_at = p.get('created_at') or ''
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(format_id('PMT', pid))),
                ft.DataCell(ft.Text(user_email)),
                ft.DataCell(ft.Text(format_name(listing_addr))),
                ft.DataCell(ft.Text(f"\u20b1{amount_val:,.2f}")),
                ft.DataCell(ft.Text(format_datetime(created_at)))
            ]))

        # format amount and date in rows already done; create styled DataTable
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("User")),
                ft.DataColumn(ft.Text("Listing")),
                ft.DataColumn(ft.Text("Amount")),
                ft.DataColumn(ft.Text("Date")),
            ],
            rows=rows,
            border=ft.border.all(1, "#E0E0E0"),
            heading_row_color="#F5F5F5",
            column_spacing=12,
            expand=True
        )

        tc = TableCard(title="Payments", table=table, width=1200, expand=True)
        self.table_container.content = tc.build()

    def _build_pagination(self):
        payments = self.admin_service.get_all_payments()
        total_items = len(payments)
        prev_disabled = self.page_index <= 0
        next_disabled = (self.page_index + 1) * self.page_size >= max(1, total_items)
        return ft.Row(controls=[
            ft.ElevatedButton("Prev", disabled=prev_disabled, on_click=lambda e: self._change_page(-1)),
            ft.Text(f"Page {self.page_index + 1} of {max(1, (total_items + self.page_size -1)//self.page_size)}"),
            ft.ElevatedButton("Next", disabled=next_disabled, on_click=lambda e: self._change_page(1)),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=12)

    def _change_page(self, delta: int):
        self.page_index = max(0, self.page_index + delta)
        self._render_table()
        self.page.update()
