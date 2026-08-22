from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class CompanySettingsBase(BaseModel):
    company_name: str
    company_logo: Optional[str] = None
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    address: Optional[str] = None


class CompanySettingsUpdate(BaseModel):
    company_name: Optional[str] = None
    company_logo: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None


class CompanySettingsRead(CompanySettingsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
