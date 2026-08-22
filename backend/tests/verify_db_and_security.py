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

    # Verify plain text passwords using SQLAlchemy session
    from backend.app.core.database import SessionLocal
    db = SessionLocal()
    users = db.query(User).all()
    print("\n[2] User account security verification:")
    for u in users:
        is_bcrypt = u.password_hash.startswith("$2b$") or u.password_hash.startswith("$2a$")
        print(f"  - User {u.id}: {u.login_id} ({u.email}) | Role: {u.role.value if hasattr(u.role, 'value') else u.role} | Bcrypt Hashed: {is_bcrypt} | Hash len: {len(u.password_hash)}")
    db.close()

if __name__ == "__main__":
    verify()
