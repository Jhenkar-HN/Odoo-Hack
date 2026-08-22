from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app import crud

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    id: int
    username: str
    role: str
    employee_id: Optional[int] = None
    display_name: str
    avatar_url: Optional[str] = None
    emp_login_id: Optional[str] = None
    department: Optional[str] = None
    job_position: Optional[str] = None
    token: str


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    """Authenticate user (HR or Employee) with email/Login ID and password."""
    user = crud.authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Please verify your Login ID / Work Email and password."
        )

    token = f"hrms-token-{user['id']}-{user['role']}"
    
    return {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "employee_id": user.get("employee_id"),
        "display_name": user["display_name"],
        "avatar_url": user.get("avatar_url"),
        "emp_login_id": user.get("emp_login_id"),
        "department": user.get("department"),
        "job_position": user.get("job_position"),
        "token": token
    }


@router.get("/me")
def get_current_user_profile(authorization: Optional[str] = Header(None)):
    """Retrieve current session user information."""
    if not authorization or not authorization.startswith("hrms-token-"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")
    
    try:
        parts = authorization.split("-")
        user_id = int(parts[2])
        user = crud.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
        return user
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")


@router.post("/logout")
def logout():
    """Logout current user session."""
    return {"message": "Logged out successfully."}
