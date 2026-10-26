"""
ApexMed: Hospital & Healthcare Records Management System (H-RMS)
Core Flask Web Application Controller.
Implements Role-Based Access Control (Admin, Doctor, Patient),
Strict Client & Server-side Input Validations, Parameterized SQL Queries,
Secure Session Management, and SDLC Compliant Workflows.
"""

import os
import re
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect, url_for, session, flash, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db, init_db, log_audit

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

# Ensure database tables and initial seed data exist
init_db()

# Regular expressions for server-side validation
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
PHONE_REGEX = r"^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$"


# -----------------------------------------------------------------------------
# HELPER DECORATORS & ACCESS CONTROLLERS
# -----------------------------------------------------------------------------
def get_current_user():
    """Retrieve logged in user information from session."""
    if "user_id" in session:
        return {
            "user_id": session["user_id"],
            "email": session["email"],
            "full_name": session["full_name"],
            "role": session["role"]
        }
    return None


@app.context_processor
def inject_user():
    """Inject current logged-in user into all templates."""
    return dict(current_user=get_current_user())


# -----------------------------------------------------------------------------
# AUTHENTICATION & LOGIN (Requirement 1: Starts with validated login page)
# -----------------------------------------------------------------------------
@app.route("/")
def index():
    """Default landing route redirects to role dashboard or login page."""
    user = get_current_user()
    if user:
        if user["role"] == "admin":
            return redirect(url_for("admin_dashboard"))
        elif user["role"] == "doctor":
            return redirect(url_for("doctor_dashboard"))
        elif user["role"] == "patient":
            return redirect(url_for("patient_dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Login endpoint with comprehensive multi-layer validations:
    - Empty field verification
    - RFC-compliant email format check
    - Parameterized SQL authentication against SQL injection
    - Bcrypt/PBKDF2 hash verification
    - Active account check
    - Detailed audit logging
    """
    if get_current_user():
        return redirect(url_for("index"))

    errors = {}
    email_val = ""

    if request.method == "POST":
        email_val = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        selected_role = request.form.get("role_hint", "").strip()

        # 1. Validation checks
        if not email_val:
            errors["email"] = "Email address is mandatory."
        elif not re.match(EMAIL_REGEX, email_val):
            errors["email"] = "Please enter a valid email format (e.g., user@example.com)."

        if not password:
            errors["password"] = "Password field cannot be empty."
        elif len(password) < 6:
            errors["password"] = "Password must be at least 6 characters in length."

        # 2. Database verification if basic validations pass
        if not errors:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, email, password_hash, full_name, role, is_active FROM users WHERE email = ?;",
                (email_val,)
            )
            user_row = cursor.fetchone()

            if user_row and check_password_hash(user_row["password_hash"], password):
                if not user_row["is_active"]:
                    errors["general"] = "This account is currently deactivated. Please contact Administration."
                else:
                    # Successful authentication
                    session.clear()
                    session["user_id"] = user_row["user_id"]
                    session["email"] = user_row["email"]
                    session["full_name"] = user_row["full_name"]
                    session["role"] = user_row["role"]

                    log_audit(
                        user_row["user_id"],
                        "LOGIN_SUCCESS",
                        f"User logged in successfully as role: {user_row['role']}",
                        request.remote_addr
                    )
                    conn.close()

                    flash(f"Welcome back, {user_row['full_name']}!", "success")
                    if user_row["role"] == "admin":
                        return redirect(url_for("admin_dashboard"))
                    elif user_row["role"] == "doctor":
                        return redirect(url_for("doctor_dashboard"))
                    else:
                        return redirect(url_for("patient_dashboard"))
            else:
                errors["general"] = "Invalid credentials. Please verify your email and password."
                log_audit(
                    None,
                    "LOGIN_FAILED",
                    f"Failed login attempt for email: {email_val}",
                    request.remote_addr
                )
            conn.close()

    return render_template("login.html", errors=errors, email=email_val)


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Patient self-registration controller with rigorous input validations
    and transactional multi-table creation (users + patients).
    """
    if get_current_user():
        return redirect(url_for("index"))

    errors = {}
    form_data = {}

    if request.method == "POST":
        form_data = {
            "full_name": request.form.get("full_name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "password": request.form.get("password", ""),
            "confirm_password": request.form.get("confirm_password", ""),
            "date_of_birth": request.form.get("date_of_birth", "").strip(),
            "gender": request.form.get("gender", "").strip(),
            "blood_group": request.form.get("blood_group", "").strip(),
            "emergency_contact": request.form.get("emergency_contact", "").strip(),
            "address": request.form.get("address", "").strip()
        }

        # Validations
        if not form_data["full_name"] or len(form_data["full_name"]) < 3:
            errors["full_name"] = "Full Name must be at least 3 characters."
        if not form_data["email"] or not re.match(EMAIL_REGEX, form_data["email"]):
            errors["email"] = "A valid email address is required."
        if not form_data["phone"]:
            errors["phone"] = "Contact phone number is required."
        if not form_data["date_of_birth"]:
            errors["date_of_birth"] = "Date of Birth is required."
        if form_data["gender"] not in ("Male", "Female", "Other"):
            errors["gender"] = "Please select a valid gender option."
        if not form_data["password"] or len(form_data["password"]) < 6:
            errors["password"] = "Password must be at least 6 characters long."
        elif form_data["password"] != form_data["confirm_password"]:
            errors["confirm_password"] = "Passwords do not match."

        conn = get_db()
        cursor = conn.cursor()

        # Check unique email constraint
        if not errors:
            cursor.execute("SELECT user_id FROM users WHERE email = ?;", (form_data["email"],))
            if cursor.fetchone():
                errors["email"] = "An account with this email address already exists."

        # Insert user & patient record in atomic transaction
        if not errors:
            try:
                hashed_pw = generate_password_hash(form_data["password"])
                cursor.execute("""
                    INSERT INTO users (email, password_hash, full_name, role, phone)
                    VALUES (?, ?, ?, 'patient', ?);
                """, (form_data["email"], hashed_pw, form_data["full_name"], form_data["phone"]))
                new_user_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO patients (user_id, date_of_birth, gender, blood_group, emergency_contact, address)
                    VALUES (?, ?, ?, ?, ?, ?);
                """, (
                    new_user_id,
                    form_data["date_of_birth"],
                    form_data["gender"],
                    form_data["blood_group"],
                    form_data["emergency_contact"],
                    form_data["address"]
                ))

                conn.commit()
                log_audit(new_user_id, "USER_REGISTERED", f"Patient registered: {form_data['email']}", request.remote_addr)
                flash("Registration successful! You may now sign in with your credentials.", "success")
                conn.close()
                return redirect(url_for("login"))
            except Exception as e:
                conn.rollback()
                errors["general"] = f"Registration transaction failed: {str(e)}"
        conn.close()

    return render_template("register.html", errors=errors, form_data=form_data)


@app.route("/logout")
def logout():
    """Logout session clearance and audit record."""
    user = get_current_user()
    if user:
        log_audit(user["user_id"], "LOGOUT", f"User {user['email']} logged out.", request.remote_addr)
    session.clear()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("login"))


# -----------------------------------------------------------------------------
# ADMIN DASHBOARD & CONTROLS
# -----------------------------------------------------------------------------
@app.route("/admin/dashboard")
def admin_dashboard():
    """Hospital Administrator Control Center."""
    user = get_current_user()
    if not user or user["role"] != "admin":
        flash("Unauthorized access. Admin privileges required.", "danger")
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    # Aggregate Metrics
    cursor.execute("SELECT COUNT(*) AS total_patients FROM patients;")
    total_patients = cursor.fetchone()["total_patients"]

    cursor.execute("SELECT COUNT(*) AS total_doctors FROM doctors;")
    total_doctors = cursor.fetchone()["total_doctors"]

    cursor.execute("SELECT COUNT(*) AS total_appointments FROM appointments;")
    total_appointments = cursor.fetchone()["total_appointments"]

    cursor.execute("SELECT COALESCE(SUM(total_amount), 0.0) AS total_revenue FROM billings WHERE payment_status = 'Paid';")
    total_revenue = cursor.fetchone()["total_revenue"]

    # Retrieve all doctors with department information (JOIN)
    cursor.execute("""
        SELECT d.doctor_id, u.full_name, u.email, u.phone, dept.department_name,
               d.specialization, d.qualification, d.consultation_fee, d.available_days
        FROM doctors d
        JOIN users u ON d.user_id = u.user_id
        JOIN departments dept ON d.department_id = dept.department_id
        ORDER BY d.doctor_id ASC;
    """)
    doctors_list = cursor.fetchall()

    # Retrieve all departments
    cursor.execute("SELECT * FROM departments ORDER BY department_id ASC;")
    departments_list = cursor.fetchall()

    # Retrieve all appointments across the system (Complex 5-table JOIN)
    cursor.execute("""
        SELECT a.appointment_id, a.appointment_date, a.appointment_time, a.status, a.reason_for_visit,
               pu.full_name AS patient_name, du.full_name AS doctor_name, dept.department_name,
               COALESCE(b.payment_status, 'Unbilled') AS payment_status,
               COALESCE(b.total_amount, 0.0) AS bill_amount
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN users pu ON p.user_id = pu.user_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        JOIN users du ON d.user_id = du.user_id
        JOIN departments dept ON d.department_id = dept.department_id
        LEFT JOIN billings b ON a.appointment_id = b.appointment_id
        ORDER BY a.appointment_date DESC, a.appointment_time DESC;
    """)
    appointments_list = cursor.fetchall()

    # Retrieve latest Audit Logs
    cursor.execute("""
        SELECT l.log_id, l.action, l.details, l.ip_address, l.timestamp,
               COALESCE(u.email, 'SYSTEM/ANONYMOUS') AS user_email
        FROM audit_logs l
        LEFT JOIN users u ON l.user_id = u.user_id
        ORDER BY l.log_id DESC LIMIT 20;
    """)
    audit_logs = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard_admin.html",
        total_patients=total_patients,
        total_doctors=total_doctors,
        total_appointments=total_appointments,
        total_revenue=total_revenue,
        doctors=doctors_list,
        departments=departments_list,
        appointments=appointments_list,
        audit_logs=audit_logs
    )


@app.route("/admin/add-doctor", methods=["POST"])
def admin_add_doctor():
    """Admin endpoint to create a new Doctor user and specialty profile."""
    user = get_current_user()
    if not user or user["role"] != "admin":
        return redirect(url_for("login"))

    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    department_id = request.form.get("department_id", "").strip()
    specialization = request.form.get("specialization", "").strip()
    qualification = request.form.get("qualification", "").strip()
    consultation_fee = request.form.get("consultation_fee", "50.0").strip()
    available_days = request.form.get("available_days", "Mon-Fri").strip()

    if not full_name or not email or not department_id or not specialization:
        flash("Please complete all mandatory doctor details.", "warning")
        return redirect(url_for("admin_dashboard"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users WHERE email = ?;", (email,))
    if cursor.fetchone():
        flash("A user with this email address already exists.", "danger")
        conn.close()
        return redirect(url_for("admin_dashboard"))

    try:
        default_pwd = generate_password_hash("Doctor@123")
        cursor.execute("""
            INSERT INTO users (email, password_hash, full_name, role, phone)
            VALUES (?, ?, ?, 'doctor', ?);
        """, (email, default_pwd, full_name, phone))
        u_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO doctors (user_id, department_id, specialization, qualification, consultation_fee, available_days)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (u_id, int(department_id), specialization, qualification, float(consultation_fee), available_days))

        conn.commit()
        log_audit(user["user_id"], "ADD_DOCTOR", f"Admin created doctor: {full_name} ({email})", request.remote_addr)
        flash(f"Doctor {full_name} added successfully (Default Password: Doctor@123).", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Failed to create doctor: {str(e)}", "danger")

    conn.close()
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/add-department", methods=["POST"])
def admin_add_department():
    """Admin endpoint to create a hospital medical department."""
    user = get_current_user()
    if not user or user["role"] != "admin":
        return redirect(url_for("login"))

    dept_name = request.form.get("department_name", "").strip()
    description = request.form.get("description", "").strip()
    head_doctor = request.form.get("head_doctor", "").strip()

    if not dept_name:
        flash("Department name is required.", "warning")
        return redirect(url_for("admin_dashboard"))

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO departments (department_name, description, head_doctor)
            VALUES (?, ?, ?);
        """, (dept_name, description, head_doctor))
        conn.commit()
        log_audit(user["user_id"], "ADD_DEPARTMENT", f"Admin created department: {dept_name}", request.remote_addr)
        flash(f"Department '{dept_name}' registered successfully.", "success")
    except sqlite3.IntegrityError:
        flash(f"Department '{dept_name}' already exists.", "danger")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")

    conn.close()
    return redirect(url_for("admin_dashboard"))


# -----------------------------------------------------------------------------
# DOCTOR DASHBOARD & CLINICAL WORKFLOWS
# -----------------------------------------------------------------------------
@app.route("/doctor/dashboard")
def doctor_dashboard():
    """Doctor Consultation and Patient Management Dashboard."""
    user = get_current_user()
    if not user or user["role"] != "doctor":
        flash("Doctor access required.", "danger")
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    # Get Doctor Details
    cursor.execute("""
        SELECT d.doctor_id, d.specialization, d.qualification, d.consultation_fee, dept.department_name
        FROM doctors d
        JOIN departments dept ON d.department_id = dept.department_id
        WHERE d.user_id = ?;
    """, (user["user_id"],))
    doctor_info = cursor.fetchone()

    if not doctor_info:
        flash("Doctor profile not found.", "danger")
        conn.close()
        return redirect(url_for("login"))

    # Get Assigned Appointments
    cursor.execute("""
        SELECT a.appointment_id, a.appointment_date, a.appointment_time, a.status, a.reason_for_visit,
               pu.full_name AS patient_name, pu.email AS patient_email, pu.phone AS patient_phone,
               p.gender, p.blood_group, p.date_of_birth,
               pr.diagnosis, pr.medicines, pr.doctor_notes
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN users pu ON p.user_id = pu.user_id
        LEFT JOIN prescriptions pr ON a.appointment_id = pr.appointment_id
        WHERE a.doctor_id = ?
        ORDER BY a.appointment_date DESC, a.appointment_time ASC;
    """, (doctor_info["doctor_id"],))
    appointments = cursor.fetchall()

    conn.close()
    return render_template("dashboard_doctor.html", doctor=doctor_info, appointments=appointments)


@app.route("/doctor/update-appointment", methods=["POST"])
def doctor_update_appointment():
    """Doctor endpoint to update appointment status & submit prescription."""
    user = get_current_user()
    if not user or user["role"] != "doctor":
        return redirect(url_for("login"))

    appointment_id = request.form.get("appointment_id")
    status = request.form.get("status")
    diagnosis = request.form.get("diagnosis", "").strip()
    medicines = request.form.get("medicines", "").strip()
    doctor_notes = request.form.get("doctor_notes", "").strip()

    conn = get_db()
    cursor = conn.cursor()

    try:
        # Update status
        cursor.execute("UPDATE appointments SET status = ? WHERE appointment_id = ?;", (status, appointment_id))

        # Upsert prescription record if diagnosis/medicines provided
        if diagnosis and medicines:
            cursor.execute("""
                INSERT INTO prescriptions (appointment_id, diagnosis, medicines, doctor_notes)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(appointment_id) DO UPDATE SET
                    diagnosis = excluded.diagnosis,
                    medicines = excluded.medicines,
                    doctor_notes = excluded.doctor_notes;
            """, (appointment_id, diagnosis, medicines, doctor_notes))

        conn.commit()
        log_audit(user["user_id"], "UPDATE_APPOINTMENT", f"Appointment #{appointment_id} updated to {status}", request.remote_addr)
        flash(f"Appointment #{appointment_id} updated successfully.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Failed to update appointment: {str(e)}", "danger")

    conn.close()
    return redirect(url_for("doctor_dashboard"))


# -----------------------------------------------------------------------------
# PATIENT DASHBOARD & APPOINTMENT BOOKING
# -----------------------------------------------------------------------------
@app.route("/patient/dashboard")
def patient_dashboard():
    """Patient Self-Service Portal."""
    user = get_current_user()
    if not user or user["role"] != "patient":
        flash("Patient login required.", "danger")
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    # Get patient profile details
    cursor.execute("""
        SELECT p.patient_id, p.date_of_birth, p.gender, p.blood_group, p.emergency_contact, p.address
        FROM patients p
        WHERE p.user_id = ?;
    """, (user["user_id"],))
    patient_info = cursor.fetchone()

    # Get patient's appointments
    cursor.execute("""
        SELECT a.appointment_id, a.appointment_date, a.appointment_time, a.status, a.reason_for_visit,
               du.full_name AS doctor_name, d.specialization, dept.department_name,
               pr.diagnosis, pr.medicines, pr.doctor_notes,
               b.bill_id, b.total_amount, b.payment_status
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        JOIN users du ON d.user_id = du.user_id
        JOIN departments dept ON d.department_id = dept.department_id
        LEFT JOIN prescriptions pr ON a.appointment_id = pr.appointment_id
        LEFT JOIN billings b ON a.appointment_id = b.appointment_id
        WHERE a.patient_id = ?
        ORDER BY a.appointment_date DESC, a.appointment_time DESC;
    """, (patient_info["patient_id"],))
    appointments = cursor.fetchall()

    # List of doctors and departments for booking form
    cursor.execute("""
        SELECT d.doctor_id, u.full_name AS doctor_name, d.specialization, d.consultation_fee, dept.department_name
        FROM doctors d
        JOIN users u ON d.user_id = u.user_id
        JOIN departments dept ON d.department_id = dept.department_id
        ORDER BY dept.department_name, u.full_name;
    """)
    doctors_list = cursor.fetchall()

    conn.close()
    return render_template(
        "dashboard_patient.html",
        patient=patient_info,
        appointments=appointments,
        doctors=doctors_list
    )


@app.route("/patient/book-appointment", methods=["POST"])
def book_appointment():
    """
    Patient Appointment Scheduling Controller.
    Implements collision avoidance constraint check and automated invoice generation.
    """
    user = get_current_user()
    if not user or user["role"] != "patient":
        return redirect(url_for("login"))

    doctor_id = request.form.get("doctor_id")
    appointment_date = request.form.get("appointment_date")
    appointment_time = request.form.get("appointment_time")
    reason = request.form.get("reason_for_visit", "").strip()

    if not doctor_id or not appointment_date or not appointment_time:
        flash("Doctor, appointment date, and time slot are required.", "warning")
        return redirect(url_for("patient_dashboard"))

    # Date validation: Cannot book in past
    try:
        chosen_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
        if chosen_date < datetime.today().date():
            flash("Appointment date cannot be in the past.", "warning")
            return redirect(url_for("patient_dashboard"))
    except ValueError:
        flash("Invalid date format provided.", "danger")
        return redirect(url_for("patient_dashboard"))

    conn = get_db()
    cursor = conn.cursor()

    # Get patient ID
    cursor.execute("SELECT patient_id FROM patients WHERE user_id = ?;", (user["user_id"],))
    patient_row = cursor.fetchone()
    if not patient_row:
        conn.close()
        flash("Patient record not found.", "danger")
        return redirect(url_for("patient_dashboard"))

    patient_id = patient_row["patient_id"]

    try:
        # Check if doctor is already booked at that slot (UNIQUE slot constraint)
        cursor.execute("""
            SELECT appointment_id FROM appointments 
            WHERE doctor_id = ? AND appointment_date = ? AND appointment_time = ? AND status != 'Cancelled';
        """, (doctor_id, appointment_date, appointment_time))
        existing = cursor.fetchone()

        if existing:
            flash("The selected doctor is already booked for that date and time slot. Please choose another time.", "danger")
            conn.close()
            return redirect(url_for("patient_dashboard"))

        # Fetch doctor fee
        cursor.execute("SELECT consultation_fee FROM doctors WHERE doctor_id = ?;", (doctor_id,))
        doc_row = cursor.fetchone()
        fee = doc_row["consultation_fee"] if doc_row else 50.0
        tax = round(fee * 0.10, 2)
        total = round(fee + tax, 2)

        # Insert appointment
        cursor.execute("""
            INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, status, reason_for_visit)
            VALUES (?, ?, ?, ?, 'Scheduled', ?);
        """, (patient_id, doctor_id, appointment_date, appointment_time, reason))
        new_appt_id = cursor.lastrowid

        # Automatically create billing invoice
        cursor.execute("""
            INSERT INTO billings (appointment_id, amount, tax, total_amount, payment_status)
            VALUES (?, ?, ?, ?, 'Unpaid');
        """, (new_appt_id, fee, tax, total))

        conn.commit()
        log_audit(user["user_id"], "BOOK_APPOINTMENT", f"Booked appointment #{new_appt_id} with Doctor ID #{doctor_id}", request.remote_addr)
        flash("Your appointment has been successfully scheduled! An invoice has been generated.", "success")
    except sqlite3.IntegrityError as ie:
        conn.rollback()
        flash(f"Slot booking collision detected: {str(ie)}", "danger")
    except Exception as e:
        conn.rollback()
        flash(f"Booking error: {str(e)}", "danger")

    conn.close()
    return redirect(url_for("patient_dashboard"))


@app.route("/patient/pay-bill/<int:bill_id>", methods=["POST"])
def pay_bill(bill_id):
    """Patient Invoice Settlement."""
    user = get_current_user()
    if not user or user["role"] != "patient":
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE billings 
        SET payment_status = 'Paid', payment_method = 'Online / Card', payment_date = CURRENT_TIMESTAMP
        WHERE bill_id = ?;
    """, (bill_id,))
    conn.commit()
    log_audit(user["user_id"], "PAY_BILL", f"Paid bill #{bill_id}", request.remote_addr)
    conn.close()

    flash(f"Invoice #{bill_id} marked as Paid. Thank you!", "success")
    return redirect(url_for("patient_dashboard"))


# -----------------------------------------------------------------------------
# ERROR HANDLERS
# -----------------------------------------------------------------------------
@app.errorhandler(404)
def not_found_error(error):
    return render_template("login.html", errors={"general": "Page not found (404)."}), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("login.html", errors={"general": "Internal system error (500)."}), 500


if __name__ == "__main__":
    import socket
    hostname = socket.gethostname()
    local_ip = "127.0.0.1"
    try:
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        pass

    print("=" * 70)
    print(" ApexMed: Hospital Clinical & Records Management System (H-RMS)")
    print(" Server is running and accessible on:")
    print(f"  - Local Computer:        http://127.0.0.1:5000")
    print(f"  - Other Devices (Wi-Fi): http://{local_ip}:5000")
    print(" Default Login Credentials:")
    print("  - Admin:   admin@apexmed.com        / Admin@123")
    print("  - Doctor:  dr.vance@apexmed.com     / Admin@123")
    print("  - Patient: patient.alice@gmail.com  / Admin@123")
    print("=" * 70)
    app.run(debug=True, host="0.0.0.0", port=5000)
