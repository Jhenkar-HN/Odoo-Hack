from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.dependencies.auth import get_current_active_user
from backend.app.models.user import User
from backend.app.services.auth_service import auth_service
from backend.app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    PasswordChangeRequest,
    SignUpRequest,
    EmailVerificationRequest,
)
from backend.app.schemas.user import UserRead
from backend.app.schemas.common import ApiResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=ApiResponse[TokenResponse])
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user with login_id or email and return JWT token."""
    token_resp = auth_service.authenticate_user(db, login_data)
    return ApiResponse(
        success=True,
        message="Authentication successful",
        data=token_resp,
    )


@router.post("/signup", response_model=ApiResponse[TokenResponse], status_code=status.HTTP_201_CREATED)
def signup(signup_data: SignUpRequest, db: Session = Depends(get_db)):
    """Register a new user account with employee code, email, and security-compliant password."""
    token_resp = auth_service.register_user(db, signup_data)
    return ApiResponse(
        success=True,
        message="Account created and authenticated successfully",
        data=token_resp,
    )


@router.post("/verify-email", response_model=ApiResponse[dict])
def verify_email(data: EmailVerificationRequest):
    """Verify email address with verification code."""
    return ApiResponse(
        success=True,
        message="Email verified successfully",
        data={"email": data.email, "verified": True},
    )



@router.post("/logout", response_model=ApiResponse[None])
def logout(current_user: User = Depends(get_current_active_user)):
    """Log out current user (client invalidates token)."""
    return ApiResponse(
        success=True,
        message="Successfully logged out",
        data=None,
    )


@router.get("/me", response_model=ApiResponse[UserRead])
def get_me(current_user: User = Depends(get_current_active_user)):
    """Retrieve current authenticated user's profile and assigned role."""
    return ApiResponse(
        success=True,
        message="Current user profile retrieved",
        data=UserRead.model_validate(current_user),
    )


@router.post("/change-password", response_model=ApiResponse[None])
def change_password(
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Change current user password."""
    auth_service.change_password(db, current_user, data)
    return ApiResponse(
        success=True,
        message="Password updated successfully",
        data=None,
    )
