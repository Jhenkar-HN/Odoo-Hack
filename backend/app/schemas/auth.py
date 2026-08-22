from typing import Optional, Any
from pydantic import BaseModel, Field, model_validator
from backend.app.models.user import UserRole


class LoginRequest(BaseModel):
    login_id: Optional[str] = Field(None, description="Login ID (e.g. OIJH2026001) or Email")
    username: Optional[str] = Field(None, description="Alternative field for Login ID or Email")
    password: str = Field(..., description="User password", min_length=1)

    @model_validator(mode="before")
    @classmethod
    def normalize_login_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            u = data.get("username")
            l = data.get("login_id")
            val = l or u
            if val:
                data["login_id"] = str(val).strip()
                data["username"] = str(val).strip()
        return data


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

    # Extra helper fields for frontend compatibility
    token: Optional[str] = None
    username: Optional[str] = None
    display_name: Optional[str] = None


class TokenPayload(BaseModel):
    sub: str
    role: UserRole
    employee_id: Optional[int] = None
    exp: int


class PasswordChangeRequest(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, description="New password with minimum 6 characters")
