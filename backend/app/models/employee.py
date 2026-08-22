from datetime import datetime, date, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, ForeignKey, Table, UniqueConstraint
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)

    employees = relationship("EmployeeSkill", back_populates="skill", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Skill id={self.id} name='{self.name}'>"


class EmployeeSkill(Base):
    __tablename__ = "employee_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("employee_id", "skill_id", name="uq_employee_skill"),
    )

    employee = relationship("Employee", back_populates="skills")
    skill = relationship("Skill", back_populates="employees")


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    issuing_organization = Column(String(255), nullable=False)
    issue_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=True)

    employee = relationship("Employee", back_populates="certifications")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    employee = relationship("Employee", back_populates="resumes")


class EmployeePrivateInfo(Base):
    __tablename__ = "employee_private_info"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    pan = Column(String(20), nullable=True)
    uan = Column(String(30), nullable=True)
    bank_account_number = Column(String(50), nullable=True)
    bank_name = Column(String(100), nullable=True)
    ifsc = Column(String(20), nullable=True)
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    employee = relationship("Employee", back_populates="private_info")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_code = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(30), nullable=True)
    department = Column(String(100), nullable=False, index=True)
    job_position = Column(String(100), nullable=False, index=True)
    manager_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, index=True)
    company = Column(String(150), default="HRMS Corp", nullable=False)
    location = Column(String(100), default="Headquarters", nullable=False)
    date_of_joining = Column(Date, default=date.today, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    nationality = Column(String(50), nullable=True)
    marital_status = Column(String(30), nullable=True)
    residing_address = Column(Text, nullable=True)
    personal_email = Column(String(255), nullable=True)
    profile_picture = Column(String(500), nullable=True)
    about = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="employee", uselist=False)
    private_info = relationship("EmployeePrivateInfo", back_populates="employee", uselist=False, cascade="all, delete-orphan")
    skills = relationship("EmployeeSkill", back_populates="employee", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="employee", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="employee", cascade="all, delete-orphan")
    salaries = relationship("Salary", back_populates="employee", cascade="all, delete-orphan")
    attendances = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")
    leave_balances = relationship("LeaveBalance", back_populates="employee", cascade="all, delete-orphan")
    time_off_requests = relationship("TimeOffRequest", back_populates="employee", foreign_keys="TimeOffRequest.employee_id", cascade="all, delete-orphan")
    subordinates = relationship("Employee", backref="manager", remote_side=[id])

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Employee id={self.id} code='{self.employee_code}' name='{self.full_name}'>"
