"""
app/health.py

Startup health checks for DB and crypto.
"""
from storage import db
import sys


def run_startup_checks(fail_on_error: bool = True) -> bool:
    ok, msg = db.check_argon2_compatibility(fail_on_missing=fail_on_error)
    if not ok:
        print(f"[health] Argon2 check: {msg}", file=sys.stderr)
        if fail_on_error:
            raise RuntimeError(msg)
    else:
        print("[health] Argon2 check passed")

    ok2, msg2 = db.check_db_pragmas()
    if not ok2:
        print(f"[health] PRAGMA check: {msg2}", file=sys.stderr)
        if fail_on_error:
            raise RuntimeError(msg2)
    else:
        print(f"[health] PRAGMA check passed: {msg2}")

    return True
