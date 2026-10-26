"""
ApexMed: Hospital & Healthcare Records Management System (H-RMS)
Automated Test Suite (SDLC Testing Phase)
Tests Authentication, RBAC, Data Validation, SQL Injection Immunity,
Database Transactions, Constraint Violations, and Clinical Workflows.
"""

import unittest
import os
import sys

# Ensure parent directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from database import get_db, init_db


class ApexMedSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test client and ensure test database is initialized."""
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        cls.client = app.test_client()
        init_db()

    def setUp(self):
        """Clear session before each test."""
        with self.client.session_transaction() as sess:
            sess.clear()

    # -------------------------------------------------------------------------
    # TEST SUITE 1: LOGIN VALIDATION & AUTHENTICATION
    # -------------------------------------------------------------------------
    def test_tc01_unauthenticated_redirect_to_login(self):
        """TC01: Verify root URL redirects unauthenticated visitors to login page."""
        response = self.client.get("/", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_tc02_login_empty_fields_validation(self):
        """TC02: Verify login with empty fields fails validation."""
        response = self.client.post("/login", data={"email": "", "password": ""}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Email address is mandatory", response.data)
        self.assertIn(b"Password field cannot be empty", response.data)

    def test_tc03_login_invalid_email_format(self):
        """TC03: Verify login with invalid email syntax fails validation."""
        response = self.client.post(
            "/login",
            data={"email": "invalid-email-address", "password": "SecretPassword123"},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please enter a valid email format", response.data)

    def test_tc04_login_incorrect_password(self):
        """TC04: Verify login fails with incorrect password."""
        response = self.client.post(
            "/login",
            data={"email": "admin@apexmed.com", "password": "WrongPassword999"},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid credentials", response.data)

    def test_tc05_sql_injection_immunity(self):
        """TC05: Verify login is immune to classical SQL Injection attacks."""
        sql_injection_payload = "admin@apexmed.com' OR '1'='1"
        response = self.client.post(
            "/login",
            data={"email": sql_injection_payload, "password": "' OR '1'='1"},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        # Should not log in as admin, should fail format or credentials
        with self.client.session_transaction() as sess:
            self.assertNotIn("user_id", sess)

    def test_tc06_admin_login_success(self):
        """TC06: Verify valid Admin credentials grant access to Admin dashboard."""
        response = self.client.post(
            "/login",
            data={"email": "admin@apexmed.com", "password": "Admin@123"},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Master Appointment Registry", response.data)
        self.assertIn(b"Apex Administrator", response.data)

    def test_tc07_doctor_login_success(self):
        """TC07: Verify valid Doctor credentials grant access to Doctor dashboard."""
        response = self.client.post(
            "/login",
            data={"email": "dr.vance@apexmed.com", "password": "Admin@123"},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Patient Consultation Queue", response.data)
        self.assertIn(b"Dr. Marcus Vance", response.data)

    def test_tc08_patient_login_success(self):
        """TC08: Verify valid Patient credentials grant access to Patient dashboard."""
        response = self.client.post(
            "/login",
            data={"email": "patient.alice@gmail.com", "password": "Admin@123"},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Book Doctor Appointment", response.data)
        self.assertIn(b"Alice Johnson", response.data)

    # -------------------------------------------------------------------------
    # TEST SUITE 2: ACCESS CONTROL & AUTHORIZATION (RBAC)
    # -------------------------------------------------------------------------
    def test_tc09_rbac_unauthorized_dashboard_access(self):
        """TC09: Verify Patient cannot access Admin dashboard without admin role."""
        # Sign in as patient
        self.client.post("/login", data={"email": "patient.alice@gmail.com", "password": "Admin@123"})
        # Attempt to access admin dashboard
        response = self.client.get("/admin/dashboard", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Unauthorized access. Admin privileges required.", response.data)

    # -------------------------------------------------------------------------
    # TEST SUITE 3: REGISTRATION & DATABASE INTEGRITY
    # -------------------------------------------------------------------------
    def test_tc10_patient_registration_flow(self):
        """TC10: Verify new patient registration successfully inserts records in users & patients."""
        test_email = "test.patient.sdlc@example.com"
        # Cleanup in case already exists
        conn = get_db()
        conn.execute("DELETE FROM users WHERE email = ?;", (test_email,))
        conn.commit()
        conn.close()

        reg_data = {
            "full_name": "SDLC Automated Tester",
            "email": test_email,
            "phone": "+1-555-0999",
            "password": "Password@123",
            "confirm_password": "Password@123",
            "date_of_birth": "1995-07-20",
            "gender": "Female",
            "blood_group": "B+",
            "emergency_contact": "+1-555-1111",
            "address": "404 Test Parkway, Silicon Valley"
        }
        response = self.client.post("/register", data=reg_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Registration successful", response.data)

        # Verify database record exists
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT u.user_id, u.role, p.blood_group FROM users u JOIN patients p ON u.user_id = p.user_id WHERE u.email = ?;", (test_email,))
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["role"], "patient")
        self.assertEqual(row["blood_group"], "B+")
        conn.close()

    def test_tc11_duplicate_email_registration_prevention(self):
        """TC11: Verify unique constraint prevents registering existing email."""
        reg_data = {
            "full_name": "Duplicate Alice",
            "email": "patient.alice@gmail.com",
            "phone": "+1-555-0301",
            "password": "Password@123",
            "confirm_password": "Password@123",
            "date_of_birth": "1994-05-14",
            "gender": "Female",
            "blood_group": "O+",
            "emergency_contact": "555-9999",
            "address": "742 Evergreen"
        }
        response = self.client.post("/register", data=reg_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"An account with this email address already exists", response.data)

    # -------------------------------------------------------------------------
    # TEST SUITE 4: TRANSACTIONS & CONSTRAINT ENFORCEMENT
    # -------------------------------------------------------------------------
    def test_tc12_appointment_booking_and_billing_generation(self):
        """TC12: Verify booking an appointment generates both appointment and billing records."""
        # Clean up any previous test appointment for this slot to ensure test idempotence
        conn = get_db()
        conn.execute("DELETE FROM appointments WHERE doctor_id = 3 AND appointment_date = '2026-11-15' AND appointment_time = '10:00 AM';")
        conn.commit()
        conn.close()

        # Login as patient Alice
        self.client.post("/login", data={"email": "patient.alice@gmail.com", "password": "Admin@123"})

        booking_data = {
            "doctor_id": "3",  # Dr. Alan Grant
            "appointment_date": "2026-11-15",
            "appointment_time": "10:00 AM",
            "reason_for_visit": "Persistent right knee pain after marathon."
        }
        response = self.client.post("/patient/book-appointment", data=booking_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"appointment has been successfully scheduled", response.data)

        # Check DB for appointment and billing
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.appointment_id, b.bill_id, b.payment_status, b.total_amount 
            FROM appointments a 
            JOIN billings b ON a.appointment_id = b.appointment_id 
            WHERE a.doctor_id = 3 AND a.appointment_date = '2026-11-15' AND a.appointment_time = '10:00 AM';
        """)
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["payment_status"], "Unpaid")
        self.assertGreater(row["total_amount"], 0)
        conn.close()

    def test_tc13_doctor_slot_double_booking_collision_prevention(self):
        """TC13: Verify multi-column UNIQUE constraint prevents double-booking same doctor slot."""
        # Clean up any previous test appointment for this slot to ensure test idempotence
        conn = get_db()
        conn.execute("DELETE FROM appointments WHERE doctor_id = 3 AND appointment_date = '2026-12-01' AND appointment_time = '09:00 AM';")
        conn.commit()
        conn.close()

        # Patient Alice books slot with Doctor 3 on 2026-12-01 at 09:00 AM
        self.client.post("/login", data={"email": "patient.alice@gmail.com", "password": "Admin@123"})
        self.client.post("/patient/book-appointment", data={
            "doctor_id": "3",
            "appointment_date": "2026-12-01",
            "appointment_time": "09:00 AM",
            "reason_for_visit": "First checkup."
        })

        # Patient Bob logs in and tries to book exact same slot with Doctor 3
        self.client.post("/login", data={"email": "patient.bob@gmail.com", "password": "Admin@123"})
        response = self.client.post("/patient/book-appointment", data={
            "doctor_id": "3",
            "appointment_date": "2026-12-01",
            "appointment_time": "09:00 AM",
            "reason_for_visit": "Conflicting checkup."
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"already booked for that date and time slot", response.data)

    def test_tc14_bill_payment_transaction(self):
        """TC14: Verify patient can pay pending invoice and status changes to Paid."""
        # Login as Bob who has an unpaid bill seeded
        self.client.post("/login", data={"email": "patient.bob@gmail.com", "password": "Admin@123"})
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT bill_id FROM billings WHERE payment_status = 'Unpaid' LIMIT 1;")
        bill = cursor.fetchone()
        conn.close()

        if bill:
            bill_id = bill["bill_id"]
            response = self.client.post(f"/patient/pay-bill/{bill_id}", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"marked as Paid", response.data)

            # Confirm in DB
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT payment_status FROM billings WHERE bill_id = ?;", (bill_id,))
            updated_bill = cursor.fetchone()
            self.assertEqual(updated_bill["payment_status"], "Paid")
            conn.close()

    def test_tc15_doctor_prescription_upsert(self):
        """TC15: Verify doctor can record clinical diagnosis and prescription for an appointment."""
        self.client.post("/login", data={"email": "dr.vance@apexmed.com", "password": "Admin@123"})
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT appointment_id FROM appointments WHERE doctor_id = 1 LIMIT 1;")
        appt = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(appt)
        appt_id = appt["appointment_id"]

        consult_data = {
            "appointment_id": appt_id,
            "status": "Completed",
            "diagnosis": "Automated Unit Test - Acute Rhinitis",
            "medicines": "Cetirizine 10mg once daily x 5 days",
            "doctor_notes": "Steam inhalation recommended twice daily."
        }
        response = self.client.post("/doctor/update-appointment", data=consult_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"updated successfully", response.data)

        # Verify prescription in database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT diagnosis, medicines FROM prescriptions WHERE appointment_id = ?;", (appt_id,))
        presc = cursor.fetchone()
        self.assertEqual(presc["diagnosis"], "Automated Unit Test - Acute Rhinitis")
        conn.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
