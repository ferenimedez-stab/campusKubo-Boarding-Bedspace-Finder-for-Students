# app/views/admin_reports_view.py

import flet as ft
from services.report_service import ReportService
from state.session_state import SessionState
from components.navbar import DashboardNavBar

class AdminReportsView:

    def __init__(self, page):
        self.page = page
        self.session = SessionState(page)
        self.report_service = ReportService()

    def build(self):
        if not self.session.require_auth(): return None
        if not self.session.is_admin(): self.page.go("/"); return None

        reports = self.report_service.get_all_reports()

        report_cards = []
        for r in reports:
            rid = r.get('id') if isinstance(r, dict) else getattr(r, 'id', None)
            reporter = r.get('reporter_email') if isinstance(r, dict) else getattr(r, 'reporter_email', None)
            message = r.get('message') if isinstance(r, dict) else getattr(r, 'message', None)
            addr = r.get('listing_address') if isinstance(r, dict) else getattr(r, 'listing_address', None)
            resolve_btn = ft.ElevatedButton("Resolve", on_click=lambda e, _id=rid: self._resolve_report(_id) if _id else None)
            report_cards.append(
                ft.Container(
                    padding=20,
                    bgcolor="white",
                    border_radius=12,
                    margin=ft.margin.only(bottom=12),
                    content=ft.Column([
                        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                            ft.Text(f"Report #{rid}", size=18, weight=ft.FontWeight.BOLD),
                            ft.Text(addr or "", size=12, color=ft.Colors.BLACK)
                        ]),
                        ft.Text(f"Submitted by: {reporter}"),
                        ft.Text(f"Message: {message}"),
                        ft.Row(controls=[resolve_btn], alignment=ft.MainAxisAlignment.END)
                    ])
                )
            )

        return ft.View(
            "/admin_reports",
            scroll=ft.ScrollMode.AUTO,
            controls=[
                DashboardNavBar(self.page, "Report Management", self.session.get_email() or "").view(),
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Row(controls=[
                            ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: self.page.go('/admin')),
                            ft.Text("Reports", size=26, weight=ft.FontWeight.BOLD)
                        ], alignment=ft.MainAxisAlignment.START),
                        ft.Divider(),
                        ft.Column(report_cards)
                    ])
                )
            ]
        )

    def _resolve_report(self, report_id: int):
        from services.report_service import ReportService
        ok = ReportService.update_report_status(report_id, 'resolved')
        if ok:
            snack = ft.SnackBar(ft.Text('Report marked resolved'))
            self.page.overlay.append(snack)  # type: ignore
            snack.open = True
            self.page.update()
        else:
            snack = ft.SnackBar(ft.Text('Failed to update report'))
            self.page.overlay.append(snack)  # type: ignore
            snack.open = True
            self.page.update()
            self.page.go('/admin_reports')
