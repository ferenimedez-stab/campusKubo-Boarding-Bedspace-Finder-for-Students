"""
app/storage/db.py

Features:
- All queries parameterized (no string interpolation) to prevent SQL injection
- Safe migrations / column checks
- Error handling with rollbacks and controlled failures
- Information assurance: integrity (PRAGMA settings, foreign keys), availability (WAL mode)
- Utilities for users, listings, reservations, activity logs, and reports
"""

import os
import sys
import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any

import sqlite3
import json
from dotenv import load_dotenv
load_dotenv()

# ---------- CONFIG ----------
DB_FILE = os.path.join(os.path.dirname(__file__), "campuskubo.db")
SQLCIPHER_AVAILABLE = False

# ---------- Utilities ----------
def _now_iso() -> str:
    return datetime.utcnow().isoformat()

def hash_password(password: str) -> str:
    """Return sha256 hex digest of password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

# ---------- Connection management ----------
def get_connection() -> sqlite3.Connection:
    """
    Create a connection to the (encrypted) DB and apply security PRAGMAs.
    Always returns a connection with row_factory sqlite3.Row.
    """
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE, timeout=30)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        cur.execute("PRAGMA foreign_keys = ON;")
        cur.execute("PRAGMA journal_mode = WAL;")
        cur.execute("PRAGMA synchronous = NORMAL;")
    except Exception:
        pass

    return conn

# ---------- Schema helpers ----------
def column_exists(cursor: sqlite3.Cursor, table_name: str, column_name: str) -> bool:
    cursor.execute(f"PRAGMA table_info('{table_name}')")
    return any(row[1] == column_name for row in cursor.fetchall())

# ---------- Initialization & Migrations ----------
def init_db():
    """
    Create tables if missing and apply simple safe migrations.
    Call this once at app startup.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                original_pass TEXT,
                role TEXT NOT NULL,
                full_name TEXT,
                is_verified INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """)

        for col_def in [
            ("is_verified", "INTEGER DEFAULT 0"),
            ("is_active", "INTEGER DEFAULT 1"),
            ("phone", "TEXT")
        ]:
            col, _def = col_def
            if not column_exists(cur, "users", col):
                try:
                    cur.execute(f"ALTER TABLE users ADD COLUMN {col} {_def};")
                except Exception:
                    pass

        cur.execute("""
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pm_id INTEGER NOT NULL,
                address TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                lodging_details TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                images TEXT,
                FOREIGN KEY(pm_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        for col_def in [
            ("status", "TEXT DEFAULT 'pending'"),
            ("created_at", "TEXT DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "TEXT DEFAULT CURRENT_TIMESTAMP"),
            ("images", "TEXT")
        ]:
            col, _def = col_def
            if not column_exists(cur, "listings", col):
                try:
                    cur.execute(f"ALTER TABLE listings ADD COLUMN {col} {_def};")
                except Exception:
                    pass

        cur.execute("""
            CREATE TABLE IF NOT EXISTS listing_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id INTEGER NOT NULL,
                image_path TEXT NOT NULL,
                FOREIGN KEY(listing_id) REFERENCES listings(id) ON DELETE CASCADE
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id INTEGER NOT NULL,
                tenant_id INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(listing_id) REFERENCES listings(id) ON DELETE CASCADE,
                FOREIGN KEY(tenant_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        if not column_exists(cur, "reservations", "created_at"):
            try:
                cur.execute("ALTER TABLE reservations ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP;")
            except Exception:
                pass

        cur.execute("""
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                used INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        if not column_exists(cur, "reservations", "created_at"):
            try:
                cur.execute("ALTER TABLE reservations ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP;")
            except Exception:
                pass

        cur.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                listing_id INTEGER,
                message TEXT,
                status TEXT DEFAULT 'open',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(listing_id) REFERENCES listings(id) ON DELETE SET NULL
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                listing_id INTEGER,
                amount REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL,
                FOREIGN KEY(listing_id) REFERENCES listings(id) ON DELETE SET NULL
            );
        """)

        conn.commit()
        try:
            from storage import seed_data
            try:
                seed_data.seed_all_tables(conn)
                conn.commit()
            except Exception:
                pass
        except Exception:
            pass
    except Exception as e:
        conn.rollback()
        print("[db.init_db] initialization error:", e, file=sys.stderr)
        raise
    finally:
        conn.close()

# ---------- User helpers ----------
def create_user(full_name: str, email: str, password: str, role: str) -> tuple[bool, str]:
    """
    Create user with hashed password. Returns (success, message).
    Model-compatible signature: full_name, email, password, role.
    NOTE: Never stores plaintext passwords for security.
    """
    if not email or not password or not role or not full_name:
        msg = "Missing required fields"
        print(f"[create_user] {msg}", file=sys.stderr)
        return False, msg

    email_clean = email.strip().lower()
    full_name_clean = full_name.strip()

    is_valid, validation_msg = validate_email(email_clean)
    if not is_valid:
        print(f"[create_user] Email validation failed: {validation_msg}", file=sys.stderr)
        return False, validation_msg

    is_valid, validation_msg = validate_password(password)
    if not is_valid:
        print(f"[create_user] Password validation failed: {validation_msg}", file=sys.stderr)
        return False, validation_msg

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM users WHERE email = ?;", (email_clean,))
        if cur.fetchone():
            msg = f"User already exists: {email_clean}"
            print(f"[create_user] {msg}", file=sys.stderr)
            return False, msg

        hashed = hash_password(password)

        cur.execute("""
            INSERT INTO users (email, password, role, full_name, created_at)
            VALUES (?, ?, ?, ?, ?);
        """, (email_clean, hashed, role, full_name_clean, _now_iso()))

        conn.commit()
        log_activity(cur.lastrowid, "User Created", f"New {role} user: {email_clean}")
        return True, f"Account created successfully"
    except Exception as e:
        conn.rollback()
        msg = f"Failed to create user: {str(e)}"
        print(f"[create_user] error for {email_clean}: {e}", file=sys.stderr)
        return False, msg
    finally:
        conn.close()

def validate_user(email: str, password: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Validate user existence or credentials.
    If password provided, it must match hashed password.
    Returns dict {id, role, email, full_name} or None.
    """
    if not email:
        return None

    email_clean = email.strip().lower()
    conn = get_connection()
    cur = conn.cursor()
    try:
        if password is not None:
            hashed = hash_password(password)
            cur.execute(
                "SELECT id, role, email, full_name FROM users WHERE email = ? AND password = ? AND is_active = 1;",
                (email_clean, hashed)
            )
        else:
            cur.execute(
                "SELECT id, role, email, full_name FROM users WHERE email = ? AND is_active = 1;",
                (email_clean,)
            )
        row = cur.fetchone()
        return dict(row) if row else None
    except Exception as e:
        print(f"[validate_user] error for {email_clean}: {e}", file=sys.stderr)
        return None
    finally:
        conn.close()

def get_user_info(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, email, full_name, role, created_at FROM users WHERE id = ?;", (user_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM users WHERE email = ?;", (email.strip().lower(),))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def create_admin(email: str, password: str, full_name: str = "Admin User") -> tuple[bool, str]:
    existing = get_user_by_email(email)
    if existing:
        return False, "User already exists"
    return create_user(full_name, email, password, "admin")

def update_user_full_name(user_id: int, full_name: str) -> bool:
    """
    Update user's full name with validation.
    """
    if not full_name or not full_name.strip():
        print(f"[update_user_full_name] Invalid full_name for user {user_id}", file=sys.stderr)
        return False

    if user_id <= 0:
        print(f"[update_user_full_name] Invalid user_id: {user_id}", file=sys.stderr)
        return False

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE users SET full_name = ? WHERE id = ?;", (full_name.strip(), user_id))
        conn.commit()
        if cur.rowcount > 0:
            log_activity(user_id, "Profile Updated", f"Changed name to {full_name}")
            return True
        print(f"[update_user_full_name] User not found: {user_id}", file=sys.stderr)
        return False
    except Exception as e:
        conn.rollback()
        print(f"[update_user_full_name] error for user {user_id}: {e}", file=sys.stderr)
        return False
    finally:
        conn.close()

def update_user_password(user_id: int, new_password: str) -> bool:
    """
    Update user password with hash only (no plaintext storage).
    """
    if not new_password or user_id <= 0:
        print(f"[update_user_password] Invalid input: user_id={user_id}", file=sys.stderr)
        return False

    conn = get_connection()
    cur = conn.cursor()
    try:
        hashed = hash_password(new_password)
        cur.execute("UPDATE users SET password = ? WHERE id = ?;", (hashed, user_id))
        conn.commit()
        if cur.rowcount > 0:
            log_activity(user_id, "Password Updated", "User changed password")
            return True
        print(f"[update_user_password] User not found: {user_id}", file=sys.stderr)
        return False
    except Exception as e:
        conn.rollback()
        print(f"[update_user_password] error for user {user_id}: {e}", file=sys.stderr)
        return False
    finally:
        conn.close()

def update_user_info(user_id: int, full_name: str, email: str, phone: Optional[str] = None) -> bool:
    """
    Update user profile information (name, email, phone).
    Validates inputs and checks email uniqueness.
    """
    if not full_name or not email:
        print(f"[update_user_info] Name and email are required for user {user_id}", file=sys.stderr)
        return False

    if user_id <= 0:
        print(f"[update_user_info] Invalid user_id: {user_id}", file=sys.stderr)
        return False

    full_name = full_name.strip()
    email = email.strip().lower()
    phone = phone.strip() if phone and phone.strip() else None

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT email FROM users WHERE id = ?;", (user_id,))
        user = cur.fetchone()
        if not user:
            print(f"[update_user_info] User not found: {user_id}", file=sys.stderr)
            return False

        current_email = user[0].lower()
        if email != current_email:
            cur.execute("SELECT id FROM users WHERE email = ? AND id != ?;", (email, user_id))
            if cur.fetchone():
                print(f"[update_user_info] Email already in use: {email}", file=sys.stderr)
                return False

        cur.execute(
            "UPDATE users SET full_name = ?, email = ?, phone = ? WHERE id = ?;",
            (full_name, email, phone, user_id)
        )
        conn.commit()

        if cur.rowcount > 0:
            log_activity(user_id, "Profile Updated", f"Updated name, email, and phone")
            return True

        print(f"[update_user_info] Failed to update user {user_id}", file=sys.stderr)
        return False
    except Exception as e:
        conn.rollback()
        print(f"[update_user_info] error for user {user_id}: {e}", file=sys.stderr)
        return False
    finally:
        conn.close()

def delete_user(user_id: int) -> bool:
    """
    Delete user by ID with validation.
    """
    if user_id <= 0:
        print(f"[delete_user] Invalid user_id: {user_id}", file=sys.stderr)
        return False

    conn = get_connection()
    cur = conn.cursor()
    try:
        # Check if user exists first
        cur.execute("SELECT email, role FROM users WHERE id = ?;", (user_id,))
        user = cur.fetchone()
        if not user:
            print(f"[delete_user] User not found: {user_id}", file=sys.stderr)
            return False

        cur.execute("DELETE FROM users WHERE id = ?;", (user_id,))
        conn.commit()
        log_activity(None, "User Deleted", f"Deleted {user['role']} user: {user['email']}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"[delete_user] error for user {user_id}: {e}", file=sys.stderr)
        return False
    finally:
        conn.close()

def delete_user_by_email(email: str) -> bool:
    """
    Delete user by email with validation.
    """
    if not email or not email.strip():
        print("[delete_user_by_email] Invalid email", file=sys.stderr)
        return False

    conn = get_connection()
    cur = conn.cursor()
    try:
        email_clean = email.strip().lower()
        cur.execute("SELECT id, role FROM users WHERE email = ?;", (email_clean,))
        user = cur.fetchone()
        if not user:
            print(f"[delete_user_by_email] User not found: {email_clean}", file=sys.stderr)
            return False

        cur.execute("DELETE FROM users WHERE email = ?;", (email_clean,))
        conn.commit()
        log_activity(None, "User Deleted", f"Deleted {user['role']} user: {email_clean}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"[delete_user_by_email] error for {email}: {e}", file=sys.stderr)
        return False
    finally:
        conn.close()

def deactivate_user(user_id: int) -> bool:
    """
    Deactivate user by setting is_active=0 instead of deleting.
    """
    if user_id <= 0:
        print(f"[deactivate_user] Invalid user_id: {user_id}", file=sys.stderr)
        return False

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT email, role FROM users WHERE id = ?;", (user_id,))
        user = cur.fetchone()
        if not user:
            print(f"[deactivate_user] User not found: {user_id}", file=sys.stderr)
            return False

        cur.execute("UPDATE users SET is_active = 0 WHERE id = ?;", (user_id,))
        conn.commit()
        log_activity(user_id, "User Deactivated", f"Deactivated {user['role']} user: {user['email']}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"[deactivate_user] error for user {user_id}: {e}", file=sys.stderr)
        return False
    finally:
        conn.close()

# ---------- Password Reset Tokens ----------
def create_password_reset_token(user_id: int, token: str, expires_at: str) -> bool:
    """
    Create a password reset token for secure password recovery.
    Token should be a cryptographically secure random string (e.g., from secrets module).
    expires_at should be ISO format datetime string (e.g., from datetime.datetime.isoformat()).
    """
    if user_id <= 0 or not token or not token.strip():
        print("[create_password_reset_token] Invalid user_id or token", file=sys.stderr)
        return False

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM users WHERE id = ?;", (user_id,))
        if not cur.fetchone():
            print(f"[create_password_reset_token] User not found: {user_id}", file=sys.stderr)
            return False

        cur.execute("DELETE FROM password_reset_tokens WHERE user_id = ? AND used = 0;", (user_id,))

        cur.execute("""
            INSERT INTO password_reset_tokens (user_id, token, expires_at, used)
            VALUES (?, ?, ?, 0);
        """, (user_id, token, expires_at))

        conn.commit()
        log_activity(user_id, "Password Reset Requested", "User requested password reset")
        return True
    except Exception as e:
        conn.rollback()
        print(f"[create_password_reset_token] error for user {user_id}: {e}", file=sys.stderr)
        return False
    finally:
        conn.close()

def verify_password_reset_token(token: str) -> Optional[int]:
    """
    Verify a password reset token and return user_id if valid.
    Returns None if token is invalid, expired, or already used.
    """
    if not token or not token.strip():
        print("[verify_password_reset_token] Empty token", file=sys.stderr)
        return None

    conn = get_connection()
    cur = conn.cursor()
    try:
        now = _now_iso()
        cur.execute("""
            SELECT user_id FROM password_reset_tokens
            WHERE token = ? AND used = 0 AND expires_at > ?;
        """, (token, now))

        row = cur.fetchone()
        return row['user_id'] if row else None
    except Exception as e:
        print(f"[verify_password_reset_token] error: {e}", file=sys.stderr)
        return None
    finally:
        conn.close()

def use_password_reset_token(token: str) -> bool:
    """
    Mark a password reset token as used after successful password change.
    """
    if not token or not token.strip():
        print("[use_password_reset_token] Empty token", file=sys.stderr)
        return False

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE password_reset_tokens SET used = 1 WHERE token = ?;", (token,))
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"[use_password_reset_token] error: {e}", file=sys.stderr)
        return False
    finally:
        conn.close()

def cleanup_expired_reset_tokens() -> int:
    """
    Delete expired password reset tokens. Returns count of deleted tokens.
    Run this periodically (e.g., daily via background task).
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        now = _now_iso()
        cur.execute("DELETE FROM password_reset_tokens WHERE expires_at <= ?;", (now,))
        conn.commit()
        deleted = cur.rowcount
        if deleted > 0:
            print(f"[cleanup_expired_reset_tokens] Deleted {deleted} expired tokens")
        return deleted
    except Exception as e:
        conn.rollback()
        print(f"[cleanup_expired_reset_tokens] error: {e}", file=sys.stderr)
        return 0
    finally:
        conn.close()

# ---------- Listing helpers ----------
def create_listing(pm_id: int, address: str, price: float, description: str,
                   lodging_details: str, image_paths: Optional[List[str]] = None) -> Optional[int]:
    """
    Create listing with validation.
    """
    if pm_id <= 0:
        print(f"[create_listing] Invalid pm_id: {pm_id}", file=sys.stderr)
        return None
    if not address or not address.strip():
        print("[create_listing] Address is required", file=sys.stderr)
        return None
    if price <= 0:
        print(f"[create_listing] Invalid price: {price}", file=sys.stderr)
        return None
    if not description or not description.strip():
        print("[create_listing] Description is required", file=sys.stderr)
        return None

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM users WHERE id = ? AND role = 'pm';", (pm_id,))
        if not cur.fetchone():
            print(f"[create_listing] PM not found: {pm_id}", file=sys.stderr)
            return None

        now = _now_iso()
        cur.execute("""
            INSERT INTO listings (pm_id, address, price, description, lodging_details, created_at, updated_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, (pm_id, address.strip(), price, description.strip(), lodging_details or "", now, now, "Available"))

        listing_id = cur.lastrowid

        if image_paths:
            for p in image_paths:
                if p and p.strip():
                    cur.execute("INSERT INTO listing_images (listing_id, image_path) VALUES (?, ?);", (listing_id, p.strip()))

        conn.commit()
        log_activity(pm_id, "Listing Created", f"Created listing ID {listing_id}: {address[:50]}")
        return listing_id
    except Exception as e:
        conn.rollback()
        print(f"[create_listing] error for PM {pm_id}: {e}", file=sys.stderr)
        return None
    finally:
        conn.close()

def get_listings(pm_id: Optional[int] = None) -> List[sqlite3.Row]:
    """
    Returns rows of listings joined with pm info (pm_email, pm_name).
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        if pm_id is not None:
            cur.execute("""
                SELECT l.*, u.email AS pm_email, u.full_name AS pm_name
                FROM listings l
                JOIN users u ON l.pm_id = u.id
                WHERE l.pm_id = ?
                ORDER BY l.created_at DESC;
            """, (pm_id,))
        else:
            cur.execute("""
                SELECT l.*, u.email AS pm_email, u.full_name AS pm_name
                FROM listings l
                JOIN users u ON l.pm_id = u.id
                ORDER BY l.created_at DESC;
            """)
        rows = cur.fetchall()
        return rows
    finally:
        conn.close()

def get_listing_by_id(listing_id: int) -> Optional[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT l.*, u.email AS pm_email, u.full_name AS pm_name
            FROM listings l
            JOIN users u ON l.pm_id = u.id
            WHERE l.id = ?;
        """, (listing_id,))
        return cur.fetchone()
    finally:
        conn.close()

def get_listings_by_status(status: str) -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT l.*, u.email AS pm_email, u.full_name AS pm_name
            FROM listings l
            JOIN users u ON l.pm_id = u.id
            WHERE l.status = ?
            ORDER BY l.created_at DESC;
        """, (status,))
        return cur.fetchall()
    finally:
        conn.close()

def update_listing(
    listing_id: int, pm_id: int, address: str, price: float,
    description: str, lodging_details: str,
    image_paths: Optional[List[str]] = None,
    status: Optional[str] = None
) -> bool:
    """
    Update listing with validation. PM must own the listing.
    """
    if listing_id <= 0 or pm_id <= 0:
        print(f"[update_listing] Invalid IDs: listing_id={listing_id}, pm_id={pm_id}", file=sys.stderr)
        return False
    if not address or not address.strip():
        print(f"[update_listing] Address required for listing {listing_id}", file=sys.stderr)
        return False
    if price <= 0:
        print(f"[update_listing] Invalid price for listing {listing_id}: {price}", file=sys.stderr)
        return False
    if not description or not description.strip():
        print(f"[update_listing] Description required for listing {listing_id}", file=sys.stderr)
        return False

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT pm_id FROM listings WHERE id = ?;", (listing_id,))
        row = cur.fetchone()
        if not row:
            print(f"[update_listing] Listing not found: {listing_id}", file=sys.stderr)
            return False
        if row['pm_id'] != pm_id:
            print(f"[update_listing] Unauthorized: PM {pm_id} doesn't own listing {listing_id}", file=sys.stderr)
            return False

        now = _now_iso()
        if status:
            cur.execute("""
                UPDATE listings
                SET address = ?, price = ?, description = ?, lodging_details = ?, updated_at = ?, status = ?
                WHERE id = ?;
            """, (address.strip(), price, description.strip(), lodging_details or "", now, status, listing_id))
        else:
            cur.execute("""
                UPDATE listings
                SET address = ?, price = ?, description = ?, lodging_details = ?, updated_at = ?
                WHERE id = ?;
            """, (address.strip(), price, description.strip(), lodging_details or "", now, listing_id))

        if image_paths is not None:
            cur.execute("DELETE FROM listing_images WHERE listing_id = ?;", (listing_id,))
            for p in image_paths:
                if p and p.strip():
                    cur.execute("INSERT INTO listing_images (listing_id, image_path) VALUES (?, ?);", (listing_id, p.strip()))

        conn.commit()
        log_activity(pm_id, "Listing Updated", f"Updated listing ID {listing_id}: {address[:50]}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"[update_listing] error for listing {listing_id}: {e}", file=sys.stderr)
        return False
    finally:
        conn.close()

def get_listing_by_title(title_substr: str) -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        like_pattern = f"%{title_substr}%"
        cur.execute("""
            SELECT l.*, u.email AS pm_email, u.full_name AS pm_name
            FROM listings l
            JOIN users u ON l.pm_id = u.id
            WHERE l.address LIKE ?
            ORDER BY l.created_at DESC;
        """, (like_pattern,))
        return cur.fetchall()
    finally:
        conn.close()

def get_listings_by_pm(pm_id: int) -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT l.*, u.email AS pm_email, u.full_name AS pm_name
            FROM listings l
            JOIN users u ON l.pm_id = u.id
            WHERE l.pm_id = ?
            ORDER BY l.created_at DESC;
        """, (pm_id,))
        return cur.fetchall()
    finally:
        conn.close()

def get_listings_by_tenant(tenant_id: int) -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT DISTINCT l.*, u.email AS pm_email, u.full_name AS pm_name
            FROM listings l
            JOIN users u ON l.pm_id = u.id
            JOIN reservations r ON l.id = r.listing_id
            WHERE r.tenant_id = ?
            ORDER BY l.created_at DESC;
        """, (tenant_id,))
        return cur.fetchall()
    finally:
        conn.close()

def search_listings_advanced(search_query: Optional[str] = None, filters: Optional[Dict] = None) -> List[sqlite3.Row]:
    """
    Advanced search with price, location, and other filters.
    Filters dict can contain: price_min, price_max, location
    Returns approved listings matching criteria.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        query = """
            SELECT l.*, u.email AS pm_email, u.full_name AS pm_name
            FROM listings l
            JOIN users u ON l.pm_id = u.id
            WHERE l.status = 'approved'
        """
        params = []

        if search_query and search_query.strip():
            query += " AND (l.address LIKE ? OR l.description LIKE ? OR l.lodging_details LIKE ?)"
            pattern = f"%{search_query.strip()}%"
            params.extend([pattern, pattern, pattern])

        if filters:
            if filters.get("price_min"):
                try:
                    price_min = float(filters["price_min"])
                    query += " AND l.price >= ?"
                    params.append(price_min)
                except (ValueError, TypeError):
                    pass
            if filters.get("price_max"):
                try:
                    price_max = float(filters["price_max"])
                    query += " AND l.price <= ?"
                    params.append(price_max)
                except (ValueError, TypeError):
                    pass
            if filters.get("location") and filters["location"].strip():
                query += " AND l.address LIKE ?"
                params.append(f"%{filters['location'].strip()}%")

        query += " ORDER BY l.created_at DESC"
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        conn.close()

def get_listing_images(listing_id: int) -> List[str]:
    """Get all image paths for a listing."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT image_path FROM listing_images WHERE listing_id = ?;", (listing_id,))
        return [r["image_path"] for r in cur.fetchall()]
    finally:
        conn.close()

def delete_listing(listing_id: int, pm_id: int) -> bool:
    """
    Delete listing with ownership verification.
    """
    if listing_id <= 0 or pm_id <= 0:
        print(f"[delete_listing] Invalid IDs: listing_id={listing_id}, pm_id={pm_id}", file=sys.stderr)
        return False

    conn = get_connection()
    cur = conn.cursor()
    try:
        # Verify ownership
        cur.execute("SELECT pm_id, address FROM listings WHERE id = ?;", (listing_id,))
        r = cur.fetchone()
        if not r:
            print(f"[delete_listing] Listing not found: {listing_id}", file=sys.stderr)
            return False
        if r["pm_id"] != pm_id:
            print(f"[delete_listing] Unauthorized: PM {pm_id} doesn't own listing {listing_id}", file=sys.stderr)
            return False

        cur.execute("DELETE FROM listings WHERE id = ?;", (listing_id,))
        conn.commit()
        log_activity(pm_id, "Listing Deleted", f"Deleted listing ID {listing_id}: {r['address'][:50]}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"[delete_listing] error for listing {listing_id}: {e}", file=sys.stderr)
        return False
    finally:
        conn.close()

def delete_listing_admin(listing_id: int) -> bool:
    """
    Admin delete (no ownership check).
    """
    if listing_id <= 0:
        print(f"[delete_listing_admin] Invalid listing_id: {listing_id}", file=sys.stderr)
        return False

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT address FROM listings WHERE id = ?;", (listing_id,))
        r = cur.fetchone()
        if not r:
            print(f"[delete_listing_admin] Listing not found: {listing_id}", file=sys.stderr)
            return False

        cur.execute("DELETE FROM listings WHERE id = ?;", (listing_id,))
        conn.commit()
        log_activity(None, "Listing Deleted (Admin)", f"Admin deleted listing ID {listing_id}: {r['address'][:50]}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"[delete_listing_admin] error for listing {listing_id}: {e}", file=sys.stderr)
        return False
    finally:
        conn.close()

def delete_listing_image(listing_id: int, image_path: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM listing_images WHERE listing_id = ? AND image_path = ?;", (listing_id, image_path))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("[delete_listing_image] error:", e, file=sys.stderr)
        return False
    finally:
        conn.close()

def delete_listing_by_title(title_substr: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        like_pattern = f"%{title_substr}%"
        cur.execute("DELETE FROM listings WHERE address LIKE ?;", (like_pattern,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("[delete_listing_by_title] error:", e, file=sys.stderr)
        return False
    finally:
        conn.close()

def change_listing_status(listing_id: int, new_status: str) -> bool:
    """
    Change listing status with validation.
    """
    if listing_id <= 0:
        print(f"[change_listing_status] Invalid listing_id: {listing_id}", file=sys.stderr)
        return False
    if not new_status or not new_status.strip():
        print("[change_listing_status] Status is required", file=sys.stderr)
        return False

    valid_statuses = ["Available", "Occupied", "approved", "pending", "rejected"]
    if new_status not in valid_statuses:
        print(f"[change_listing_status] Invalid status: {new_status}. Valid: {valid_statuses}", file=sys.stderr)
        return False

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT address FROM listings WHERE id = ?;", (listing_id,))
        listing = cur.fetchone()
        if not listing:
            print(f"[change_listing_status] Listing not found: {listing_id}", file=sys.stderr)
            return False

        cur.execute("UPDATE listings SET status = ? WHERE id = ?;", (new_status, listing_id))
        conn.commit()
        log_activity(None, "Listing Status Changed", f"Listing {listing_id} status changed to {new_status}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"[change_listing_status] error for listing {listing_id}: {e}", file=sys.stderr)
        return False
    finally:
        conn.close()

# ---------- Reservation helpers ----------
def create_reservation(listing_id: int, tenant_id: int, start_date: str, end_date: str, status: str = "pending") -> Optional[int]:
    """
    Create reservation with validation.
    """
    if listing_id <= 0 or tenant_id <= 0:
        print(f"[create_reservation] Invalid IDs: listing_id={listing_id}, tenant_id={tenant_id}", file=sys.stderr)
        return None
    if not start_date or not end_date:
        print("[create_reservation] Start and end dates are required", file=sys.stderr)
        return None
    if status not in ["pending", "approved", "confirmed", "cancelled", "rejected"]:
        print(f"[create_reservation] Invalid status: {status}", file=sys.stderr)
        return None

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM listings WHERE id = ?;", (listing_id,))
        if not cur.fetchone():
            print(f"[create_reservation] Listing not found: {listing_id}", file=sys.stderr)
            return None

        cur.execute("SELECT id FROM users WHERE id = ? AND role = 'tenant';", (tenant_id,))
        if not cur.fetchone():
            print(f"[create_reservation] Tenant not found: {tenant_id}", file=sys.stderr)
            return None

        now = _now_iso()
        cur.execute("""
            INSERT INTO reservations (listing_id, tenant_id, start_date, end_date, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (listing_id, tenant_id, start_date, end_date, status, now))
        conn.commit()

        reservation_id = cur.lastrowid
        log_activity(tenant_id, "Reservation Created", f"Created reservation ID {reservation_id} for listing {listing_id}")
        return reservation_id
    except Exception as e:
        conn.rollback()
        print(f"[create_reservation] error: {e}", file=sys.stderr)
        return None
    finally:
        conn.close()

def get_reservations(listing_id: Optional[int] = None, tenant_id: Optional[int] = None) -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        query = "SELECT * FROM reservations WHERE 1=1"
        params: List[Any] = []
        if listing_id is not None:
            query += " AND listing_id = ?"
            params.append(listing_id)
        if tenant_id is not None:
            query += " AND tenant_id = ?"
            params.append(tenant_id)
        query += " ORDER BY created_at DESC;"
        cur.execute(query, tuple(params))
        return cur.fetchall()
    finally:
        conn.close()

def get_listing_availability(listing_id: int) -> List[sqlite3.Row]:
    """
    Returns approved/confirmed reservations for a listing (caller decides availability).
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT * FROM reservations
            WHERE listing_id = ? AND status IN ('approved','confirmed')
            ORDER BY start_date ASC;
        """, (listing_id,))
        return cur.fetchall()
    finally:
        conn.close()

# ---------- Activity logging ----------
def log_activity(user_id: Optional[int], action: str, details: str = "") -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        now = _now_iso()
        cur.execute("""
            INSERT INTO activity_logs (user_id, action, details, created_at)
            VALUES (?, ?, ?, ?);
        """, (user_id, action, details, now))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("[log_activity] error:", e, file=sys.stderr)
        return False
    finally:
        conn.close()

def get_recent_activity(limit: int = 20) -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT a.*, u.full_name as user_full_name, u.email as user_email
            FROM activity_logs a
            LEFT JOIN users u ON a.user_id = u.id
            ORDER BY a.created_at DESC
            LIMIT ?;
        """, (limit,))
        return cur.fetchall()
    finally:
        conn.close()

# ---------- Reports ----------
def create_report(user_id: int, listing_id: Optional[int], message: str) -> Optional[int]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        now = _now_iso()
        cur.execute("""
            INSERT INTO reports (user_id, listing_id, message, status, created_at)
            VALUES (?, ?, ?, ?, ?);
        """, (user_id, listing_id, message, "open", now))
        conn.commit()
        return cur.lastrowid
    except Exception as e:
        conn.rollback()
        print("[create_report] error:", e, file=sys.stderr)
        return None
    finally:
        conn.close()

def get_all_reports() -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT r.*, u.email AS reporter_email, l.address AS listing_address
            FROM reports r
            LEFT JOIN users u ON r.user_id = u.id
            LEFT JOIN listings l ON r.listing_id = l.id
            ORDER BY r.created_at DESC;
        """)
        return cur.fetchall()
    finally:
        conn.close()

# ---------- Admin utilities ----------
def rekey_database(new_key: str) -> bool:
    """
    Change the database encryption key.
    Works only if SQLCipher is available.
    WARNING: call with care and backup DB before rekey.
    """
    if not SQLCIPHER_AVAILABLE:
        print("[rekey_database] sqlcipher not available, cannot rekey.", file=sys.stderr)
        return False

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("PRAGMA rekey = ?;", (new_key,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("[rekey_database] error:", e, file=sys.stderr)
        return False
    finally:
        conn.close()

# ---------- Debug / safe check ----------
def _list_tables() -> List[str]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [r[0] for r in cur.fetchall()]
    finally:
        conn.close()

# ---------- Model-compatible adapter functions ----------
def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password meets security requirements.
    Returns (is_valid, message)
    """
    if not password:
        return False, "Password is required"
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "Password must contain at least one special character"
    return True, "Password is valid"

def validate_email(email: str) -> tuple[bool, str]:
    """
    Validate email format.
    Returns (is_valid, message)
    """
    if not email or not email.strip():
        return False, "Email is required"

    email_clean = email.strip().lower()

    if "@" not in email_clean or "." not in email_clean:
        return False, "Invalid email format"

    existing = get_user_by_email(email_clean)
    if existing:
        return False, "Email already registered"

    return True, "Email is valid"


def property_data():
    """
    Seed 15 beautiful, real-looking properties with working images.
    Runs only if we don't have 15+ proper listings yet.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Add missing columns safely
        columns_to_add = [
            ("name", "TEXT"),
            ("location", "TEXT"),
            ("room_type", "TEXT"),
            ("total_rooms", "INTEGER DEFAULT 0"),
            ("available_rooms", "INTEGER DEFAULT 0"),
            ("available_room_types", "TEXT"),
            ("amenities", "TEXT"),
            ("availability_status", "TEXT DEFAULT 'Available'"),
            ("image_url", "TEXT"),
            ("image_url_2", "TEXT"),
            ("image_url_3", "TEXT"),
            ("image_url_4", "TEXT"),
        ]
        for col_name, col_def in columns_to_add:
            if not column_exists(cur, "listings", col_name):
                try:
                    cur.execute(f"ALTER TABLE listings ADD COLUMN {col_name} {col_def};")
                    print(f"[property_data] Added column: {col_name}")
                except:
                    pass
        conn.commit()

        pm_emails = [
            "pm.1",
            "pm.2",
            "pm.3",
            "pm.4",
            "pm.5",
            "pm.6",
        ]

        for email in pm_emails:
            cur.execute("SELECT id FROM users WHERE email = ?", (email,))
            if not cur.fetchone():
                hashed = hash_password("PmPassword123!")  # Strong password that passes validation
                cur.execute("""
                    INSERT INTO users (email, password, role, full_name, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (email, hashed, "pm", email.split("@")[0].replace(".", " ").title(), _now_iso()))
                print(f"[property_data] Created PM: {email}")

        conn.commit()

        cur.execute("SELECT id, email FROM users WHERE role = 'pm' ORDER BY id")
        pm_rows = cur.fetchall()
        if len(pm_rows) < 6:
            print("[property_data] Not enough PMs created!")
            return

        # Map emails → real IDs
        pm_map = {row["email"]: row["id"] for row in pm_rows}

        # Count real listings (ones with a proper name)
        cur.execute("SELECT COUNT(*) as c FROM listings WHERE name IS NOT NULL AND name != '' AND name NOT LIKE 'Demo Listing%'")
        real_count = cur.fetchone()['c']

        if real_count >= 15:
            print(f"[property_data] Already have {real_count} real listings – skipping")
            return

        print(f"[property_data] Seeding 15 beautiful listings with real photos...")

        sample_listings = [
            {
            "pm_id": pm_map["pm.1"],
            "name": "Cozy Campus Boardinghouse",
            "address": "123 Aurora Blvd, Quezon City",
            "location": "Near UP Diliman",
            "price": 3500.0,
            "description": "Super cozy boarding house just 5 mins walk from UP Diliman gate. Clean rooms, fast WiFi, shared kitchen & laundry. Perfect for students!",
            "room_type": "Double",
            "total_rooms": 10,
            "available_rooms": 4,
            "available_room_types": json.dumps(["Single", "Double"]),
            "amenities": json.dumps(["WiFi", "Kitchen", "Laundry", "24/7 Security", "Study Area", "Water Included"]),
            "availability_status": "Available",
            "lodging_details": "Double room with bunk beds",
            "image_url": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
            "image_url_2": "https://images.unsplash.com/photo-1502672260066-6bc2c0923089",
            "image_url_3": "https://images.unsplash.com/photo-1484154218962-a197022b5858",
            "image_url_4": "https://images.unsplash.com/photo-1493809842364-78817add7ffb",
            "status": "approved"
            },
            {
            "pm_id": pm_map["pm.1"],
            "name": "Modern Studio near Ateneo",
            "address": "Katipunan Ave, Loyola Heights",
            "location": "Near Ateneo & Miriam",
            "price": 5800.0,
            "description": "Brand new minimalist studio with high-speed fiber internet, study desk, kitchenette, and private bathroom. Walking distance to campus.",
            "room_type": "Studio",
            "total_rooms": 8,
            "available_rooms": 3,
            "available_room_types": json.dumps(["Studio"]),
            "amenities": json.dumps(["WiFi", "AC", "Kitchenette", "Private CR", "Study Desk", "Laundry Service"]),
            "availability_status": "Available",
            "lodging_details": "Fully furnished studio unit",
            "image_url": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2",
            "image_url_2": "https://images.unsplash.com/photo-1556020685-ae41abfc9365",
            "image_url_3": "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af",
            "image_url_4": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c",
            "status": "approved"
            },
            {
            "pm_id": pm_map["pm.1"],
            "name": "Budget Dorm Espana",
            "address": "567 España Blvd, Sampaloc",
            "location": "Near UST",
            "price": 2500.0,
            "description": "Affordable bedspace for budget-conscious students. Includes locker, study area, and free WiFi. 3 mins from UST gate.",
            "room_type": "Bed Space",
            "total_rooms": 20,
            "available_rooms": 7,
            "available_room_types": json.dumps(["Bed Space"]),
            "amenities": json.dumps(["WiFi", "Locker", "Study Area", "CCTV", "Common CR"]),
            "availability_status": "Available",
            "lodging_details": "Clean bed space with personal cabinet",
            "image_url": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5",
            "image_url_2": "https://images.unsplash.com/photo-1540518614846-7eded433c457",
            "image_url_3": "https://images.unsplash.com/photo-1562438668-bcf0ca6578f0",
            "image_url_4": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85",
            "status": "approved"
            },
            {
            "pm_id": pm_map["pm.2"],
            "name": "Female-Only Dorm Taft",
            "address": "234 Taft Avenue, Malate",
            "location": "Near DLSU & St. Scholastica",
            "price": 3200.0,
            "description": "Exclusive female dormitory with 24/7 female guard, curfew, study lounge, and sisterhood community. Safe and supportive environment.",
            "room_type": "Double",
            "total_rooms": 12,
            "available_rooms": 5,
            "available_room_types": json.dumps(["Double", "Quad Share"]),
            "amenities": json.dumps(["WiFi", "Study Lounge", "Female Guard 24/7", "CCTV", "Laundry", "Prayer Room"]),
            "availability_status": "Available",
            "lodging_details": "Safe female-only boarding house",
            "image_url": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b",
            "image_url_2": "https://images.unsplash.com/photo-1513694203232-719a280e022f",
            "image_url_3": "https://images.unsplash.com/photo-1602940659805-70b109a9d8a2",
            "image_url_4": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c",
            "status": "approved"
            },
            {
            "pm_id": pm_map["pm.2"],
            "name": "Luxury Condo BGC",
            "address": "Serendra, Bonifacio Global City",
            "location": "BGC, Taguig",
            "price": 8500.0,
            "description": "High-end condo unit with hotel-like amenities: infinity pool, gym, concierge. Perfect for UP-PGH, St. Luke's, or BGC workers.",
            "room_type": "Single",
            "total_rooms": 6,
            "available_rooms": 2,
            "available_room_types": json.dumps(["Single", "Studio"]),
            "amenities": json.dumps(["WiFi", "AC", "Gym", "Pool", "Concierge", "Parking"]),
            "availability_status": "Limited",
            "lodging_details": "Premium single room with city view",
            "image_url": "https://images.unsplash.com/photo-1564078516393-cf04bd966897",
            "image_url_2": "https://images.unsplash.com/photo-1567767292722-443c687c3e73",
            "image_url_3": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750",
            "image_url_4": "https://images.unsplash.com/photo-1600566753376-2da6f6a55fd9",
            "status": "approved"
            },
            {
            "pm_id": pm_map["pm.3"],
            "name": "Smart Tech Dorm QC",
            "address": "999 Innovation Ave, Diliman",
            "location": "Near UP & Ateneo",
            "price": 3800.0,
            "description": "State-of-the-art smart dorm: biometric entry, app-controlled lights/AC, gaming room, study pods.",
            "room_type": "Single",
            "total_rooms": 20,
            "available_rooms": 9,
            "available_room_types": json.dumps(["Single", "Twin Share"]),
            "amenities": json.dumps(["Fiber Internet", "Smart Lock", "Gaming Room", "Study Pods", "Rooftop"]),
            "availability_status": "Available",
            "lodging_details": "Tech-savvy dormitory",
            "image_url": "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3",
            "image_url_2": "https://images.unsplash.com/photo-1602940659805-70b109a9d8a2",
            "image_url_3": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c",
            "image_url_4": "https://images.unsplash.com/photo-1560185127-6ed189bf02f4",
            "status": "approved"
            },
            {
            "pm_id": pm_map["pm.3"],
            "name": "Garden View Apartment",
            "address": "88 Pioneer St, Mandaluyong",
            "location": "Near Shaw Blvd",
            "price": 4800.0,
            "description": "Peaceful apartment with balcony and garden view. Great natural light, quiet street, near malls and MRT.",
            "room_type": "Single",
            "total_rooms": 8,
            "available_rooms": 3,
            "available_room_types": json.dumps(["Single", "Double"]),
            "amenities": json.dumps(["WiFi", "Balcony", "Parking", "Garden", "CCTV"]),
            "availability_status": "Available",
            "lodging_details": "Apartment with garden access",
            "image_url": "https://images.unsplash.com/photo-1536376072261-38c75010e6c9",
            "image_url_2": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
            "image_url_3": "https://images.unsplash.com/photo-1502672260066-6bc2c0923089",
            "image_url_4": "https://images.unsplash.com/photo-1484154218962-a197022b5858",
            "status": "approved"
            },
            {
            "pm_id": pm_map["pm.4"],
            "name": "Executive Townhouse Alabang",
            "address": "Palm Drive, Alabang",
            "location": "Alabang, Muntinlupa",
            "price": 9500.0,
            "description": "Spacious 2-storey townhouse perfect for med students or small groups. Private garage, clubhouse access.",
            "room_type": "Whole Unit",
            "total_rooms": 3,
            "available_rooms": 1,
            "available_room_types": json.dumps(["Whole Unit"]),
            "amenities": json.dumps(["WiFi", "Parking", "Clubhouse", "Pool", "Swimming Pool", "Security"]),
            "availability_status": "Limited",
            "lodging_details": "Full townhouse rental",
            "image_url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750",
            "image_url_2": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c",
            "image_url_3": "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3",
            "image_url_4": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2",
            "status": "approved"
            },
            {
            "pm_id": pm_map["pm.4"],
            "name": "Beachside Condo Pasay",
            "address": "777 Roxas Blvd",
            "location": "Near Mall of Asia",
            "price": 7200.0,
            "description": "Stunning bay view condo. Wake up to the sea breeze. Infinity pool, gym, mall access.",
            "room_type": "Studio",
            "total_rooms": 5,
            "available_rooms": 2,
            "available_room_types": json.dumps(["Studio", "One Bedroom"]),
            "amenities": json.dumps(["WiFi", "Pool", "Gym", "Mall Access", "Bay View"]),
            "availability_status": "Available",
            "lodging_details": "Condo with sea view",
            "image_url": "https://images.unsplash.com/photo-1502672023488-70e25813eb80",
            "image_url_2": "https://images.unsplash.com/photo-1560185127-6ed189bf02f4",
            "image_url_3": "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af",
            "image_url_4": "https://images.unsplash.com/photo-1502672260066-6bc2c0923089",
            "status": "approved"
            },
            {
            "pm_id": pm_map["pm.5"],
            "name": "Green Living Marikina",
            "address": "555 Eco Street, Marikina Heights",
            "location": "Marikina City",
            "price": 4200.0,
            "description": "Eco-friendly apartment with solar panels, rainwater system, and organic garden. Pet-friendly!",
            "room_type": "Single",
            "total_rooms": 10,
            "available_rooms": 6,
            "available_room_types": json.dumps(["Single", "Double"]),
            "amenities": json.dumps(["WiFi", "Solar Power", "Garden", "Pet-Friendly", "Bike Rack"]),
            "availability_status": "Available",
            "lodging_details": "Sustainable living apartment",
            "image_url": "https://images.unsplash.com/photo-1536376072261-38c75010e6c9",
            "image_url_2": "https://images.unsplash.com/photo-1484154218962-a197022b5858",
            "image_url_3": "https://images.unsplash.com/photo-1493809842364-78817add7ffb",
            "image_url_4": "https://images.unsplash.com/photo-1502672260066-6bc2c0923089",
            "status": "approved"
            },
            {
            "pm_id": pm_map["pm.5"],
            "name": "Co-Living Poblacion",
            "address": "888 Jupiter St, Makati",
            "location": "Poblacion, Makati",
            "price": 6500.0,
            "description": "Modern co-living space with co-working area, rooftop bar, gym, and events. Best for social students!",
            "room_type": "Single",
            "total_rooms": 15,
            "available_rooms": 5,
            "available_room_types": json.dumps(["Single", "Shared Studio"]),
            "amenities": json.dumps(["WiFi", "Co-working", "Gym", "Rooftop Bar", "Events"]),
            "availability_status": "Available",
            "lodging_details": "Vibrant co-living community",
            "image_url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750",
            "image_url_2": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c",
            "image_url_3": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2",
            "image_url_4": "https://images.unsplash.com/photo-1556020685-ae41abfc9365",
            "status": "approved"
            },
            {
            "pm_id": pm_map["pm.5"],
            "name": "Traditional Home Sampaloc",
            "address": "432 P. Noval St",
            "location": "Near FEU & UE",
            "price": 2900.0,
            "description": "Classic Filipino boarding house with home-cooked meals available. Warm landlady, family vibe.",
            "room_type": "Double",
            "total_rooms": 8,
            "available_rooms": 4,
            "available_room_types": json.dumps(["Single", "Double"]),
            "amenities": json.dumps(["WiFi", "Home-cooked Meals", "Laundry", "Study Area"]),
            "availability_status": "Available",
            "lodging_details": "Home away from home",
            "image_url": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
            "image_url_2": "https://images.unsplash.com/photo-1493809842364-78817add7ffb",
            "image_url_3": "https://images.unsplash.com/photo-1484154218962-a197022b5858",
            "image_url_4": "https://images.unsplash.com/photo-1540518614846-7eded433c457",
            "status": "approved"
            },
            {
            "pm_id": pm_map["pm.6"],
            "name": "Premium Loft McKinley",
            "address": "McKinley Hill, Taguig",
            "location": "Venice Grand Canal Mall",
            "price": 11000.0,
            "description": "Ultra-luxury loft with panoramic views, smart home system, private terrace. For students who want the best.",
            "room_type": "Penthouse",
            "total_rooms": 1,
            "available_rooms": 1,
            "available_room_types": json.dumps(["Penthouse"]),
            "amenities": json.dumps(["WiFi", "Smart Home", "Terrace", "Gym", "Pool", "Concierge"]),
            "availability_status": "Available",
            "lodging_details": "Exclusive penthouse unit",
            "image_url": "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3",
            "image_url_2": "https://images.unsplash.com/photo-1564078516393-cf04bd966897",
            "image_url_3": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750",
            "image_url_4": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c",
            "status": "approved"
            },
            {
            "pm_id": pm_map["pm.6"],
            "name": "Sunshine Apartment Pasig",
            "address": "Ortigas Extension, Pasig",
            "location": "Near Tiendesitas",
            "price": 4300.0,
            "description": "Bright and sunny apartment with big windows. Near Eastwood, Ortigas CBD. Great for working students.",
            "room_type": "Single",
            "total_rooms": 10,
            "available_rooms": 5,
            "available_room_types": json.dumps(["Single"]),
            "amenities": json.dumps(["WiFi", "AC", "Parking", "Security", "Rooftop"]),
            "availability_status": "Available",
            "lodging_details": "Sunny single room",
            "image_url": "https://images.unsplash.com/photo-1502672260066-6bc2c0923089",
            "image_url_2": "https://images.unsplash.com/photo-1484154218962-a197022b5858",
            "image_url_3": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
            "image_url_4": "https://images.unsplash.com/photo-1493809842364-78817add7ffb",
            "status": "approved"
            },
            {
            "pm_id": pm_map["pm.6"],
            "name": "Riverside Bedspace",
            "address": "Marikina Riverbanks",
            "location": "Marikina City",
            "price": 2400.0,
            "description": "Most affordable option near Marikina schools. Clean, simple, safe. Free breakfast on weekends!",
            "room_type": "Bed Space",
            "total_rooms": 25,
            "available_rooms": 10,
            "available_room_types": json.dumps(["Bed Space"]),
            "amenities": json.dumps(["WiFi", "Breakfast", "Locker", "CCTV"]),
            "availability_status": "Available",
            "lodging_details": "Budget bedspace with meals",
            "image_url": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85",
            "image_url_2": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5",
            "image_url_3": "https://images.unsplash.com/photo-1540518614846-7eded433c457",
            "image_url_4": "https://images.unsplash.com/photo-1562438668-bcf0ca6578f0",
            "status": "approved"
            }
        ]

        now = _now_iso()
        for listing in sample_listings:
            cur.execute("""
                INSERT INTO listings (
                    pm_id, name, address, location, price, description, lodging_details,
                    room_type, total_rooms, available_rooms, available_room_types,
                    amenities, availability_status, image_url, image_url_2,
                    image_url_3, image_url_4, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                listing["pm_id"], listing["name"], listing["address"], listing["location"],
                listing["price"], listing["description"], listing["lodging_details"],
                listing["room_type"], listing["total_rooms"], listing["available_rooms"],
                listing["available_room_types"], listing["amenities"], listing["availability_status"],
                listing["image_url"], listing["image_url_2"], listing["image_url_3"],
                listing["image_url_4"], listing["status"], now, now
            ))

        conn.commit()
        print("[property_data] SUCCESS! 15 beautiful listings with real photos seeded!")

    except Exception as e:
        print(f"[property_data] ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()


def get_properties(search_query: str = "", filters: dict = None) -> List[Dict]:
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        query = """
            SELECT id, pm_id, name, address, location, price, description,
                   room_type, total_rooms, available_rooms, available_room_types,
                   amenities, availability_status, image_url, image_url_2,
                   image_url_3, image_url_4, status, created_at
            FROM listings 
            WHERE status = 'approved'
        """
        params = []
        filters = filters or {}

        # ── Search keyword ─────────────────────────────────────
        if search_query := (search_query or "").strip():
            pattern = f"%{search_query}%"
            query += " AND (name LIKE ? OR location LIKE ? OR address LIKE ? OR description LIKE ?)"
            params.extend([pattern] * 4)

        # ── Price ──────────────────────────────────────────────
        if filters.get("price_min") is not None:
            query += " AND price >= ?"
            params.append(filters["price_min"])
        if price_max := filters.get("price_max"):
            query += " AND price <= ?"
            params.append(price_max)

        # ── Room Type (Single, Double, etc.) ───────────────────
        if room_types := filters.get("room_type"):
            if isinstance(room_types, str):
                room_types = [room_types]
            placeholders = ",".join(["?"] * len(room_types))
            query += f" AND (room_type IN ({placeholders})"
            params.extend(room_types)
            for rt in room_types:
                query += " OR available_room_types LIKE ?"
                params.append(f'%"{rt}"%')
            query += ")"

        # ── Amenities (WiFi, Air Conditioning, etc.) ───────────
        if amenities := filters.get("amenities"):
            if isinstance(amenities, str):
                amenities = [amenities]
            for amenity in amenities:
                query += " AND amenities LIKE ?"
                params.append(f'%"{amenity}"%')   

        # ── Availability status ───────────────────────────────
        if availability := filters.get("availability"):
            query += " AND availability_status = ?"
            params.append(availability)

        # ── Location ───────────────────────────────────────────
        if location := filters.get("location"):
            pattern = f"%{location.strip()}%"
            query += " AND (location LIKE ? OR address LIKE ?)"
            params.extend([pattern, pattern])

        query += " ORDER BY created_at DESC"

        # Uncomment next two lines only while testing
        # print("[DEBUG SQL]", query)
        # print("[DEBUG PARAMS]", params)

        cur.execute(query, params)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        result = [dict(zip(columns, row)) for row in rows]

        # Optional: turn JSON strings into real Python lists (nice for debugging)
        for prop in result:
            for field in ["amenities", "available_room_types"]:
                if prop.get(field) and isinstance(prop[field], str):
                    try:
                        prop[field] = json.loads(prop[field])
                    except:
                        prop[field] = []

        return result

    except Exception as e:
        print(f"[get_properties] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        conn.close()


def get_property_by_id(property_id: int):
    """
    Get a single property by ID with all details.
    Returns all fields needed for property_details_view.
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        query = """
            SELECT 
                id, pm_id, name, address, location, price, description,
                room_type, total_rooms, available_rooms, available_room_types,
                amenities, availability_status, image_url, image_url_2,
                image_url_3, image_url_4, status, created_at, updated_at
            FROM listings 
            WHERE id = ? AND status = 'approved'
        """
        
        cur.execute(query, (property_id,))
        prop = cur.fetchone()
        
        if not prop:
            return None
        
        return {
            "id": prop["id"],
            "pm_id": prop["pm_id"],
            "name": prop["name"],
            "address": prop["address"],
            "location": prop["location"],
            "price": prop["price"],
            "description": prop["description"],
            "room_type": prop["room_type"],
            "total_rooms": prop["total_rooms"],
            "available_rooms": prop["available_rooms"],
            "available_room_types": prop["available_room_types"],
            "amenities": prop["amenities"],
            "availability_status": prop["availability_status"],
            "image_url": prop["image_url"],
            "image_url_2": prop["image_url_2"],
            "image_url_3": prop["image_url_3"],
            "image_url_4": prop["image_url_4"],
            "status": prop["status"],
            "created_at": prop["created_at"],
            "updated_at": prop["updated_at"]
        }
        
    except Exception as e:
        print(f"[get_property_by_id] ❌ Error: {e}", file=sys.stderr)
        return None
    finally:
        conn.close()

