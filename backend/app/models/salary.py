from datetime import datetime, date, timezone
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, Numeric, Date, DateTime, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Salary(Base):
    __tablename__ = "salaries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    
    monthly_wage = Column(Numeric(12, 2), nullable=False, default=0.00)
    yearly_wage = Column(Numeric(12, 2), nullable=False, default=0.00)
    basic_salary = Column(Numeric(12, 2), nullable=False, default=0.00)
    hra = Column(Numeric(12, 2), nullable=False, default=0.00)
    standard_allowance = Column(Numeric(12, 2), nullable=False, default=0.00)
    performance_bonus = Column(Numeric(12, 2), nullable=False, default=0.00)
    leave_travel_allowance = Column(Numeric(12, 2), nullable=False, default=0.00)
    fixed_allowance = Column(Numeric(12, 2), nullable=False, default=0.00)
    professional_tax = Column(Numeric(12, 2), nullable=False, default=0.00)
    employee_pf = Column(Numeric(12, 2), nullable=False, default=0.00)
    employer_pf = Column(Numeric(12, 2), nullable=False, default=0.00)

    effective_from = Column(Date, default=date.today, nullable=False)
    effective_to = Column(Date, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        CheckConstraint("monthly_wage >= 0", name="chk_salary_monthly_wage_nonneg"),
        CheckConstraint("yearly_wage >= 0", name="chk_salary_yearly_wage_nonneg"),
        CheckConstraint("basic_salary >= 0", name="chk_salary_basic_salary_nonneg"),
        CheckConstraint("hra >= 0", name="chk_salary_hra_nonneg"),
        CheckConstraint("standard_allowance >= 0", name="chk_salary_standard_allowance_nonneg"),
        CheckConstraint("performance_bonus >= 0", name="chk_salary_perf_bonus_nonneg"),
        CheckConstraint("leave_travel_allowance >= 0", name="chk_salary_lta_nonneg"),
        CheckConstraint("fixed_allowance >= 0", name="chk_salary_fixed_allowance_nonneg"),
        CheckConstraint("professional_tax >= 0", name="chk_salary_ptax_nonneg"),
        CheckConstraint("employee_pf >= 0", name="chk_salary_epf_nonneg"),
        CheckConstraint("employer_pf >= 0", name="chk_salary_emppf_nonneg"),
    )

    employee = relationship("Employee", back_populates="salaries")

    @property
    def total_earnings(self) -> Decimal:
        def _to_dec(v) -> Decimal:
            if v is None:
                return Decimal("0.00")
            if isinstance(v, Decimal):
                return v
            return Decimal(str(v))

        return (
            _to_dec(self.basic_salary)
            + _to_dec(self.hra)
            + _to_dec(self.standard_allowance)
            + _to_dec(self.performance_bonus)
            + _to_dec(self.leave_travel_allowance)
            + _to_dec(self.fixed_allowance)
        )

    @property
    def total_deductions(self) -> Decimal:
        def _to_dec(v) -> Decimal:
            if v is None:
                return Decimal("0.00")
            if isinstance(v, Decimal):
                return v
            return Decimal(str(v))

        return _to_dec(self.professional_tax) + _to_dec(self.employee_pf)

    @property
    def net_salary(self) -> Decimal:
        return self.total_earnings - self.total_deductions

    def __repr__(self):
        return f"<Salary id={self.id} employee_id={self.employee_id} monthly={self.monthly_wage}>"
