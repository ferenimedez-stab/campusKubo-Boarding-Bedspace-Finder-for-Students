#!/usr/bin/env python3
"""
Module Validation Script
Validates all module names and imports across the application
"""
import sys
import os
import importlib
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent / 'app'))

def test_core_packages():
    """Test that all core packages can be imported"""
    packages = [
        'components',
        'config',
        'models',
        'services',
        'state',
        'storage',
        'utils',
        'views'
    ]

    print("Testing core package imports...")
    for pkg in packages:
        try:
            importlib.import_module(pkg)
            print(f"  ✓ {pkg}")
        except Exception as e:
            print(f"  ✗ {pkg}: {e}")
            return False
    return True

def test_critical_modules():
    """Test critical module imports"""
    modules = [
        'services.admin_service',
        'services.user_service',
        'services.listing_service',
        'services.reservation_service',
        'services.auth_service',
        'services.refresh_service',
        'components.navbar',
        'components.footer',
        'components.profile_section',
        'state.session_state',
        'storage.db',
        'models.user',
        'models.listing',
    ]

    print("\nTesting critical module imports...")
    for mod in modules:
        try:
            importlib.import_module(mod)
            print(f"  ✓ {mod}")
        except Exception as e:
            print(f"  ✗ {mod}: {e}")
            return False
    return True

def test_view_modules():
    """Test all view module imports"""
    view_modules = [
        'views.admin_dashboard_view',
        'views.admin_users_view',
        'views.admin_listings_view',
        'views.admin_reservations_view',
        'views.admin_payments_view',
        'views.admin_reports_view',
        'views.admin_profile_view',
        'views.admin_settings_view',
        'views.home_view',
        'views.login_view',
        'views.signup_view',
        'views.browse_view',
        'views.profile_view',
    ]

    print("\nTesting view module imports...")
    for mod in view_modules:
        try:
            importlib.import_module(mod)
            print(f"  ✓ {mod}")
        except Exception as e:
            print(f"  ✗ {mod}: {e}")
            return False
    return True

def check_init_files():
    """Verify all __init__.py files exist"""
    base_path = Path(__file__).parent / 'app'
    required_inits = [
        '__init__.py',
        'components/__init__.py',
        'config/__init__.py',
        'models/__init__.py',
        'services/__init__.py',
        'state/__init__.py',
        'storage/__init__.py',
        'tests/__init__.py',
        'utils/__init__.py',
        'views/__init__.py',
    ]

    print("\nChecking __init__.py files...")
    all_exist = True
    for init_file in required_inits:
        path = base_path / init_file
        if path.exists():
            print(f"  ✓ app/{init_file}")
        else:
            print(f"  ✗ app/{init_file} MISSING")
            all_exist = False
    return all_exist

def main():
    print("="*60)
    print("Module Validation Check")
    print("="*60)

    results = []

    # Run all tests
    results.append(("Core Packages", test_core_packages()))
    results.append(("Critical Modules", test_critical_modules()))
    results.append(("View Modules", test_view_modules()))
    results.append(("Init Files", check_init_files()))

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    all_passed = True
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name:.<50} {status}")
        if not passed:
            all_passed = False

    print("="*60)

    if all_passed:
        print("\n✅ All module validations PASSED!")
        return 0
    else:
        print("\n❌ Some module validations FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
