# app/views/admin_reservations_view.py

import flet as ft
from services.reservation_service import ReservationService
from components.navbar import DashboardNavBar
from components.admin_utils import format_id, format_name, format_datetime
from components.table_card import TableCard
from state.session_state import SessionState

class AdminReservationsView:

    def __init__(self, page):
        self.page = page
        self.session = SessionState(page)
        self.reservation_service = ReservationService()
        # pagination state
        self.page_index = 0
        self.page_size = 8
        self.table_container = ft.Container()

    def build(self):
        if not self.session.require_auth(): return None
        if not self.session.is_admin(): self.page.go("/"); return None

        # initial render
        self._render_table()

        return ft.View(
            "/admin_reservations",
            scroll=ft.ScrollMode.AUTO,
            controls=[
                DashboardNavBar(self.page, "Reservation Oversight", self.session.get_email() or "").view(),
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Row(controls=[
                            ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: self.page.go('/admin')),
                            ft.Text("All Reservations", size=26, weight= ft.FontWeight.BOLD)
                        ], alignment=ft.MainAxisAlignment.START),
                        ft.Divider(),
                        ft.Container(height=440, content=self.table_container),
                        ft.Divider(),
                        self._build_pagination()
                    ])
                )
            ]
        )

    def _update_reservation(self, reservation_id: int, new_status: str):
        ok = self.reservation_service.update_reservation_status(reservation_id, new_status)
        if ok:
            self.page.open(ft.SnackBar(ft.Text(f"Reservation {new_status}")))
        else:
            self.page.open(ft.SnackBar(ft.Text("Failed to update reservation")))
        # refresh current page
        self._render_table()
        self.page.update()

    def _render_table(self):
        reservations = self.reservation_service.get_all_reservations()

        # pagination slice
        total = len(reservations)
        start = self.page_index * self.page_size
        end = start + self.page_size
        page_items = reservations[start:end]

        data_rows = []
        for r in page_items:
            rid = r.get('id') if isinstance(r, dict) else r['id']
            listing_id = r.get('listing_id') if isinstance(r, dict) else r['listing_id']
            tenant_id = r.get('tenant_id') if isinstance(r, dict) else r['tenant_id']
            start_date = r.get('start_date') if isinstance(r, dict) else r['start_date']
            end_date = r.get('end_date') if isinstance(r, dict) else r['end_date']
            status = r.get('status') if isinstance(r, dict) else r['status']

            approve_btn = ft.ElevatedButton("Approve", on_click=lambda e, _id=rid: self._update_reservation(_id, 'approved'))
            cancel_btn = ft.OutlinedButton("Cancel", on_click=lambda e, _id=rid: self._update_reservation(_id, 'cancelled'))

            data_rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(format_id('R', rid))),
                    ft.DataCell(ft.Text(format_id('L', listing_id))),
                    ft.DataCell(ft.Text(format_id('U', tenant_id))),
                    ft.DataCell(ft.Text(format_datetime(start_date))),
                    ft.DataCell(ft.Text(format_datetime(end_date))),
                    ft.DataCell(ft.Text(str(status).title())),
                    ft.DataCell(ft.Row([approve_btn, cancel_btn], spacing=6))
                ])
            )

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Listing ID")),
                ft.DataColumn(ft.Text("Tenant ID")),
                ft.DataColumn(ft.Text("Start")),
                ft.DataColumn(ft.Text("End")),
                ft.DataColumn(ft.Text("Status")),
                ft.DataColumn(ft.Text("Actions")),
            ],
            rows=data_rows,
            border=ft.border.all(1, "#E0E0E0"),
            heading_row_color="#F5F5F5",
            column_spacing=12,
            expand=True
        )

        tc = TableCard(title="Reservations", table=table, width=1200, expand=True)
        self.table_container.content = tc.build()

    def _build_pagination(self):
        reservations = self.reservation_service.get_all_reservations()
        total_items = len(reservations)

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
