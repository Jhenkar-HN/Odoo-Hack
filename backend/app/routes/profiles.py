from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.exceptions import BusinessRuleException, NotFoundException
from backend.app.dependencies.auth import get_current_active_user
from backend.app.models.user import User
from backend.app.repositories.employee_repo import employee_repo
from backend.app.services.employee_service import employee_service
from backend.app.schemas.employee import (
    EmployeeDetailRead,
    EmployeeRead,
    EmployeePrivateInfoRead,
    EmployeeUpdate,
    SkillRead,
    CertificationRead,
)
from backend.app.schemas.common import ApiResponse

router = APIRouter(prefix="/profiles", tags=["Employee Profile Self-Service"])


@router.get("/me", response_model=ApiResponse[EmployeeDetailRead])
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve full profile of the logged-in employee."""
    if not current_user.employee_id:
        raise BusinessRuleException("Current user is not linked to an employee profile.")

    emp = employee_service.get_employee_by_id(db, current_user.employee_id)
    skills = [SkillRead.model_validate(es.skill) for es in emp.skills if es.skill]
    certs = [CertificationRead.model_validate(c) for c in emp.certifications]
    pinfo = (
        EmployeePrivateInfoRead.model_validate(emp.private_info)
        if emp.private_info
        else None
    )

    detail = EmployeeDetailRead(
        **EmployeeRead.model_validate(emp).model_dump(),
        skills=skills,
        certifications=certs,
        private_info=pinfo,
        user_login_id=current_user.login_id,
    )

    return ApiResponse(
        success=True,
        message="Profile retrieved successfully",
        data=detail,
    )


@router.put("/me", response_model=ApiResponse[EmployeeRead])
def update_my_profile(
    update_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update editable fields of current logged-in employee."""
    if not current_user.employee_id:
        raise BusinessRuleException("Current user is not linked to an employee profile.")

    # Restrict employees from modifying job_position, department, date_of_joining, etc.
    filtered_update = EmployeeUpdate(
        phone=update_data.phone,
        residing_address=update_data.residing_address,
        personal_email=update_data.personal_email,
        profile_picture=update_data.profile_picture,
        about=update_data.about,
        marital_status=update_data.marital_status,
    )

    emp = employee_service.update_employee(db, current_user.employee_id, filtered_update)
    return ApiResponse(
        success=True,
        message="Profile updated successfully",
        data=EmployeeRead.model_validate(emp),
    )
