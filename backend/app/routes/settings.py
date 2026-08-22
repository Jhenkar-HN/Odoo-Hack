from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.dependencies.auth import get_current_active_user
from backend.app.dependencies.rbac import require_admin
from backend.app.models.user import User
from backend.app.models.company import CompanySettings
from backend.app.schemas.company import (
    CompanySettingsRead,
    CompanySettingsUpdate,
)
from backend.app.schemas.common import ApiResponse

router = APIRouter(prefix="/settings", tags=["Company Settings"])


def _get_or_create_settings(db: Session) -> CompanySettings:
    st = db.query(CompanySettings).first()
    if not st:
        st = CompanySettings(
            company_name="HRMS Enterprise Corp",
            contact_email="admin@hrmscorp.com",
            contact_phone="+1-800-HRMS-SYS",
            address="100 Enterprise Way, Suite 400",
        )
        db.add(st)
        db.commit()
        db.refresh(st)
    return st


@router.get("", response_model=ApiResponse[CompanySettingsRead])
def get_company_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve company settings and configuration."""
    st = _get_or_create_settings(db)
    return ApiResponse(
        success=True,
        message="Company settings retrieved",
        data=CompanySettingsRead.model_validate(st),
    )


@router.put("", response_model=ApiResponse[CompanySettingsRead])
def update_company_settings(
    settings_in: CompanySettingsUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Update company settings (ADMIN only)."""
    st = _get_or_create_settings(db)
    update_data = settings_in.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(st, k, v)
    db.commit()
    db.refresh(st)

    return ApiResponse(
        success=True,
        message="Company settings updated successfully",
        data=CompanySettingsRead.model_validate(st),
    )
