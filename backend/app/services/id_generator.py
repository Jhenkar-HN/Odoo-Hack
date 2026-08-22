import re
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.user import User
from backend.app.models.employee import Employee


class IDGeneratorService:
    """Service to generate standardized Login IDs and Employee Codes."""

    @staticmethod
    def generate_login_id(
        db: Session,
        first_name: str,
        last_name: str,
        date_of_joining: Optional[date] = None,
    ) -> str:
        """
        Generate unique login ID based on format:
        OI + first 2 letters of first name + first 2 letters of last name + joining year + 3-digit serial number.
        Example: John Henke joining in 2026 -> OIJH2026001 (or OIJOH2026001 depending on 2+2)
        """
        fn_clean = re.sub(r"[^A-Za-z]", "", first_name or "EM").upper()
        ln_clean = re.sub(r"[^A-Za-z]", "", last_name or "PL").upper()

        fn_prefix = (fn_clean[:2] if len(fn_clean) >= 2 else (fn_clean + "X")[:2])
        ln_prefix = (ln_clean[:2] if len(ln_clean) >= 2 else (ln_clean + "X")[:2])

        year = str(date_of_joining.year if date_of_joining else date.today().year)
        base_prefix = f"OI{fn_prefix}{ln_prefix}{year}"

        # Find existing users with this prefix to calculate next serial
        matching_users = (
            db.query(User.login_id)
            .filter(User.login_id.like(f"{base_prefix}%"))
            .all()
        )

        max_seq = 0
        for (login_id,) in matching_users:
            suffix = login_id[len(base_prefix):]
            if suffix.isdigit():
                max_seq = max(max_seq, int(suffix))

        new_serial = f"{max_seq + 1:03d}"
        return f"{base_prefix}{new_serial}"

    @staticmethod
    def generate_employee_code(db: Session, joining_date: Optional[date] = None) -> str:
        """Generate unique internal employee code: EMP + Year + 4-digit sequence."""
        year = str(joining_date.year if joining_date else date.today().year)
        base_prefix = f"EMP{year}"

        matching_employees = (
            db.query(Employee.employee_code)
            .filter(Employee.employee_code.like(f"{base_prefix}%"))
            .all()
        )

        max_seq = 0
        for (emp_code,) in matching_employees:
            suffix = emp_code[len(base_prefix):]
            if suffix.isdigit():
                max_seq = max(max_seq, int(suffix))

        new_serial = f"{max_seq + 1:04d}"
        return f"{base_prefix}{new_serial}"
