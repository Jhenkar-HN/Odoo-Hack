from typing import Callable, List, Union
from fastapi import Depends
from backend.app.core.exceptions import PermissionDeniedException
from backend.app.dependencies.auth import get_current_active_user
from backend.app.models.user import User, UserRole


def require_role(*allowed_roles: Union[UserRole, str]) -> Callable:
    """Dependency factory that checks if the authenticated user has one of the allowed roles."""
    roles = [r.value if isinstance(r, UserRole) else str(r) for r in allowed_roles]

    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        user_role_str = current_user.role.value if isinstance(current_user.role, UserRole) else str(current_user.role)
        if user_role_str not in roles:
            raise PermissionDeniedException(
                f"Access forbidden: Role '{user_role_str}' lacks required permission (allowed: {', '.join(roles)})"
            )
        return current_user

    return role_checker


# Shortcuts
require_admin = require_role(UserRole.ADMIN)
require_hr_or_admin = require_role(UserRole.ADMIN, UserRole.HR_OFFICER)
require_authenticated = get_current_active_user


def verify_employee_access(
    target_employee_id: int,
    current_user: User,
    allowed_elevated_roles: List[UserRole] = [UserRole.ADMIN, UserRole.HR_OFFICER]
) -> None:
    """
    Verify that current_user has access to target_employee_id.
    - If user is ADMIN or HR_OFFICER (or roles in allowed_elevated_roles), access is granted.
    - If user is EMPLOYEE, user.employee_id MUST match target_employee_id.
    """
    if current_user.role in allowed_elevated_roles:
        return

    if current_user.employee_id != target_employee_id:
        raise PermissionDeniedException(
            "Access denied: You are not authorized to view or modify another employee's records."
        )
