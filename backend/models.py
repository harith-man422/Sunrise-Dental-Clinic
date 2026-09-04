"""
Sunrise Dental Clinic — Data access functions.

All database interaction goes through here.
Each function opens its own connection and returns plain dicts
(or raises ValueError / returns None) so the Flask routes stay thin.
"""

import sqlite3
from database import get_connection, hash_password

# ── Treatment price list (LKR) ──────────────────────────────────────
CONSULTATION_FEE = 1000

TREATMENT_PRICES = {
    "Scaling":    3000,
    "Filling":    5000,
    "Extraction": 4000,
    "Root Canal": 15000,
}


# ── Authentication ──────────────────────────────────────────────────
def authenticate(username: str, password: str) -> dict | None:
    """Return staff row as dict if credentials match, else None."""
    if not username or not password:
        return None
    conn = get_connection()
    row = conn.execute(
        "SELECT id, username, role FROM staff WHERE username = ? AND password_hash = ?",
        (username, hash_password(password)),
    ).fetchone()
    conn.close()
    if row:
        return {"id": row["id"], "username": row["username"], "role": row["role"]}
    return None


# ── Staff Management ────────────────────────────────────────────────
def get_all_staff() -> list[dict]:
    """Return all staff members with their plain passwords visible."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, username, password_plain, role, created_at FROM staff ORDER BY id"
    ).fetchall()
    conn.close()
    return [
        {
            "id": row["id"],
            "username": row["username"],
            "password": row["password_plain"],
            "role": row["role"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def add_staff(username: str, password: str, role: str = "staff") -> dict:
    """
    Add a new staff member.

    Returns {"success": True, "staff": {...}} on success.
    Raises ValueError if username already exists or input is invalid.
    """
    if not username or not username.strip():
        raise ValueError("Username is required.")
    if not password or len(password) < 4:
        raise ValueError("Password must be at least 4 characters.")
    if role not in ["admin", "staff"]:
        raise ValueError("Role must be 'admin' or 'staff'.")

    username = username.strip()
    conn = get_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO staff (username, password_hash, password_plain, role)
               VALUES (?, ?, ?, ?)""",
            (username, hash_password(password), password, role),
        )
        conn.commit()
        staff_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError(f"Username '{username}' already exists.")
    finally:
        conn.close()

    return {
        "success": True,
        "staff": {"id": staff_id, "username": username, "password": password, "role": role},
    }


def update_staff(staff_id: int, username: str = None, password: str = None) -> dict:
    """
    Update a staff member's username and/or password.

    Returns {"success": True} on success.
    Raises ValueError if staff not found or input is invalid.
    """
    if not staff_id:
        raise ValueError("Staff ID is required.")

    conn = get_connection()

    # Check if staff exists
    row = conn.execute("SELECT id FROM staff WHERE id = ?", (staff_id,)).fetchone()
    if not row:
        conn.close()
        raise ValueError(f"Staff member with ID {staff_id} not found.")

    updates = []
    params = []

    if username:
        if not username.strip():
            conn.close()
            raise ValueError("Username cannot be empty.")
        updates.append("username = ?")
        params.append(username.strip())

    if password:
        if len(password) < 4:
            conn.close()
            raise ValueError("Password must be at least 4 characters.")
        updates.append("password_hash = ?")
        updates.append("password_plain = ?")
        params.append(hash_password(password))
        params.append(password)

    if not updates:
        conn.close()
        raise ValueError("No updates provided.")

    params.append(staff_id)

    try:
        conn.execute(
            f"UPDATE staff SET {', '.join(updates)} WHERE id = ?",
            params,
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError(f"Username '{username}' already exists.")
    finally:
        conn.close()

    return {"success": True}


def delete_staff(staff_id: int, current_user_id: int) -> dict:
    """
    Delete a staff member.

    Returns {"success": True} on success.
    Raises ValueError if trying to delete self or admin, or if staff not found.
    """
    if not staff_id:
        raise ValueError("Staff ID is required.")

    if staff_id == current_user_id:
        raise ValueError("You cannot delete your own account while logged in.")

    conn = get_connection()

    # Check if staff exists and get their role
    row = conn.execute(
        "SELECT id, username, role FROM staff WHERE id = ?", (staff_id,)
    ).fetchone()

    if not row:
        conn.close()
        raise ValueError(f"Staff member with ID {staff_id} not found.")

    # Prevent deleting the primary admin account
    if row["username"] == "admin":
        conn.close()
        raise ValueError("Cannot delete the primary admin account.")

    conn.execute("DELETE FROM staff WHERE id = ?", (staff_id,))
    conn.commit()
    conn.close()

    return {"success": True}


# ── Appointments ────────────────────────────────────────────────────
REQUIRED_FIELDS = [
    "appointment_no",
    "patient_name",
    "address",
    "contact_number",
    "dentist_name",
    "treatment_type",
    "appointment_date",
    "appointment_time",
]


def register_appointment(data: dict) -> dict:
    """
    Insert a new appointment.

    Returns {"success": True, "appointment": {...}} on success.
    Raises ValueError with a human-readable message on failure.
    """
    # Check mandatory fields
    missing = [f for f in REQUIRED_FIELDS if not data.get(f, "").strip()]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    # Validate treatment type
    if data["treatment_type"] not in TREATMENT_PRICES:
        allowed = ", ".join(TREATMENT_PRICES.keys())
        raise ValueError(
            f"Unknown treatment type '{data['treatment_type']}'. "
            f"Allowed types: {allowed}"
        )

    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO appointments
               (appointment_no, patient_name, address, contact_number,
                dentist_name, treatment_type, appointment_date, appointment_time)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            tuple(data[f].strip() for f in REQUIRED_FIELDS),
        )
        conn.commit()
    except sqlite3.IntegrityError as exc:
        conn.close()
        err = str(exc).lower()
        if "appointment_no" in err or "unique" in err and "appointment" in err:
            raise ValueError(
                f"Appointment number '{data['appointment_no']}' already exists."
            )
        if "idx_no_double_booking" in err:
            raise ValueError(
                f"Double-booking: {data['dentist_name']} already has an appointment "
                f"on {data['appointment_date']} at {data['appointment_time']}."
            )
        raise ValueError(f"Database constraint error: {exc}")
    finally:
        conn.close()

    return {"success": True, "appointment": {f: data[f].strip() for f in REQUIRED_FIELDS}}


def find_appointment(appointment_no: str) -> dict | None:
    """Return the appointment dict for a given appointment_no, or None."""
    if not appointment_no or not appointment_no.strip():
        return None
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM appointments WHERE appointment_no = ?",
        (appointment_no.strip(),),
    ).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_all_appointments() -> list[dict]:
    """Return all active (not billed) appointments."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM appointments WHERE is_billed = 0 ORDER BY appointment_date DESC, appointment_time DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_appointment_history() -> list[dict]:
    """Return all billed/completed appointments."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM appointments WHERE is_billed = 1 ORDER BY billed_at DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def mark_appointment_billed(appointment_no: str) -> dict:
    """Mark an appointment as billed and remove it from active list."""
    from datetime import datetime

    appointment = find_appointment(appointment_no)
    if appointment is None:
        raise ValueError(f"Appointment '{appointment_no}' not found.")

    conn = get_connection()
    try:
        conn.execute(
            """UPDATE appointments SET is_billed = 1, billed_at = ?
               WHERE appointment_no = ?""",
            (datetime.now().isoformat(), appointment_no),
        )
        conn.commit()
    finally:
        conn.close()

    return {"success": True}


def calculate_bill(appointment_no: str) -> dict:
    """
    Build an itemised bill for the given appointment.

    Returns a dict with patient info, line items, and total.
    Raises ValueError if appointment not found or treatment unknown.
    """
    appointment = find_appointment(appointment_no)
    if appointment is None:
        raise ValueError(f"Appointment '{appointment_no}' not found.")

    treatment = appointment["treatment_type"]
    if treatment not in TREATMENT_PRICES:
        raise ValueError(f"Unknown treatment type '{treatment}' on record.")

    treatment_price = TREATMENT_PRICES[treatment]
    total = CONSULTATION_FEE + treatment_price

    return {
        "patient_name":    appointment["patient_name"],
        "appointment_no":  appointment["appointment_no"],
        "dentist_name":    appointment["dentist_name"],
        "treatment_type":  treatment,
        "consultation_fee": CONSULTATION_FEE,
        "treatment_price": treatment_price,
        "total":           total,
        "appointment_date": appointment["appointment_date"],
        "appointment_time": appointment["appointment_time"],
    }
