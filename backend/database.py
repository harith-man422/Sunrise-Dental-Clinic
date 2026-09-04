"""
Sunrise Dental Clinic — SQLite database setup and connection.

Creates the clinic.db file on first run, defines the schema,
and seeds initial data (admin user + sample appointment).
"""

import sqlite3
import hashlib
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "clinic.db")


def get_connection():
    """Return a new SQLite connection with row-factory enabled."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row          # rows behave like dicts
    conn.execute("PRAGMA journal_mode=WAL")  # safer concurrent reads
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def hash_password(password: str) -> str:
    """SHA-256 hash for password storage."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_db():
    """Create tables (if missing), migrate columns, and insert seed data."""
    conn = get_connection()
    cursor = conn.cursor()

    # ── Staff users table ────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            username       TEXT    NOT NULL UNIQUE,
            password_hash  TEXT    NOT NULL,
            password_plain TEXT    NOT NULL DEFAULT '',
            role           TEXT    NOT NULL DEFAULT 'staff',
            created_at     TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Check if existing table needs column migration
    cursor.execute("PRAGMA table_info(staff)")
    columns = [row["name"] for row in cursor.fetchall()]
    if "password_plain" not in columns:
        cursor.execute("ALTER TABLE staff ADD COLUMN password_plain TEXT NOT NULL DEFAULT ''")
    if "role" not in columns:
        cursor.execute("ALTER TABLE staff ADD COLUMN role TEXT NOT NULL DEFAULT 'staff'")
    if "created_at" not in columns:
        cursor.execute("ALTER TABLE staff ADD COLUMN created_at TEXT DEFAULT '2026-01-01'")

    # ── Appointments table ───────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_no    TEXT    NOT NULL UNIQUE,
            patient_name      TEXT    NOT NULL,
            address           TEXT    NOT NULL,
            contact_number    TEXT    NOT NULL,
            dentist_name      TEXT    NOT NULL,
            treatment_type    TEXT    NOT NULL,
            appointment_date  TEXT    NOT NULL,
            appointment_time  TEXT    NOT NULL,
            is_billed         INTEGER DEFAULT 0,
            billed_at         TEXT    DEFAULT NULL,
            created_at        TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Check if existing appointments table needs column migration
    cursor.execute("PRAGMA table_info(appointments)")
    columns = [row["name"] for row in cursor.fetchall()]
    if "is_billed" not in columns:
        cursor.execute("ALTER TABLE appointments ADD COLUMN is_billed INTEGER DEFAULT 0")
    if "billed_at" not in columns:
        cursor.execute("ALTER TABLE appointments ADD COLUMN billed_at TEXT DEFAULT NULL")
    if "created_at" not in columns:
        cursor.execute("ALTER TABLE appointments ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP")


    # Unique index to prevent double-booking (same dentist, date, time)
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_no_double_booking
        ON appointments (dentist_name, appointment_date, appointment_time)
    """)

    # ── Seed data ────────────────────────────────────────────────────
    # Admin user
    cursor.execute("SELECT id FROM staff WHERE username = ?", ("admin",))
    admin_row = cursor.fetchone()
    if admin_row is None:
        cursor.execute(
            """INSERT INTO staff (username, password_hash, password_plain, role)
               VALUES (?, ?, ?, ?)""",
            ("admin", hash_password("Clinic@123"), "Clinic@123", "admin"),
        )
    else:
        # Ensure password_plain is set for admin
        cursor.execute(
            """UPDATE staff SET password_plain = ?, role = 'admin'
               WHERE username = 'admin' AND (password_plain IS NULL OR password_plain = '')""",
            ("Clinic@123",),
        )

    # Sample appointment
    try:
        cursor.execute(
            """INSERT INTO appointments
               (appointment_no, patient_name, address, contact_number,
                dentist_name, treatment_type, appointment_date, appointment_time)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "A1001",
                "Nimal Perera",
                "45 Galle Road, Colombo 06",
                "0771234567",
                "Dr. Silva",
                "Scaling",
                "2026-09-10",
                "10:30",
            ),
        )
    except sqlite3.IntegrityError:
        pass  # sample already exists

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialised at {DATABASE_PATH}")
