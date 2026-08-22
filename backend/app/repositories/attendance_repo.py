from datetime import date
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from backend.app.models.attendance import Attendance
from backend.app.repositories.base import BaseRepository


class AttendanceRepository(BaseRepository[Attendance]):
    def __init__(self):
        super().__init__(Attendance)

    def get_by_employee_and_date(
        self, db: Session, employee_id: int, attendance_date: date
    ) -> Optional[Attendance]:
        return (
            db.query(Attendance)
            .filter(
                Attendance.employee_id == employee_id,
                Attendance.attendance_date == attendance_date,
            )
            .first()
        )

    def get_history(
        self,
        db: Session,
        employee_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Attendance], int]:
        q = db.query(Attendance)
        if employee_id:
            q = q.filter(Attendance.employee_id == employee_id)
        if start_date:
            q = q.filter(Attendance.attendance_date >= start_date)
        if end_date:
            q = q.filter(Attendance.attendance_date <= end_date)

        total = q.count()
        records = (
            q.order_by(Attendance.attendance_date.desc(), Attendance.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return records, total


attendance_repo = AttendanceRepository()
