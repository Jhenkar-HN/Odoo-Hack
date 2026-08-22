from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict
from backend.app.models.attendance import AttendanceStatus


class CheckInRequest(BaseModel):
    attendance_date: Optional[date] = None


class CheckOutRequest(BaseModel):
    attendance_date: Optional[date] = None


class AttendanceRead(BaseModel):
    id: int
    employee_id: int
    attendance_date: date
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    work_hours: Decimal
    extra_hours: Decimal
    status: AttendanceStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AttendanceSummary(BaseModel):
    employee_id: int
    total_days_present: int
    total_days_absent: int
    total_work_hours: Decimal
    total_overtime_hours: Decimal
