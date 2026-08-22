from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.employee import Employee
from backend.app.models.attendance import Attendance, AttendanceStatus
from backend.app.models.leave import TimeOffRequest, LeaveRequestStatus
from backend.app.schemas.common import ApiResponse

router = APIRouter(prefix="/stats", tags=["Dashboard Analytics"])


@router.get("/dashboard", response_model=ApiResponse[dict])
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Retrieve summarized analytics KPIs for dashboard cards, attendance charts, and departments."""
    total_employees = db.query(Employee).count()
    today = date.today()

    present_today = db.query(Attendance).filter(
        Attendance.attendance_date == today,
        Attendance.status == AttendanceStatus.PRESENT
    ).count()

    on_leave_today = db.query(TimeOffRequest).filter(
        TimeOffRequest.status == LeaveRequestStatus.APPROVED,
        TimeOffRequest.start_date <= today,
        TimeOffRequest.end_date >= today
    ).count()

    absent_today = max(0, total_employees - present_today - on_leave_today)

    # Department breakdown
    depts = db.query(Employee.department).all()
    dept_counts = {}
    for (d,) in depts:
        if d:
            dept_counts[d] = dept_counts.get(d, 0) + 1

    return ApiResponse(
        success=True,
        message="Dashboard stats retrieved successfully",
        data={
            "total_employees": total_employees,
            "present_today": present_today,
            "on_leave_today": on_leave_today,
            "absent_today": absent_today,
            "department_breakdown": dept_counts,
        }
    )
