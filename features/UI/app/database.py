import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.utils import generate_login_id, calculate_salary_breakdown
from app.auth import hash_password

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hrms.db")


def get_db_connection() -> sqlite3.Connection:
    """Create and return a database connection with dict-like row factory."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def init_db():
    """Initialize database tables and seed starter data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_code TEXT UNIQUE NOT NULL,
        login_id TEXT UNIQUE NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        full_name TEXT NOT NULL,
        work_email TEXT UNIQUE NOT NULL COLLATE NOCASE,
        personal_email TEXT DEFAULT '',
        phone TEXT NOT NULL,
        department TEXT NOT NULL,
        job_position TEXT NOT NULL,
        manager_name TEXT DEFAULT '',
        location TEXT DEFAULT 'Headquarters',
        date_of_joining TEXT NOT NULL,
        
        -- Private & Demographic Info
        date_of_birth TEXT DEFAULT '',
        gender TEXT DEFAULT 'Not Specified',
        marital_status TEXT DEFAULT 'Single',
        nationality TEXT DEFAULT 'Indian',
        residing_address TEXT DEFAULT '',
        pan_number TEXT DEFAULT '',
        uan_number TEXT DEFAULT '',

        -- Bank Details
        bank_name TEXT DEFAULT '',
        account_number TEXT DEFAULT '',
        ifsc_code TEXT DEFAULT '',

        -- Compensation & Work
        monthly_wage REAL DEFAULT 50000.0,
        work_hours TEXT DEFAULT '40 hrs/week (09:00 - 18:00)',

        -- Culture & Bio
        about TEXT DEFAULT '',
        interests_hobbies TEXT DEFAULT '',
        avatar_url TEXT DEFAULT '',
        resume_url TEXT DEFAULT '',
        resume_filename TEXT DEFAULT '',

        -- Statuses
        status TEXT DEFAULT 'active',              -- active, inactive, on_leave, terminated
        attendance_status TEXT DEFAULT 'present',  -- present, absent, on_leave

        -- JSON data for skills and certifications
        skills_json TEXT DEFAULT '[]',
        certifications_json TEXT DEFAULT '[]',

        -- Timestamps
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_employees_email ON employees(work_email);
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_employees_dept ON employees(department);
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_employees_status ON employees(status);
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_employees_attendance ON employees(attendance_status);
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        action TEXT NOT NULL,
        details TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
    );
    """)

    # Users / Auth Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL COLLATE NOCASE, -- Login ID or email
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,                           -- 'hr' or 'employee'
        employee_id INTEGER,                          -- Null for standalone HR Admin, or FK to employees.id
        display_name TEXT NOT NULL,
        avatar_url TEXT DEFAULT '',
        created_at TEXT NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE SET NULL
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);")

    # Leave / Time-off Requests Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leave_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        leave_type TEXT NOT NULL,                      -- 'Paid Time Off', 'Sick Leave', 'Unpaid Leave'
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        days_count REAL NOT NULL,
        reason TEXT DEFAULT '',
        status TEXT DEFAULT 'pending',                -- 'pending', 'approved', 'rejected'
        reviewed_by TEXT DEFAULT '',
        created_at TEXT NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leave_emp ON leave_requests(employee_id);")

    conn.commit()

    # Check if empty, then seed
    cursor.execute("SELECT COUNT(*) as cnt FROM employees;")
    count = cursor.fetchone()["cnt"]

    if count == 0:
        seed_initial_data(conn)
    else:
        # Ensure HR user exists
        ensure_default_users(conn)

    conn.close()


def ensure_default_users(conn: sqlite3.Connection):
    """Ensure HR admin user and employee users exist in users table."""
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()
    
    # 1. Check HR Admin user
    cursor.execute("SELECT * FROM users WHERE username = 'admin@hrms.com' OR username = 'admin';")
    hr_user = cursor.fetchone()
    if not hr_user:
        hr_pwd = hash_password("admin123")
        cursor.execute("""
        INSERT INTO users (username, password_hash, role, employee_id, display_name, avatar_url, created_at)
        VALUES ('admin@hrms.com', ?, 'hr', NULL, 'HR Administrator', 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150', ?);
        """, (hr_pwd, now_str))

    # 2. Check each employee in employees table
    cursor.execute("SELECT id, login_id, work_email, full_name, avatar_url FROM employees;")
    employees = cursor.fetchall()
    emp_pwd = hash_password("employee123")

    for emp in employees:
        # Check by work_email or login_id
        cursor.execute("SELECT * FROM users WHERE username = ? OR username = ?;", (emp["work_email"], emp["login_id"]))
        user = cursor.fetchone()
        if not user:
            cursor.execute("""
            INSERT INTO users (username, password_hash, role, employee_id, display_name, avatar_url, created_at)
            VALUES (?, ?, 'employee', ?, ?, ?, ?);
            """, (emp["work_email"], emp_pwd, emp["id"], emp["full_name"], emp["avatar_url"], now_str))

    conn.commit()


def seed_initial_data(conn: sqlite3.Connection):
    """Seed initial realistic employee dataset, users, and leave requests."""
    sample_employees = [
        {
            "first_name": "Aarav",
            "last_name": "Sharma",
            "work_email": "aarav.sharma@odooindia.com",
            "personal_email": "aarav.sharma.personal@gmail.com",
            "phone": "+91 98234 56789",
            "department": "Engineering",
            "job_position": "Lead Software Architect",
            "manager_name": "Vikram Malhotra",
            "location": "Mumbai, India",
            "date_of_joining": "2023-03-15",
            "date_of_birth": "1992-06-18",
            "gender": "Male",
            "marital_status": "Married",
            "nationality": "Indian",
            "residing_address": "Flat 402, Lotus Heights, Powai, Mumbai - 400076",
            "pan_number": "ABCPS1234D",
            "uan_number": "100987654321",
            "bank_name": "HDFC Bank",
            "account_number": "50100234567890",
            "ifsc_code": "HDFC0000128",
            "monthly_wage": 95000.0,
            "work_hours": "40 hrs/week (09:00 - 18:00)",
            "about": "Passionate about distributed backend systems, clean microservice patterns, and mentoring junior engineers.",
            "interests_hobbies": "Trekking, playing guitar, and open-source contributions.",
            "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
            "resume_url": "",
            "resume_filename": "Aarav_Sharma_Resume.pdf",
            "status": "active",
            "attendance_status": "present",
            "skills": [
                {"name": "Python", "level": "Expert"},
                {"name": "FastAPI", "level": "Expert"},
                {"name": "PostgreSQL", "level": "Advanced"},
                {"name": "Docker & K8s", "level": "Advanced"},
                {"name": "System Architecture", "level": "Expert"}
            ],
            "certifications": [
                {
                    "title": "AWS Certified Solutions Architect - Professional",
                    "issuer": "Amazon Web Services",
                    "issue_date": "2023-01",
                    "expiry_date": "2026-01",
                    "credential_id": "AWS-PSA-98231",
                    "credential_url": "https://aws.amazon.com/verify"
                }
            ]
        },
        {
            "first_name": "Priya",
            "last_name": "Nair",
            "work_email": "priya.nair@odooindia.com",
            "personal_email": "priya.nair94@gmail.com",
            "phone": "+91 91234 87654",
            "department": "Design",
            "job_position": "Senior Product Designer (UI/UX)",
            "manager_name": "Vikram Malhotra",
            "location": "Bengaluru, India",
            "date_of_joining": "2023-08-01",
            "date_of_birth": "1995-11-24",
            "gender": "Female",
            "marital_status": "Single",
            "nationality": "Indian",
            "residing_address": "304, Green Glen Layout, Bellandur, Bengaluru - 560103",
            "pan_number": "BZXPN8765F",
            "uan_number": "100987654322",
            "bank_name": "ICICI Bank",
            "account_number": "004501598765",
            "ifsc_code": "ICIC0000045",
            "monthly_wage": 75000.0,
            "work_hours": "40 hrs/week (10:00 - 19:00)",
            "about": "Obsessed with intuitive user experiences, design systems, and delightful micro-interactions.",
            "interests_hobbies": "Oil painting, pottery, and typography design.",
            "avatar_url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80",
            "resume_url": "",
            "resume_filename": "Priya_Nair_Portfolio_Resume.pdf",
            "status": "active",
            "attendance_status": "present",
            "skills": [
                {"name": "Figma & Design Systems", "level": "Expert"},
                {"name": "User Research", "level": "Advanced"}
            ],
            "certifications": []
        },
        {
            "first_name": "Rohan",
            "last_name": "Deshmukh",
            "work_email": "rohan.deshmukh@odooindia.com",
            "personal_email": "rohan.deshmukh@yahoo.com",
            "phone": "+91 97654 32100",
            "department": "Human Resources",
            "job_position": "HR Operations & Talent Manager",
            "manager_name": "Sneha Sen",
            "location": "Pune, India",
            "date_of_joining": "2024-01-10",
            "date_of_birth": "1993-04-12",
            "gender": "Male",
            "marital_status": "Married",
            "nationality": "Indian",
            "residing_address": "B-12, Kumar Park, Baner Road, Pune - 411045",
            "pan_number": "CPQRD9988G",
            "uan_number": "100987654323",
            "bank_name": "State Bank of India",
            "account_number": "33445566778",
            "ifsc_code": "SBIN0001423",
            "monthly_wage": 65000.0,
            "work_hours": "40 hrs/week (09:30 - 18:30)",
            "about": "Building high-performance company cultures, transparent payroll pipelines, and seamless onboarding experiences.",
            "interests_hobbies": "Cricket, reading organizational psychology, photography.",
            "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
            "resume_url": "",
            "resume_filename": "Rohan_Deshmukh_HR_Resume.pdf",
            "status": "active",
            "attendance_status": "on_leave",
            "skills": [
                {"name": "Talent Acquisition", "level": "Expert"},
                {"name": "Payroll & Benefits", "level": "Expert"}
            ],
            "certifications": []
        }
    ]

    cursor = conn.cursor()
    seq = 1
    now_str = datetime.now().isoformat()

    # 1. Insert HR Admin User
    hr_pwd = hash_password("admin123")
    cursor.execute("""
    INSERT INTO users (username, password_hash, role, employee_id, display_name, avatar_url, created_at)
    VALUES ('admin@hrms.com', ?, 'hr', NULL, 'HR Administrator', 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150', ?);
    """, (hr_pwd, now_str))

    emp_default_pwd = hash_password("employee123")

    for emp in sample_employees:
        login_id = generate_login_id(emp["first_name"], emp["last_name"], emp["date_of_joining"], seq)
        emp_code = login_id
        full_name = f"{emp['first_name']} {emp['last_name']}".strip()

        cursor.execute("""
        INSERT INTO employees (
            emp_code, login_id, first_name, last_name, full_name,
            work_email, personal_email, phone, department, job_position,
            manager_name, location, date_of_joining, date_of_birth,
            gender, marital_status, nationality, residing_address,
            pan_number, uan_number, bank_name, account_number, ifsc_code,
            monthly_wage, work_hours, about, interests_hobbies,
            avatar_url, resume_url, resume_filename, status,
            attendance_status, skills_json, certifications_json,
            created_at, updated_at
        ) VALUES (
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?
        );
        """, (
            emp_code, login_id, emp["first_name"], emp["last_name"], full_name,
            emp["work_email"], emp["personal_email"], emp["phone"], emp["department"], emp["job_position"],
            emp["manager_name"], emp["location"], emp["date_of_joining"], emp["date_of_birth"],
            emp["gender"], emp["marital_status"], emp["nationality"], emp["residing_address"],
            emp["pan_number"], emp["uan_number"], emp["bank_name"], emp["account_number"], emp["ifsc_code"],
            emp["monthly_wage"], emp["work_hours"], emp["about"], emp["interests_hobbies"],
            emp["avatar_url"], emp["resume_url"], emp["resume_filename"], emp["status"],
            emp["attendance_status"], json.dumps(emp["skills"]), json.dumps(emp["certifications"]),
            now_str, now_str
        ))

        emp_id = cursor.lastrowid

        # Insert user account for employee
        cursor.execute("""
        INSERT INTO users (username, password_hash, role, employee_id, display_name, avatar_url, created_at)
        VALUES (?, ?, 'employee', ?, ?, ?, ?);
        """, (emp["work_email"], emp_default_pwd, emp_id, full_name, emp["avatar_url"], now_str))

        cursor.execute("""
        INSERT INTO activity_logs (employee_id, action, details, created_at)
        VALUES (?, 'CREATED', 'Employee profile created via system seed.', ?);
        """, (emp_id, now_str))

        if emp["first_name"] == "Rohan":
            # Add sample approved leave
            cursor.execute("""
            INSERT INTO leave_requests (employee_id, leave_type, start_date, end_date, days_count, reason, status, reviewed_by, created_at)
            VALUES (?, 'Paid Time Off', '2026-08-20', '2026-08-23', 4.0, 'Annual family vacation', 'approved', 'HR Admin', ?);
            """, (emp_id, now_str))

        seq += 1

    conn.commit()
