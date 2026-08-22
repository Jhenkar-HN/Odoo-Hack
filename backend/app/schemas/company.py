from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=20)


class CompanyCreate(CompanyBase):
    pass


class CompanyRead(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SerialNumberLookup(BaseModel):
    company_code: str = Field(..., description="Company code prefix (e.g. CE)")
    year: int = Field(..., description="Year of joining (e.g. 2024)")
    next_serial: int = Field(..., description="Raw integer serial number")
    formatted_serial: str = Field(..., description="Zero-padded 4-digit serial (e.g. 0001)")
    next_login_id_preview: Optional[str] = Field(None, description="Example preview of generated Login ID")


class CompanySettingsBase(BaseModel):
    company_name: Optional[str] = Field("HRMS Corp", max_length=200)
    company_logo: Optional[str] = Field(None, max_length=500)
    contact_email: Optional[str] = Field("contact@hrmscorp.com", max_length=255)
    contact_phone: Optional[str] = Field("+1-555-0199", max_length=50)
    address: Optional[str] = None


class CompanySettingsUpdate(CompanySettingsBase):
    pass


class CompanySettingsRead(CompanySettingsBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
