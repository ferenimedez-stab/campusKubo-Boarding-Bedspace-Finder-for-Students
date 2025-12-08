import pytest

from storage.db import create_reservation, create_password_reset_token


def test_create_reservation_invalid_ids():
    # invalid ids should return None
    assert create_reservation(0, 0, "2025-01-01", "2025-01-02") is None
    assert create_reservation(-1, 5, "2025-01-01", "2025-01-02") is None


def test_create_password_reset_token_invalid_user():
    # invalid user id should return False
    assert create_password_reset_token(0, "token", "2099-01-01T00:00:00") is False
