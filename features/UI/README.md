# Human Resource Management System (HRMS)

A modern, full-stack enterprise Human Resource Management System built with **FastAPI**, **SQLite**, and a responsive **Single-Page Application (SPA)** with glassmorphism design aesthetics.

---

## 🌟 Key Features

### 1. Backend & API Services
- **RESTful Architecture**: High-performance FastAPI endpoints with automatic Swagger documentation at `/docs`.
- **Database Integration**: SQLite database with relational tables (`employees`, `activity_logs`), indexed columns, and automatic database migration & seeding.
- **Login ID Auto-Generation**: Generates official company employee codes in the format:
  `OI[First2][Last2][YYYY][SEQ]` (e.g. `OIJODO20250001`).
- **Real-Time Salary Structure Computation**: Automatically calculates salary breakdowns based on the defined monthly wage:
  - **Basic Salary**: 50% of monthly wage
  - **House Rent Allowance (HRA)**: 50% of Basic Salary (25% of wage)
  - **Standard Allowance**: ₹4,167 (or remaining balance)
  - **Performance Bonus**: 8.33% of Basic
  - **Leave Travel Allowance (LTA)**: 8.333% of Basic
  - **Fixed Allowance**: Dynamic balance component so the sum equals monthly wage exactly
  - **Provident Fund (PF)**: 12% deduction of Basic Salary
  - **Professional Tax (PTax)**: Fixed ₹200 deduction
  - **Net In-Hand Monthly & Annual CTC**
- **Strict Validation & Conflict Detection**:
  - Name required
  - RFC-compliant email validation
  - Duplicate corporate email prevention (HTTP 409 Conflict)
  - Phone format validation (7 to 15 digits)
  - Date of joining verification
  - Form validation with inline error feedback

### 2. Frontend Application (SPA)
- **Executive Dashboard**: Real-time KPI metric widgets (Total Headcount, Present, On Leave, Absent), department distribution progress meters, and recently onboarded team members.
- **Employee Directory**:
  - **Cards View**: Grid cards displaying avatar, presence status indicator ring, department, role, email, phone, and skills.
  - **Table View**: High-density data table with sorting, quick actions, and status badges.
  - **Global Search & Multi-criteria Filtering**: Instant search across name, role, email, phone, skills, and Login ID; filter by Department, Employment Status, and Attendance State.
- **Onboard / Edit Employee Form**:
  - Multi-section tabbed layout (Personal & Company, Private & Bank, Salary Structure, Skills & Certifications, Bio & Resume).
  - Dynamic skill tag manager (Skill Name + Level: Beginner, Intermediate, Advanced, Expert).
  - Dynamic certification manager (Title, Issuer, Issue Date, Expiry, Credential ID).
  - Live salary preview calculation that updates as the wage input changes.
  - Resume and avatar document upload handler.
- **5-Tab Interactive Employee Profile**:
  1. *Overview & Personal Info*: Work email, phone, manager, location, work schedule, bio, and hobbies.
  2. *Skills & Certifications*: Proficiency badges and credential cards.
  3. *Private & Bank Details*: DOB, gender, nationality, marital status, residential address, PAN number, UAN, Bank Name, Account Number, and IFSC code.
  4. *Salary Structure & Benefits*: Complete transparent compensation sheet with earning components, tax/PF deductions, and net monthly take-home.
  5. *Documents & Resume*: Resume viewer and downloader.
- **Attendance Systray**:
  - Top-right corner attendance widget with 🟢 Present, 🟡 Absent, and ✈️ On Leave indicators.
  - Quick Check In / Check Out toggle for employee attendance tracking.
- **Design & Themes**:
  - Dark Mode & Light Mode switcher.
  - Glassmorphism, smooth micro-interactions, skeleton loaders, and animated toast notifications.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ installed

### Installation & Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch Application**:
   ```bash
   python run.py
   ```

3. **Access Application**:
   - Web App: `http://localhost:8000`
   - Interactive Swagger API Documentation: `http://localhost:8000/docs`
   - ReDoc API Documentation: `http://localhost:8000/redoc`

---

## 🧪 Running Automated Tests

Run the test suite covering CRUD, validation constraints, duplicate email prevention, and salary breakdown calculations:
```bash
python tests/test_api.py
```

---

## 📂 Project Architecture

```
hrms/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application, CORS, static mounts, SPA routing
│   ├── database.py          # SQLite database schema initialization & realistic dataset seeding
│   ├── models.py            # Pydantic schemas and validation rules
│   ├── crud.py              # Database query operations, filters, sorting, activity logs
│   ├── utils.py             # Login ID generator, salary structure calculator, regex validators
│   └── routers/
│       ├── employees.py     # Employee CRUD, status toggles, departments
│       ├── stats.py         # Dashboard analytics KPIs
│       └── uploads.py       # Resume and document file upload handler
├── static/
│   ├── css/
│   │   ├── variables.css    # Design tokens, themes (dark/light), colors
│   │   ├── base.css         # Reset, layout shell, sidebar, header
│   │   ├── components.css   # Buttons, badges, tables, modals, tabs, toasts, forms
│   │   ├── dashboard.css    # KPI cards, filter bar, employee grid cards
│   │   ├── profile.css      # Detailed profile hero, tabs, salary sheet
│   │   └── animations.css   # Micro-interactions, skeleton loaders, pulse glow
│   ├── js/
│   │   ├── api.js           # API client with centralized error formatting
│   │   ├── toast.js         # Animated toast alert notifications
│   │   ├── validation.js    # Client-side input validation and error feedback
│   │   ├── components/
│   │   │   ├── header.js    # Sticky top header, breadcrumb, theme toggle, systray
│   │   │   ├── sidebar.js   # Sidebar navigation
│   │   │   ├── statsView.js # Dashboard KPI metrics and charts
│   │   │   ├── employeeCard.js # Employee card component
│   │   │   ├── employeeTable.js# Dense data table component
│   │   │   ├── employeeForm.js # Multi-section dynamic form with live salary preview
│   │   │   └── employeeProfile.js # 5-tab profile view
│   │   └── app.js           # Application router and state controller
│   ├── uploads/             # Storage for uploaded resumes
│   └── index.html           # Single Page Application HTML shell
├── tests/
│   └── test_api.py          # Automated test suite
├── requirements.txt         # Project dependencies
├── run.py                   # One-click startup runner
└── README.md                # Documentation
```
