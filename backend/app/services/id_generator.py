import re
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.employee import Employee
from backend.app.repositories.company_repo import company_repo
from backend.app.schemas.company import SerialNumberLookup


class IDGeneratorService:
    """Service to generate standardized Login IDs and Employee Codes."""

    @staticmethod
    def generate_login_id(
        db: Session,
        first_name: str,
        last_name: str,
        company: Optional[str] = None,
        date_of_joining: Optional[date] = None,
    ) -> str:
        """
        Generate standardized Login ID in the format:
        [CompanyCode][First 2 letters of first name][First 2 letters of last name][Year of joining][4-digit serial]
        Example: John Doe joining company 'CE' in 2024 -> CEJODO20240001

        Requirements:
        - CompanyCode comes from the companies table
        - Serial increments per company per year, zero-padded to 4 digits
        - Handles duplicate initials safely via transactional serial increment
        """
        # 1. Resolve Company Code
        company_obj = None
        if company:
            company_obj = company_repo.get_by_name_or_code(db, company)

        if not company_obj:
            company_obj = company_repo.get_or_create_default(db, name="HRMS Corp", code="CE")

        company_code = company_obj.code.strip().upper()

        # 2. First and Last name initials (2 letters each, uppercase, padded with 'X' if single char)
        fn_clean = re.sub(r"[^A-Za-z]", "", first_name or "").upper()
        ln_clean = re.sub(r"[^A-Za-z]", "", last_name or "").upper()

        fn_2 = (fn_clean[:2] if len(fn_clean) >= 2 else (fn_clean + "X")[:2]) or "EM"
        ln_2 = (ln_clean[:2] if len(ln_clean) >= 2 else (ln_clean + "X")[:2]) or "PL"

        # 3. Year of joining (4 digits)
        year = date_of_joining.year if date_of_joining else date.today().year

        # 4. Atomic serial allocation
        serial_int = company_repo.get_next_serial_transactional(db, company_code, year)
        serial_str = f"{serial_int:04d}"

        # 5. Build Login ID
        login_id = f"{company_code}{fn_2}{ln_2}{year}{serial_str}"

        # 6. Safety check: ensure no collision if un-sequenced IDs exist
        while db.query(User).filter(User.login_id == login_id).first():
            serial_int = company_repo.get_next_serial_transactional(db, company_code, year)
            serial_str = f"{serial_int:04d}"
            login_id = f"{company_code}{fn_2}{ln_2}{year}{serial_str}"

        return login_id

    @staticmethod
    def get_next_serial_info(
        db: Session,
        company_code: str,
        year: Optional[int] = None,
    ) -> SerialNumberLookup:
        """Query next serial lookup schema for a company code and year."""
        target_year = year or date.today().year
        next_serial = company_repo.get_next_serial_transactional(db, company_code, target_year)
        formatted = f"{next_serial:04d}"
        preview = f"{company_code.upper()}JODO{target_year}{formatted}"
        return SerialNumberLookup(
            company_code=company_code.upper(),
            year=target_year,
            next_serial=next_serial,
            formatted_serial=formatted,
            next_login_id_preview=preview,
        )

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
