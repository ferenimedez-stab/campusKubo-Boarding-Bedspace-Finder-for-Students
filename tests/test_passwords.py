import hashlib
import pytest

from storage.db import verify_password
try:
    from storage.db import _PH
except Exception:
    _PH = None


def test_sha256_verify():
    pwd = "TestPass1!"
    hashed = hashlib.sha256(pwd.encode('utf-8')).hexdigest()
    assert verify_password(hashed, pwd) is True
    assert verify_password(hashed, "wrong") is False


def test_argon2_verify_if_available():
    if _PH is None:
        pytest.skip("Argon2 not available in this environment")
    pwd = "AnotherPass2$"
    hashed = _PH.hash(pwd)
    assert verify_password(hashed, pwd) is True
    assert verify_password(hashed, "wrong") is False
