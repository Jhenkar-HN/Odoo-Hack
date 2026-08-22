from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class SkillCreate(SkillBase):
    pass


class SkillRead(SkillBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CertificationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    issuing_organization: str = Field(..., min_length=1, max_length=255)
    issue_date: date
    expiry_date: Optional[date] = None


class CertificationCreate(CertificationBase):
    pass


class CertificationRead(CertificationBase):
    id: int
    employee_id: int
    model_config = ConfigDict(from_attributes=True)


class ResumeRead(BaseModel):
    id: int
    employee_id: int
    file_path: str
    uploaded_at: datetime
    model_config = ConfigDict(from_attributes=True)


class EmployeePrivateInfoBase(BaseModel):
    pan: Optional[str] = Field(None, max_length=20)
    uan: Optional[str] = Field(None, max_length=30)
    bank_account_number: Optional[str] = Field(None, max_length=50)
    bank_name: Optional[str] = Field(None, max_length=100)
    ifsc: Optional[str] = Field(None, max_length=20)
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=30)


class EmployeePrivateInfoUpdate(EmployeePrivateInfoBase):
    pass


class EmployeePrivateInfoRead(EmployeePrivateInfoBase):
    id: int
    employee_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class EmployeeBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30)
    department: str = Field(..., min_length=1, max_length=100)
    job_position: str = Field(..., min_length=1, max_length=100)
    manager_id: Optional[int] = None
    company: str = "HRMS Corp"
    location: str = "Headquarters"
    date_of_joining: date = Field(default_factory=date.today)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    marital_status: Optional[str] = None
    residing_address: Optional[str] = None
    personal_email: Optional[EmailStr] = None
    profile_picture: Optional[str] = None
    about: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    # Optional initial password; if omitted, a secure temporary password is generated
    initial_password: Optional[str] = None
    role: Optional[str] = "EMPLOYEE"
    # Optional private info at creation time
    private_info: Optional[EmployeePrivateInfoBase] = None


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    job_position: Optional[str] = None
    manager_id: Optional[int] = None
    company: Optional[str] = None
    location: Optional[str] = None
    date_of_joining: Optional[date] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    marital_status: Optional[str] = None
    residing_address: Optional[str] = None
    personal_email: Optional[EmailStr] = None
    profile_picture: Optional[str] = None
    about: Optional[str] = None


class EmployeeRead(EmployeeBase):
    id: int
    employee_code: str
    full_name: Optional[str] = None
    work_email: Optional[EmailStr] = None
    attendance_status: Optional[str] = None
    salary_breakdown: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class EmployeeDetailRead(EmployeeRead):
    skills: List[SkillRead] = []
    certifications: List[CertificationRead] = []
    private_info: Optional[EmployeePrivateInfoRead] = None
    user_login_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
