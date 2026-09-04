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
        "SELECT id, username FROM staff WHERE username = ? AND password_hash = ?",
        (username, hash_password(password)),
    ).fetchone()
    conn.close()
    if row:
        return {"id": row["id"], "username": row["username"]}
    return None


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
