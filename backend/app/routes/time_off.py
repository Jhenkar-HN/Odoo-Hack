from datetime import datetime, timezone
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
from backend.app.models.leave import LeaveRequestStatus
from backend.app.repositories.leave_repo import leave_repo
from backend.app.services.leave_service import leave_service
from backend.app.schemas.leave import (
    LeaveTypeCreate,
    LeaveTypeRead,
    LeaveBalanceRead,
    TimeOffRequestCreate,
    TimeOffRequestRead,
    TimeOffReviewRequest,
)
from backend.app.schemas.common import ApiResponse, PaginatedResponse

router = APIRouter(prefix="/time-off", tags=["Time Off & Leave Management"])


# --- Leave Types ---

@router.get("/leave-types", response_model=ApiResponse[List[LeaveTypeRead]])
def list_leave_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all available leave categories (Paid Leave, Sick Leave, Unpaid Leave, etc.)."""
    types = leave_repo.get_all_leave_types(db)
    return ApiResponse(
        success=True,
        message="Leave types retrieved",
        data=[LeaveTypeRead.model_validate(t) for t in types],
    )


@router.post("/leave-types", response_model=ApiResponse[LeaveTypeRead], status_code=status.HTTP_201_CREATED)
def create_leave_type(
    type_in: LeaveTypeCreate,
    db: Session = Depends(get_db),
    admin_hr: User = Depends(require_hr_or_admin),
):
    """Create new leave category (ADMIN or HR_OFFICER only)."""
    existing = leave_repo.get_leave_type_by_name(db, type_in.name)
    if existing:
        raise BusinessRuleException(f"Leave type '{type_in.name}' already exists.")

    lt = leave_repo.create_leave_type(db, type_in.name, type_in.default_allocation)
    return ApiResponse(
        success=True,
        message="Leave type created successfully",
        data=LeaveTypeRead.model_validate(lt),
    )


# --- Leave Balances ---

@router.get("/my-balances", response_model=ApiResponse[List[LeaveBalanceRead]])
def get_my_leave_balances(
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get remaining leave balances for the logged-in employee."""
    if not current_user.employee_id:
        raise BusinessRuleException("User is not linked to an employee profile.")

    query_year = year or datetime.now(timezone.utc).year
    balances = leave_repo.get_all_balances_by_employee(db, current_user.employee_id, query_year)
    if not balances:
        balances = leave_repo.initialize_balances_for_employee(db, current_user.employee_id, query_year)

    results = []
    for b in balances:
        br = LeaveBalanceRead.model_validate(b)
        br.leave_type_name = b.leave_type.name if b.leave_type else None
        results.append(br)

    return ApiResponse(
        success=True,
        message="Leave balances retrieved",
        data=results,
    )


@router.get("/balances/{employee_id}", response_model=ApiResponse[List[LeaveBalanceRead]])
def get_employee_leave_balances(
    employee_id: int,
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get leave balances for a specific employee. Protected: ADMIN, HR, or Self."""
    verify_employee_access(employee_id, current_user)

    query_year = year or datetime.now(timezone.utc).year
    balances = leave_repo.get_all_balances_by_employee(db, employee_id, query_year)
    if not balances:
        balances = leave_repo.initialize_balances_for_employee(db, employee_id, query_year)

    results = []
    for b in balances:
        br = LeaveBalanceRead.model_validate(b)
        br.leave_type_name = b.leave_type.name if b.leave_type else None
        results.append(br)

    return ApiResponse(
        success=True,
        message="Employee leave balances retrieved",
        data=results,
    )


# --- Time-Off Requests ---

@router.post("/requests", response_model=ApiResponse[TimeOffRequestRead], status_code=status.HTTP_201_CREATED)
def apply_time_off(
    request_in: TimeOffRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Submit a new time-off / leave application."""
    if not current_user.employee_id:
        raise BusinessRuleException("User is not linked to an employee profile.")

    req = leave_service.apply_for_time_off(db, current_user.employee_id, request_in)
    res = TimeOffRequestRead.model_validate(req)
    res.employee_name = req.employee.full_name if req.employee else None
    res.leave_type_name = req.leave_type.name if req.leave_type else None

    return ApiResponse(
        success=True,
        message="Time-off request submitted successfully",
        data=res,
    )


@router.get("/my-requests", response_model=ApiResponse[PaginatedResponse[TimeOffRequestRead]])
def get_my_time_off_requests(
    status: Optional[LeaveRequestStatus] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List personal time-off requests."""
    if not current_user.employee_id:
        raise BusinessRuleException("User is not linked to an employee profile.")

    skip = (page - 1) * size
    items, total = leave_repo.get_requests(
        db, employee_id=current_user.employee_id, status=status, skip=skip, limit=size
    )
    pages = (total + size - 1) // size

    records = []
    for r in items:
        tr = TimeOffRequestRead.model_validate(r)
        tr.employee_name = r.employee.full_name if r.employee else None
        tr.leave_type_name = r.leave_type.name if r.leave_type else None
        records.append(tr)

    return ApiResponse(
        success=True,
        message="Time-off requests retrieved",
        data=PaginatedResponse(
            items=records,
            total=total,
            page=page,
            size=size,
            pages=pages,
        ),
    )


@router.get("/requests", response_model=ApiResponse[PaginatedResponse[TimeOffRequestRead]])
def list_all_time_off_requests(
    employee_id: Optional[int] = Query(None),
    status: Optional[LeaveRequestStatus] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_hr: User = Depends(require_hr_or_admin),
):
    """List all employee time-off requests across company (ADMIN or HR_OFFICER only)."""
    skip = (page - 1) * size
    items, total = leave_repo.get_requests(
        db, employee_id=employee_id, status=status, skip=skip, limit=size
    )
    pages = (total + size - 1) // size

    records = []
    for r in items:
        tr = TimeOffRequestRead.model_validate(r)
        tr.employee_name = r.employee.full_name if r.employee else None
        tr.leave_type_name = r.leave_type.name if r.leave_type else None
        records.append(tr)

    return ApiResponse(
        success=True,
        message="Time-off requests retrieved",
        data=PaginatedResponse(
            items=records,
            total=total,
            page=page,
            size=size,
            pages=pages,
        ),
    )


@router.put("/requests/{id}/review", response_model=ApiResponse[TimeOffRequestRead])
def review_time_off_request(
    id: int,
    review_data: TimeOffReviewRequest,
    db: Session = Depends(get_db),
    admin_hr: User = Depends(require_hr_or_admin),
):
    """Approve or reject time-off request and adjust leave balance (ADMIN or HR_OFFICER only)."""
    req = leave_service.review_request(db, id, admin_hr.id, review_data)
    tr = TimeOffRequestRead.model_validate(req)
    tr.employee_name = req.employee.full_name if req.employee else None
    tr.leave_type_name = req.leave_type.name if req.leave_type else None

    return ApiResponse(
        success=True,
        message=f"Time-off request marked as {req.status.value}",
        data=tr,
    )


@router.put("/requests/{id}/approve", response_model=ApiResponse[TimeOffRequestRead])
def approve_time_off_request(
    id: int,
    db: Session = Depends(get_db),
    admin_hr: User = Depends(require_hr_or_admin),
):
    """Approve time-off request (ADMIN or HR_OFFICER only)."""
    return review_time_off_request(
        id=id,
        review_data=TimeOffReviewRequest(status=LeaveRequestStatus.APPROVED),
        db=db,
        admin_hr=admin_hr,
    )


@router.put("/requests/{id}/reject", response_model=ApiResponse[TimeOffRequestRead])
def reject_time_off_request(
    id: int,
    rejection_reason: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin_hr: User = Depends(require_hr_or_admin),
):
    """Reject time-off request (ADMIN or HR_OFFICER only)."""
    return review_time_off_request(
        id=id,
        review_data=TimeOffReviewRequest(
            status=LeaveRequestStatus.REJECTED, rejection_reason=rejection_reason
        ),
        db=db,
        admin_hr=admin_hr,
    )


@router.post("/requests/{id}/cancel", response_model=ApiResponse[TimeOffRequestRead])
def cancel_time_off_request(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Cancel personal time-off request."""
    if not current_user.employee_id:
        raise BusinessRuleException("User is not linked to an employee profile.")

    req = leave_service.cancel_request(db, id, current_user.employee_id)
    tr = TimeOffRequestRead.model_validate(req)
    tr.employee_name = req.employee.full_name if req.employee else None
    tr.leave_type_name = req.leave_type.name if req.leave_type else None

    return ApiResponse(
        success=True,
        message="Time-off request cancelled",
        data=tr,
    )
