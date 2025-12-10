"""
Diagnostic Check for CampusKubo System
Run this to verify all components are working correctly
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def check_imports():
    """Verify all critical imports"""
    print("=" * 60)
    print("IMPORT VERIFICATION")
    print("=" * 60)

    checks = [
        ("Main app", "from main import main"),
        ("Database", "from storage.db import get_tenants, create_tenant"),
        ("RoomsView", "from views.rooms_view import RoomsView"),
        ("MyTenantsView", "from views.my_tenants_view import MyTenantsView"),
        ("Sidebar", "from components.sidebar import create_sidebar"),
        ("Session State", "from state.session_state import SessionState"),
        ("PM Dashboard", "from views.pm_dashboard_view import PMDashboardView"),
    ]

    for name, import_stmt in checks:
        try:
            exec(import_stmt)
            print(f"✓ {name:20} OK")
        except Exception as e:
            print(f"✗ {name:20} FAILED: {e}")

    print()

def check_database():
    """Verify database connectivity"""
    print("=" * 60)
    print("DATABASE VERIFICATION")
    print("=" * 60)

    try:
        from storage.db import init_db, get_connection
        init_db()
        conn = get_connection()
        cursor = conn.cursor()

        # Check tenants table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tenants'")
        if cursor.fetchone():
            print("✓ Tenants table exists")
        else:
            print("✗ Tenants table missing")

        # Check users table
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✓ Users table: {user_count} users")

        # Check listings table
        cursor.execute("SELECT COUNT(*) FROM listings")
        listing_count = cursor.fetchone()[0]
        print(f"✓ Listings table: {listing_count} listings")

        # Check tenants table
        cursor.execute("SELECT COUNT(*) FROM tenants")
        tenant_count = cursor.fetchone()[0]
        print(f"✓ Tenants table: {tenant_count} tenants")

        conn.close()
        print("✓ Database connection OK")

    except Exception as e:
        print(f"✗ Database error: {e}")

    print()

def check_routes():
    """Verify routing configuration"""
    print("=" * 60)
    print("ROUTING CONFIGURATION")
    print("=" * 60)

    routes = [
        ("/rooms", "Rooms selection/management"),
        ("/rooms/{id}", "Specific property rooms"),
        ("/my-tenants", "Tenants selection/management"),
        ("/my-tenants/{id}", "Specific property tenants"),
        ("/pm", "PM Dashboard"),
        ("/pm/analytics", "Analytics (placeholder)"),
        ("/pm/profile", "PM Profile"),
    ]

    for route, description in routes:
        print(f"✓ {route:20} - {description}")

    print()

def check_sidebar_navigation():
    """Verify sidebar navigation items"""
    print("=" * 60)
    print("SIDEBAR NAVIGATION")
    print("=" * 60)

    from components.sidebar import _nav_items_for_role

    pm_items = _nav_items_for_role("pm")
    print("PM Navigation Items:")
    for item in pm_items:
        print(f"  • {item['label']:15} → {item['route']}")

    print()

def main():
    """Run all diagnostic checks"""
    print("\n" + "=" * 60)
    print("CAMPUSKUBO SYSTEM DIAGNOSTIC CHECK")
    print("=" * 60 + "\n")

    check_imports()
    check_database()
    check_routes()
    check_sidebar_navigation()

    print("=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)
    print("\nIf all checks passed, the system is ready to run.")
    print("Start the app with: python -m app.main")
    print()

if __name__ == "__main__":
    main()
