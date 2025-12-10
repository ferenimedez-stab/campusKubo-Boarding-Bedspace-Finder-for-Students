import importlib
import flet as ft
from datetime import datetime


class DummySession:
    def __init__(self):
        self._d = {}

    def set(self, k, v):
        self._d[k] = v

    def get(self, k, default=None):
        return self._d.get(k, default)

    def clear(self):
        self._d.clear()


class DummyClientStorage:
    def __init__(self):
        self._d = {}

    def contains_key(self, key):
        return key in self._d

    def get(self, key):
        return self._d.get(key)

    def set(self, key, value):
        self._d[key] = value


class DummyPage:
    def __init__(self):
        self.session = DummySession()
        self.client_storage = DummyClientStorage()
        self._last_route = None
        self.width = 1024
        self.height = 768

    def go(self, route):
        self._last_route = route

    def update(self):
        pass


def _patch_admin_services(monkeypatch):
    mod = importlib.import_module('views.admin_dashboard_view')

    class StubAdminService:
        def get_stats(self):
            return {
                'total_tenants': 10,
                'total_pms': 5,
                'total_listings': 20,
                'approved_listings': 15,
                'pending_listings': 5,
                'total_reservations': 50,
                'total_reports': 2,
                'total_payments': 1000,
            }

        def get_pending_pm_count(self):
            return 3

    class StubListingService:
        def __init__(self):
            pass

    class StubReservationService:
        def get_reservations_per_month(self):
            return [("Jan", 5), ("Feb", 8), ("Mar", 12)]

    class StubActivityService:
        def get_recent_activities(self, limit=8):
            return [
                {'message': 'User registered'},
                {'message': 'Listing created'},
            ]

    monkeypatch.setattr(mod, 'AdminService', StubAdminService)
    monkeypatch.setattr(mod, 'ListingService', StubListingService)
    monkeypatch.setattr(mod, 'ReservationService', StubReservationService)
    monkeypatch.setattr(mod, 'ActivityService', StubActivityService)


def test_admin_dashboard_build(monkeypatch):
    _patch_admin_services(monkeypatch)
    from views.admin_dashboard_view import AdminDashboardView

    page = DummyPage()
    # simulate admin logged in with valid session
    page.session.set('is_logged_in', True)
    page.session.set('role', 'admin')
    page.session.set('email', 'admin@example.com')
    page.session.set('user_id', 1)
    page.session.set('last_activity', datetime.utcnow().isoformat())

    view = AdminDashboardView(page).build()
    assert view is not None
    assert isinstance(view, ft.View)


def test_pm_dashboard_build(monkeypatch):
    # stub ListingService used by PM view
    pm_mod = importlib.import_module('views.pm_dashboard_view')

    class StubListingService:
        def get_all_listings(self, owner_id=None):
            return []

        def check_availability(self, listing_id):
            return True

    monkeypatch.setattr(pm_mod, 'ListingService', StubListingService)

    from views.pm_dashboard_view import PMDashboardView

    page = DummyPage()
    page.session.set('user_id', 2)
    page.session.set('email', 'pm@example.com')
    page.session.set('full_name', 'Property Manager')

    view = PMDashboardView(page).build()
    assert view is not None
    assert isinstance(view, ft.View)


def test_tenant_dashboard_build():
    from views.tenant_dashboard_view import TenantDashboardView

    page = DummyPage()
    page.session.set('is_logged_in', True)
    page.session.set('role', 'tenant')
    page.session.set('email', 'tenant@example.com')
    page.session.set('user_id', 3)
    page.session.set('last_activity', datetime.utcnow().isoformat())

    view = TenantDashboardView(page).build()
    assert view is not None
    assert isinstance(view, ft.View)
