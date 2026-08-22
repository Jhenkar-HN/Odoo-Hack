from sqlalchemy.orm import Session
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.core.exceptions import UnauthorizedException, BusinessRuleException
from backend.app.models.user import User
from backend.app.repositories.user_repo import user_repo
from backend.app.schemas.auth import LoginRequest, TokenResponse, PasswordChangeRequest


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
