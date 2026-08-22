from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app import crud

router = APIRouter(prefix="/api/timeoff", tags=["Time Off & Leaves"])


class LeaveApplyRequest(BaseModel):
    employee_id: int
    leave_type: str = Field(..., description="Paid Time Off, Sick Leave, Unpaid Leave")
    start_date: str
    end_date: str
    days_count: float = Field(default=1.0, gt=0.0)
    reason: Optional[str] = ""


class LeaveStatusUpdateRequest(BaseModel):
    status: str = Field(..., description="approved, rejected")
    reviewer: Optional[str] = "HR Admin"


@router.post("/apply", status_code=status.HTTP_201_CREATED)
def apply_for_leave(req: LeaveApplyRequest):
    """Employee submits a time-off or sick leave application."""
    emp = crud.get_employee_by_id(req.employee_id)
    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee #{req.employee_id} not found."
        )

    leave = crud.apply_leave_request(
        emp_id=req.employee_id,
        leave_type=req.leave_type,
        start_date=req.start_date,
        end_date=req.end_date,
        days_count=req.days_count,
        reason=req.reason or ""
    )
    return leave


@router.get("/my-leaves")
def get_my_leaves(employee_id: int = Query(..., description="ID of employee")):
    """Get leave application history for an employee."""
    return crud.get_employee_leaves(employee_id)


@router.get("/all")
def get_all_leaves_for_hr():
    """HR view of all pending and reviewed leave requests."""
    return crud.get_all_leaves()


@router.patch("/{leave_id}/status")
def review_leave_request(leave_id: int, req: LeaveStatusUpdateRequest):
    """HR approves or rejects employee leave request."""
    updated = crud.update_leave_status(leave_id, req.status, req.reviewer or "HR Admin")
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leave request #{leave_id} not found."
        )
    return updated
