from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from backend.app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self):
        return f"<Company id={self.id} code='{self.code}' name='{self.name}'>"


class CompanySequence(Base):
    """Tracks sequential numbers per company and year for transactional atomic increments."""
    __tablename__ = "company_sequences"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_code = Column(String(20), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    last_serial = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("company_code", "year", name="uq_company_year_sequence"),
    )

    def __repr__(self):
        return f"<CompanySequence code='{self.company_code}' year={self.year} last_serial={self.last_serial}>"


class CompanySettings(Base):
    __tablename__ = "company_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_name = Column(String(200), default="HRMS Corp", nullable=False)
    company_logo = Column(String(500), nullable=True)
    contact_email = Column(String(255), default="contact@hrmscorp.com", nullable=False)
    contact_phone = Column(String(50), default="+1-555-0199", nullable=True)
    address = Column(Text, default="100 Innovation Way, Tech Park", nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self):
        return f"<CompanySettings id={self.id} company='{self.company_name}'>"
