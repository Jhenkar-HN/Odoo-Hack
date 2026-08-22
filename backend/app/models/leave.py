import enum
from datetime import datetime, date, timezone
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Date, DateTime, ForeignKey, Enum, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class LeaveRequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class LeaveType(Base):
    __tablename__ = "leave_types"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    default_allocation = Column(Integer, default=12, nullable=False)

    balances = relationship("LeaveBalance", back_populates="leave_type", cascade="all, delete-orphan")
    requests = relationship("TimeOffRequest", back_populates="leave_type")

    def __repr__(self):
        return f"<LeaveType id={self.id} name='{self.name}' default_allocation={self.default_allocation}>"


class LeaveBalance(Base):
    __tablename__ = "leave_balances"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id", ondelete="CASCADE"), nullable=False, index=True)
    year = Column(Integer, default=lambda: datetime.now(timezone.utc).year, nullable=False)
    allocated_days = Column(Numeric(5, 1), default=0.0, nullable=False)
    used_days = Column(Numeric(5, 1), default=0.0, nullable=False)
    remaining_days = Column(Numeric(5, 1), default=0.0, nullable=False)

    __table_args__ = (
        UniqueConstraint("employee_id", "leave_type_id", "year", name="uq_emp_leave_type_year"),
        CheckConstraint("allocated_days >= 0", name="chk_leave_allocated_nonneg"),
        CheckConstraint("used_days >= 0", name="chk_leave_used_nonneg"),
        CheckConstraint("remaining_days >= 0", name="chk_leave_remaining_nonneg"),
    )

    employee = relationship("Employee", back_populates="leave_balances")
    leave_type = relationship("LeaveType", back_populates="balances")

    def __repr__(self):
        return f"<LeaveBalance emp={self.employee_id} type={self.leave_type_id} remaining={self.remaining_days}>"


class TimeOffRequest(Base):
    __tablename__ = "time_off_requests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id", ondelete="RESTRICT"), nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    number_of_days = Column(Numeric(4, 1), nullable=False)
    reason = Column(Text, nullable=True)
    attachment_path = Column(String(500), nullable=True)
    status = Column(Enum(LeaveRequestStatus), default=LeaveRequestStatus.PENDING, nullable=False, index=True)
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="chk_time_off_dates_valid"),
        CheckConstraint("number_of_days > 0", name="chk_time_off_days_pos"),
    )

    employee = relationship("Employee", back_populates="time_off_requests", foreign_keys=[employee_id])
    leave_type = relationship("LeaveType", back_populates="requests")
    reviewer = relationship("User", foreign_keys=[reviewed_by])

    def __repr__(self):
        return f"<TimeOffRequest id={self.id} emp={self.employee_id} status={self.status}>"
