import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from app.database import get_db_connection
from app.models import EmployeeCreate, EmployeeUpdate
from app.utils import generate_login_id, calculate_salary_breakdown
from app.auth import hash_password, verify_password


def row_to_employee_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert a database Row object to a clean response dictionary."""
    data = dict(row)
    
    try:
        data["skills"] = json.loads(data.get("skills_json") or "[]")
    except Exception:
        data["skills"] = []

    try:
        data["certifications"] = json.loads(data.get("certifications_json") or "[]")
    except Exception:
        data["certifications"] = []

    data.pop("skills_json", None)
    data.pop("certifications_json", None)

    wage = float(data.get("monthly_wage") or 0.0)
    data["salary_breakdown"] = calculate_salary_breakdown(wage)

    return data


# --- AUTH & USER CRUD ---

def authenticate_user(username_or_email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user with username/email/login_id and password."""
    clean_user = username_or_email.strip().lower()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT u.*, e.login_id as emp_login_id, e.department, e.job_position
    FROM users u
    LEFT JOIN employees e ON u.employee_id = e.id
    WHERE u.username = ? COLLATE NOCASE
       OR e.login_id = ? COLLATE NOCASE
       OR e.work_email = ? COLLATE NOCASE;
    """, (clean_user, clean_user.upper(), clean_user))

    user_row = cursor.fetchone()
    conn.close()

    if not user_row:
        return None

    if not verify_password(password, user_row["password_hash"]):
        return None

    user_dict = dict(user_row)
    user_dict.pop("password_hash", None)
    return user_dict


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Fetch user by primary key."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT u.*, e.login_id as emp_login_id, e.department, e.job_position
    FROM users u
    LEFT JOIN employees e ON u.employee_id = e.id
    WHERE u.id = ?;
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    res = dict(row)
    res.pop("password_hash", None)
    return res


# --- EMPLOYEE CRUD ---

def get_employees(
    search: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    attendance_status: Optional[str] = None,
    sort_by: str = "id",
    sort_order: str = "desc",
    page: int = 1,
    limit: int = 50,
) -> Tuple[List[Dict[str, Any]], int]:
    """Retrieve filtered, searched, sorted, and paginated employees."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM employees WHERE 1=1"
    count_query = "SELECT COUNT(*) as total FROM employees WHERE 1=1"
    params: List[Any] = []

    if search and search.strip():
        s = f"%{search.strip()}%"
        condition = """
         AND (
            first_name LIKE ? OR
            last_name LIKE ? OR
            full_name LIKE ? OR
            work_email LIKE ? OR
            personal_email LIKE ? OR
            phone LIKE ? OR
            job_position LIKE ? OR
            login_id LIKE ? OR
            skills_json LIKE ?
        )"""
        query += condition
        count_query += condition
        params.extend([s, s, s, s, s, s, s, s, s])

    if department and department.strip() and department.lower() != "all":
        query += " AND department = ?"
        count_query += " AND department = ?"
        params.append(department.strip())

    if status and status.strip() and status.lower() != "all":
        query += " AND status = ?"
        count_query += " AND status = ?"
        params.append(status.strip().lower())

    if attendance_status and attendance_status.strip() and attendance_status.lower() != "all":
        query += " AND attendance_status = ?"
        count_query += " AND attendance_status = ?"
        params.append(attendance_status.strip().lower())

    cursor.execute(count_query, params)
    total = cursor.fetchone()["total"]

    allowed_sort_fields = {
        "id": "id",
        "name": "full_name",
        "first_name": "first_name",
        "department": "department",
        "job_position": "job_position",
        "date_of_joining": "date_of_joining",
        "monthly_wage": "monthly_wage",
        "status": "status",
        "attendance_status": "attendance_status",
    }
    col = allowed_sort_fields.get(sort_by.lower(), "id")
    order = "ASC" if sort_order.upper() == "ASC" else "DESC"
    query += f" ORDER BY {col} {order}"

    offset = max(0, (page - 1) * limit)
    query += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    items = [row_to_employee_dict(r) for r in rows]
    return items, total


def get_employee_by_id(emp_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a single employee by integer primary key."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees WHERE id = ?;", (emp_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return row_to_employee_dict(row)


def get_employee_by_email(email: str, exclude_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Check if an email already exists in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if exclude_id:
        cursor.execute("SELECT * FROM employees WHERE work_email = ? COLLATE NOCASE AND id != ?;", (email.strip().lower(), exclude_id))
    else:
        cursor.execute("SELECT * FROM employees WHERE work_email = ? COLLATE NOCASE;", (email.strip().lower(),))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return row_to_employee_dict(row)


def get_next_sequence_number(joining_year: str) -> int:
    """Get next sequential employee number for joining year."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM employees WHERE date_of_joining LIKE ?;", (f"{joining_year}%",))
    count = cursor.fetchone()["cnt"]
    conn.close()
    return count + 1


def create_employee(emp_data: EmployeeCreate) -> Dict[str, Any]:
    """Create a new employee record and auto-provision their user credentials."""
    work_email = emp_data.work_email.strip().lower()
    
    if get_employee_by_email(work_email):
        raise ValueError(f"An employee with email '{work_email}' already exists.")

    year = emp_data.date_of_joining[:4] if len(emp_data.date_of_joining) >= 4 else str(datetime.now().year)
    seq = get_next_sequence_number(year)

    login_id = generate_login_id(emp_data.first_name, emp_data.last_name, emp_data.date_of_joining, seq)
    emp_code = login_id
    full_name = f"{emp_data.first_name} {emp_data.last_name}".strip()
    now_str = datetime.now().isoformat()

    skills_json = json.dumps([s.model_dump() for s in emp_data.skills])
    certifications_json = json.dumps([c.model_dump() for c in emp_data.certifications])

    avatar = emp_data.avatar_url.strip() if emp_data.avatar_url else "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80"

    conn = get_db_connection()
    cursor = conn.cursor()
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
        emp_code, login_id, emp_data.first_name.strip(), emp_data.last_name.strip(), full_name,
        work_email, emp_data.personal_email or "", emp_data.phone.strip(), emp_data.department.strip(), emp_data.job_position.strip(),
        emp_data.manager_name or "", emp_data.location or "Headquarters", emp_data.date_of_joining, emp_data.date_of_birth or "",
        emp_data.gender or "Not Specified", emp_data.marital_status or "Single", emp_data.nationality or "Indian", emp_data.residing_address or "",
        emp_data.pan_number or "", emp_data.uan_number or "", emp_data.bank_name or "", emp_data.account_number or "", emp_data.ifsc_code or "",
        float(emp_data.monthly_wage or 0.0), emp_data.work_hours or "40 hrs/week (09:00 - 18:00)", emp_data.about or "", emp_data.interests_hobbies or "",
        avatar, emp_data.resume_url or "", emp_data.resume_filename or "", emp_data.status or "active",
        emp_data.attendance_status or "present", skills_json, certifications_json,
        now_str, now_str
    ))

    emp_id = cursor.lastrowid

    # Auto-provision user account for this new employee
    default_pwd_hash = hash_password("Welcome@123")
    cursor.execute("""
    INSERT INTO users (username, password_hash, role, employee_id, display_name, avatar_url, created_at)
    VALUES (?, ?, 'employee', ?, ?, ?, ?);
    """, (work_email, default_pwd_hash, emp_id, full_name, avatar, now_str))

    cursor.execute("""
    INSERT INTO activity_logs (employee_id, action, details, created_at)
    VALUES (?, 'CREATED', 'New employee onboarded and user credentials provisioned.', ?);
    """, (emp_id, now_str))

    conn.commit()
    conn.close()

    created = get_employee_by_id(emp_id)
    if not created:
        raise RuntimeError("Failed to retrieve created employee.")
    return created


def update_employee(emp_id: int, update_data: EmployeeUpdate) -> Optional[Dict[str, Any]]:
    """Update employee details."""
    existing = get_employee_by_id(emp_id)
    if not existing:
        return None

    if update_data.work_email:
        new_email = update_data.work_email.strip().lower()
        duplicate = get_employee_by_email(new_email, exclude_id=emp_id)
        if duplicate:
            raise ValueError(f"Email '{new_email}' is already in use by another employee.")

    conn = get_db_connection()
    cursor = conn.cursor()

    updates: List[str] = []
    params: List[Any] = []

    field_dict = update_data.model_dump(exclude_unset=True)

    first_name = field_dict.get("first_name", existing["first_name"])
    last_name = field_dict.get("last_name", existing["last_name"])
    field_dict["full_name"] = f"{first_name} {last_name}".strip()

    for k, v in field_dict.items():
        if k == "skills":
            updates.append("skills_json = ?")
            params.append(json.dumps([s.model_dump() if hasattr(s, "model_dump") else s for s in v]))
        elif k == "certifications":
            updates.append("certifications_json = ?")
            params.append(json.dumps([c.model_dump() if hasattr(c, "model_dump") else c for c in v]))
        elif k not in ("id", "login_id", "emp_code", "created_at", "updated_at"):
            updates.append(f"{k} = ?")
            params.append(v)

    now_str = datetime.now().isoformat()
    updates.append("updated_at = ?")
    params.append(now_str)

    params.append(emp_id)
    query = f"UPDATE employees SET {', '.join(updates)} WHERE id = ?;"
    cursor.execute(query, params)

    # Sync display_name/avatar to users table if updated
    if "first_name" in field_dict or "last_name" in field_dict or "avatar_url" in field_dict:
        cursor.execute("""
        UPDATE users SET display_name = ?, avatar_url = ? WHERE employee_id = ?;
        """, (field_dict["full_name"], field_dict.get("avatar_url", existing.get("avatar_url")), emp_id))

    cursor.execute("""
    INSERT INTO activity_logs (employee_id, action, details, created_at)
    VALUES (?, 'UPDATED', 'Employee details updated.', ?);
    """, (emp_id, now_str))

    conn.commit()
    conn.close()

    return get_employee_by_id(emp_id)


def delete_employee(emp_id: int, hard_delete: bool = False) -> bool:
    """Soft delete (deactivate) or hard delete employee."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if hard_delete:
        cursor.execute("DELETE FROM users WHERE employee_id = ?;", (emp_id,))
        cursor.execute("DELETE FROM employees WHERE id = ?;", (emp_id,))
    else:
        now_str = datetime.now().isoformat()
        cursor.execute("UPDATE employees SET status = 'inactive', updated_at = ? WHERE id = ?;", (now_str, emp_id))
        cursor.execute("""
        INSERT INTO activity_logs (employee_id, action, details, created_at)
        VALUES (?, 'DEACTIVATED', 'Employee status changed to inactive.', ?);
        """, (emp_id, now_str))

    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected


def toggle_employee_status(emp_id: int, new_status: str) -> Optional[Dict[str, Any]]:
    """Toggle employee status."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()

    cursor.execute("UPDATE employees SET status = ?, updated_at = ? WHERE id = ?;", (new_status.lower(), now_str, emp_id))
    cursor.execute("""
    INSERT INTO activity_logs (employee_id, action, details, created_at)
    VALUES (?, 'STATUS_CHANGE', ?, ?);
    """, (emp_id, f"Status changed to {new_status}", now_str))

    conn.commit()
    conn.close()
    return get_employee_by_id(emp_id)


def toggle_attendance_status(emp_id: int, attendance_status: str) -> Optional[Dict[str, Any]]:
    """Toggle employee attendance state."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()

    cursor.execute("UPDATE employees SET attendance_status = ?, updated_at = ? WHERE id = ?;", (attendance_status.lower(), now_str, emp_id))
    cursor.execute("""
    INSERT INTO activity_logs (employee_id, action, details, created_at)
    VALUES (?, 'ATTENDANCE_CHANGE', ?, ?);
    """, (emp_id, f"Attendance updated to {attendance_status}", now_str))

    conn.commit()
    conn.close()
    return get_employee_by_id(emp_id)


# --- LEAVE / TIMEOFF CRUD ---

def apply_leave_request(emp_id: int, leave_type: str, start_date: str, end_date: str, days_count: float, reason: str) -> Dict[str, Any]:
    """Submit a new leave application for an employee."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()

    cursor.execute("""
    INSERT INTO leave_requests (employee_id, leave_type, start_date, end_date, days_count, reason, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, 'pending', ?);
    """, (emp_id, leave_type, start_date, end_date, days_count, reason, now_str))

    leave_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "id": leave_id,
        "employee_id": emp_id,
        "leave_type": leave_type,
        "start_date": start_date,
        "end_date": end_date,
        "days_count": days_count,
        "reason": reason,
        "status": "pending",
        "created_at": now_str
    }


def get_employee_leaves(emp_id: int) -> List[Dict[str, Any]]:
    """Get all leave requests submitted by a specific employee."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT lr.*, e.full_name, e.department, e.job_position, e.login_id
    FROM leave_requests lr
    JOIN employees e ON lr.employee_id = e.id
    WHERE lr.employee_id = ?
    ORDER BY lr.created_at DESC;
    """, (emp_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_leaves() -> List[Dict[str, Any]]:
    """Get all leave requests for HR review."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT lr.*, e.full_name, e.department, e.job_position, e.login_id, e.avatar_url
    FROM leave_requests lr
    JOIN employees e ON lr.employee_id = e.id
    ORDER BY lr.created_at DESC;
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_leave_status(leave_id: int, new_status: str, reviewer: str = "HR Admin") -> Optional[Dict[str, Any]]:
    """Approve or reject a leave request."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE leave_requests SET status = ?, reviewed_by = ? WHERE id = ?;", (new_status.lower(), reviewer, leave_id))
    
    # If approved, also update employee's attendance status to 'on_leave'
    if new_status.lower() == "approved":
        cursor.execute("SELECT employee_id FROM leave_requests WHERE id = ?;", (leave_id,))
        lr = cursor.fetchone()
        if lr:
            cursor.execute("UPDATE employees SET attendance_status = 'on_leave' WHERE id = ?;", (lr["employee_id"],))

    conn.commit()
    cursor.execute("SELECT * FROM leave_requests WHERE id = ?;", (leave_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_dashboard_stats() -> Dict[str, Any]:
    """Calculate aggregated analytics KPIs for dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM employees;")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as active FROM employees WHERE status = 'active';")
    active = cursor.fetchone()["active"]

    cursor.execute("SELECT COUNT(*) as present FROM employees WHERE attendance_status = 'present' AND status = 'active';")
    present = cursor.fetchone()["present"]

    cursor.execute("SELECT COUNT(*) as on_leave FROM employees WHERE attendance_status = 'on_leave' AND status = 'active';")
    on_leave = cursor.fetchone()["on_leave"]

    cursor.execute("SELECT COUNT(*) as absent FROM employees WHERE attendance_status = 'absent' AND status = 'active';")
    absent = cursor.fetchone()["absent"]

    cursor.execute("SELECT department, COUNT(*) as cnt FROM employees GROUP BY department ORDER BY cnt DESC;")
    dept_rows = cursor.fetchall()
    dept_distribution = {r["department"]: r["cnt"] for r in dept_rows}

    cursor.execute("SELECT status, COUNT(*) as cnt FROM employees GROUP BY status;")
    status_rows = cursor.fetchall()
    status_distribution = {r["status"]: r["cnt"] for r in status_rows}

    cursor.execute("SELECT attendance_status, COUNT(*) as cnt FROM employees GROUP BY attendance_status;")
    att_rows = cursor.fetchall()
    att_distribution = {r["attendance_status"]: r["cnt"] for r in att_rows}

    # Count pending leave requests
    cursor.execute("SELECT COUNT(*) as cnt FROM leave_requests WHERE status = 'pending';")
    pending_leaves = cursor.fetchone()["cnt"]

    cursor.execute("SELECT * FROM employees ORDER BY date_of_joining DESC LIMIT 5;")
    recent_rows = cursor.fetchall()
    recent_joiners = [row_to_employee_dict(r) for r in recent_rows]

    conn.close()

    return {
        "total_employees": total,
        "active_employees": active,
        "present_today": present,
        "on_leave_today": on_leave,
        "absent_today": absent,
        "pending_leaves": pending_leaves,
        "departments_count": len(dept_distribution),
        "department_distribution": dept_distribution,
        "status_distribution": status_distribution,
        "attendance_distribution": att_distribution,
        "recent_joiners": recent_joiners,
    }
