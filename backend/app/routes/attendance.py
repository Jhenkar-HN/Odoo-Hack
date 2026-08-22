from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.exceptions import BusinessRuleException, NotFoundException
from backend.app.dependencies.auth import get_current_active_user
from backend.app.dependencies.rbac import (
    require_hr_or_admin,
    verify_employee_access,
)
from backend.app.models.user import User
from backend.app.repositories.attendance_repo import attendance_repo
from backend.app.services.attendance_service import attendance_service
from backend.app.schemas.attendance import (
    CheckInRequest,
    CheckOutRequest,
    AttendanceRead,
    AttendanceSummary,
)
from backend.app.schemas.common import ApiResponse, PaginatedResponse

router = APIRouter(prefix="/attendance", tags=["Attendance Management"])


@router.post("/check-in", response_model=ApiResponse[AttendanceRead], status_code=status.HTTP_201_CREATED)
def check_in(
    data: CheckInRequest = CheckInRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Record attendance check-in timestamp for current employee."""
    if not current_user.employee_id:
        raise BusinessRuleException("User is not linked to an employee profile.")

    record = attendance_service.check_in(db, current_user.employee_id, data.attendance_date)
    return ApiResponse(
        success=True,
        message="Check-in recorded successfully",
        data=AttendanceRead.model_validate(record),
    )


@router.post("/check-out", response_model=ApiResponse[AttendanceRead])
def check_out(
    data: CheckOutRequest = CheckOutRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Record attendance check-out and compute total & overtime hours."""
    if not current_user.employee_id:
        raise BusinessRuleException("User is not linked to an employee profile.")

    record = attendance_service.check_out(db, current_user.employee_id, data.attendance_date)
    return ApiResponse(
        success=True,
        message="Check-out recorded and hours computed",
        data=AttendanceRead.model_validate(record),
    )


@router.get("/today", response_model=ApiResponse[Optional[AttendanceRead]])
def get_today_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current employee's attendance record for today."""
    if not current_user.employee_id:
        raise BusinessRuleException("User is not linked to an employee profile.")

    record = attendance_repo.get_by_employee_and_date(db, current_user.employee_id, date.today())
    return ApiResponse(
        success=True,
        message="Today's attendance status retrieved",
        data=AttendanceRead.model_validate(record) if record else None,
    )


@router.get("/my-history", response_model=ApiResponse[PaginatedResponse[AttendanceRead]])
def get_my_attendance_history(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get personal attendance log history."""
    if not current_user.employee_id:
        raise BusinessRuleException("User is not linked to an employee profile.")

    skip = (page - 1) * size
    items, total = attendance_repo.get_history(
        db,
        employee_id=current_user.employee_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=size,
    )
    pages = (total + size - 1) // size

    return ApiResponse(
        success=True,
        message="Attendance history retrieved",
        data=PaginatedResponse(
            items=[AttendanceRead.model_validate(r) for r in items],
            total=total,
            page=page,
            size=size,
            pages=pages,
        ),
    )


@router.get("/my-summary", response_model=ApiResponse[AttendanceSummary])
def get_my_attendance_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get attendance summary (days present, work hours, overtime) for logged-in employee."""
    if not current_user.employee_id:
        raise BusinessRuleException("User is not linked to an employee profile.")

    summary = attendance_service.get_summary(db, current_user.employee_id)
    return ApiResponse(
        success=True,
        message="Attendance summary retrieved",
        data=summary,
    )


@router.get("", response_model=ApiResponse[PaginatedResponse[AttendanceRead]])
def list_all_attendance(
    employee_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_hr: User = Depends(require_hr_or_admin),
):
    """List attendance records across the organization (ADMIN or HR_OFFICER only)."""
    skip = (page - 1) * size
    items, total = attendance_repo.get_history(
        db,
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=size,
    )
    pages = (total + size - 1) // size

    return ApiResponse(
        success=True,
        message="Attendance records retrieved",
        data=PaginatedResponse(
            items=[AttendanceRead.model_validate(r) for r in items],
            total=total,
            page=page,
            size=size,
            pages=pages,
        ),
    )


@router.get("/employee/{employee_id}", response_model=ApiResponse[PaginatedResponse[AttendanceRead]])
def get_employee_attendance(
    employee_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get attendance records for a specific employee. Protected: ADMIN, HR, or Self."""
    verify_employee_access(employee_id, current_user)

    skip = (page - 1) * size
    items, total = attendance_repo.get_history(
        db,
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=size,
    )
    pages = (total + size - 1) // size

    return ApiResponse(
        success=True,
        message="Employee attendance retrieved",
        data=PaginatedResponse(
            items=[AttendanceRead.model_validate(r) for r in items],
            total=total,
            page=page,
            size=size,
            pages=pages,
        ),
    )
