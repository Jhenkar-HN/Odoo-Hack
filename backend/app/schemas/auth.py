from typing import Optional
from pydantic import BaseModel, Field
from backend.app.models.user import UserRole


class LoginRequest(BaseModel):
    login_id: str = Field(..., description="Login ID (e.g. OIJH2026001) or Email", min_length=3)
    password: str = Field(..., description="User password", min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user_id: int
    login_id: str
    email: str
    role: UserRole
    employee_id: Optional[int] = None
    must_change_password: bool = False


class TokenPayload(BaseModel):
    sub: str
    role: UserRole
    employee_id: Optional[int] = None
    exp: int


class PasswordChangeRequest(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, description="New password with minimum 6 characters")
