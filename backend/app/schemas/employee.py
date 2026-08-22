from datetime import date, datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, EmailStr, ConfigDict, Field, model_validator


class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class SkillCreate(SkillBase):
    level: Optional[str] = "Intermediate"


class SkillRead(SkillBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CertificationBase(BaseModel):
    name: Optional[str] = None
    issuing_organization: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = None


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
    
    # Extra payload fields from frontend UI form
    work_email: Optional[str] = None
    monthly_wage: Optional[float] = None
    skills: Optional[List[Any]] = None
    certifications: Optional[List[Any]] = None
    interests_hobbies: Optional[str] = None
    work_hours: Optional[str] = None
    resume_filename: Optional[str] = None
    resume_url: Optional[str] = None
    manager_name: Optional[str] = None
    attendance_status: Optional[str] = None
    status: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_employee_payload(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        
        # 1. Normalize email
        if not data.get("email") and data.get("work_email"):
            data["email"] = data["work_email"].strip()

        # 2. Normalize avatar / profile picture
        if not data.get("profile_picture") and data.get("avatar_url"):
            data["profile_picture"] = data["avatar_url"].strip() or None

        # 3. Clean empty strings for optional fields
        for field in ["date_of_birth", "personal_email", "phone", "gender", "nationality", 
                      "marital_status", "residing_address", "about", "profile_picture", 
                      "initial_password", "manager_id"]:
            val = data.get(field)
            if val is not None and isinstance(val, str) and not val.strip():
                data[field] = None
            elif val == "Not Specified":
                data[field] = None

        # 4. Assemble private_info if sent flat
        pan = data.get("pan") or data.get("pan_number")
        uan = data.get("uan") or data.get("uan_number")
        bank_acc = data.get("bank_account_number") or data.get("account_number")
        ifsc = data.get("ifsc") or data.get("ifsc_code")
        bank_name = data.get("bank_name")

        if not data.get("private_info") and any([pan, uan, bank_acc, ifsc, bank_name]):
            data["private_info"] = {
                "pan": pan.strip() if pan else None,
                "uan": uan.strip() if uan else None,
                "bank_account_number": bank_acc.strip() if bank_acc else None,
                "bank_name": bank_name.strip() if bank_name else None,
                "ifsc": ifsc.strip() if ifsc else None,
            }

        return data


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    work_email: Optional[str] = None
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
    monthly_wage: Optional[float] = None
    skills: Optional[List[Any]] = None
    certifications: Optional[List[Any]] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_update_payload(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        if not data.get("email") and data.get("work_email"):
            data["email"] = data["work_email"].strip()
        if not data.get("profile_picture") and data.get("avatar_url"):
            data["profile_picture"] = data["avatar_url"].strip() or None
        for field in ["date_of_birth", "personal_email", "phone", "gender", "nationality", 
                      "marital_status", "residing_address", "about", "profile_picture", "manager_id"]:
            val = data.get(field)
            if val is not None and isinstance(val, str) and not val.strip():
                data[field] = None
            elif val == "Not Specified":
                data[field] = None
        return data


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
