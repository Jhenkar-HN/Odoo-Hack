from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class SalaryBase(BaseModel):
    monthly_wage: Decimal = Field(default=Decimal("0.00"), ge=0)
    yearly_wage: Decimal = Field(default=Decimal("0.00"), ge=0)
    basic_salary: Decimal = Field(default=Decimal("0.00"), ge=0)
    hra: Decimal = Field(default=Decimal("0.00"), ge=0)
    standard_allowance: Decimal = Field(default=Decimal("0.00"), ge=0)
    performance_bonus: Decimal = Field(default=Decimal("0.00"), ge=0)
    leave_travel_allowance: Decimal = Field(default=Decimal("0.00"), ge=0)
    fixed_allowance: Decimal = Field(default=Decimal("0.00"), ge=0)
    professional_tax: Decimal = Field(default=Decimal("0.00"), ge=0)
    employee_pf: Decimal = Field(default=Decimal("0.00"), ge=0)
    employer_pf: Decimal = Field(default=Decimal("0.00"), ge=0)
    effective_from: date = Field(default_factory=date.today)
    effective_to: Optional[date] = None


class SalaryCreate(SalaryBase):
    pass


class SalaryUpdate(BaseModel):
    monthly_wage: Optional[Decimal] = Field(None, ge=0)
    yearly_wage: Optional[Decimal] = Field(None, ge=0)
    basic_salary: Optional[Decimal] = Field(None, ge=0)
    hra: Optional[Decimal] = Field(None, ge=0)
    standard_allowance: Optional[Decimal] = Field(None, ge=0)
    performance_bonus: Optional[Decimal] = Field(None, ge=0)
    leave_travel_allowance: Optional[Decimal] = Field(None, ge=0)
    fixed_allowance: Optional[Decimal] = Field(None, ge=0)
    professional_tax: Optional[Decimal] = Field(None, ge=0)
    employee_pf: Optional[Decimal] = Field(None, ge=0)
    employer_pf: Optional[Decimal] = Field(None, ge=0)
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None


class SalaryRead(SalaryBase):
    id: int
    employee_id: int
    created_at: datetime
    updated_at: datetime

    total_earnings: Optional[Decimal] = None
    total_deductions: Optional[Decimal] = None
    net_salary: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True)


class SalaryBreakdown(BaseModel):
    employee_id: int
    employee_name: str
    monthly_wage: Decimal
    basic_salary: Decimal
    hra: Decimal
    allowances_total: Decimal
    gross_earnings: Decimal
    total_deductions: Decimal
    net_salary: Decimal
    pf_total: Decimal
    effective_from: date


class PayslipRead(BaseModel):
    employee_id: int
    employee_name: str
    employee_code: str
    department: str
    job_position: str
    month: int
    year: int
    month_name: str
    total_working_days: int
    present_days: float
    payable_days: float
    unpaid_leaves: float
    monthly_wage: Decimal
    basic_salary: Decimal
    hra: Decimal
    standard_allowance: Decimal
    performance_bonus: Decimal
    leave_travel_allowance: Decimal
    fixed_allowance: Decimal
    gross_earnings: Decimal
    pf_deduction: Decimal
    professional_tax: Decimal
    total_deductions: Decimal
    net_payable: Decimal
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    pan: Optional[str] = None

