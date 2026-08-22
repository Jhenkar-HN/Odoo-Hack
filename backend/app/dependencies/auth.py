from typing import Optional
from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.security import decode_access_token
from backend.app.core.exceptions import UnauthorizedException
from backend.app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Validate Bearer token and return the current authenticated User."""
    actual_token = token
    if not actual_token and authorization and authorization.startswith("Bearer "):
        actual_token = authorization.split(" ")[1]

    if not actual_token:
        raise UnauthorizedException("Authentication token is required")

    payload = decode_access_token(actual_token)
    if not payload:
        raise UnauthorizedException("Invalid or expired authentication token")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Malformed authentication token payload")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise UnauthorizedException("User associated with this token does not exist")

    if not user.is_active:
        raise UnauthorizedException("User account is inactive. Please contact your administrator.")

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure active user."""
    return current_user
