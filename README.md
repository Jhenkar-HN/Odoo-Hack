# Human Resource Management System (HRMS) — Backend & Database Core

## 1. Project Overview & Architecture

This repository contains the backend core, database architecture, authentication system, and role-based authorization services for the **Human Resource Management System (HRMS)**.

The system follows a **Layered Clean Architecture** pattern designed for high cohesion, low coupling, strict security enforcement, and frictionless integration across the team:

```text
HTTP Request (Frontend / Client)
       │
       ▼
[ Middleware Layer ] (CORS, Error Handlers, OpenTelemetry/Logging)
       │
       ▼
[ Route Controllers ] (FastAPI Routers: Auth, Users, Employees, Profiles, Salaries, Attendance, Time-off, Settings)
       │
       ▼
[ Dependency Injection & RBAC Guards ] (JWT decoding, Role checks: require_admin, require_hr_or_admin, verify_employee_access)
       │
       ▼
[ Business Services ] (AuthService, IDGeneratorService, EmployeeService, SalaryService, AttendanceService, LeaveService)
       │
       ▼
[ Repositories / Data Access ] (Generic BaseRepository, UserRepository, EmployeeRepository, SalaryRepository, etc.)
       │
       ▼
[ SQLAlchemy 2.0 ORM & Alembic ] (13 Normalized Relational Entities & Migrations)
       │
       ▼
[ Relational Database Engine ] (PostgreSQL / MySQL / SQLite)
```

---

## 2. Technology Stack

* **Language**: Python 3.13+
* **Framework**: FastAPI (Asynchronous, OpenAPI 3.0 / Swagger UI auto-generation)
* **ORM**: SQLAlchemy 2.0 (Declarative mapping with relationships & constraints)
* **Migrations**: Alembic
* **Data Validation**: Pydantic v2
* **Authentication**: JWT (JSON Web Tokens) with `HS256` / `RS256`
* **Password Hashing**: `bcrypt` (Salt rounds = 12)
* **Database**: PostgreSQL / MySQL / SQLite (configurable via `DATABASE_URL`)
* **Testing**: Pytest & HTTPX TestClient

---

## 3. Team Member Modules & Responsibilities

| Role | Focus Area | Consumed / Exposed APIs |
| :--- | :--- | :--- |
| **Person 1 (Backend Core & Auth)** | DB Architecture, Auth, RBAC, Core APIs, Security, Migrations | Exposes `/api/v1/auth`, `/api/v1/users`, `/api/v1/employees`, `/api/v1/salaries`, `/api/v1/attendance`, `/api/v1/time-off`, `/api/v1/settings` |
| **Person 2 (Member 2)** | Employee Management & Directory | Consumes `/api/v1/employees`, `/api/v1/profiles` |
| **Person 3 (Member 3)** | Salary & Payroll Management | Consumes `/api/v1/salaries` |
| **Person 4 (Member 4)** | Attendance & Time-Off UI/UX | Consumes `/api/v1/attendance`, `/api/v1/time-off` |

---

## 4. Database Architecture & Normalized Schema

The database consists of 13 normalized relational tables:

1. **`users`**: System authentication accounts with hashed passwords and role flags.
2. **`employees`**: Core employee demographics, job position, manager reference, and joining details.
3. **`employee_private_info`**: Sensitive personal data (PAN, UAN, Bank Account, IFSC, Emergency Contacts).
4. **`skills`**: Master skills dictionary.
5. **`employee_skills`**: Many-to-many junction between employees and skills.
6. **`certifications`**: Professional certificates, issuing organizations, and expiry dates.
7. **`resumes`**: Uploaded resume documents and storage paths.
8. **`salaries`**: Granular breakdown of wage components (Basic, HRA, Standard Allowance, Bonus, LTA, Fixed Allowance, P-Tax, EPF, Employer PF).
9. **`attendances`**: Daily check-in/check-out timestamps, computed regular work hours, and overtime hours.
10. **`leave_types`**: Leave categories (Paid Time Off, Sick Leave, Casual Leave, Unpaid Leave).
11. **`leave_balances`**: Real-time balance tracking per employee per year (Allocated, Used, Remaining).
12. **`time_off_requests`**: Leave applications, requested date ranges, approval status, reviewer ID, and rejection rationale.
13. **`company_settings`**: Enterprise profile, logo, address, and contact details.

### Relational Constraints & Data Protection
* **Automatic Login ID Generator**: When an employee is created, a unique standardized Login ID is automatically generated: `OI + first 2 letters of first name + first 2 letters of last name + joining year + 3-digit sequence` (e.g. `OIJH2026001`).
* **Check Constraints**: Non-negative values for all salary components; `end_date >= start_date` for time-off requests; `number_of_days > 0`.
* **Unique Constraints**: `(employee_id, attendance_date)` on attendance; `(employee_id, leave_type_id, year)` on leave balances; `(employee_id, skill_id)` on employee skills.
* **Cascades**: Deleting an employee safely cascades to dependent sub-entities (`private_info`, `skills`, `certifications`, `balances`), while preserving auditability.

---

## 5. Centralized Role-Based Access Control (RBAC) Matrix

| Resource / Endpoint | ADMIN | HR_OFFICER | EMPLOYEE |
| :--- | :--- | :--- | :--- |
| **Authentication (`/api/v1/auth/*`)** | All | All | Self (login, me, change-password) |
| **User Management (`/api/v1/users/*`)** | Full Access | No Access | No Access |
| **Employee Management (`/api/v1/employees`)** | Full CRUD | Full CRUD | Read-only Directory |
| **Private Info (`/api/v1/employees/{id}/private-info`)** | Full Access | Full Access | **Self Only** (`user.employee_id == id`) |
| **Self Profile (`/api/v1/profiles/me`)** | Yes | Yes | Yes (Update permitted fields) |
| **Salaries (`/api/v1/salaries/*`)** | Full CRUD | Read-only | **Self Only** (Read-only for own salary) |
| **Attendance Check-In / Out (`/api/v1/attendance/check-*`)** | Yes | Yes | **Self Only** |
| **Attendance Records (`/api/v1/attendance/*`)** | View all / Manage | View all / Manage | **Self Only** (Own history & summary) |
| **Leave Types (`/api/v1/time-off/leave-types`)** | Full CRUD | Full CRUD | Read-only |
| **Time Off Requests (`/api/v1/time-off/requests`)** | View all, Approve/Reject | View all, Approve/Reject | Submit own, View own, Cancel own |
| **Company Settings (`/api/v1/settings`)** | Full CRUD | Read-only | Read-only |

---

## 6. Installation & Quick Start

### 1. Prerequisites
* Python 3.10+ installed
* Git

### 2. Environment Setup
```bash
# Clone the repository
git clone <repo-url>
cd odoo

# Create and activate virtual environment
python -m venv .venv

# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

**Database Configuration Options**:
* **SQLite (Default / Zero setup)**: `DATABASE_URL="sqlite:///./hrms.db"`
* **PostgreSQL**: `DATABASE_URL="postgresql+psycopg2://postgres:password@localhost:5432/hrms_db"`
* **MySQL**: `DATABASE_URL="mysql+pymysql://root:password@localhost:3306/hrms_db"`

### 4. Run Migrations & Seed Database
```bash
# Apply migrations
alembic upgrade head

# Seed initial test accounts, leave types, skills, and salaries
python -m backend.app.utils.seeder
```

### 5. Start the Server
```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

The API and interactive OpenAPI documentation will be accessible at:
* **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
* **OpenAPI JSON Spec**: [http://127.0.0.1:8000/api/v1/openapi.json](http://127.0.0.1:8000/api/v1/openapi.json)

---

## 7. Default Test Accounts

| Role | Name | Login ID / Email | Password | Permissions Summary |
| :--- | :--- | :--- | :--- | :--- |
| **ADMIN** | System Administrator | `admin@hrmscorp.com` / `OIAD2025001` | `Admin@123` | Full administrative control, user status toggle, salary configuration |
| **HR_OFFICER** | Sarah Jenkins | `hr@hrmscorp.com` / `OISJ2025001` | `Hr@123` | Employee onboarding, attendance logs, time-off approvals |
| **EMPLOYEE 1** | John Doe | `john.doe@hrmscorp.com` / `OIJD2025001` | `Emp@123` | Self profile, check-in/out, personal salary view, leave applications |
| **EMPLOYEE 2** | Alice Smith | `alice.smith@hrmscorp.com` / `OIAS2025001` | `Emp@123` | Self profile, check-in/out, personal salary view, leave applications |

---

## 8. Running Automated Tests

Run the complete test suite with verbose reporting:
```bash
pytest -v
```

All 29 tests verify:
* Authentication & JWT expiration handling
* RBAC guards and cross-employee data isolation
* Auto Login ID generation (`OI...`) & unique constraint enforcement
* Salary calculation, breakdown, and negative input rejection
* Attendance check-in, duplicate prevention, and work/overtime computation
* Time-off request submission, approval workflows, and balance deduction

---

## 9. Standard API Response Structure

All API endpoints follow a unified response envelope:

### Success Response (`200 OK`, `201 Created`)
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... }
}
```

### Error Response (`400`, `401`, `403`, `404`, `409`, `422`, `500`)
```json
{
  "success": false,
  "error_code": "PERMISSION_DENIED",
  "message": "Access denied: You are not authorized to view or modify another employee's records.",
  "details": null
}
```

---

## 10. Git Workflow & Branching Strategy

```text
main           (Production-ready releases)
  │
develop        (Integration branch)
  ├── feature/backend-auth   (Person 1: Database & Auth Core)
  ├── feature/employee       (Person 2: Employee Management)
  ├── feature/salary         (Person 3: Salary & Payroll)
  └── feature/attendance     (Person 4: Attendance & Time-Off)
```
