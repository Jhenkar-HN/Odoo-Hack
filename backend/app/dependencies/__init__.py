from backend.app.dependencies.auth import get_current_user, get_current_active_user
from backend.app.dependencies.rbac import (
    require_role,
    require_admin,
    require_hr_or_admin,
    require_authenticated,
    verify_employee_access,
)

__all__ = [
    "get_current_user",
    "get_current_active_user",
    "require_role",
    "require_admin",
    "require_hr_or_admin",
    "require_authenticated",
    "verify_employee_access",
]
