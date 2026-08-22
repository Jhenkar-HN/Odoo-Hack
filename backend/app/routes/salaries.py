from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.exceptions import NotFoundException
from backend.app.dependencies.auth import get_current_active_user
from backend.app.dependencies.rbac import (
    require_admin,
    require_hr_or_admin,
    verify_employee_access,
)
from backend.app.models.user import User
from backend.app.services.salary_service import salary_service
from backend.app.schemas.salary import (
    SalaryCreate,
    SalaryUpdate,
    SalaryRead,
    SalaryBreakdown,
)
from backend.app.schemas.common import ApiResponse

router = APIRouter(prefix="/salaries", tags=["Salary & Payroll"])


@router.get("", response_model=ApiResponse[List[SalaryRead]])
def list_salaries(
    db: Session = Depends(get_db),
    admin_hr: User = Depends(require_hr_or_admin),
):
    """List all salary records across the company (ADMIN or HR_OFFICER only)."""
    salaries = salary_service.get_all_salaries(db)
    items = []
    for s in salaries:
        sr = SalaryRead.model_validate(s)
        sr.total_earnings = s.total_earnings
        sr.total_deductions = s.total_deductions
        sr.net_salary = s.net_salary
        items.append(sr)

    return ApiResponse(
        success=True,
        message="Salary records retrieved",
        data=items,
    )


@router.get("/employee/{employee_id}", response_model=ApiResponse[SalaryRead])
def get_employee_salary(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get salary record for a specific employee.
    Protected: ADMIN, HR_OFFICER, or Self (employee viewing own salary).
    """
    verify_employee_access(employee_id, current_user)

    salary = salary_service.get_employee_salary(db, employee_id)
    if not salary:
        raise NotFoundException("Salary record for employee", employee_id)

    sr = SalaryRead.model_validate(salary)
    sr.total_earnings = salary.total_earnings
    sr.total_deductions = salary.total_deductions
    sr.net_salary = salary.net_salary

    return ApiResponse(
        success=True,
        message="Salary details retrieved",
        data=sr,
    )


@router.get("/employee/{employee_id}/breakdown", response_model=ApiResponse[SalaryBreakdown])
def get_salary_breakdown(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get computed breakdown of salary components, gross earnings, PF, and net take-home pay.
    Protected: ADMIN, HR_OFFICER, or Self.
    """
    verify_employee_access(employee_id, current_user)
    breakdown = salary_service.get_salary_breakdown(db, employee_id)
    return ApiResponse(
        success=True,
        message="Salary breakdown computed",
        data=breakdown,
    )


@router.post("/employee/{employee_id}", response_model=ApiResponse[SalaryRead], status_code=status.HTTP_201_CREATED)
def set_employee_salary(
    employee_id: int,
    salary_in: SalaryCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Create or update employee salary structure (ADMIN only)."""
    salary = salary_service.create_or_update_salary(db, employee_id, salary_in)

    sr = SalaryRead.model_validate(salary)
    sr.total_earnings = salary.total_earnings
    sr.total_deductions = salary.total_deductions
    sr.net_salary = salary.net_salary

    return ApiResponse(
        success=True,
        message="Salary structure configured successfully",
        data=sr,
    )
