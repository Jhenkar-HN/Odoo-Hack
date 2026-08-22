import secrets
import string
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from backend.app.core.security import get_password_hash
from backend.app.core.exceptions import (
    DuplicateResourceException,
    NotFoundException,
    BusinessRuleException,
)
from backend.app.models.user import User, UserRole
from backend.app.models.employee import (
    Employee,
    EmployeePrivateInfo,
    Certification,
)
from backend.app.repositories.employee_repo import employee_repo
from backend.app.repositories.user_repo import user_repo
from backend.app.repositories.leave_repo import leave_repo
from backend.app.services.id_generator import IDGeneratorService
from backend.app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeePrivateInfoUpdate,
    CertificationCreate,
)


class EmployeeService:
    @staticmethod
    def create_employee(
        db: Session, employee_in: EmployeeCreate
    ) -> Tuple[Employee, User, str]:
        """
        Create employee, generate login ID, create linked user account, and initialize leave balances.
        Returns: (Employee, User, temporary_password)
        """
        # 1. Check for duplicate email in employees or users
        email = employee_in.email or employee_in.work_email
        if not email:
            raise BusinessRuleException("Work email is required.")

        if employee_repo.get_by_email(db, email):
            raise DuplicateResourceException("Employee", "email", email)
        if user_repo.get_by_email(db, email):
            raise DuplicateResourceException("User", "email", email)

        # 2. Generate unique employee code
        emp_code = IDGeneratorService.generate_employee_code(db, employee_in.date_of_joining)

        # 3. Create employee entity with only valid columns
        employee_cols = {
            "first_name", "last_name", "email", "phone", "department", "job_position",
            "manager_id", "company", "location", "date_of_joining", "date_of_birth",
            "gender", "nationality", "marital_status", "residing_address",
            "personal_email", "profile_picture", "about"
        }
        raw_emp_dict = employee_in.model_dump()
        raw_emp_dict["email"] = email
        emp_dict = {k: v for k, v in raw_emp_dict.items() if k in employee_cols}
        emp_dict["employee_code"] = emp_code
        db_employee = Employee(**emp_dict)
        db.add(db_employee)
        db.flush()  # Obtain db_employee.id

        # 4. Create private info if provided
        if employee_in.private_info:
            pinfo_data = employee_in.private_info.model_dump(exclude_unset=True)
            if any(pinfo_data.values()):
                pinfo = EmployeePrivateInfo(employee_id=db_employee.id, **pinfo_data)
                db.add(pinfo)

        # 5. Create salary if monthly_wage provided
        monthly_wage = employee_in.monthly_wage
        if monthly_wage is not None and float(monthly_wage) > 0:
            from decimal import Decimal
            from backend.app.models.salary import Salary
            wage = Decimal(str(monthly_wage))
            basic = (wage * Decimal("0.50")).quantize(Decimal("0.01"))
            hra = (basic * Decimal("0.50")).quantize(Decimal("0.01"))
            bonus = (basic * Decimal("0.0833")).quantize(Decimal("0.01"))
            lta = (basic * Decimal("0.0833")).quantize(Decimal("0.01"))
            temp_sum = basic + hra + bonus + lta
            std_allow = Decimal("4167.00") if wage >= (temp_sum + Decimal("4167.00")) else max(Decimal("0.00"), wage - temp_sum)
            fixed_allow = max(Decimal("0.00"), wage - (basic + hra + bonus + lta + std_allow))
            pf = (basic * Decimal("0.12")).quantize(Decimal("0.01"))
            pt = Decimal("200.00") if wage > Decimal("15000.00") else Decimal("0.00")

            salary = Salary(
                employee_id=db_employee.id,
                monthly_wage=wage,
                yearly_wage=wage * 12,
                basic_salary=basic,
                hra=hra,
                standard_allowance=std_allow,
                performance_bonus=bonus,
                leave_travel_allowance=lta,
                fixed_allowance=fixed_allow,
                employee_pf=pf,
                employer_pf=pf,
                professional_tax=pt,
                effective_from=db_employee.date_of_joining or date.today(),
            )
            db.add(salary)

        # 6. Save skills if provided
        if employee_in.skills:
            for s in employee_in.skills:
                skill_name = s.get("name") if isinstance(s, dict) else (getattr(s, "name", None) or str(s))
                if skill_name and skill_name.strip():
                    sk = employee_repo.get_or_create_skill(db, skill_name.strip())
                    employee_repo.add_employee_skill(db, db_employee.id, sk.id)

        # 7. Save certifications if provided
        if employee_in.certifications:
            for c in employee_in.certifications:
                if isinstance(c, dict):
                    title = c.get("title") or c.get("name")
                    issuer = c.get("issuer") or c.get("issuing_organization") or "Organization"
                    issue_d = c.get("issue_date")
                    expiry_d = c.get("expiry_date")
                    if title and issue_d:
                        try:
                            if isinstance(issue_d, str) and len(issue_d) == 7:
                                issue_d_val = datetime.strptime(f"{issue_d}-01", "%Y-%m-%d").date()
                            elif isinstance(issue_d, str):
                                issue_d_val = datetime.strptime(issue_d, "%Y-%m-%d").date()
                            else:
                                issue_d_val = issue_d

                            expiry_d_val = None
                            if expiry_d:
                                if isinstance(expiry_d, str) and len(expiry_d) == 7:
                                    expiry_d_val = datetime.strptime(f"{expiry_d}-01", "%Y-%m-%d").date()
                                elif isinstance(expiry_d, str):
                                    expiry_d_val = datetime.strptime(expiry_d, "%Y-%m-%d").date()
                                else:
                                    expiry_d_val = expiry_d

                            employee_repo.add_certification(db, db_employee.id, {
                                "name": title,
                                "issuing_organization": issuer,
                                "issue_date": issue_d_val,
                                "expiry_date": expiry_d_val,
                            })
                        except Exception:
                            pass

        # 8. Save resume if provided
        if employee_in.resume_url:
            from backend.app.models.employee import Resume
            resume = Resume(
                employee_id=db_employee.id,
                file_path=employee_in.resume_url,
            )
            db.add(resume)

        # 9. Generate Login ID: OI + 2 letters first + 2 letters last + year + seq
        login_id = IDGeneratorService.generate_login_id(
            db=db,
            first_name=db_employee.first_name,
            last_name=db_employee.last_name,
            date_of_joining=db_employee.date_of_joining,
        )

        # 10. Generate temporary password
        if employee_in.initial_password:
            raw_password = employee_in.initial_password
            must_change = False
        else:
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            raw_password = "".join(secrets.choice(alphabet) for _ in range(10))
            must_change = True

        role_enum = UserRole.EMPLOYEE
        if employee_in.role:
            try:
                role_enum = UserRole(employee_in.role.upper())
            except ValueError:
                role_enum = UserRole.EMPLOYEE

        # 11. Create User Account
        user_account = User(
            employee_id=db_employee.id,
            login_id=login_id,
            email=db_employee.email,
            password_hash=get_password_hash(raw_password),
            role=role_enum,
            is_active=True,
            must_change_password=must_change,
        )
        db.add(user_account)

        # 12. Initialize leave balances for current year
        current_year = db_employee.date_of_joining.year or datetime.now(timezone.utc).year
        leave_repo.initialize_balances_for_employee(db, db_employee.id, current_year)

        db.commit()
        db.refresh(db_employee)
        db.refresh(user_account)

        return db_employee, user_account, raw_password

    @staticmethod
    def get_employee_by_id(db: Session, employee_id: int) -> Employee:
        emp = employee_repo.get(db, employee_id)
        if not emp:
            raise NotFoundException("Employee", employee_id)
        return emp

    @staticmethod
    def update_employee(
        db: Session, employee_id: int, update_data: EmployeeUpdate
    ) -> Employee:
        emp = EmployeeService.get_employee_by_id(db, employee_id)

        update_dict = update_data.model_dump(exclude_unset=True)
        email = update_dict.get("email") or update_dict.get("work_email")
        if email and email != emp.email:
            existing = employee_repo.get_by_email(db, email)
            if existing and existing.id != employee_id:
                raise DuplicateResourceException("Employee", "email", email)
            emp.email = email
            if emp.user:
                emp.user.email = email

        employee_cols = {
            "first_name", "last_name", "phone", "department", "job_position",
            "manager_id", "company", "location", "date_of_joining", "date_of_birth",
            "gender", "nationality", "marital_status", "residing_address",
            "personal_email", "profile_picture", "about"
        }
        for k, v in update_dict.items():
            if k in employee_cols:
                setattr(emp, k, v)

        if "monthly_wage" in update_dict and update_dict["monthly_wage"] is not None:
            from decimal import Decimal
            from backend.app.schemas.salary import SalaryCreate
            from backend.app.services.salary_service import salary_service
            wage = Decimal(str(update_dict["monthly_wage"]))
            salary_service.create_or_update_salary(
                db, employee_id, SalaryCreate(monthly_wage=wage)
            )

        db.commit()
        db.refresh(emp)
        return emp

    @staticmethod
    def delete_employee(db: Session, employee_id: int) -> bool:
        emp = EmployeeService.get_employee_by_id(db, employee_id)
        if emp.user:
            db.delete(emp.user)
        db.delete(emp)
        db.commit()
        return True

    # Private info
    @staticmethod
    def get_private_info(db: Session, employee_id: int) -> Optional[EmployeePrivateInfo]:
        emp = EmployeeService.get_employee_by_id(db, employee_id)
        return emp.private_info

    @staticmethod
    def update_private_info(
        db: Session, employee_id: int, info_in: EmployeePrivateInfoUpdate
    ) -> EmployeePrivateInfo:
        # Ensure employee exists
        EmployeeService.get_employee_by_id(db, employee_id)
        return employee_repo.set_private_info(
            db, employee_id, info_in.model_dump(exclude_unset=True)
        )

    # Skills
    @staticmethod
    def add_skill(db: Session, employee_id: int, skill_name: str) -> None:
        EmployeeService.get_employee_by_id(db, employee_id)
        skill = employee_repo.get_or_create_skill(db, skill_name)
        employee_repo.add_employee_skill(db, employee_id, skill.id)

    @staticmethod
    def remove_skill(db: Session, employee_id: int, skill_id: int) -> bool:
        return employee_repo.remove_employee_skill(db, employee_id, skill_id)

    # Certifications
    @staticmethod
    def add_certification(
        db: Session, employee_id: int, cert_in: CertificationCreate
    ) -> Certification:
        EmployeeService.get_employee_by_id(db, employee_id)
        return employee_repo.add_certification(db, employee_id, cert_in.model_dump())

    @staticmethod
    def delete_certification(db: Session, cert_id: int) -> bool:
        return employee_repo.delete_certification(db, cert_id)


employee_service = EmployeeService()
