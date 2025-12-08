import os
import sys

# Ensure project root is on sys.path for imports like 'storage' and 'services'
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
APP_DIR = os.path.join(ROOT, 'app')
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import importlib
import sqlite3
import pytest

from storage import db as db_module
from storage import seed_data


@pytest.fixture(scope="function")
def temp_db(monkeypatch, tmp_path):
    """Provide an isolated temp DB by monkeypatching DB_FILE and disabling seeding."""
    db_path = tmp_path / "temp.db"
    # Disable seeding for isolated tests
    monkeypatch.setattr(seed_data, "seed_all_tables", lambda conn: None, raising=False)
    monkeypatch.setattr(db_module, "DB_FILE", str(db_path), raising=False)
    # Re-init DB on this path
    db_module.init_db()
    yield db_path
    try:
        db_path.unlink(missing_ok=True)
    except Exception:
        pass
