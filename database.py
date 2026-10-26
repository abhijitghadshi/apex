"""
ApexMed: Hospital & Healthcare Records Management System (H-RMS)
Database Layer - SQLite / MySQL compatible parameterized query interface.
Provides schema creation, normalization enforcement, foreign key constraints,
auto-seeding of sample users, doctors, departments, and audit logging.
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apexmed.db")


def get_db():
    """Establish connection to SQLite database with foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Create all relational tables and seed default users/departments if empty."""
    conn = get_db()
    cursor = conn.cursor()

    # 1. Departments Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            department_id INTEGER PRIMARY KEY AUTOINCREMENT,
            department_name TEXT NOT NULL UNIQUE,
            description TEXT,
            head_doctor TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. Users Table (RBAC: admin, doctor, patient)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'doctor', 'patient')),
            phone TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 3. Doctors Table (1:1 with users, M:1 with departments)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            department_id INTEGER NOT NULL,
            specialization TEXT NOT NULL,
            qualification TEXT NOT NULL,
            consultation_fee REAL NOT NULL DEFAULT 50.0 CHECK (consultation_fee >= 0),
            available_days TEXT DEFAULT 'Mon-Fri',
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE RESTRICT
        );
    """)

    # 4. Patients Table (1:1 with users)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            date_of_birth TEXT NOT NULL,
            gender TEXT NOT NULL CHECK(gender IN ('Male', 'Female', 'Other')),
            blood_group TEXT,
            emergency_contact TEXT,
            address TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
    """)

    # 5. Appointments Table (M:1 with patient, M:1 with doctor)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            status TEXT DEFAULT 'Scheduled' CHECK(status IN ('Scheduled', 'Completed', 'Cancelled', 'In-Progress')),
            reason_for_visit TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
            FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE,
            UNIQUE(doctor_id, appointment_date, appointment_time)
        );
    """)

    # 6. Prescriptions Table (1:1 with appointment)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prescriptions (
            prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER NOT NULL UNIQUE,
            diagnosis TEXT NOT NULL,
            medicines TEXT NOT NULL,
            doctor_notes TEXT,
            issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE CASCADE
        );
    """)

    # 7. Billings Table (1:1 with appointment)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS billings (
            bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER NOT NULL UNIQUE,
            amount REAL NOT NULL CHECK(amount >= 0),
            tax REAL NOT NULL DEFAULT 0.0,
            total_amount REAL NOT NULL,
            payment_status TEXT DEFAULT 'Unpaid' CHECK(payment_status IN ('Unpaid', 'Paid', 'Refunded')),
            payment_method TEXT,
            payment_date TIMESTAMP,
            FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE CASCADE
        );
    """)

    # 8. Audit Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            ip_address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
        );
    """)

    # Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_appt_date ON appointments(appointment_date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_appt_patient ON appointments(patient_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_appt_doctor ON appointments(doctor_id);")

    # Seed initial data if users table is empty
    cursor.execute("SELECT COUNT(*) AS count FROM users;")
    if cursor.fetchone()["count"] == 0:
        seed_data(conn)

    conn.commit()
    conn.close()


def seed_data(conn):
    """Seed sample departments, admin, doctors, patients, and initial appointment."""
    cursor = conn.cursor()
    pwd_hash = generate_password_hash("Admin@123")

    # 1. Seed Departments
    departments = [
        ("Cardiology", "Heart health, rhythm disorders, and cardiovascular care", "Dr. Marcus Vance"),
        ("Neurology", "Comprehensive diagnosis of brain, nervous system, and spinal conditions", "Dr. Elena Rostova"),
        ("Orthopedics", "Bone fractures, joint replacements, and sports injuries", "Dr. Alan Grant"),
        ("Pediatrics", "Specialized care, immunizations, and wellness for children", "Dr. Meredith Grey"),
        ("General Medicine", "Primary outpatient consultation, preventive screenings, and health checks", "Dr. John Watson")
    ]
    cursor.executemany(
        "INSERT INTO departments (department_name, description, head_doctor) VALUES (?, ?, ?);",
        departments
    )

    # 2. Seed Admin User
    cursor.execute(
        "INSERT INTO users (email, password_hash, full_name, role, phone) VALUES (?, ?, ?, ?, ?);",
        ("admin@apexmed.com", pwd_hash, "Apex Administrator", "admin", "+1-800-555-0199")
    )

    # 3. Seed Doctor Users & Doctor profiles
    doctor_users = [
        ("dr.vance@apexmed.com", pwd_hash, "Dr. Marcus Vance", "doctor", "+1-800-555-0201", 1, "Cardiologist", "MD, FACC", 120.0, "Mon,Wed,Fri"),
        ("dr.rostova@apexmed.com", pwd_hash, "Dr. Elena Rostova", "doctor", "+1-800-555-0202", 2, "Neurologist", "MD, PhD (Neuro)", 150.0, "Tue,Thu,Sat"),
        ("dr.grant@apexmed.com", pwd_hash, "Dr. Alan Grant", "doctor", "+1-800-555-0203", 3, "Orthopedic Surgeon", "MS, Ortho", 110.0, "Mon-Fri"),
        ("dr.grey@apexmed.com", pwd_hash, "Dr. Meredith Grey", "doctor", "+1-800-555-0204", 4, "Pediatrician", "MD, FAAP", 90.0, "Mon-Thu")
    ]

    for email, pw, name, role, phone, dept_id, spec, qual, fee, days in doctor_users:
        cursor.execute(
            "INSERT INTO users (email, password_hash, full_name, role, phone) VALUES (?, ?, ?, ?, ?);",
            (email, pw, name, role, phone)
        )
        u_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO doctors (user_id, department_id, specialization, qualification, consultation_fee, available_days) VALUES (?, ?, ?, ?, ?, ?);",
            (u_id, dept_id, spec, qual, fee, days)
        )

    # 4. Seed Patient Users & Patient profiles
    patients_data = [
        ("patient.alice@gmail.com", pwd_hash, "Alice Johnson", "patient", "+1-800-555-0301", "1994-05-14", "Female", "O+", "+1-800-555-9999", "742 Evergreen Terrace, Springfield"),
        ("patient.bob@gmail.com", pwd_hash, "Bob Martinez", "patient", "+1-800-555-0302", "1988-11-23", "Male", "A+", "+1-800-555-8888", "100 Elm Street, Metropolis")
    ]

    patient_ids = []
    for email, pw, name, role, phone, dob, gender, blood, em_phone, addr in patients_data:
        cursor.execute(
            "INSERT INTO users (email, password_hash, full_name, role, phone) VALUES (?, ?, ?, ?, ?);",
            (email, pw, name, role, phone)
        )
        u_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO patients (user_id, date_of_birth, gender, blood_group, emergency_contact, address) VALUES (?, ?, ?, ?, ?, ?);",
            (u_id, dob, gender, blood, em_phone, addr)
        )
        patient_ids.append(cursor.lastrowid)

    # 5. Seed a Sample Completed Appointment with Prescription and Paid Bill
    cursor.execute("""
        INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, status, reason_for_visit)
        VALUES (1, 1, '2026-10-20', '10:00 AM', 'Completed', 'Routine cardiovascular checkup and mild chest tightness.');
    """)
    appt_id1 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO prescriptions (appointment_id, diagnosis, medicines, doctor_notes)
        VALUES (?, ?, ?, ?);
    """, (
        appt_id1,
        "Mild Hypertension (Stage 1) - Sinus Rhythm Normal",
        "1. Amlodipine 5mg (Once daily morning)\n2. Aspirin 75mg (Post-lunch daily)",
        "Patient advised low sodium diet, 30 min daily brisk walk. Follow-up in 4 weeks."
    ))

    cursor.execute("""
        INSERT INTO billings (appointment_id, amount, tax, total_amount, payment_status, payment_method, payment_date)
        VALUES (?, 120.00, 12.00, 132.00, 'Paid', 'Credit Card', '2026-10-20 10:45:00');
    """, (appt_id1,))

    # 6. Seed an Upcoming Appointment for Bob
    cursor.execute("""
        INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, status, reason_for_visit)
        VALUES (2, 2, '2026-10-25', '02:00 PM', 'Scheduled', 'Recurrent tension headaches and insomnia.');
    """)
    appt_id2 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO billings (appointment_id, amount, tax, total_amount, payment_status)
        VALUES (?, 150.00, 15.00, 165.00, 'Unpaid');
    """, (appt_id2,))

    # Log initial seed event in audit table
    cursor.execute("""
        INSERT INTO audit_logs (user_id, action, details, ip_address)
        VALUES (1, 'SYSTEM_INIT', 'Database schema initialized and seed records created.', '127.0.0.1');
    """)


def log_audit(user_id, action, details, ip_address="127.0.0.1"):
    """Helper to record system audit entries."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO audit_logs (user_id, action, details, ip_address) VALUES (?, ?, ?, ?);",
        (user_id, action, details, ip_address)
    )
    conn.commit()
    conn.close()
