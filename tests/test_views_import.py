import importlib


VIEW_MODULES = [
    "views.admin_dashboard_view",
    "views.admin_users_view",
    "views.admin_pm_verification_view",
    "views.admin_listings_view",
    "views.admin_reservations_view",
    "views.admin_payments_view",
    "views.admin_reports_view",
    "views.admin_profile_view",
    "views.home_view",
    "views.browse_view",
    "views.login_view",
    "views.signup_view",
    "views.tenant_dashboard_view",
    "views.pm_dashboard_view",
    "views.pm_profile_view",
    "views.pm_add_edit_view",
    "views.property_detail_view",
    "views.reservation_view",
    "views.listing_detail_view",
    "views.listing_detail_extended_view",
]


def test_view_modules_import():
    for mod in VIEW_MODULES:
        importlib.import_module(mod)