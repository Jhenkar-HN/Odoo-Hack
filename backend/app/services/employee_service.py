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
        if employee_repo.get_by_email(db, employee_in.email):
            raise DuplicateResourceException("Employee", "email", employee_in.email)
        if user_repo.get_by_email(db, employee_in.email):
            raise DuplicateResourceException("User", "email", employee_in.email)

        # 2. Generate unique employee code
        emp_code = IDGeneratorService.generate_employee_code(db, employee_in.date_of_joining)

        # 3. Create employee entity
        emp_dict = employee_in.model_dump(exclude={"initial_password", "role", "private_info"})
        emp_dict["employee_code"] = emp_code
        db_employee = Employee(**emp_dict)
        db.add(db_employee)
        db.flush()  # Obtain db_employee.id

        # 4. Create private info if provided
        if employee_in.private_info:
            pinfo_data = employee_in.private_info.model_dump(exclude_unset=True)
            pinfo = EmployeePrivateInfo(employee_id=db_employee.id, **pinfo_data)
            db.add(pinfo)

        # 5. Generate Login ID: OI + 2 letters first + 2 letters last + year + seq
        login_id = IDGeneratorService.generate_login_id(
            db=db,
            first_name=db_employee.first_name,
            last_name=db_employee.last_name,
            date_of_joining=db_employee.date_of_joining,
        )

        # 6. Generate temporary password
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

        # 7. Create User Account
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

        # 8. Initialize leave balances for current year
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
        if "email" in update_dict and update_dict["email"] != emp.email:
            existing = employee_repo.get_by_email(db, update_dict["email"])
            if existing and existing.id != employee_id:
                raise DuplicateResourceException("Employee", "email", update_dict["email"])
            # Also update user email if exists
            if emp.user:
                emp.user.email = update_dict["email"]

        for k, v in update_dict.items():
            setattr(emp, k, v)

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
