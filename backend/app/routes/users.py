from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.exceptions import NotFoundException, BusinessRuleException
from backend.app.dependencies.rbac import require_admin
from backend.app.models.user import User
from backend.app.repositories.user_repo import user_repo
from backend.app.schemas.user import UserRead, UserStatusUpdate, UserUpdate
from backend.app.schemas.common import ApiResponse, PaginatedResponse

router = APIRouter(prefix="/users", tags=["User Management"])


@router.get("", response_model=ApiResponse[PaginatedResponse[UserRead]])
def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """List all registered system users (ADMIN only)."""
    skip = (page - 1) * size
    users = user_repo.get_all(db, skip=skip, limit=size)
    total = user_repo.count(db)
    pages = (total + size - 1) // size

    return ApiResponse(
        success=True,
        message="Users retrieved successfully",
        data=PaginatedResponse(
            items=[UserRead.model_validate(u) for u in users],
            total=total,
            page=page,
            size=size,
            pages=pages,
        ),
    )


@router.get("/{id}", response_model=ApiResponse[UserRead])
def get_user(
    id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """Get single user by ID (ADMIN only)."""
    user = user_repo.get(db, id)
    if not user:
        raise NotFoundException("User", id)
    return ApiResponse(
        success=True,
        message="User details retrieved",
        data=UserRead.model_validate(user),
    )


@router.put("/{id}/status", response_model=ApiResponse[UserRead])
def update_user_status(
    id: int,
    status_data: UserStatusUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """Activate or deactivate user account (ADMIN only)."""
    user = user_repo.get(db, id)
    if not user:
        raise NotFoundException("User", id)

    if user.id == admin_user.id and not status_data.is_active:
        raise BusinessRuleException("You cannot deactivate your own admin account.")

    user.is_active = status_data.is_active
    db.commit()
    db.refresh(user)

    return ApiResponse(
        success=True,
        message=f"User account {'activated' if user.is_active else 'deactivated'} successfully",
        data=UserRead.model_validate(user),
    )
