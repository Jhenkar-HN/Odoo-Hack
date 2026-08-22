import enum
from datetime import datetime, date, timezone
from sqlalchemy import (
    Column, Integer, Numeric, Date, DateTime, ForeignKey, Enum, UniqueConstraint
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    HALF_DAY = "HALF_DAY"
    ON_LEAVE = "ON_LEAVE"


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    attendance_date = Column(Date, default=date.today, nullable=False, index=True)
    check_in = Column(DateTime, nullable=True)
    check_out = Column(DateTime, nullable=True)
    work_hours = Column(Numeric(5, 2), default=0.00, nullable=False)
    extra_hours = Column(Numeric(5, 2), default=0.00, nullable=False)
    status = Column(Enum(AttendanceStatus), default=AttendanceStatus.PRESENT, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("employee_id", "attendance_date", name="uq_employee_attendance_date"),
    )

    employee = relationship("Employee", back_populates="attendances")

    def __repr__(self):
        return f"<Attendance id={self.id} employee_id={self.employee_id} date={self.attendance_date} status={self.status}>"
