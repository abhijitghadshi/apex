-- ============================================================================
-- ApexMed: Hospital & Healthcare Records Management System (H-RMS)
-- Complete Relational Database Schema (SQLite 3 Compatible)
-- Normalized to 3NF/BCNF with Referential Integrity & Multi-Column Constraints
-- ============================================================================

PRAGMA foreign_keys = ON;

-- 1. DEPARTMENTS TABLE
CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_name TEXT NOT NULL UNIQUE,
    description TEXT,
    head_doctor TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. USERS TABLE (Authentication & Role-Based Access Control)
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

-- 3. DOCTORS TABLE
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

-- 4. PATIENTS TABLE
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

-- 5. APPOINTMENTS TABLE
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

-- 6. PRESCRIPTIONS TABLE
CREATE TABLE IF NOT EXISTS prescriptions (
    prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id INTEGER NOT NULL UNIQUE,
    diagnosis TEXT NOT NULL,
    medicines TEXT NOT NULL,
    doctor_notes TEXT,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE CASCADE
);

-- 7. BILLINGS TABLE
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

-- 8. AUDIT LOGS TABLE
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    ip_address TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_appt_date ON appointments(appointment_date);
CREATE INDEX IF NOT EXISTS idx_appt_patient ON appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_appt_doctor ON appointments(doctor_id);
