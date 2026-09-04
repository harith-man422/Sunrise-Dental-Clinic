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
    """SHA-256 hash for password storage (adequate for a clinic demo)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_db():
    """Create tables (if missing) and insert seed data."""
    conn = get_connection()
    cursor = conn.cursor()

    # ── Staff users table ────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL
        )
    """)

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
            appointment_time  TEXT    NOT NULL
        )
    """)

    # Unique index to prevent double-booking (same dentist, date, time)
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_no_double_booking
        ON appointments (dentist_name, appointment_date, appointment_time)
    """)

    # ── Seed data ────────────────────────────────────────────────────
    # Admin user
    try:
        cursor.execute(
            "INSERT INTO staff (username, password_hash) VALUES (?, ?)",
            ("admin", hash_password("Clinic@123")),
        )
    except sqlite3.IntegrityError:
        pass  # admin already exists

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
