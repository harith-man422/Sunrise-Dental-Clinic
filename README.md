# 🦷 Sunrise Dental Clinic — Appointment & Patient Management System

A full-stack Appointment & Patient Management System for Sunrise Dental Clinic, built with Python (Flask), SQLite, and pure HTML/CSS/JavaScript.

## 🚀 Tech Stack

- **Backend:** Python 3, Flask, SQLite (sqlite3 with WAL mode), Flask-CORS
- **Frontend:** Plain HTML5, CSS3, JavaScript (Fetch API) — *No frontend framework dependencies*

---

## ✨ Features

1. **Staff Authentication**
   - Username and password-protected staff access.
   - SHA-256 password hashing.
   - Protected API endpoints using session-based authentication.

2. **Appointment Registration**
   - Mandatory field validation.
   - Automatic rejection of duplicate appointment numbers.
   - **Double-booking prevention:** prevents booking the same dentist for the same date and time.

3. **Appointment Search**
   - Search by appointment number to retrieve full patient & treatment details.
   - Graceful handling of non-existent records.

4. **Billing & Receipts**
   - Automatic calculation: Flat Consultation Fee (**LKR 1,000**) + Treatment Price.
   - Price list:
     - **Scaling:** LKR 3,000
     - **Filling:** LKR 5,000
     - **Extraction:** LKR 4,000
     - **Root Canal:** LKR 15,000
   - Printable receipt view with browser print dialog integration (`window.print()`).

5. **Staff Help Guide**
   - Built-in step-by-step instructions for all clinic functions.

6. **Exit & Logout**
   - Secure session termination and redirection to login.

---

## 📂 Project Structure

```
.
├── backend/
│   ├── app.py          # Flask application & REST API routes
│   ├── models.py       # Data access functions & business logic
│   ├── database.py     # SQLite database connection & initial schema seeding
│   └── clinic.db       # SQLite database (auto-created on startup)
├── frontend/
│   ├── index.html      # Staff login page
│   ├── dashboard.html  # Main dashboard (Register, Search, Bill, Help)
│   ├── css/
│   │   └── styles.css  # Modern responsive styles & print stylesheet
│   └── js/
│       ├── api.js          # Fetch API wrapper for backend calls
│       ├── login.js        # Authentication logic
│       ├── appointments.js # Registration & search logic
│       └── billing.js      # Billing & receipt generation
├── .gitignore
└── README.md
```

---

## 🛠️ Getting Started

### 1. Prerequisites
- Python 3.10+ installed

### 2. Install Dependencies
```bash
pip install flask flask-cors
```

### 3. Run the Backend & Application
```bash
cd backend
python app.py
```
*The server will start on `http://localhost:5000`.*

### 4. Access the App
Open your browser and navigate to:
👉 **[http://localhost:5000](http://localhost:5000)**

---

## 🔑 Default Credentials & Test Data

- **Staff Login:**
  - **Username:** `admin`
  - **Password:** `Clinic@123`

- **Pre-seeded Appointment:**
  - **Appointment No:** `A1001`
  - **Patient Name:** `Nimal Perera`
  - **Dentist:** `Dr. Silva`
  - **Treatment:** `Scaling`
  - **Date:** `2026-09-10`
  - **Time:** `10:30`
