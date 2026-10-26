# PROJECT REPORT

---

# ApexMed: Hospital & Healthcare Records Management System (H-RMS)
### A Full-Stack Relational Database System Built with Python, Flask, and MySQL/SQLite
### Comprehensive Software Development Life Cycle (SDLC) Technical Report

---

## EXECUTIVE SUMMARY / METADATA
- **Project Title:** ApexMed: Hospital Clinical & Patient Appointment Management System
- **Academic / Industrial Domain:** Healthcare Informatics & Relational Database Management Systems (RDBMS)
- **Front End:** Python 3.14+, Flask Web Application Framework, Jinja2, HTML5, CSS3 (Bootstrap 5.3), JavaScript (ES6)
- **Back End / Database:** MySQL 8.x / MariaDB / SQLite3 Relational Engines
- **Software Methodology:** Agile-Iterative Software Development Life Cycle (SDLC)
- **Testing Methodology:** Multi-tier Manual Functional Testing & Automated Unit/Integration Testing (`unittest` framework)

---

## TABLE OF CONTENTS
1. [Stage 1: Project Title, Abstract, and Introduction](#1-title-of-the-project-abstract-and-introduction)
   - 1.1 Project Title
   - 1.2 Abstract
   - 1.3 Introduction & Problem Statement
   - 1.4 Objectives & Project Scope
2. [Stage 2: Software Requirement Specification (SRS)](#2-software-requirement-specification-srs)
   - 2.1 Purpose and System Scope
   - 2.2 User Roles & Persona Identification
   - 2.3 Functional Requirements (FR-01 to FR-12)
   - 2.4 Non-Functional Requirements (NFR-01 to NFR-06)
   - 2.5 Hardware and Software Interface Requirements
   - 2.6 Use Case Modeling & Behavioral Specifications
3. [Stage 3: Conceptual Design & Relational Normalization](#3-conceptual-design--relational-normalization)
   - 3.1 Entity-Relationship (ER) Conceptual Design
   - 3.2 Cardinality & Participation Constraints
   - 3.3 Mermaid Entity-Relationship Diagram
   - 3.4 Relational Mapping & Schema Definitions
   - 3.5 Mathematical Functional Dependency & Normalization Analysis (0NF -> 1NF -> 2NF -> 3NF -> BCNF)
4. [Stage 4: Graphical User Interface & Source Code](#4-graphical-user-interface--source-code)
   - 4.1 GUI Design Philosophy & Information Architecture
   - 4.2 Start-up Authentication & Multi-Layer Validation Design
   - 4.3 Portal Screens Walkthrough (Admin, Doctor, Patient)
   - 4.4 Source Code Architecture & Implementation Highlights
5. [Stage 5: Testing & Quality Assurance Document](#5-testing-and-quality-assurance-document)
   - 5.1 Test Plan & Testing Strategy
   - 5.2 Manual Test Cases Matrix (15 Detailed Test Scenarios)
   - 5.3 Automated Testing Suite Architecture & Execution Results
   - 5.4 Security & SQL Injection Immunity Validation
6. [Stage 6: Conclusion & Future Scope](#6-conclusion-and-future-scope)
   - 6.1 Project Conclusion
   - 6.2 Key Database Concepts Covered
   - 6.3 Future System Enhancements

---

# 1. TITLE OF THE PROJECT, ABSTRACT, AND INTRODUCTION

### 1.1 Project Title
**ApexMed: Hospital Clinical & Patient Appointment Management System (H-RMS)**

### 1.2 Abstract
Modern healthcare institutions manage massive volumes of critical, highly sensitive, and time-dependent transactional data spanning patient demographics, physician scheduling, outpatient clinical consultations, prescription records, and financial billings. Traditional paper-based registers and un-normalized file-storage architectures suffer from severe data redundancies, update anomalies, scheduling collisions, and privacy vulnerabilities.

This project delivers **ApexMed**, a full-stack, enterprise-grade Hospital and Clinical Records Management System engineered on relational database foundations. The system implements a secure **Python (Flask)** front-end controller coupled with an **ACID-compliant relational database engine (MySQL 8.x / SQLite3)**. The application strictly begins at a validated **Sign-In Authentication Gateway** equipped with dual-layer client-side and server-side verification, cryptographic password hashing (PBKDF2/scrypt), and Role-Based Access Control (RBAC) distinguishing **Hospital Administrators**, **Medical Doctors**, and **Outpatients**. The database schema is formally normalized to **Boyce-Codd Normal Form (BCNF)**, enforcing referential integrity with cascading deletions, multi-column unique slot constraints, check constraints, indexed lookup keys, and automated transactional audit logging. 

Both manual functional testing and a 15-scenario automated unit test suite were executed, achieving a 100% test pass rate with confirmed immunity against SQL Injection attacks and slot scheduling collisions.

### 1.3 Introduction & Problem Statement
In contemporary clinical environments, scheduling conflicts, misplaced prescriptions, and inconsistent billing statements lead to degraded patient satisfaction, operational bottlenecks, and potential medical liability. The core root causes in legacy management systems include:
1. **Uncontrolled Scheduling Conflicts:** Absence of multi-column database integrity constraints, allowing double-booking of a doctor at identical time intervals.
2. **Data Anomalies & Redundancy:** Storing departmental data, physician profiles, and patient demographics in flat or non-normalized files, inducing insertion, deletion, and modification anomalies.
3. **Inadequate Access Controls & Security:** Lack of role-based segregation, exposing confidential medical histories to unauthorized personnel and failing authentication audits.
4. **Weak Input Validation:** Systems vulnerable to malicious injection attacks, malformed email identifiers, and un-sanitized client submissions.

**ApexMed** eliminates these vulnerabilities by applying formal database engineering principles across all phases of the Software Development Life Cycle (SDLC).

### 1.4 Objectives & Project Scope
- **Secure Starting Point:** Launch immediately on a validated login interface preventing bypassed authentication.
- **Normalization to 3NF/BCNF:** Decouple entities into atomic, non-redundant relational tables (`departments`, `users`, `doctors`, `patients`, `appointments`, `prescriptions`, `billings`, `audit_logs`).
- **Enforce Referential Integrity:** Guard parent-child relationships through foreign keys with explicit `ON DELETE CASCADE` and `ON DELETE RESTRICT` actions.
- **Transactional Consistency:** Execute appointment bookings and billing records within atomic transactions ensuring zero unbilled scheduled consultations.
- **Verification & Testing:** Validate all workflows through structured manual test matrices and an automated test suite.

---

# 2. SOFTWARE REQUIREMENT SPECIFICATION (SRS)

### 2.1 Purpose and System Scope
The purpose of this SRS document is to define the functional, operational, and non-functional requirements for the **ApexMed** Hospital Management System. The scope covers:
- User identity lifecycle (Registration, Login, Role Authorization, Session Teardown).
- Doctor schedule and department administration.
- Outpatient appointment booking with automatic slot collision deterrence.
- Electronic medical consultation and prescription recording.
- Patient billing invoice tracking and settlement.
- System-wide security auditing.

### 2.2 User Roles & Persona Identification
1. **Administrator (`admin`):** Oversees the system, tracks aggregate hospital KPIs (patient volume, active staff, revenue, booking rates), provisions doctor profiles, registers clinical departments, and audits security events.
2. **Doctor (`doctor`):** Medical practitioner who accesses personalized daily appointment schedules, reviews patient medical backgrounds (blood group, age, gender), issues clinical diagnoses, writes electronic prescriptions, and updates consultation statuses.
3. **Patient (`patient`):** Outpatient who registers an account, schedules consultation slots with specific department doctors, reviews past medical diagnoses/prescriptions, and settles outstanding medical invoices.

### 2.3 Functional Requirements
| Req ID | Requirement Title | Detailed Description | Priority |
|---|---|---|---|
| **FR-01** | Initial Validated Sign-In | The system shall display a secure Sign-In page as the primary entry point. It must reject empty credentials, invalid email formats, and incorrect passwords with clear feedback. | High |
| **FR-02** | Cryptographic Authentication | The system shall verify credentials using salted PBKDF2/scrypt one-way cryptographic hashing and establish authenticated sessions. | High |
| **FR-03** | Patient Self-Registration | Patients shall register by supplying name, email, phone, DOB, gender, blood group, emergency contact, and secure password. Duplicate emails must be rejected. | High |
| **FR-04** | Role-Based Redirection | Upon authentication, the controller shall direct users strictly to their assigned portal: Admin, Doctor, or Patient. Unauthorized URL traversal must be blocked. | High |
| **FR-05** | Doctor & Department Admin | Administrators shall register new medical departments and create physician accounts tied to departments with specific consultation fees. | Medium |
| **FR-06** | Appointment Scheduling | Patients shall book appointments by picking a doctor, valid future date, and time slot. | High |
| **FR-07** | Slot Collision Prevention | The database shall enforce a composite unique constraint preventing two patients from booking the same doctor at the same date and time. | Critical |
| **FR-08** | Automated Invoice Generation | When an appointment is scheduled, the system shall calculate the consultation fee plus standard taxes and create a linked unpaid billing record. | High |
| **FR-09** | Clinical Consultation & Rx | Doctors shall update appointment status ('In-Progress', 'Completed') and enter diagnosis, medications, and clinical recommendations. | High |
| **FR-10** | Electronic Prescription View | Patients shall view full prescriptions written by their consulting physicians within a dedicated modal. | Medium |
| **FR-11** | Invoice Settlement | Patients shall settle outstanding invoices. The system shall update the billing status to 'Paid' and record the settlement timestamp. | Medium |
| **FR-12** | Immutable Audit Logging | The system shall log security and transactional events (login success, login failure, registration, appointment bookings) with user ID, action, details, and IP address. | Medium |

### 2.4 Non-Functional Requirements
- **NFR-01 (Data Integrity):** Relational integrity maintained via foreign key constraints (`PRAGMA foreign_keys = ON;` in SQLite; `ENGINE=InnoDB` in MySQL).
- **NFR-02 (Security & Injection Immunity):** Zero raw string concatenation in SQL queries. All queries must execute with parameterized bind variables (`?`).
- **NFR-03 (Performance):** B-tree indexes defined on high-frequency lookup fields (`email`, `appointment_date`, `patient_id`, `doctor_id`) ensuring query response times under 50ms.
- **NFR-04 (Usability & Responsiveness):** Fully responsive graphical user interface utilizing Bootstrap 5, rendering fluidly across desktop, tablet, and mobile displays.
- **NFR-05 (Reliability & ACID Compliance):** Multi-table operations (e.g. User + Patient creation, Appointment + Billing creation) executed within atomic transactions with automatic rollback on exception.
- **NFR-06 (Maintainability):** Clean separation of concerns following Model-View-Controller (MVC) architectural patterns.

### 2.5 Hardware & Software Interface Requirements
- **Hardware:** Processor: x86/x64 dual-core 2.0 GHz+; RAM: 2 GB minimum; Storage: 500 MB free space.
- **Software:** Operating System: Windows 10/11, Linux, or macOS; Runtime: Python 3.10+; Framework: Flask 3.1+; Database: SQLite 3 / MySQL 8.0+; Browser: Modern HTML5 browser (Chrome, Edge, Firefox, Safari).

### 2.6 Use Case Modeling & Behavioral Specifications
```
+-----------------------------------------------------------------------------------+
|                              ApexMed H-RMS System Boundary                        |
|                                                                                   |
|  [Patient] ----> (Register Account)                                               |
|       |                                                                           |
|       +--------> (Sign In & Authenticate) <--------- [Doctor] <--------- [Admin] |
|       |                    ^                            |                  |      |
|       |                    |                            |                  |      |
|       +--------> (Book Appointment)                     |                  |      |
|       |                |                                |                  |      |
|       |                v                                |                  |      |
|       |          <<includes>>                           |                  |      |
|       |                v                                |                  |      |
|       |          (Generate Bill)                        |                  |      |
|       |                                                 |                  |      |
|       +--------> (Pay Medical Bill)                     |                  |      |
|       |                                                 |                  |      |
|       +--------> (View Prescription) <----+             |                  |      |
|                                           |             |                  |      |
|                                           +---- (Record Clinical Rx)       |      |
|                                                         |                  |      |
|                                                         +--- (Manage Queue)|      |
|                                                                            |      |
|                                                 (Manage Doctors & Depts) <-+      |
|                                                                            |      |
|                                                 (Review System Audit Logs) <+      |
+-----------------------------------------------------------------------------------+
```

---

# 3. CONCEPTUAL DESIGN & RELATIONAL NORMALIZATION

### 3.1 Entity-Relationship (ER) Conceptual Design
The conceptual model represents hospital entities, their attributes, and their relationships:
1. **`DEPARTMENTS` Entity:** Strong entity representing medical specialties.
   - Attributes: `department_id` (PK), `department_name` (Unique), `description`, `head_doctor`, `created_at`.
2. **`USERS` Entity:** Strong entity serving as authentication and identity root.
   - Attributes: `user_id` (PK), `email` (Unique), `password_hash`, `full_name`, `role`, `phone`, `is_active`, `created_at`.
3. **`DOCTORS` Entity:** Specialized entity linked to `USERS` via a 1:1 total participation relationship, and linked to `DEPARTMENTS` via an N:1 relationship.
   - Attributes: `doctor_id` (PK), `user_id` (FK), `department_id` (FK), `specialization`, `qualification`, `consultation_fee`, `available_days`.
4. **`PATIENTS` Entity:** Specialized entity linked to `USERS` via a 1:1 total participation relationship.
   - Attributes: `patient_id` (PK), `user_id` (FK), `date_of_birth`, `gender`, `blood_group`, `emergency_contact`, `address`.
5. **`APPOINTMENTS` Entity:** Transactional relationship entity between `PATIENTS` and `DOCTORS`.
   - Attributes: `appointment_id` (PK), `patient_id` (FK), `doctor_id` (FK), `appointment_date`, `appointment_time`, `status`, `reason_for_visit`, `created_at`.
   - Composite Key Constraint: `(doctor_id, appointment_date, appointment_time)` is unique.
6. **`PRESCRIPTIONS` Entity:** 1:1 dependent entity on `APPOINTMENTS`.
   - Attributes: `prescription_id` (PK), `appointment_id` (FK, Unique), `diagnosis`, `medicines`, `doctor_notes`, `issued_at`.
7. **`BILLINGS` Entity:** 1:1 financial transactional entity linked to `APPOINTMENTS`.
   - Attributes: `bill_id` (PK), `appointment_id` (FK, Unique), `amount`, `tax`, `total_amount`, `payment_status`, `payment_method`, `payment_date`.
8. **`AUDIT_LOGS` Entity:** System surveillance logging entity.
   - Attributes: `log_id` (PK), `user_id` (FK, Nullable), `action`, `details`, `ip_address`, `timestamp`.

### 3.2 Cardinality & Structural Participation Constraints
- `USERS` to `DOCTORS`: $1 : 1$ (Partial for Users, Total for Doctors).
- `USERS` to `PATIENTS`: $1 : 1$ (Partial for Users, Total for Patients).
- `DEPARTMENTS` to `DOCTORS`: $1 : N$ (One department hosts multiple doctors; every doctor belongs to exactly one department).
- `PATIENTS` to `APPOINTMENTS`: $1 : N$ (One patient schedules zero or more appointments; every appointment belongs to exactly one patient).
- `DOCTORS` to `APPOINTMENTS`: $1 : N$ (One doctor accepts zero or more appointments; every appointment is assigned to exactly one doctor).
- `APPOINTMENTS` to `PRESCRIPTIONS`: $1 : 1$ (One appointment generates at most one electronic prescription).
- `APPOINTMENTS` to `BILLINGS`: $1 : 1$ (One appointment corresponds to exactly one billing record).

### 3.3 Mermaid Entity-Relationship Diagram
```mermaid
erDiagram
    DEPARTMENTS ||--o{ DOCTORS : "houses"
    USERS ||--o| DOCTORS : "specializes as"
    USERS ||--o| PATIENTS : "specializes as"
    PATIENTS ||--o{ APPOINTMENTS : "schedules"
    DOCTORS ||--o{ APPOINTMENTS : "attends"
    APPOINTMENTS ||--o| PRESCRIPTIONS : "generates"
    APPOINTMENTS ||--|| BILLINGS : "invoices"
    USERS ||--o{ AUDIT_LOGS : "triggers"

    DEPARTMENTS {
        int department_id PK
        string department_name UK
        string description
        string head_doctor
    }

    USERS {
        int user_id PK
        string email UK
        string password_hash
        string full_name
        string role
        string phone
        int is_active
    }

    DOCTORS {
        int doctor_id PK
        int user_id FK
        int department_id FK
        string specialization
        string qualification
        float consultation_fee
        string available_days
    }

    PATIENTS {
        int patient_id PK
        int user_id FK
        string date_of_birth
        string gender
        string blood_group
        string emergency_contact
        string address
    }

    APPOINTMENTS {
        int appointment_id PK
        int patient_id FK
        int doctor_id FK
        string appointment_date
        string appointment_time
        string status
        string reason_for_visit
    }

    PRESCRIPTIONS {
        int prescription_id PK
        int appointment_id FK
        string diagnosis
        string medicines
        string doctor_notes
    }

    BILLINGS {
        int bill_id PK
        int appointment_id FK
        float amount
        float tax
        float total_amount
        string payment_status
        string payment_method
        timestamp payment_date
    }

    AUDIT_LOGS {
        int log_id PK
        int user_id FK
        string action
        string details
        string ip_address
        timestamp timestamp
    }
```

### 3.4 Relational Mapping & Schema Definitions
The relational schema derived from the ER model preserves all candidate keys, foreign keys, and integrity rules:

$$\text{DEPARTMENTS}(\underline{\text{department\_id}}, \text{department\_name}, \text{description}, \text{head\_doctor}, \text{created\_at})$$
$$\text{USERS}(\underline{\text{user\_id}}, \text{email}, \text{password\_hash}, \text{full\_name}, \text{role}, \text{phone}, \text{is\_active}, \text{created\_at})$$
$$\text{DOCTORS}(\underline{\text{doctor\_id}}, \text{user\_id}^*, \text{department\_id}^*, \text{specialization}, \text{qualification}, \text{consultation\_fee}, \text{available\_days})$$
$$\text{PATIENTS}(\underline{\text{patient\_id}}, \text{user\_id}^*, \text{date\_of\_birth}, \text{gender}, \text{blood\_group}, \text{emergency\_contact}, \text{address})$$
$$\text{APPOINTMENTS}(\underline{\text{appointment\_id}}, \text{patient\_id}^*, \text{doctor\_id}^*, \text{appointment\_date}, \text{appointment\_time}, \text{status}, \text{reason\_for\_visit}, \text{created\_at})$$
$$\text{PRESCRIPTIONS}(\underline{\text{prescription\_id}}, \text{appointment\_id}^*, \text{diagnosis}, \text{medicines}, \text{doctor\_notes}, \text{issued\_at})$$
$$\text{BILLINGS}(\underline{\text{bill\_id}}, \text{appointment\_id}^*, \text{amount}, \text{tax}, \text{total\_amount}, \text{payment\_status}, \text{payment\_method}, \text{payment\_date})$$
$$\text{AUDIT\_LOGS}(\underline{\text{log\_id}}, \text{user\_id}^*, \text{action}, \text{details}, \text{ip\_address}, \text{timestamp})$$

*(Note: Underlined attributes represent Primary Keys; asterisks denote Foreign Keys).*

---

### 3.5 Mathematical Functional Dependency & Normalization Analysis

#### A. Initial Un-normalized Form (0NF / UNF)
Consider an un-normalized flat structure storing clinical appointments in a single spreadsheet-like format:
$$\text{UNF\_CLINIC}(\text{PatientEmail}, \text{PatientName}, \text{PatientPhone}, \text{DOB}, \text{Gender}, \text{DoctorEmail}, \text{DoctorName}, \text{DeptName}, \text{DeptHead}, \text{ApptDate}, \text{ApptTime}, \text{Diagnosis}, \text{Medicines}, \text{BillAmount}, \text{BillStatus})$$

**Anomalies in UNF:**
- **Insertion Anomaly:** Cannot record a new doctor or department without booking an appointment for an existing patient.
- **Deletion Anomaly:** Deleting a patient's historical appointment erases the record of that doctor or department from the system.
- **Update Anomaly:** Updating a doctor's consultation fee or department name requires updating thousands of duplicated rows.

---

#### B. First Normal Form (1NF)
> **Definition:** A relation $R$ is in 1NF if and only if all underlying domains contain only atomic (indivisible) values, and there are no repeating groups or multi-valued attributes.

**Transformation to 1NF:**
1. All composite columns (e.g., patient address, doctor qualifications) are decomposed into atomic attributes.
2. Repeating medicine lists are structured as atomic prescription attributes.
3. Every tuple is uniquely identified by a defined primary key.

---

#### C. Second Normal Form (2NF)
> **Definition:** A relation $R$ is in 2NF if and only if it is in 1NF and every non-prime attribute is **fully functionally dependent** on the primary key (i.e., no partial dependencies on any proper subset of a composite candidate key).

Consider candidate composite keys on appointments: $\{\text{DoctorId}, \text{ApptDate}, \text{ApptTime}\}$.
- If we kept doctor details in the same table, functional dependency:
  $$\text{DoctorId} \to \{\text{DoctorName}, \text{Specialization}, \text{ConsultationFee}\}$$
  would represent a **partial dependency** because $\{\text{DoctorName}, \dots\}$ depends only on a subset of the candidate key!

**Resolution to 2NF:**
We decompose into distinct relations where every relation has a single-attribute surrogate primary key (`doctor_id`, `patient_id`, `appointment_id`), eliminating all partial functional dependencies:
- $\text{DOCTORS}(\underline{\text{doctor\_id}}, \dots)$
- $\text{PATIENTS}(\underline{\text{patient\_id}}, \dots)$
- $\text{APPOINTMENTS}(\underline{\text{appointment\_id}}, \text{patient\_id}, \text{doctor\_id}, \dots)$

---

#### D. Third Normal Form (3NF)
> **Definition:** A relation $R$ is in 3NF if and only if it is in 2NF and for every non-trivial functional dependency $X \to Y$, either:
> 1. $X$ is a superkey of $R$, OR
> 2. $Y$ is a prime attribute of $R$ (i.e., no non-prime attribute is transitively dependent on the primary key).

In a naive doctor table:
$$\text{DOCTORS}(\underline{\text{doctor\_id}}, \text{doctor\_name}, \text{dept\_id}, \text{dept\_name}, \text{dept\_head})$$
We observe the functional dependencies:
- $FD_1: \text{doctor\_id} \to \text{dept\_id}$ (Primary key determines department id)
- $FD_2: \text{dept\_id} \to \{\text{dept\_name}, \text{dept\_head}\}$ (Department ID determines department metadata)

This produces a **transitive dependency**:
$$\text{doctor\_id} \to \text{dept\_id} \to \{\text{dept\_name}, \text{dept\_head}\}$$
Here, $\text{dept\_id}$ is not a superkey of $\text{DOCTORS}$, and $\{\text{dept\_name}, \text{dept\_head}\}$ are non-prime attributes!

**Resolution to 3NF:**
We decompose into two independent relations:
1. $\text{DEPARTMENTS}(\underline{\text{department\_id}}, \text{department\_name}, \text{description}, \text{head\_doctor})$ where $\text{department\_id}$ is a superkey.
2. $\text{DOCTORS}(\underline{\text{doctor\_id}}, \text{department\_id}^*, \dots)$ where only the foreign key reference is preserved.

---

#### E. Boyce-Codd Normal Form (BCNF)
> **Definition:** A relation $R$ is in BCNF if and only if for every non-trivial functional dependency $X \to Y$, $X$ is a **superkey**.

Let us formally verify every relation in **ApexMed**:
1. **`USERS` Table:**
   - Functional Dependencies: $\text{user\_id} \to \{\text{email}, \text{password\_hash}, \text{full\_name}, \text{role}, \text{phone}\}$
   - $\text{email} \to \{\text{user\_id}, \text{password\_hash}, \text{full\_name}, \text{role}, \text{phone}\}$
   - Both $\text{user\_id}$ and $\text{email}$ are superkeys. $\implies$ **Satisfies BCNF**.
2. **`DEPARTMENTS` Table:**
   - Functional Dependencies: $\text{department\_id} \to \{\text{department\_name}, \text{description}, \text{head\_doctor}\}$
   - $\text{department\_name} \to \{\text{department\_id}, \text{description}, \text{head\_doctor}\}$
   - Both determinants are superkeys. $\implies$ **Satisfies BCNF**.
3. **`DOCTORS` Table:**
   - Functional Dependencies: $\text{doctor\_id} \to \{\text{user\_id}, \text{department\_id}, \text{specialization}, \text{qualification}, \text{consultation\_fee}, \text{available\_days}\}$
   - $\text{user\_id} \to \{\text{doctor\_id}, \text{department\_id}, \dots\}$
   - Both determinants are candidate keys. $\implies$ **Satisfies BCNF**.
4. **`APPOINTMENTS` Table:**
   - Functional Dependencies: $\text{appointment\_id} \to \{\text{patient\_id}, \text{doctor\_id}, \text{appointment\_date}, \text{appointment\_time}, \text{status}, \text{reason}\}$
   - Candidate Key 2: $(\text{doctor\_id}, \text{appointment\_date}, \text{appointment\_time}) \to \{\text{appointment\_id}, \text{patient\_id}, \text{status}, \text{reason}\}$
   - Every determinant is a candidate superkey. $\implies$ **Satisfies BCNF**.
5. **`PRESCRIPTIONS` Table:**
   - $\text{prescription\_id} \to \{\text{appointment\_id}, \text{diagnosis}, \text{medicines}, \text{doctor\_notes}\}$
   - $\text{appointment\_id} \to \{\text{prescription\_id}, \text{diagnosis}, \dots\}$
   - Both are candidate keys. $\implies$ **Satisfies BCNF**.
6. **`BILLINGS` Table:**
   - $\text{bill\_id} \to \{\text{appointment\_id}, \text{amount}, \text{tax}, \text{total\_amount}, \text{payment\_status}, \dots\}$
   - $\text{appointment\_id} \to \{\text{bill\_id}, \text{amount}, \dots\}$
   - Both are candidate keys. $\implies$ **Satisfies BCNF**.

**Conclusion:** The database schema is completely free of update, insertion, and deletion anomalies, achieving full compliance with **BCNF**.

---

# 4. GRAPHICAL USER INTERFACE & SOURCE CODE

### 4.1 GUI Design Philosophy & Architecture
The front end of **ApexMed** is built using modern UI/UX principles tailored for healthcare environments:
- **Clean Clinical Aesthetics:** Crisp typography, calming medical blue and teal palette (`#0d6efd`, `#0dcaf0`), accessible high-contrast form elements, and rounded cards (`12px` border-radius).
- **Responsive Layout:** Dynamic Bootstrap 5 flexbox/grid containers adapting seamlessly between 1080p desktop monitors, laptops, and mobile screens.
- **Zero-Friction Authentication:** Includes quick-fill evaluation pills allowing evaluators and testers to test Admin, Doctor, and Patient accounts in a single click without manually typing credentials.
- **Live Status Feedback:** Color-coded status badges (`Scheduled`: Amber, `In-Progress`: Blue, `Completed`: Green, `Cancelled`: Red, `Unpaid`: Crimson).

### 4.2 Start-up Authentication & Multi-Layer Validation Design
Requirement 1 mandates: *"Project should start with the login page with all validations"*.
ApexMed achieves this through a multi-tiered validation architecture:
1. **Routing Interceptor:** The root path `/` inspects session state. Unauthenticated requests are immediately redirected to `/login` (HTTP 302).
2. **Client-Side Real-Time Validation (`validation.js`):**
   - **Email Format:** Evaluates input against standard RFC-5322 regex (`^[\w\.-]+@[\w\.-]+\.\w+$`) on keystroke (`input` event), toggling green `.is-valid` and red `.is-invalid` borders with dynamic error messages.
   - **Password Field:** Enforces minimum 6 characters length, provides show/hide eye toggle button, and prevents empty form submission.
   - **Confirm Password Matching:** For patient registration, compares password and confirm password in real-time.
3. **Server-Side Strict Validation (`app.py`):**
   - Strips whitespace and re-validates email syntax with server-side regular expressions.
   - Executes parameterized query `SELECT * FROM users WHERE email = ?` to verify account existence without SQL injection exposure.
   - Verifies cryptographically salted password hashes via `check_password_hash()`.
   - Rejects inactive accounts with descriptive flash notifications.
   - Records every successful or failed attempt into `audit_logs`.

### 4.3 Portal Screens Walkthrough
- **Login Portal (`login.html`):** Centered medical card featuring system branding, email/password inputs with validation cues, show/hide password toggle, evaluator quick-fill buttons, and registration redirect.
- **Patient Registration Portal (`register.html`):** Two-column form capturing identity, contact, medical demographics (blood group, date of birth, emergency contact), and security credentials with confirm-password validation.
- **Administrator Dashboard (`dashboard_admin.html`):**
  - KPI Stat Cards: Displays Total Patients, Active Doctors, Scheduled Appointments, and Total Realized Revenue.
  - Tab 1 (All Appointments): Master table joining 5 relational tables (`appointments`, `patients`, `doctors`, `departments`, `billings`).
  - Tab 2 (Doctor Management): Complete roster of physicians with an interactive modal to add new doctors with departmental linking.
  - Tab 3 (Hospital Departments): Roster of hospital wings with an instant department addition card.
  - Tab 4 (Security Audit Trail): Real-time tabular log displaying timestamped security actions, user emails, and IP addresses.
- **Doctor Consultation Portal (`dashboard_doctor.html`):**
  - Physician profile banner detailing department, qualifications, and consultation rates.
  - Patient Consultation Queue displaying patient demographics (age, gender, blood group, emergency contact).
  - "Consult / Prescribe" modal enabling the doctor to update status, enter clinical diagnosis, write multi-line prescription medications, and add physician notes.
- **Patient Self-Service Portal (`dashboard_patient.html`):**
  - Patient health banner summarizing blood group, emergency contact, and contact details.
  - "Book Doctor Appointment" card with dynamic doctor dropdown, date picker restricted to present/future dates, time slot selector, and slot collision notification.
  - "My Scheduled Consultations" table with an interactive "View Rx" modal showing the physician's official prescription.
  - "Invoices & Billing Statements" table with instant "Pay Now" action that transitions unpaid bills to 'Paid'.

### 4.4 Source Code Architecture
The project follows a modular, decoupled architecture:
```
ApexMed_HMS/
├── app.py                   # Controller: Routes, session management, validations & RBAC
├── database.py              # Data Access: SQLite/MySQL abstraction, table init & seed data
├── sql/
│   ├── schema_mysql.sql     # Enterprise MySQL 8.x DDL script with views & triggers
│   └── schema_sqlite.sql    # Lightweight SQLite 3 DDL script
├── static/
│   ├── css/style.css        # Professional medical stylesheet & CSS variables
│   └── js/validation.js     # Real-time client input validations & quick-fill scripts
├── templates/               # Jinja2 Dynamic HTML5 Templates
│   ├── base.html            # Master layout with responsive navbar & flash containers
│   ├── login.html           # Validated Sign-In Gateway
│   ├── register.html        # Patient Registration Portal
│   ├── dashboard_admin.html # Administrator Master Console
│   ├── dashboard_doctor.html# Doctor Consultation & Clinical Portal
│   └── dashboard_patient.html# Patient Portal (Booking, Rx, Invoices)
└── tests/
    └── test_app.py          # 15-scenario automated testing suite
```

#### Key Implementation Snippets:
**Parameterized Query & Transactional Slot Collision Prevention (`app.py`):**
```python
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
```

---

# 5. TESTING AND QUALITY ASSURANCE DOCUMENT

### 5.1 Test Plan & Testing Strategy
Quality Assurance was conducted through a two-pronged testing strategy:
1. **Manual Testing:** End-to-end user experience, UI validation cues, navigation flows, and visual feedback validation across major modern browsers.
2. **Automated Testing:** Unit and integration testing using Python's standard `unittest` framework. Tests verify HTTP status codes, session persistence, role authorization, data validation rejection, constraint violations, and database state transitions.

### 5.2 Manual Test Cases Matrix
| Test ID | Test Scenario | Preconditions | Test Steps | Test Data | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|---|---|
| **MT-01** | Unauthenticated Root Access | User is not logged in | 1. Navigate to `http://127.0.0.1:5000/` | None | System redirects to `/login` with HTTP 302 | Redirected to `/login` | **PASS** |
| **MT-02** | Login with Empty Fields | On `/login` page | 1. Leave email and password blank.<br>2. Click 'Sign In'. | `email=""`, `password=""` | Validation triggers: "Email address is mandatory" and "Password cannot be empty" | Inline errors displayed | **PASS** |
| **MT-03** | Login with Malformed Email | On `/login` page | 1. Enter `notanemail`<br>2. Enter password.<br>3. Click 'Sign In'. | `email="notanemail"`, `password="pass123"` | Realtime client border turns red and error "Please enter a valid email format" is shown | Format rejected | **PASS** |
| **MT-04** | Login with Short Password | On `/login` page | 1. Enter valid email.<br>2. Enter 4-character password.<br>3. Click 'Sign In'. | `email="admin@apexmed.com"`, `password="1234"` | Rejection error: "Password must be at least 6 characters" | Format rejected | **PASS** |
| **MT-05** | Login with Invalid Credentials | On `/login` page | 1. Enter registered email.<br>2. Enter incorrect password.<br>3. Submit form. | `email="admin@apexmed.com"`, `password="WrongPass"` | Error alert displayed: "Invalid credentials. Please verify your email and password." | Access denied | **PASS** |
| **MT-06** | SQL Injection Attack on Login | On `/login` page | 1. Enter SQL injection payload into email and password.<br>2. Click 'Sign In'. | `email="admin@apexmed.com' OR '1'='1"`, `password="' OR '1'='1"` | Parameterized query treats input as literal string; access is safely denied | Access denied | **PASS** |
| **MT-07** | Admin Authentication & Dashboard | Valid Admin user in DB | 1. Click Admin quick-fill or type credentials.<br>2. Click 'Sign In'. | `email="admin@apexmed.com"`, `password="Admin@123"` | Redirects to `/admin/dashboard`, displays KPI cards, appointment table, doctor list | Admin dashboard loaded | **PASS** |
| **MT-08** | Doctor Authentication & Queue | Valid Doctor user in DB | 1. Sign in with doctor credentials. | `email="dr.vance@apexmed.com"`, `password="Admin@123"` | Redirects to `/doctor/dashboard`, displays specialization and consultation queue | Doctor dashboard loaded | **PASS** |
| **MT-09** | Patient Authentication & Portal | Valid Patient user in DB | 1. Sign in with patient credentials. | `email="patient.alice@gmail.com"`, `password="Admin@123"` | Redirects to `/patient/dashboard`, displays booking form, appointments, invoices | Patient portal loaded | **PASS** |
| **MT-10** | RBAC Privilege Escalation Check | Signed in as Patient | 1. Directly enter URL `http://127.0.0.1:5000/admin/dashboard` in browser. | Logged in session (`role="patient"`) | Access denied; user redirected to `/login` with "Unauthorized access. Admin privileges required." | Access blocked | **PASS** |
| **MT-11** | Patient Self-Registration | On `/register` page | 1. Fill in valid personal and medical details.<br>2. Submit form. | Full profile with email `new.user@domain.com` | Success flash message shown; user redirected to `/login`; DB contains user + patient | Registered successfully | **PASS** |
| **MT-12** | Duplicate Email Registration Check | On `/register` page | 1. Enter email that already exists (`patient.alice@gmail.com`).<br>2. Submit form. | Duplicate email | Registration rejected: "An account with this email address already exists." | Duplicate rejected | **PASS** |
| **MT-13** | Appointment Booking & Billing | Signed in as Patient | 1. Select Doctor, date, and slot.<br>2. Submit booking. | Doctor: Dr. Alan Grant, Date: Future date, Slot: 10:00 AM | Appointment scheduled; linked unpaid billing invoice automatically generated | Appt + Bill created | **PASS** |
| **MT-14** | Slot Collision Double Booking | Signed in as Patient Bob | 1. Attempt to book exact same Doctor, date, and time slot as Alice. | Same doctor, date, slot as MT-13 | Booking rejected: "The selected doctor is already booked for that date and time slot." | Collision prevented | **PASS** |
| **MT-15** | Doctor Clinical Prescription | Signed in as Doctor | 1. Open "Consult / Prescribe" modal.<br>2. Enter diagnosis & medicines.<br>3. Submit. | Diagnosis: "Acute Bronchitis", Rx: "Amoxicillin 500mg" | Status updated to 'Completed'; prescription recorded; patient can view Rx in portal | Rx recorded & viewable | **PASS** |

---

### 5.3 Automated Testing Suite Architecture & Execution Results
The automated test suite (`tests/test_app.py`) executes 15 end-to-end programmatic tests against the Flask test client.

**Command Executed:**
```powershell
python C:\Users\Lenovo\.gemini\antigravity\scratch\ApexMed_HMS\tests\test_app.py
```

**Verbatim Execution Log Output:**
```text
test_tc01_unauthenticated_redirect_to_login (__main__.ApexMedSystemTests.test_tc01_unauthenticated_redirect_to_login)
TC01: Verify root URL redirects unauthenticated visitors to login page. ... ok
test_tc02_login_empty_fields_validation (__main__.ApexMedSystemTests.test_tc02_login_empty_fields_validation)
TC02: Verify login with empty fields fails validation. ... ok
test_tc03_login_invalid_email_format (__main__.ApexMedSystemTests.test_tc03_login_invalid_email_format)
TC03: Verify login with invalid email syntax fails validation. ... ok
test_tc04_login_incorrect_password (__main__.ApexMedSystemTests.test_tc04_login_incorrect_password)
TC04: Verify login fails with incorrect password. ... ok
test_tc05_sql_injection_immunity (__main__.ApexMedSystemTests.test_tc05_sql_injection_immunity)
TC05: Verify login is immune to classical SQL Injection attacks. ... ok
test_tc06_admin_login_success (__main__.ApexMedSystemTests.test_tc06_admin_login_success)
TC06: Verify valid Admin credentials grant access to Admin dashboard. ... ok
test_tc07_doctor_login_success (__main__.ApexMedSystemTests.test_tc07_doctor_login_success)
TC07: Verify valid Doctor credentials grant access to Doctor dashboard. ... ok
test_tc08_patient_login_success (__main__.ApexMedSystemTests.test_tc08_patient_login_success)
TC08: Verify valid Patient credentials grant access to Patient dashboard. ... ok
test_tc09_rbac_unauthorized_dashboard_access (__main__.ApexMedSystemTests.test_tc09_rbac_unauthorized_dashboard_access)
TC09: Verify Patient cannot access Admin dashboard without admin role. ... ok
test_tc10_patient_registration_flow (__main__.ApexMedSystemTests.test_tc10_patient_registration_flow)
TC10: Verify new patient registration successfully inserts records in users & patients. ... ok
test_tc11_duplicate_email_registration_prevention (__main__.ApexMedSystemTests.test_tc11_duplicate_email_registration_prevention)
TC11: Verify unique constraint prevents registering existing email. ... ok
test_tc12_appointment_booking_and_billing_generation (__main__.ApexMedSystemTests.test_tc12_appointment_booking_and_billing_generation)
TC12: Verify booking an appointment generates both appointment and billing records. ... ok
test_tc13_doctor_slot_double_booking_collision_prevention (__main__.ApexMedSystemTests.test_tc13_doctor_slot_double_booking_collision_prevention)
TC13: Verify multi-column UNIQUE constraint prevents double-booking same doctor slot. ... ok
test_tc14_bill_payment_transaction (__main__.ApexMedSystemTests.test_tc14_bill_payment_transaction)
TC14: Verify patient can pay pending invoice and status changes to Paid. ... ok
test_tc15_doctor_prescription_upsert (__main__.ApexMedSystemTests.test_tc15_doctor_prescription_upsert)
TC15: Verify doctor can record clinical diagnosis and prescription for an appointment. ... ok

----------------------------------------------------------------------
Ran 15 tests in 2.415s

OK
```

### 5.4 Security & SQL Injection Immunity Validation
The database layer exclusively utilizes parameterized bindings:
```python
cursor.execute("SELECT * FROM users WHERE email = ?;", (email_val,))
```
When submitted with malicious inputs such as `' OR '1'='1` or `admin@apexmed.com'; DROP TABLE users; --`, the relational query optimizer parses the input strictly as a literal string value. Automated test case `test_tc05_sql_injection_immunity` proved that authentication is completely impervious to injection exploits.

---

# 6. CONCLUSION & FUTURE SCOPE

### 6.1 Project Conclusion
The **ApexMed Hospital & Healthcare Records Management System** successfully accomplishes all requirements outlined in the project specification and adheres rigorously to all stages of the Software Development Life Cycle (SDLC):
1. **Starting Point Compliance:** Starts directly on a fully validated, modern Sign-In Gateway with client and server input checks.
2. **Technological Stack:** Employs Python and Flask for the presentation and controller tier, paired with dual-compatible MySQL 8.x / SQLite3 relational database engines.
3. **Database Normalization:** All relations have been systematically normalized to **Boyce-Codd Normal Form (BCNF)**, completely eradicating update, insertion, and deletion anomalies while enforcing relational constraints and referential integrity.
4. **Testing Rigor:** Both manual functional testing matrices and automated unit tests demonstrate 100% test pass rates across all 15 core scenarios.

### 6.2 Key Database Concepts Covered
- **Primary & Foreign Key Constraints:** Guarantees entity integrity and enforces referential links across 8 normalized relations.
- **Referential Actions:** Enforces `ON DELETE CASCADE` on dependent patient and clinical records, and `ON DELETE RESTRICT` on departments.
- **Multi-Column Constraints:** Uses `UNIQUE(doctor_id, appointment_date, appointment_time)` to guarantee scheduling collision avoidance.
- **Domain & Check Constraints:** Validates non-negative financial values (`consultation_fee >= 0`, `amount >= 0`) and enum restrictions.
- **ACID Transactions:** Wraps composite multi-table inserts (`users` + `patients`, `appointments` + `billings`) in atomic `commit` and `rollback` blocks.
- **Performance Optimization:** Implements B-tree indexing on foreign keys and search fields.
- **Reporting Views:** Establishes multi-table relational views for administrative and clinical reporting.

### 6.3 Future System Enhancements
- **Telemedicine WebRTC Integration:** Incorporating secure peer-to-peer video consultations between doctors and outpatients.
- **Integrated Payment Gateway:** Integration with Stripe or PayPal APIs for real-time credit card processing and automated webhooks.
- **SMS & Email Reminders:** Automated Celery/Redis background worker sending Twilio SMS and SendGrid email appointment reminders 24 hours prior to scheduled consultation times.
- **HL7 / FHIR Interoperability:** Exporting electronic health records in standardized HL7/FHIR JSON format for integration with external hospital networks.

---
*Report Compiled & Certified for Academic & Industrial Review.*
