from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from backend.app.models.leave import LeaveRequestStatus


class LeaveTypeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    default_allocation: int = Field(default=12, ge=0)


class LeaveTypeCreate(LeaveTypeBase):
    pass


class LeaveTypeRead(LeaveTypeBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class LeaveBalanceRead(BaseModel):
    id: int
    employee_id: int
    leave_type_id: int
    leave_type_name: Optional[str] = None
    year: int
    allocated_days: Decimal
    used_days: Decimal
    remaining_days: Decimal

    model_config = ConfigDict(from_attributes=True)


class TimeOffRequestCreate(BaseModel):
    leave_type_id: int
    start_date: date
    end_date: date
    reason: Optional[str] = None
    attachment_path: Optional[str] = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date cannot be earlier than start_date")
        return self


class TimeOffReviewRequest(BaseModel):
    status: LeaveRequestStatus = Field(..., description="Must be APPROVED or REJECTED")
    rejection_reason: Optional[str] = None


class TimeOffRequestRead(BaseModel):
    id: int
    employee_id: int
    employee_name: Optional[str] = None
    leave_type_id: int
    leave_type_name: Optional[str] = None
    start_date: date
    end_date: date
    number_of_days: Decimal
    reason: Optional[str] = None
    attachment_path: Optional[str] = None
    status: LeaveRequestStatus
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
