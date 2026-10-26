# ApexMed: Hospital & Clinical Records Management System (H-RMS)

A complete, enterprise-grade, SDLC-compliant Relational Database Management System (RDBMS) Web Application built with Python (Flask) front-end controller and SQLite/MySQL back-end database.

---

## 🌟 Key Features
- **Starts on Validated Login Page**: Multi-tier client-side (HTML5 + Regex JS) and server-side validation with PBKDF2/scrypt password hashing and SQL injection immunity.
- **Role-Based Access Control (RBAC)**:
  - 🛡️ **Administrator**: System KPIs, Doctor Management, Clinical Department Registration, Master Appointment Registry, and Live Security Audit Logs.
  - 🩺 **Doctor**: Patient queue, consultation notes, diagnosis entry, electronic prescriptions, and appointment status lifecycle.
  - 🏥 **Patient**: Self-registration, real-time doctor appointment booking with slot collision prevention, digital prescription viewer, and invoice settlement.
- **Relational Integrity & Normalization**:
  - Fully normalized to **3NF / BCNF**.
  - Strict Foreign Keys with `ON DELETE CASCADE` and `ON DELETE RESTRICT`.
  - Multi-column `UNIQUE(doctor_id, appointment_date, appointment_time)` preventing double bookings.
  - Check constraints for non-negative fees and valid status enums.
  - ACID-compliant transactions with `commit` and `rollback`.
- **Dual Database Architecture**:
  - Zero-configuration SQLite engine built-in for instant out-of-the-box run.
  - Complete MySQL 8.x DDL/DML script included in `sql/schema_mysql.sql`.

---

## 🚀 Quick Start Guide

### 1. Requirements
- Python 3.10+ (Tested on Python 3.14/3.15)
- Dependencies: `pip install -r requirements.txt` (Flask, Werkzeug)

### 2. Launch the Application
Navigate to the project directory and run:
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```
*(The root route `/` automatically validates authentication and routes unauthenticated visitors directly to `/login`)*.

---

## 🔑 Default Credentials (One-Click Auto-Fill Enabled)

| Role | Email | Password | Access / Portal |
|---|---|---|---|
| **Admin** | `admin@apexmed.com` | `Admin@123` | Master control, departments, doctors, audit logs |
| **Doctor** | `dr.vance@apexmed.com` | `Admin@123` | Cardiology queue, consultations, prescriptions |
| **Doctor** | `dr.rostova@apexmed.com` | `Admin@123` | Neurology queue, consultations, prescriptions |
| **Patient** | `patient.alice@gmail.com` | `Admin@123` | Bookings, prescription viewer, unpaid invoices |
| **Patient** | `patient.bob@gmail.com` | `Admin@123` | Bookings, pending consultation, invoices |

*(Note: On the login page, you can simply click the **Admin**, **Doctor**, or **Patient** quick-fill button to populate credentials instantly).*

---

## 🧪 Running Automated Tests
Run the 15-scenario automated unit and integration test suite:
```bash
python tests/test_app.py
```
**Test Coverage Includes:**
- Root redirection & route guards
- Empty field & malformed email validations
- SQL injection immunity verification
- PBKDF2 credential verification
- Patient transactional registration
- Duplicate email prevention
- RBAC privilege escalation prevention
- Appointment scheduling & automatic billing generation
- Multi-column slot collision constraint prevention
- Invoice settlement transaction
- Doctor prescription upsert

---

## 📂 Project Structure
```text
ApexMed_HMS/
├── app.py                   # Main Flask application and RBAC controller
├── database.py              # Database connection, initialization, seed data & audit helper
├── requirements.txt         # Project dependencies
├── README.md                # Project documentation & instructions
├── sql/
│   ├── schema_mysql.sql     # MySQL 8.x relational schema, views & triggers
│   └── schema_sqlite.sql    # SQLite relational schema
├── static/
│   ├── css/
│   │   └── style.css        # Modern healthcare UI stylesheet
│   └── js/
│       └── validation.js    # Client-side live validation & demo quick-fill helper
├── templates/
│   ├── base.html            # Master layout with responsive navbar, flash alerts & footer
│   ├── login.html           # Dedicated login page with full validation & role pills
│   ├── register.html        # Patient self-registration portal
│   ├── dashboard_admin.html # Admin KPI metrics, doctor/department management & audit logs
│   ├── dashboard_doctor.html# Doctor patient queue & prescription modal
│   └── dashboard_patient.html# Patient booking interface, Rx viewer & invoices
└── tests/
    └── test_app.py          # 15 automated test cases (100% passing)
```
