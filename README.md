# HRMS — Human Resource Management System

A full-stack Human Resource Management System built for the Odoo Hackathon.

## Stack

- **Backend:** Python 3.11+, FastAPI
- **ORM:** SQLAlchemy 2
- **Database:** MySQL 8+ (recommended) or PostgreSQL 15+
- **Migrations:** Alembic
- **Validation:** Pydantic v2
- **Authentication:** JWT + bcrypt
- **Frontend:** Responsive vanilla HTML/CSS/JavaScript SPA
- **Testing:** Pytest + FastAPI TestClient

The application uses local database storage and does not depend on third-party business APIs.

## Architecture

```text
Browser
  ↓
Responsive SPA
  ↓
FastAPI Routes
  ↓
Authentication + RBAC + Pydantic Validation
  ↓
Service Layer
  ↓
Repository Layer
  ↓
SQLAlchemy
  ↓
MySQL / PostgreSQL
```

### Modules

1. Authentication & RBAC
2. Employee Management
3. Employee Profiles / Private Information / Skills / Certifications
4. Salary & Payroll
5. Attendance
6. Time Off & Leave
7. Dashboard / Statistics
8. Company Settings

## Database

The schema is normalized and uses foreign keys, unique constraints, check constraints and indexes.

Run migrations with:

```bash
alembic upgrade head
```

Do not use `Base.metadata.create_all()` in the application startup. Schema changes belong in Alembic migrations.

## Local setup

### 1. Create a database

MySQL:

```sql
CREATE DATABASE hrms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

PostgreSQL:

```sql
CREATE DATABASE hrms_db;
```

### 2. Create `.env`

Copy `.env.example` to `.env` and set:

```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/hrms_db
SECRET_KEY=replace-with-a-long-random-secret
```

For PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/hrms_db
```

### 3. Install dependencies

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 4. Start the application

The runner applies migrations and safely seeds demo data before starting FastAPI:

```bash
python run.py
```

Open:

- http://localhost:8000
- http://localhost:8000/docs

### Alternative manual startup

```bash
alembic upgrade head
python -m backend.app.utils.seeder
uvicorn backend.app.main:app --reload
```

## Demo accounts

| Role | Login | Password |
|---|---|---|
| Admin | `admin@hrmscorp.com` | `Admin@123` |
| HR Officer | `hr@hrmscorp.com` | `Hr@123` |
| Employee | `john.doe@hrmscorp.com` | `Emp@123` |
| Employee | `alice.smith@hrmscorp.com` | `Emp@123` |

Change demo credentials before any real deployment.

## Security and permissions

- JWT bearer authentication
- Password hashing
- Role-based authorization: `ADMIN`, `HR_OFFICER`, `EMPLOYEE`
- Employee self-access restrictions
- Salary/private-information restrictions
- Server-side Pydantic validation
- Database constraints for important business rules
- CORS configuration
- No credentials committed to `.env`

## Dynamic data

The frontend reads data from the FastAPI backend and local relational database. Examples include:

- Employee directory and search
- Department filters
- Dashboard statistics
- Salary calculations
- Attendance check-in/check-out
- Leave balances and requests
- Approval/rejection workflows

## Git workflow

Use feature branches:

```text
main
├── feature/auth
├── feature/employee
├── feature/payroll
└── feature/attendance
```

Use meaningful commits such as:

```text
Add employee profile validation
Implement salary calculation API
Add attendance check-in workflow
Implement role-based authorization
```

## Testing

Run the complete test suite:

```bash
pytest -q
```

The project includes tests for authentication, RBAC, employees, salary, attendance, time-off and an end-to-end workflow.

## Project structure

```text
Odoo-Hack/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── dependencies/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   └── tests/
├── features/
│   └── UI/
│       └── static/
├── migrations/
├── requirements.txt
├── alembic.ini
├── run.py
└── README.md
```

## Evaluation checklist

- Local MySQL/PostgreSQL database
- Alembic database migrations
- Modular layered backend
- Dynamic database-driven UI
- Robust server-side validation
- RBAC and security
- Responsive UI
- Intuitive navigation
- Meaningful Git workflow
- Automated tests
- No dependency on external business APIs
