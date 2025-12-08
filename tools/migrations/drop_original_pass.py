"""
Idempotent migration: drop `original_pass` column from `users` table if present.
This script safely recreates the `users` table without the `original_pass` column
and copies existing data. Run once during maintenance.
"""
import sqlite3
import sys
import os


def _db_path():
    # project root relative path to app/storage/campuskubo.db
    root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
    return os.path.join(root, 'app', 'storage', 'campuskubo.db')


def column_exists(cursor: sqlite3.Cursor, table_name: str, column_name: str) -> bool:
    cursor.execute(f"PRAGMA table_info('{table_name}')")
    return any(row[1] == column_name for row in cursor.fetchall())


def drop_original_pass():
    dbfile = _db_path()
    conn = sqlite3.connect(dbfile)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        if not column_exists(cur, 'users', 'original_pass'):
            print('No original_pass column found. Nothing to do.')
            return 0

        print('original_pass column found - performing migration...')
        # Turn off foreign keys during table rebuild
        cur.execute('PRAGMA foreign_keys=OFF;')
        conn.commit()

        # Create a new temporary table with desired schema (no original_pass)
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT,
                is_verified INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                phone TEXT,
                created_at TEXT
            );
        ''')
        # Copy data over (skip original_pass)
        cur.execute('''
            INSERT INTO users_new (id, email, password, role, full_name, is_verified, is_active, phone, created_at)
            SELECT id, email, password, role, full_name, is_verified, is_active, phone, created_at FROM users;
        ''')

        # Drop old table and rename new
        cur.execute('DROP TABLE users;')
        cur.execute('ALTER TABLE users_new RENAME TO users;')

        conn.commit()
        print('Migration completed: original_pass dropped.')
        return 0
    except Exception as e:
        conn.rollback()
        print('Migration failed:', e, file=sys.stderr)
        return 1
    finally:
        # Re-enable foreign keys
        try:
            cur.execute('PRAGMA foreign_keys=ON;')
            conn.commit()
        except Exception:
            pass
        conn.close()


if __name__ == '__main__':
    sys.exit(drop_original_pass())
