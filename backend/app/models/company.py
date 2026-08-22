from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from backend.app.core.database import Base


class CompanySettings(Base):
    __tablename__ = "company_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_name = Column(String(200), default="HRMS Corp", nullable=False)
    company_logo = Column(String(500), nullable=True)
    contact_email = Column(String(255), default="contact@hrmscorp.com", nullable=False)
    contact_phone = Column(String(50), default="+1-555-0199", nullable=True)
    address = Column(Text, default="100 Innovation Way, Tech Park", nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<CompanySettings id={self.id} company='{self.company_name}'>"
