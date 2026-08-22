import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    HR_OFFICER = "HR_OFFICER"
    EMPLOYEE = "EMPLOYEE"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, unique=True, index=True)
    login_id = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.EMPLOYEE, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    must_change_password = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="user", foreign_keys=[employee_id])

    def __repr__(self):
        return f"<User id={self.id} login_id='{self.login_id}' role='{self.role}'>"
