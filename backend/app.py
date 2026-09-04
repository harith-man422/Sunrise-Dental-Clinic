"""
Sunrise Dental Clinic — Flask REST API.

Endpoints
---------
POST   /api/login              Authenticate staff
POST   /api/logout             Clear session
POST   /api/appointments       Register a new appointment
GET    /api/appointments/<no>  Look up an appointment
GET    /api/bill/<no>          Calculate & return an itemised bill
GET    /api/help               Return help/instructions text
GET    /api/treatments         Return the allowed treatment list & prices
"""

import os
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from database import init_db
from models import (
    authenticate,
    register_appointment,
    find_appointment,
    get_all_appointments,
    get_registered_appointments,
    get_appointment_history,
    mark_appointment_billed,
    calculate_bill,
    get_all_staff,
    add_staff,
    update_staff,
    delete_staff,
    TREATMENT_PRICES,
    CONSULTATION_FEE,
)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

# Create Flask app WITHOUT static_url_path="" so default static handler doesn't hijack /api
app = Flask(__name__, static_folder=None)
app.secret_key = "sunrise-dental-secret-key-change-in-production"

# Enable CORS for local dev / any origin
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})

# Initialise the database (create tables + seed data) on startup
init_db()


# ── Helpers ──────────────────────────────────────────────────────────
def login_required(fn):
    """Decorator: rejects requests from unauthenticated callers."""
    from functools import wraps

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return jsonify({"error": "Unauthorised. Please log in first."}), 401
        return fn(*args, **kwargs)

    return wrapper


# ── Auth endpoints ───────────────────────────────────────────────────
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    user = authenticate(username, password)
    if user is None:
        return jsonify({"error": "Invalid username or password."}), 401

    session["user"] = user
    return jsonify({"message": "Login successful.", "user": user}), 200


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully."}), 200


# ── Appointment endpoints ───────────────────────────────────────────
@app.route("/api/appointments", methods=["POST"])
@login_required
def register():
    data = request.get_json(silent=True) or {}
    try:
        result = register_appointment(data)
        return jsonify(result), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/appointments/<appointment_no>", methods=["GET"])
@login_required
def search(appointment_no):
    record = find_appointment(appointment_no)
    if record is None:
        return jsonify({"error": f"Appointment '{appointment_no}' not found."}), 404
    return jsonify(record), 200


# ── Billing endpoint ────────────────────────────────────────────────
@app.route("/api/bill/<appointment_no>", methods=["GET"])
@login_required
def bill(appointment_no):
    try:
        result = calculate_bill(appointment_no)
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/bill/<appointment_no>/confirm", methods=["POST"])
@login_required
def confirm_bill(appointment_no):
    """Mark an appointment as billed after printing/confirmation."""
    try:
        result = mark_appointment_billed(appointment_no)
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


# ── Appointments list endpoints ─────────────────────────────────────
@app.route("/api/appointments/list/active", methods=["GET"])
@login_required
def list_active_appointments():
    """Get all active (not yet billed) appointments."""
    appointments = get_all_appointments()
    return jsonify(appointments), 200


@app.route("/api/appointments/list/registered", methods=["GET"])
@login_required
def list_registered_appointments():
    """Get all registered appointments (both billed and unbilled)."""
    appointments = get_registered_appointments()
    return jsonify(appointments), 200


@app.route("/api/appointments/list/history", methods=["GET"])
@login_required
def list_appointment_history():
    """Get all billed/completed appointments."""
    history = get_appointment_history()
    return jsonify(history), 200


# ── Treatments reference ────────────────────────────────────────────
@app.route("/api/treatments", methods=["GET"])
@login_required
def treatments():
    return jsonify({
        "consultation_fee": CONSULTATION_FEE,
        "treatments": TREATMENT_PRICES,
    }), 200


# ── Staff Management endpoints ──────────────────────────────────────
@app.route("/api/staff", methods=["GET"])
@login_required
def get_staff():
    """Get all staff members."""
    staff_list = get_all_staff()
    return jsonify(staff_list), 200


@app.route("/api/staff", methods=["POST"])
@login_required
def create_staff():
    """Create a new staff member."""
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    role = data.get("role", "staff")

    try:
        result = add_staff(username, password, role)
        return jsonify(result), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/staff/<int:staff_id>", methods=["PUT"])
@login_required
def update_staff_member(staff_id):
    """Update a staff member's username and/or password."""
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    try:
        result = update_staff(staff_id, username, password)
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/staff/<int:staff_id>", methods=["DELETE"])
@login_required
def delete_staff_member(staff_id):
    """Delete a staff member."""
    current_user_id = session.get("user", {}).get("id")
    try:
        result = delete_staff(staff_id, current_user_id)
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


# ── Help endpoint ───────────────────────────────────────────────────
@app.route("/api/help", methods=["GET"])
def help_info():
    return jsonify({
        "title": "Sunrise Dental Clinic — Staff Help Guide",
        "sections": [
            {
                "heading": "1. Login",
                "steps": [
                    "Open the application in your browser.",
                    "Enter your staff username and password.",
                    "Click the 'Login' button.",
                    "If your credentials are correct you will be taken to the dashboard.",
                    "All other features require a successful login first.",
                ],
            },
            {
                "heading": "2. Register New Appointment",
                "steps": [
                    "From the dashboard, click 'Register Appointment'.",
                    "Fill in every field: Appointment No, Patient Name, Address, "
                    "Contact Number, Dentist Name, Treatment Type, Date, and Time.",
                    "Treatment types available: Scaling, Filling, Extraction, Root Canal.",
                    "Click 'Register'. The system will reject duplicate appointment "
                    "numbers and double-bookings (same dentist, date, and time).",
                ],
            },
            {
                "heading": "3. Search Appointment",
                "steps": [
                    "From the dashboard, click 'Search Appointment'.",
                    "Enter the Appointment Number and click 'Search'.",
                    "The full patient and appointment details will be displayed.",
                    "If the number does not exist, a 'not found' message is shown.",
                ],
            },
            {
                "heading": "4. Calculate & Print Bill",
                "steps": [
                    "From the dashboard, click 'Billing'.",
                    "Enter the Appointment Number and click 'Generate Bill'.",
                    "The itemised receipt shows: consultation fee (LKR 1 000), "
                    "treatment price, and total.",
                    "Click 'Print Receipt' to open the browser print dialog.",
                ],
            },
            {
                "heading": "5. Help",
                "steps": [
                    "Click 'Help' on the dashboard to view this guide at any time.",
                ],
            },
            {
                "heading": "6. Logout / Exit",
                "steps": [
                    "Click 'Logout' in the navigation bar.",
                    "Your session is cleared and you are returned to the login screen.",
                    "Always log out before leaving the workstation.",
                ],
            },
        ],
    }), 200


# ── Static File Routes (Serve Frontend) ─────────────────────────────
@app.route("/", methods=["GET"])
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/dashboard.html", methods=["GET"])
def dashboard():
    return send_from_directory(FRONTEND_DIR, "dashboard.html")


@app.route("/<path:path>", methods=["GET"])
def serve_static(path):
    if os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    return jsonify({"error": "File not found"}), 404


# ── Run ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
