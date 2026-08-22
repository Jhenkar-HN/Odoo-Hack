from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from backend.app.models.user import UserRole


class UserBase(BaseModel):
    login_id: str
    email: EmailStr
    role: UserRole
    is_active: bool = True
    must_change_password: bool = False


class UserCreate(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.EMPLOYEE
    password: Optional[str] = None
    employee_id: Optional[int] = None
    must_change_password: bool = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    must_change_password: Optional[bool] = None


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserRead(UserBase):
    id: int
    employee_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
