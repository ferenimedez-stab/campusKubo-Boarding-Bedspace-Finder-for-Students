"""
Manual CRUD Testing Script
Run this to verify all admin CRUD operations work at the service level.
"""

import sys
sys.path.insert(0, 'app')

from services.admin_service import AdminService
from services.listing_service import ListingService
from services.report_service import ReportService
from storage.db import get_connection

def test_user_crud():
    print("\n=== TESTING USER CRUD ===")
    svc = AdminService()

    # Create
    print("1. Creating test user...")
    ok, msg = svc.create_user_account("Test User", "test@example.com", "tenant", "Password123!", True)
    print(f"   Result: {ok}, Message: {msg}")

    if ok:
        # Get the user ID
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email='test@example.com'")
        row = cursor.fetchone()
        conn.close()

        if row:
            user_id = row['id']
            print(f"   Created user ID: {user_id}")

            # Update
            print("2. Updating test user...")
            ok, msg = svc.update_user_account(user_id, "Updated Name", "test@example.com", "tenant", True, "1234567890")
            print(f"   Result: {ok}, Message: {msg}")

            # Deactivate
            print("3. Deactivating test user...")
            ok = svc.deactivate_user(user_id)
            print(f"   Result: {ok}")

            # Activate
            print("4. Activating test user...")
            ok = svc.activate_user(user_id)
            print(f"   Result: {ok}")

            # Delete
            print("5. Deleting test user...")
            ok = svc.delete_user(user_id)
            print(f"   Result: {ok}")

    print("✓ User CRUD tests complete")

def test_listing_crud():
    print("\n=== TESTING LISTING CRUD ===")
    svc = AdminService()
    listing_svc = ListingService()

    # First, we need a PM user
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE role='pm' LIMIT 1")
    pm_row = cursor.fetchone()
    conn.close()

    if not pm_row:
        print("   No PM users found. Creating one...")
        ok, msg = svc.create_user_account("Test PM", "testpm@example.com", "pm", "Password123!", True)
        print(f"   Result: {ok}, Message: {msg}")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email='testpm@example.com'")
        pm_row = cursor.fetchone()
        conn.close()

    if pm_row:
        pm_id = pm_row['id']
        print(f"   Using PM ID: {pm_id}")

        # Create listing
        print("1. Creating test listing...")
        ok, msg, listing_id = svc.create_listing_admin(
            address="123 Test Street",
            price=5000.0,
            description="Test listing",
            lodging_details="2 bedrooms",
            status="pending",
            pm_id=pm_id
        )
        print(f"   Result: {ok}, Message: {msg}, Listing ID: {listing_id if ok else 'N/A'}")

        if ok and listing_id:
            # Approve listing
            print("2. Approving test listing...")
            ok = svc.approve_listing(listing_id)
            print(f"   Result: {ok}")

            # Reject listing
            print("3. Rejecting test listing...")
            ok = svc.reject_listing(listing_id)
            print(f"   Result: {ok}")

            # Delete listing
            print("4. Deleting test listing...")
            ok, msg = listing_svc.delete_listing_by_admin(listing_id)
            print(f"   Result: {ok}, Message: {msg}")

    print("✓ Listing CRUD tests complete")

def test_pm_verification():
    print("\n=== TESTING PM VERIFICATION ===")
    svc = AdminService()

    # Create a pending PM
    print("1. Creating pending PM account...")
    ok, msg = svc.create_user_account("Pending PM", "pendingpm@example.com", "pm", "Password123!", False)
    print(f"   Result: {ok}, Message: {msg}")

    if ok:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email='pendingpm@example.com'")
        row = cursor.fetchone()
        conn.close()

        if row:
            pm_id = row['id']
            print(f"   Created PM ID: {pm_id}")

            # Approve PM
            print("2. Approving PM...")
            ok = svc.approve_pm(pm_id)
            print(f"   Result: {ok}")

            # Reject PM
            print("3. Rejecting PM...")
            ok = svc.reject_pm(pm_id)
            print(f"   Result: {ok}")

            # Cleanup
            print("4. Cleaning up PM...")
            ok = svc.delete_user(pm_id)
            print(f"   Result: {ok}")

    print("✓ PM verification tests complete")

def test_report_resolution():
    print("\n=== TESTING REPORT RESOLUTION ===")

    # Check if there are any reports
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, status FROM reports LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if row:
        report_id = row['id']
        print(f"   Testing with report ID: {report_id}")

        print("1. Resolving report...")
        ok = ReportService.update_report_status(report_id, 'resolved')
        print(f"   Result: {ok}")

        print("2. Reopening report...")
        ok = ReportService.update_report_status(report_id, 'open')
        print(f"   Result: {ok}")
    else:
        print("   No reports found in database. Skipping report tests.")

    print("✓ Report resolution tests complete")

if __name__ == "__main__":
    print("=" * 60)
    print("CAMPUSKUBO ADMIN CRUD VERIFICATION TESTS")
    print("=" * 60)

    try:
        test_user_crud()
        test_listing_crud()
        test_pm_verification()
        test_report_resolution()

        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("\nIf all tests passed, the CRUD operations work at the service level.")
        print("If UI buttons are unresponsive, the issue is in the view layer or event handlers.")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
