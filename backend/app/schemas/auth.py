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
    new_password: str = Field(..., min_length=8, description="New password with minimum 8 characters")


class SignUpRequest(BaseModel):
    employee_id: str = Field(..., min_length=2, max_length=50, description="Company Employee ID / Code")
    email: str = Field(..., min_length=5, max_length=255, description="Corporate or Work Email")
    password: str = Field(..., min_length=8, max_length=128, description="Password meeting security rules")
    role: UserRole = Field(default=UserRole.EMPLOYEE, description="Requested Role: EMPLOYEE or HR_OFFICER")
    full_name: Optional[str] = Field(None, max_length=150, description="Full Name of user")
    verification_code: Optional[str] = Field(None, max_length=10, description="Email verification code")

    @model_validator(mode="before")
    @classmethod
    def normalize_role(cls, data: Any) -> Any:
        if isinstance(data, dict) and "role" in data:
            val = str(data["role"]).upper().strip()
            if val in ["HR", "HR_ADMIN", "ADMIN"]:
                data["role"] = UserRole.HR_OFFICER.value
            elif val in ["EMPLOYEE", "EMP"]:
                data["role"] = UserRole.EMPLOYEE.value
        return data

    @model_validator(mode="after")
    def validate_password_rules(self) -> "SignUpRequest":
        pwd = self.password
        if len(pwd) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        has_letter = any(c.isalpha() for c in pwd)
        has_digit = any(c.isdigit() for c in pwd)
        if not (has_letter and has_digit):
            raise ValueError("Password must contain both letters and digits for security compliance.")
        return self


class EmailVerificationRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    code: Optional[str] = Field(None, max_length=10)

