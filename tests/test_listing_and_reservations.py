from storage import db


def test_listing_lifecycle_and_reservation(temp_db):
    # Create PM and tenant
    ok_pm, _ = db.create_user("PM User", "pm@example.com", "Passw0rd!", "pm")
    ok_tenant, _ = db.create_user("Tenant User", "tenant@example.com", "Passw0rd!", "tenant")
    assert ok_pm and ok_tenant

    pm = db.validate_user("pm@example.com", "Passw0rd!")
    tenant = db.validate_user("tenant@example.com", "Passw0rd!")
    assert pm and tenant

    listing_id = db.create_listing(pm["id"], "123 Test St", 5000, "Desc", "Details", ["img1.jpg"])
    assert listing_id

    # New listing should be pending; approve it
    assert db.change_listing_status(listing_id, "approved") is True

    # Create reservation
    res_id = db.create_reservation(listing_id, tenant["id"], "2025-01-01", "2025-02-01", status="approved")
    assert res_id

    reservations = db.get_reservations(tenant_id=tenant["id"])
    assert any(r["id"] == res_id for r in reservations)