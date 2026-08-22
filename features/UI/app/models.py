from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator
from datetime import date
from app.utils import validate_email_format, validate_phone_format


class SkillItem(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    level: str = Field(default="Intermediate", max_length=30)  # Beginner, Intermediate, Advanced, Expert


class CertificationItem(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    issuer: str = Field(default="", max_length=100)
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None


class EmployeeBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=60, description="Employee First Name")
    last_name: str = Field(..., min_length=1, max_length=60, description="Employee Last Name")
    work_email: str = Field(..., min_length=5, max_length=120, description="Corporate Work Email")
    personal_email: Optional[str] = Field(default="", max_length=120, description="Personal Email")
    phone: str = Field(..., min_length=7, max_length=20, description="Contact Phone Number")
    department: str = Field(default="Engineering", max_length=60)
    job_position: str = Field(..., min_length=2, max_length=100, description="Job Title / Position")
    manager_name: Optional[str] = Field(default="", max_length=100)
    location: Optional[str] = Field(default="Headquarters", max_length=100)
    date_of_joining: str = Field(..., min_length=4, max_length=20, description="Joining Date")
    
    # Private / Demographic Info
    date_of_birth: Optional[str] = Field(default="", max_length=20)
    gender: Optional[str] = Field(default="Not Specified", max_length=30)
    marital_status: Optional[str] = Field(default="Single", max_length=30)
    nationality: Optional[str] = Field(default="Indian", max_length=50)
    residing_address: Optional[str] = Field(default="", max_length=255)
    pan_number: Optional[str] = Field(default="", max_length=20)
    uan_number: Optional[str] = Field(default="", max_length=30)

    # Bank Information
    bank_name: Optional[str] = Field(default="", max_length=100)
    account_number: Optional[str] = Field(default="", max_length=50)
    ifsc_code: Optional[str] = Field(default="", max_length=30)

    # Wage & Schedule
    monthly_wage: float = Field(default=50000.0, ge=0.0)
    work_hours: Optional[str] = Field(default="40 hrs/week (09:00 - 18:00)", max_length=100)

    # About & Culture
    about: Optional[str] = Field(default="", max_length=1000)
    interests_hobbies: Optional[str] = Field(default="", max_length=500)
    avatar_url: Optional[str] = Field(default="", max_length=500)
    resume_url: Optional[str] = Field(default="", max_length=500)
    resume_filename: Optional[str] = Field(default="", max_length=255)

    # Statuses
    status: str = Field(default="active", max_length=30)  # active, inactive, on_leave, terminated
    attendance_status: str = Field(default="present", max_length=30)  # present, absent, on_leave

    # Nested skills and certifications
    skills: List[SkillItem] = Field(default_factory=list)
    certifications: List[CertificationItem] = Field(default_factory=list)

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 1:
            raise ValueError("Name cannot be blank.")
        return v

    @field_validator("work_email")
    @classmethod
    def validate_work_email(cls, v: str) -> str:
        v = v.strip()
        if not validate_email_format(v):
            raise ValueError(f"'{v}' is not a valid email address format.")
        return v.lower()

    @field_validator("personal_email")
    @classmethod
    def validate_personal_email(cls, v: Optional[str]) -> Optional[str]:
        if v and v.strip():
            v = v.strip().lower()
            if not validate_email_format(v):
                raise ValueError(f"'{v}' is not a valid personal email format.")
            return v
        return ""

    @field_validator("phone")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        v = v.strip()
        if not validate_phone_format(v):
            raise ValueError("Phone number must contain between 7 and 15 digits.")
        return v

    @field_validator("date_of_joining")
    @classmethod
    def validate_joining(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Date of Joining is required.")
        return v


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    work_email: Optional[str] = None
    personal_email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    job_position: Optional[str] = None
    manager_name: Optional[str] = None
    location: Optional[str] = None
    date_of_joining: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    nationality: Optional[str] = None
    residing_address: Optional[str] = None
    pan_number: Optional[str] = None
    uan_number: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    monthly_wage: Optional[float] = None
    work_hours: Optional[str] = None
    about: Optional[str] = None
    interests_hobbies: Optional[str] = None
    avatar_url: Optional[str] = None
    resume_url: Optional[str] = None
    resume_filename: Optional[str] = None
    status: Optional[str] = None
    attendance_status: Optional[str] = None
    skills: Optional[List[SkillItem]] = None
    certifications: Optional[List[CertificationItem]] = None

    @field_validator("work_email")
    @classmethod
    def validate_opt_work_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not validate_email_format(v):
                raise ValueError(f"'{v}' is not a valid email address.")
            return v.lower()
        return None

    @field_validator("personal_email")
    @classmethod
    def validate_opt_personal_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            v = v.strip().lower()
            if not validate_email_format(v):
                raise ValueError(f"'{v}' is not a valid personal email format.")
            return v
        return v

    @field_validator("phone")
    @classmethod
    def validate_opt_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not validate_phone_format(v):
                raise ValueError("Phone number must contain between 7 and 15 digits.")
            return v
        return None


class StatusToggleRequest(BaseModel):
    status: str = Field(..., max_length=30)  # active, inactive


class AttendanceToggleRequest(BaseModel):
    attendance_status: str = Field(..., max_length=30)  # present, absent, on_leave


class EmployeeResponse(EmployeeBase):
    id: int
    login_id: str
    emp_code: str
    full_name: str
    salary_breakdown: Dict[str, Any]
    created_at: str
    updated_at: str


class EmployeeListResponse(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    items: List[EmployeeResponse]


class DashboardStatsResponse(BaseModel):
    total_employees: int
    active_employees: int
    present_today: int
    on_leave_today: int
    absent_today: int
    departments_count: int
    department_distribution: Dict[str, int]
    status_distribution: Dict[str, int]
    attendance_distribution: Dict[str, int]
    recent_joiners: List[EmployeeResponse]
