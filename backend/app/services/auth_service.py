from datetime import date
from sqlalchemy.orm import Session
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.core.exceptions import UnauthorizedException, BusinessRuleException, DuplicateResourceException
from backend.app.models.user import User, UserRole
from backend.app.models.employee import Employee
from backend.app.repositories.user_repo import user_repo
from backend.app.repositories.employee_repo import employee_repo
from backend.app.schemas.auth import LoginRequest, TokenResponse, PasswordChangeRequest, SignUpRequest


class AuthService:
    @staticmethod
    def authenticate_user(db: Session, login_data: LoginRequest) -> TokenResponse:
        """Authenticate user by login_id or email and return JWT access token."""
        user = user_repo.get_by_login_or_email(db, login_data.login_id.strip())
        if not user:
            raise UnauthorizedException("Invalid login credentials")

        if not verify_password(login_data.password, user.password_hash):
            raise UnauthorizedException("Invalid login credentials")

        if not user.is_active:
            raise UnauthorizedException("User account is inactive. Please contact your administrator.")

        token = create_access_token(
            subject=user.id,
            role=user.role.value,
            employee_id=user.employee_id,
        )

        display_name = user.email.split("@")[0].replace(".", " ").title()
        if user.employee and user.employee.full_name:
            display_name = user.employee.full_name

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in_minutes=1440,
            user_id=user.id,
            login_id=user.login_id,
            email=user.email,
            role=user.role,
            employee_id=user.employee_id,
            must_change_password=user.must_change_password,
            token=token,
            username=user.login_id,
            display_name=display_name,
        )

    @staticmethod
    def register_user(db: Session, signup_data: SignUpRequest) -> TokenResponse:
        """Register a new user account with employee linking and role assignment."""
        email = signup_data.email.strip().lower()
        emp_code = signup_data.employee_id.strip()

        # Check existing user
        if user_repo.get_by_email(db, email):
            raise DuplicateResourceException("User", "email", email)

        if user_repo.get_by_login_id(db, emp_code):
            raise DuplicateResourceException("User", "login_id", emp_code)

        # Match or create employee record
        emp = employee_repo.get_by_code(db, emp_code)
        if not emp:
            emp = employee_repo.get_by_email(db, email)

        if not emp:
            name_parts = (signup_data.full_name or email.split("@")[0]).strip().split(" ", 1)
            first_name = name_parts[0].capitalize()
            last_name = name_parts[1].capitalize() if len(name_parts) > 1 else "Team"
            dept = "Human Resources" if signup_data.role == UserRole.HR_OFFICER else "Engineering"
            pos = "HR Specialist" if signup_data.role == UserRole.HR_OFFICER else "Software Engineer"

            emp = Employee(
                employee_code=emp_code,
                first_name=first_name,
                last_name=last_name,
                email=email,
                department=dept,
                job_position=pos,
                date_of_joining=date.today(),
            )
            db.add(emp)
            db.commit()
            db.refresh(emp)

        new_user = User(
            employee_id=emp.id,
            login_id=emp_code,
            email=email,
            password_hash=get_password_hash(signup_data.password),
            role=signup_data.role,
            is_active=True,
            must_change_password=False,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        token = create_access_token(
            subject=new_user.id,
            role=new_user.role.value,
            employee_id=new_user.employee_id,
        )

        display_name = emp.full_name if emp else email.split("@")[0].title()

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in_minutes=1440,
            user_id=new_user.id,
            login_id=new_user.login_id,
            email=new_user.email,
            role=new_user.role,
            employee_id=new_user.employee_id,
            must_change_password=new_user.must_change_password,
            token=token,
            username=new_user.login_id,
            display_name=display_name,
        )

    @staticmethod
    def change_password(db: Session, user: User, data: PasswordChangeRequest) -> bool:
        """Change user password after verifying existing password."""
        if not verify_password(data.old_password, user.password_hash):
            raise UnauthorizedException("Incorrect current password")

        if data.old_password == data.new_password:
            raise BusinessRuleException("New password cannot be the same as the current password")

        user.password_hash = get_password_hash(data.new_password)
        user.must_change_password = False
        db.commit()
        db.refresh(user)
        return True


auth_service = AuthService()

