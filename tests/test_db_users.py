import pytest

from storage import db


def test_user_crud_flow(temp_db):
    ok, msg = db.create_user("Test User", "user1@example.com", "Passw0rd!", "tenant")
    assert ok, msg

    user = db.validate_user("user1@example.com", "Passw0rd!")
    assert user and user["role"] == "tenant"

    assert db.update_user_password(user["id"], "NewPass1!") is True
    user2 = db.validate_user("user1@example.com", "NewPass1!")
    assert user2

    assert db.deactivate_user(user["id"]) is True
    assert db.validate_user("user1@example.com") is None  # inactive users not returned

    assert db.activate_user(user["id"]) is True
    assert db.delete_user(user["id"]) is True


def test_password_reset_flow(temp_db):
    ok, _ = db.create_user("Reset User", "reset@example.com", "Passw0rd!", "tenant")
    assert ok
    user = db.validate_user("reset@example.com", "Passw0rd!")
    assert user

    token = "tok123"
    expires = "2099-01-01T00:00:00"
    assert db.create_password_reset_token(user["id"], token, expires) is True
    uid = db.verify_password_reset_token(token)
    assert uid == user["id"]

    assert db.update_user_password(user["id"], "ResetPass1!") is True
    assert db.use_password_reset_token(token) is True
    # Token should now be used; verification should fail
    assert db.verify_password_reset_token(token) is None