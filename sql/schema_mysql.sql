-- ============================================================================
-- ApexMed: Hospital & Healthcare Records Management System (H-RMS)
-- Complete Relational Database Schema (MySQL 8.x Compatible)
-- Normalized up to 3NF / BCNF with Referential Integrity & Constraints
-- ============================================================================

CREATE DATABASE IF NOT EXISTS apexmed_db;
USE apexmed_db;

-- 1. DEPARTMENTS TABLE
CREATE TABLE IF NOT EXISTS departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    head_doctor VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. USERS TABLE (Authentication & Role-Based Access Control)
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'doctor', 'patient') NOT NULL DEFAULT 'patient',
    phone VARCHAR(20),
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 3. DOCTORS TABLE (Specialization & Department Link)
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    department_id INT NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    qualification VARCHAR(100) NOT NULL,
    consultation_fee DECIMAL(10,2) NOT NULL DEFAULT 50.00,
    available_days VARCHAR(50) DEFAULT 'Mon-Fri',
    CONSTRAINT fk_doctor_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_doctor_dept FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE RESTRICT,
    CONSTRAINT chk_doc_fee CHECK (consultation_fee >= 0)
) ENGINE=InnoDB;

-- 4. PATIENTS TABLE (Medical Demographics)
CREATE TABLE IF NOT EXISTS patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    date_of_birth DATE NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    blood_group VARCHAR(5),
    emergency_contact VARCHAR(20),
    address TEXT,
    CONSTRAINT fk_patient_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 5. APPOINTMENTS TABLE (Schedules and Slot Management)
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time VARCHAR(10) NOT NULL,
    status ENUM('Scheduled', 'Completed', 'Cancelled', 'In-Progress') DEFAULT 'Scheduled',
    reason_for_visit TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_appt_patient FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    CONSTRAINT fk_appt_doctor FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE,
    -- Prevent double booking of a doctor at the same date and time slot
    CONSTRAINT uq_doctor_slot UNIQUE (doctor_id, appointment_date, appointment_time)
) ENGINE=InnoDB;

-- 6. PRESCRIPTIONS / MEDICAL RECORDS TABLE
CREATE TABLE IF NOT EXISTS prescriptions (
    prescription_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL UNIQUE,
    diagnosis TEXT NOT NULL,
    medicines TEXT NOT NULL,
    doctor_notes TEXT,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_presc_appt FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 7. BILLINGS TABLE (Financial Transaction Tracking)
CREATE TABLE IF NOT EXISTS billings (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL UNIQUE,
    amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    tax DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    payment_status ENUM('Unpaid', 'Paid', 'Refunded') DEFAULT 'Unpaid',
    payment_method VARCHAR(50),
    payment_date TIMESTAMP NULL,
    CONSTRAINT fk_bill_appt FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE CASCADE,
    CONSTRAINT chk_bill_amount CHECK (amount >= 0)
) ENGINE=InnoDB;

-- 8. AUDIT LOGS TABLE
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- ----------------------------------------------------------------------------
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_appt_date ON appointments(appointment_date);
CREATE INDEX idx_appt_patient ON appointments(patient_id);
CREATE INDEX idx_appt_doctor ON appointments(doctor_id);
CREATE INDEX idx_bill_status ON billings(payment_status);

-- ----------------------------------------------------------------------------
-- VIEWS FOR REPORTING & ANALYTICS
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW view_appointment_details AS
SELECT 
    a.appointment_id,
    a.appointment_date,
    a.appointment_time,
    a.status AS appointment_status,
    a.reason_for_visit,
    pu.full_name AS patient_name,
    pu.email AS patient_email,
    pu.phone AS patient_phone,
    p.blood_group,
    du.full_name AS doctor_name,
    d.specialization,
    dept.department_name,
    d.consultation_fee,
    b.bill_id,
    b.total_amount,
    b.payment_status
FROM appointments a
JOIN patients p ON a.patient_id = p.patient_id
JOIN users pu ON p.user_id = pu.user_id
JOIN doctors d ON a.doctor_id = d.doctor_id
JOIN users du ON d.user_id = du.user_id
JOIN departments dept ON d.department_id = dept.department_id
LEFT JOIN billings b ON a.appointment_id = b.appointment_id;

-- ----------------------------------------------------------------------------
-- SAMPLE SEED DATA
-- ----------------------------------------------------------------------------
INSERT INTO departments (department_name, description, head_doctor) VALUES
('Cardiology', 'Heart health and cardiovascular disorders', 'Dr. Sarah Connor'),
('Neurology', 'Disorders of the brain, spinal cord, and nerves', 'Dr. Stephen Strange'),
('Orthopedics', 'Musculoskeletal system, bones, and joints', 'Dr. Gregory House'),
('Pediatrics', 'Comprehensive medical care for infants and children', 'Dr. Meredith Grey');

-- Password for all seed users is 'Admin@123' (stored as scrypt/pbkdf2 hash)
INSERT INTO users (email, password_hash, full_name, role, phone) VALUES
('admin@apexmed.com', 'scrypt:32768:8:1$7f9G9t6q0v1w...$placeholder', 'Hospital Administrator', 'admin', '555-0100'),
('doctor.carter@apexmed.com', 'scrypt:32768:8:1$7f9G9t6q0v1w...$placeholder', 'Dr. John Carter', 'doctor', '555-0101'),
('doctor.grey@apexmed.com', 'scrypt:32768:8:1$7f9G9t6q0v1w...$placeholder', 'Dr. Meredith Grey', 'doctor', '555-0102'),
('patient.alice@gmail.com', 'scrypt:32768:8:1$7f9G9t6q0v1w...$placeholder', 'Alice Johnson', 'patient', '555-0103');
