import pytest

from services.auth_service import AuthService
from storage import db


def test_register_and_login(temp_db):
    ok, msg = AuthService.register("a1@example.com", "Passw0rd!", "tenant", full_name="Alice One")
    assert ok, msg

    # Duplicate should fail
    ok2, _ = AuthService.register("a1@example.com", "Passw0rd!", "tenant", full_name="Alice One")
    assert ok2 is False

    user = AuthService.login("a1@example.com", "Passw0rd!")
    assert user and user["role"] == "tenant"


def test_register_role_validation(temp_db):
    ok, msg = AuthService.register("bad@example.com", "Passw0rd!", "unknown", full_name="Bad Role")
    assert ok is False


def test_password_reset_via_service(temp_db):
    ok, msg = AuthService.register("reset2@example.com", "Passw0rd!", "tenant", full_name="Reset Two")
    assert ok, msg
    success, _msg, token = AuthService.request_password_reset("reset2@example.com")
    assert success and token

    success2, msg2 = AuthService.reset_password_with_token(token, "BetterPass2!")
    assert success2, msg2
    user = AuthService.login("reset2@example.com", "BetterPass2!")
    assert user