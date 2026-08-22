import sqlite3
from backend.app.core.database import engine
from sqlalchemy import inspect
from backend.app.models import (
    User, Employee, EmployeePrivateInfo, Skill, EmployeeSkill,
    Certification, Resume, Salary, Attendance, LeaveType, LeaveBalance,
    TimeOffRequest, CompanySettings
)

def verify():
    insp = inspect(engine)
    tables = insp.get_table_names()
    print("[1] Tables detected by SQLAlchemy Inspector:")
    for t in sorted(tables):
        cols = [c["name"] for c in insp.get_columns(t)]
        pks = insp.get_pk_constraint(t)["constrained_columns"]
        fks = [f"{fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}" for fk in insp.get_foreign_keys(t)]
        uqs = [uq["column_names"] for uq in insp.get_unique_constraints(t)]
        idxs = [idx["name"] for idx in insp.get_indexes(t)]
        print(f"  - Table: {t}")
        print(f"    PK: {pks}")
        print(f"    FKs: {fks}")
        print(f"    Unique: {uqs}")
        print(f"    Indexes: {len(idxs)} indexes")

    # Verify plain text passwords
    con = sqlite3.connect("hrms.db")
    cur = con.cursor()
    cur.execute("SELECT id, login_id, email, password_hash, role FROM users")
    users = cur.fetchall()
    print("\n[2] User account security verification:")
    for uid, login_id, email, pwd_hash, role in users:
        is_bcrypt = pwd_hash.startswith("$2b$") or pwd_hash.startswith("$2a$")
        print(f"  - User {uid}: {login_id} ({email}) | Role: {role} | Bcrypt Hashed: {is_bcrypt} | Hash len: {len(pwd_hash)}")
    con.close()

if __name__ == "__main__":
    verify()
