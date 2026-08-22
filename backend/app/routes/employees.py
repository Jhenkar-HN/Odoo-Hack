from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.exceptions import NotFoundException, PermissionDeniedException
from backend.app.dependencies.auth import get_current_active_user
from backend.app.dependencies.rbac import (
    require_admin,
    require_hr_or_admin,
    verify_employee_access,
)
from backend.app.models.user import User, UserRole
from backend.app.repositories.employee_repo import employee_repo
from backend.app.services.employee_service import employee_service
from backend.app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeRead,
    EmployeeDetailRead,
    EmployeePrivateInfoRead,
    EmployeePrivateInfoUpdate,
    SkillCreate,
    SkillRead,
    CertificationCreate,
    CertificationRead,
)
from backend.app.schemas.common import ApiResponse, PaginatedResponse

router = APIRouter(prefix="/employees", tags=["Employee Management"])


@router.get("", response_model=ApiResponse[PaginatedResponse[EmployeeRead]])
def list_employees(
    query: Optional[str] = Query(None, description="Search by name, code, email, position"),
    department: Optional[str] = Query(None, description="Filter by department"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve directory of employees with search and pagination."""
    skip = (page - 1) * size
    items, total = employee_repo.search_employees(
        db, query_str=query, department=department, skip=skip, limit=size
    )
    pages = (total + size - 1) // size

    return ApiResponse(
        success=True,
        message="Employees retrieved successfully",
        data=PaginatedResponse(
            items=[EmployeeRead.model_validate(e) for e in items],
            total=total,
            page=page,
            size=size,
            pages=pages,
        ),
    )


@router.get("/departments", response_model=ApiResponse[List[str]])
def list_departments(db: Session = Depends(get_db)):
    """Retrieve distinct list of employee departments."""
    from backend.app.models.employee import Employee
    depts = [r[0] for r in db.query(Employee.department).distinct().filter(Employee.department != None).all()]
    return ApiResponse(
        success=True,
        message="Departments retrieved successfully",
        data=sorted(list(set(depts))) if depts else ["Engineering", "HR", "Sales", "Marketing", "Finance", "Product", "Operations"],
    )


@router.post("", response_model=ApiResponse[dict], status_code=status.HTTP_201_CREATED)
def create_employee(
    employee_in: EmployeeCreate,
    db: Session = Depends(get_db),
    admin_hr: User = Depends(require_hr_or_admin),
):
    """
    Create a new employee (ADMIN or HR_OFFICER only).
    Automatically generates standardized Login ID (OI...), creates linked User, and sets temp password.
    """
    emp, user_acc, temp_password = employee_service.create_employee(db, employee_in)

    return ApiResponse(
        success=True,
        message="Employee and user account created successfully",
        data={
            "employee": EmployeeRead.model_validate(emp),
            "user_id": user_acc.id,
            "login_id": user_acc.login_id,
            "temporary_password": temp_password,
            "role": user_acc.role,
        },
    )


@router.get("/{id}", response_model=ApiResponse[EmployeeDetailRead])
def get_employee(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get complete employee profile by ID."""
    emp = employee_service.get_employee_by_id(db, id)

    # Convert skills
    skills = [SkillRead.model_validate(es.skill) for es in emp.skills if es.skill]
    certs = [CertificationRead.model_validate(c) for c in emp.certifications]

    # Include private info only if ADMIN/HR or self
    pinfo = None
    if current_user.role in (UserRole.ADMIN, UserRole.HR_OFFICER) or current_user.employee_id == id:
        if emp.private_info:
            pinfo = EmployeePrivateInfoRead.model_validate(emp.private_info)

    detail = EmployeeDetailRead(
        **EmployeeRead.model_validate(emp).model_dump(),
        skills=skills,
        certifications=certs,
        private_info=pinfo,
        user_login_id=emp.user.login_id if emp.user else None,
    )

    return ApiResponse(
        success=True,
        message="Employee profile retrieved",
        data=detail,
    )


@router.put("/{id}", response_model=ApiResponse[EmployeeRead])
def update_employee(
    id: int,
    update_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    admin_hr: User = Depends(require_hr_or_admin),
):
    """Update employee details (ADMIN or HR_OFFICER only)."""
    emp = employee_service.update_employee(db, id, update_data)
    return ApiResponse(
        success=True,
        message="Employee updated successfully",
        data=EmployeeRead.model_validate(emp),
    )


@router.delete("/{id}", response_model=ApiResponse[None])
def delete_employee(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Delete employee and associated user account (ADMIN only)."""
    employee_service.delete_employee(db, id)
    return ApiResponse(
        success=True,
        message="Employee deleted successfully",
        data=None,
    )


# --- Private Info Sub-resources ---

@router.get("/{id}/private-info", response_model=ApiResponse[EmployeePrivateInfoRead])
def get_private_info(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get sensitive employee info (PAN, Bank, etc.). Protected: Only ADMIN, HR, or Self."""
    verify_employee_access(id, current_user)
    pinfo = employee_service.get_private_info(db, id)
    if not pinfo:
        raise NotFoundException("Private info for employee", id)
    return ApiResponse(
        success=True,
        message="Private info retrieved",
        data=EmployeePrivateInfoRead.model_validate(pinfo),
    )


@router.put("/{id}/private-info", response_model=ApiResponse[EmployeePrivateInfoRead])
def update_private_info(
    id: int,
    info_in: EmployeePrivateInfoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update sensitive employee info. Protected: Only ADMIN, HR, or Self."""
    verify_employee_access(id, current_user)
    pinfo = employee_service.update_private_info(db, id, info_in)
    return ApiResponse(
        success=True,
        message="Private info updated successfully",
        data=EmployeePrivateInfoRead.model_validate(pinfo),
    )


# --- Skills & Certifications ---

@router.get("/{id}/skills", response_model=ApiResponse[List[SkillRead]])
def list_employee_skills(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List skills of an employee."""
    emp = employee_service.get_employee_by_id(db, id)
    skills = [SkillRead.model_validate(es.skill) for es in emp.skills if es.skill]
    return ApiResponse(
        success=True,
        message="Skills retrieved",
        data=skills,
    )


@router.post("/{id}/skills", response_model=ApiResponse[None])
def add_employee_skill(
    id: int,
    skill_in: SkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add a skill to an employee. Protected: ADMIN, HR, or Self."""
    verify_employee_access(id, current_user)
    employee_service.add_skill(db, id, skill_in.name)
    return ApiResponse(
        success=True,
        message="Skill added successfully",
        data=None,
    )


@router.delete("/{id}/skills/{skill_id}", response_model=ApiResponse[None])
def delete_employee_skill(
    id: int,
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Remove a skill from an employee."""
    verify_employee_access(id, current_user)
    employee_service.remove_skill(db, id, skill_id)
    return ApiResponse(
        success=True,
        message="Skill removed successfully",
        data=None,
    )


@router.get("/{id}/certifications", response_model=ApiResponse[List[CertificationRead]])
def list_employee_certifications(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List certifications of an employee."""
    emp = employee_service.get_employee_by_id(db, id)
    certs = [CertificationRead.model_validate(c) for c in emp.certifications]
    return ApiResponse(
        success=True,
        message="Certifications retrieved",
        data=certs,
    )


@router.post("/{id}/certifications", response_model=ApiResponse[CertificationRead])
def add_certification(
    id: int,
    cert_in: CertificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add certification to employee."""
    verify_employee_access(id, current_user)
    cert = employee_service.add_certification(db, id, cert_in)
    return ApiResponse(
        success=True,
        message="Certification added successfully",
        data=CertificationRead.model_validate(cert),
    )


@router.delete("/{id}/certifications/{cert_id}", response_model=ApiResponse[None])
def delete_certification(
    id: int,
    cert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete certification."""
    verify_employee_access(id, current_user)
    employee_service.delete_certification(db, cert_id)
    return ApiResponse(
        success=True,
        message="Certification deleted successfully",
        data=None,
    )
