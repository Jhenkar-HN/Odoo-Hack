from fastapi import APIRouter, HTTPException, Query, Header, status
from typing import Optional, List
from app.models import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeListResponse,
    StatusToggleRequest,
    AttendanceToggleRequest,
)
from app import crud

router = APIRouter(prefix="/api/employees", tags=["Employees"])


def _require_hr(authorization: Optional[str] = None):
    """Validate that the request comes from an HR user via the Authorization header token."""
    if not authorization or not authorization.startswith("hrms-token-"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    parts = authorization.split("-")
    if len(parts) < 4 or parts[3] != "hr":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only HR administrators can perform this action.")


@router.get("", response_model=EmployeeListResponse)
def list_employees(
    search: Optional[str] = Query(None, description="Search by name, email, phone, role, ID, skill"),
    department: Optional[str] = Query(None, description="Filter by department"),
    status: Optional[str] = Query(None, description="Filter by status (active, inactive)"),
    attendance_status: Optional[str] = Query(None, description="Filter by attendance status"),
    sort_by: str = Query("id", description="Sort field (name, department, date_of_joining, wage)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """Retrieve all employees with full-text search, multi-factor filtering, and pagination."""
    items, total = crud.get_employees(
        search=search,
        department=department,
        status=status,
        attendance_status=attendance_status,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        limit=limit,
    )
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "items": items,
    }


@router.get("/departments", response_model=List[str])
def get_departments():
    """Get list of existing departments across all employees."""
    stats = crud.get_dashboard_stats()
    depts = list(stats.get("department_distribution", {}).keys())
    standard_depts = ["Engineering", "Design", "Human Resources", "Finance", "Marketing", "Sales", "Operations"]
    for d in standard_depts:
        if d not in depts:
            depts.append(d)
    return sorted(depts)


@router.get("/check-email")
def check_email_exists(
    email: str = Query(..., description="Email to check for duplicates"),
    exclude_id: Optional[int] = Query(None, description="Employee ID to exclude (for edit forms)"),
):
    """Check if an employee email already exists in the database. Returns {exists: bool}."""
    existing = crud.get_employee_by_email(email.strip(), exclude_id=exclude_id)
    return {"exists": existing is not None}


@router.get("/{emp_id}", response_model=EmployeeResponse)
def get_employee(emp_id: int):
    """Retrieve full employee profile by ID."""
    emp = crud.get_employee_by_id(emp_id)
    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID #{emp_id} not found."
        )
    return emp


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee_endpoint(employee_in: EmployeeCreate, authorization: Optional[str] = Header(None)):
    """Create a new employee profile with automatic ID generation, duplicate email check, and validation. HR only."""
    _require_hr(authorization)
    try:
        new_emp = crud.create_employee(employee_in)
        return new_emp
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while onboarding employee: {str(e)}"
        )


@router.put("/{emp_id}", response_model=EmployeeResponse)
def update_employee_endpoint(emp_id: int, employee_update: EmployeeUpdate, authorization: Optional[str] = Header(None)):
    """Update employee details with validation. HR only."""
    _require_hr(authorization)
    try:
        updated = crud.update_employee(emp_id, employee_update)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee #{emp_id} not found."
            )
        return updated
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error updating employee: {str(e)}"
        )


@router.delete("/{emp_id}", status_code=status.HTTP_200_OK)
def delete_employee_endpoint(emp_id: int, hard: bool = Query(False, description="Perform permanent hard delete if true"), authorization: Optional[str] = Header(None)):
    """Soft-delete (deactivate) or permanently delete an employee. HR only."""
    _require_hr(authorization)
    existing = crud.get_employee_by_id(emp_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee #{emp_id} not found."
        )
    success = crud.delete_employee(emp_id, hard_delete=hard)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete employee."
        )
    return {
        "success": True,
        "message": f"Employee #{emp_id} {'permanently deleted' if hard else 'deactivated successfully'}."
    }


@router.patch("/{emp_id}/status", response_model=EmployeeResponse)
def toggle_status(emp_id: int, req: StatusToggleRequest):
    """Toggle employee employment status (active / inactive / on_leave)."""
    updated = crud.toggle_employee_status(emp_id, req.status)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee #{emp_id} not found."
        )
    return updated


@router.patch("/{emp_id}/attendance", response_model=EmployeeResponse)
def toggle_attendance(emp_id: int, req: AttendanceToggleRequest):
    """Update employee attendance state (present, absent, on_leave)."""
    updated = crud.toggle_attendance_status(emp_id, req.attendance_status)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee #{emp_id} not found."
        )
    return updated
