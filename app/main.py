"""
CampusKubo - Main Application (Model Version)
Single-file application matching the provided model.
Uses existing modular components and database infrastructure.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import flet as ft

# Import database functions (matching model's import style)
from storage.db import (
    init_db,
    property_data
)
from services.auth_service import AuthService
from health import run_startup_checks

# Import modular components
from views.admin_dashboard_view import AdminDashboardView
from views.admin_users_view import AdminUsersView
from views.admin_pm_verification_view import AdminPMVerificationView
from views.admin_listings_view import AdminListingsView
from views.admin_reservations_view import AdminReservationsView
from views.admin_payments_view import AdminPaymentsView
from views.admin_reports_view import AdminReportsView
from views.admin_profile_view import AdminProfileView
from views.home_view import HomeView
from views.browse_view import BrowseView
from views.login_view import LoginView
from views.signup_view import SignupView
from views.tenant_dashboard_view import TenantDashboardView
from views.pm_dashboard_view import PMDashboardView
from views.pm_profile_view import PMProfileView
from views.pm_add_edit_view import PMAddEditView
from views.property_detail_view import PropertyDetailView

def main(page: ft.Page):
    """Main application entry point - modular version"""

    page.title = "CampusKubo"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.frameless = False
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Initialize database
    # Run startup health checks before initializing DB
    try:
        run_startup_checks(fail_on_error=False)
    except Exception as e:
        print(f"[main] Startup health check warning: {e}")
    init_db()
    AuthService.ensure_admin_exists()
    property_data()

    # ========== ROUTING ==========
    def route_change(route):
        page.views.clear()

        protected_routes = ["/tenant", "/pm", "/admin"]
        user_role = page.session.get("role")

        # Protect any sub-route of tenant/pm/admin by prefix
        if any(page.route.startswith(p) for p in protected_routes) and not user_role:
            page.go("/login")
            return

        if page.route.startswith("/tenant") and user_role != "tenant":
            snack_bar = ft.SnackBar(ft.Text("Access denied. Tenant role required."))
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.go("/login")
            return

        if page.route.startswith("/pm") and user_role != "pm":
            snack_bar = ft.SnackBar(ft.Text("Access denied. Property Manager role required."))
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.go("/login")
            return

        if page.route.startswith("/admin") and user_role != "admin":
            snack_bar = ft.SnackBar(ft.Text("Access denied. Admin role required."))
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.go("/login")
            return

        if page.route == "/":
            page.views.append(HomeView(page).build())
        elif page.route == "/login":
            page.views.append(LoginView(page).build())
        elif page.route == "/signup":
            page.views.append(SignupView(page).build())
        elif page.route == "/browse":
            page.views.append(BrowseView(page).build())
        elif page.route == "/property-details":
            view = PropertyDetailView(page).build()
            if view:
                page.views.append(view)
        elif page.route == "/tenant":
            page.views.append(TenantDashboardView(page).build())
        elif page.route == "/pm":
            view = PMDashboardView(page).build()
            if view:
                page.views.append(view)
        elif page.route == "/pm/add":
            view = PMAddEditView(page).build()
            if view:
                page.views.append(view)
        elif page.route.startswith("/pm/edit/"):
            view = PMAddEditView(page).build()
            if view:
                page.views.append(view)
        elif page.route == "/pm/profile":
            v = PMProfileView(page).build()
            if v:
                page.views.append(v)
        elif page.route == "/pm/profile/edit":
            v = PMProfileView(page).build_edit()
            if v:
                page.views.append(v)
        elif page.route == "/admin":
            print("Route change: /admin")
            view = AdminDashboardView(page).build()
            print(f"Admin view built: {view is not None}")
            if view:
                page.views.append(view)
            else:
                print("Admin view is None")
        elif page.route == "/admin_users":
            v = AdminUsersView(page).build()
            if v:
                page.views.append(v)
        elif page.route == "/admin_pm_verification":
            v = AdminPMVerificationView(page).build()
            if v:
                page.views.append(v)
        elif page.route == "/admin_listings":
            v = AdminListingsView(page).build()
            if v:
                page.views.append(v)
        elif page.route == "/admin_reservations":
            v = AdminReservationsView(page).build()
            if v:
                page.views.append(v)
        elif page.route == "/admin_payments":
            v = AdminPaymentsView(page).build()
            if v:
                page.views.append(v)
        elif page.route == "/admin_reports":
            v = AdminReportsView(page).build()
            if v:
                page.views.append(v)
        elif page.route == "/admin_profile":
            v = AdminProfileView(page).build()
            if v:
                page.views.append(v)
        elif page.route == "/logout":
            page.session.clear()
            page.go("/login")

        page.update()

    page.on_route_change = route_change
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")