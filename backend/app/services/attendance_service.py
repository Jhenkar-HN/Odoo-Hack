from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from backend.app.core.exceptions import (
    DuplicateResourceException,
    NotFoundException,
    BusinessRuleException,
)
from backend.app.models.attendance import Attendance, AttendanceStatus
from backend.app.repositories.attendance_repo import attendance_repo
from backend.app.repositories.employee_repo import employee_repo
from backend.app.schemas.attendance import AttendanceSummary


class AttendanceService:
    @staticmethod
    def check_in(
        db: Session, employee_id: int, target_date: Optional[date] = None
    ) -> Attendance:
        emp = employee_repo.get(db, employee_id)
        if not emp:
            raise NotFoundException("Employee", employee_id)

        att_date = target_date or date.today()
        existing = attendance_repo.get_by_employee_and_date(db, employee_id, att_date)
        if existing and existing.check_in:
            raise DuplicateResourceException(
                "Attendance", "date", f"{att_date} (Already checked in at {existing.check_in.strftime('%H:%M:%S')})"
            )

        now = datetime.now(timezone.utc)
        if existing:
            existing.check_in = now
            existing.status = AttendanceStatus.PRESENT
            db.commit()
            db.refresh(existing)
            return existing
        else:
            record = Attendance(
                employee_id=employee_id,
                attendance_date=att_date,
                check_in=now,
                status=AttendanceStatus.PRESENT,
                work_hours=Decimal("0.00"),
                extra_hours=Decimal("0.00"),
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record

    @staticmethod
    def check_out(
        db: Session, employee_id: int, target_date: Optional[date] = None
    ) -> Attendance:
        emp = employee_repo.get(db, employee_id)
        if not emp:
            raise NotFoundException("Employee", employee_id)

        att_date = target_date or date.today()
        record = attendance_repo.get_by_employee_and_date(db, employee_id, att_date)
        if not record or not record.check_in:
            raise BusinessRuleException("Cannot check out without checking in first.")

        now = datetime.now(timezone.utc)
        record.check_out = now

        # Calculate duration in hours
        # Normalize timezone-naive if needed
        check_in_time = record.check_in
        if check_in_time.tzinfo is None:
            check_in_time = check_in_time.replace(tzinfo=timezone.utc)

        duration = now - check_in_time
        hours = Decimal(str(round(duration.total_seconds() / 3600.0, 2)))
        record.work_hours = max(Decimal("0.00"), hours)

        # Standard work day: 8 hours
        standard_hours = Decimal("8.00")
        if record.work_hours > standard_hours:
            record.extra_hours = record.work_hours - standard_hours
        else:
            record.extra_hours = Decimal("0.00")

        if record.work_hours < Decimal("4.00"):
            record.status = AttendanceStatus.HALF_DAY
        else:
            record.status = AttendanceStatus.PRESENT

        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def get_summary(db: Session, employee_id: int) -> AttendanceSummary:
        emp = employee_repo.get(db, employee_id)
        if not emp:
            raise NotFoundException("Employee", employee_id)

        records, _ = attendance_repo.get_history(db, employee_id=employee_id, limit=365)
        present = sum(1 for r in records if r.status in (AttendanceStatus.PRESENT, AttendanceStatus.HALF_DAY))
        absent = sum(1 for r in records if r.status == AttendanceStatus.ABSENT)
        work_hours = sum((r.work_hours for r in records), Decimal("0.00"))
        ot_hours = sum((r.extra_hours for r in records), Decimal("0.00"))

        return AttendanceSummary(
            employee_id=employee_id,
            total_days_present=present,
            total_days_absent=absent,
            total_work_hours=work_hours,
            total_overtime_hours=ot_hours,
        )


attendance_service = AttendanceService()
