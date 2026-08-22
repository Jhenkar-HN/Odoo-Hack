from decimal import Decimal
from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.core.exceptions import NotFoundException, BusinessRuleException
from backend.app.models.salary import Salary
from backend.app.repositories.salary_repo import salary_repo
from backend.app.repositories.employee_repo import employee_repo
from backend.app.schemas.salary import SalaryCreate, SalaryUpdate, SalaryBreakdown


def _to_dec(v) -> Decimal:
    if v is None:
        return Decimal("0.00")
    if isinstance(v, Decimal):
        return v
    return Decimal(str(v))


class SalaryService:
    @staticmethod
    def get_employee_salary(db: Session, employee_id: int) -> Optional[Salary]:
        """Retrieve current salary record for a specific employee."""
        emp = employee_repo.get(db, employee_id)
        if not emp:
            raise NotFoundException("Employee", employee_id)
        return salary_repo.get_current_by_employee(db, employee_id)

    @staticmethod
    def create_or_update_salary(
        db: Session, employee_id: int, salary_in: SalaryCreate
    ) -> Salary:
        """Create or replace employee salary structure with validations and auto-computations."""
        emp = employee_repo.get(db, employee_id)
        if not emp:
            raise NotFoundException("Employee", employee_id)

        salary_data = salary_in.model_dump()
        # Validate non-negative amounts
        for k, v in salary_data.items():
            if isinstance(v, (int, float, Decimal)) and v < 0:
                raise BusinessRuleException(f"Salary field '{k}' cannot be negative.")

        # Compute gross earnings & total deductions
        gross_earnings = (
            _to_dec(salary_data.get("basic_salary"))
            + _to_dec(salary_data.get("hra"))
            + _to_dec(salary_data.get("standard_allowance"))
            + _to_dec(salary_data.get("performance_bonus"))
            + _to_dec(salary_data.get("leave_travel_allowance"))
            + _to_dec(salary_data.get("fixed_allowance"))
        )
        total_deductions = (
            _to_dec(salary_data.get("professional_tax"))
            + _to_dec(salary_data.get("employee_pf"))
        )
        if total_deductions > gross_earnings:
            raise BusinessRuleException(
                f"Total deductions ({total_deductions}) cannot exceed gross earnings ({gross_earnings})."
            )

        # Auto-compute monthly/yearly wage if not fully specified
        monthly = _to_dec(salary_data.get("monthly_wage"))
        yearly = _to_dec(salary_data.get("yearly_wage"))
        if monthly > 0 and yearly == 0:
            salary_data["yearly_wage"] = monthly * 12
        elif monthly == 0 and gross_earnings > 0:
            salary_data["monthly_wage"] = gross_earnings
            if yearly == 0:
                salary_data["yearly_wage"] = gross_earnings * 12

        existing_salary = salary_repo.get_current_by_employee(db, employee_id)
        if existing_salary:
            for k, v in salary_data.items():
                setattr(existing_salary, k, v)
            db.commit()
            db.refresh(existing_salary)
            return existing_salary
        else:
            salary = Salary(employee_id=employee_id, **salary_data)
            db.add(salary)
            db.commit()
            db.refresh(salary)
            return salary

    @staticmethod
    def update_salary(
        db: Session, employee_id: int, salary_in: SalaryUpdate
    ) -> Salary:
        """Update existing employee salary fields with validation and recalculation."""
        emp = employee_repo.get(db, employee_id)
        if not emp:
            raise NotFoundException("Employee", employee_id)

        existing_salary = salary_repo.get_current_by_employee(db, employee_id)
        if not existing_salary:
            raise NotFoundException("Salary record for employee", employee_id)

        update_data = salary_in.model_dump(exclude_unset=True)
        # Validate non-negative amounts
        for k, v in update_data.items():
            if isinstance(v, (int, float, Decimal)) and v < 0:
                raise BusinessRuleException(f"Salary field '{k}' cannot be negative.")

        # Validate total deductions vs gross earnings after applying updates
        merged_values = {
            "basic_salary": _to_dec(update_data.get("basic_salary", existing_salary.basic_salary)),
            "hra": _to_dec(update_data.get("hra", existing_salary.hra)),
            "standard_allowance": _to_dec(update_data.get("standard_allowance", existing_salary.standard_allowance)),
            "performance_bonus": _to_dec(update_data.get("performance_bonus", existing_salary.performance_bonus)),
            "leave_travel_allowance": _to_dec(update_data.get("leave_travel_allowance", existing_salary.leave_travel_allowance)),
            "fixed_allowance": _to_dec(update_data.get("fixed_allowance", existing_salary.fixed_allowance)),
            "professional_tax": _to_dec(update_data.get("professional_tax", existing_salary.professional_tax)),
            "employee_pf": _to_dec(update_data.get("employee_pf", existing_salary.employee_pf)),
        }
        gross_earnings = (
            merged_values["basic_salary"]
            + merged_values["hra"]
            + merged_values["standard_allowance"]
            + merged_values["performance_bonus"]
            + merged_values["leave_travel_allowance"]
            + merged_values["fixed_allowance"]
        )
        total_deductions = merged_values["professional_tax"] + merged_values["employee_pf"]
        if total_deductions > gross_earnings:
            raise BusinessRuleException(
                f"Total deductions ({total_deductions}) cannot exceed gross earnings ({gross_earnings})."
            )

        # Auto-compute yearly wage if monthly wage is updated without yearly wage
        if "monthly_wage" in update_data:
            new_monthly = _to_dec(update_data["monthly_wage"])
            if "yearly_wage" not in update_data or _to_dec(update_data["yearly_wage"]) == 0:
                if new_monthly > 0:
                    update_data["yearly_wage"] = new_monthly * 12

        for k, v in update_data.items():
            setattr(existing_salary, k, v)
        db.commit()
        db.refresh(existing_salary)
        return existing_salary

    @staticmethod
    def delete_salary(db: Session, employee_id: int) -> bool:
        """Delete salary record for a specific employee."""
        emp = employee_repo.get(db, employee_id)
        if not emp:
            raise NotFoundException("Employee", employee_id)

        existing_salary = salary_repo.get_current_by_employee(db, employee_id)
        if not existing_salary:
            raise NotFoundException("Salary record for employee", employee_id)

        db.delete(existing_salary)
        db.commit()
        return True

    @staticmethod
    def get_salary_breakdown(db: Session, employee_id: int) -> SalaryBreakdown:
        """Compute detailed salary breakdown including earnings, deductions, PF, and net pay."""
        emp = employee_repo.get(db, employee_id)
        if not emp:
            raise NotFoundException("Employee", employee_id)

        sal = salary_repo.get_current_by_employee(db, employee_id)
        if not sal:
            raise NotFoundException("Salary details for employee", employee_id)

        allowances = (
            _to_dec(sal.standard_allowance)
            + _to_dec(sal.performance_bonus)
            + _to_dec(sal.leave_travel_allowance)
            + _to_dec(sal.fixed_allowance)
        )

        return SalaryBreakdown(
            employee_id=emp.id,
            employee_name=emp.full_name,
            monthly_wage=_to_dec(sal.monthly_wage),
            basic_salary=_to_dec(sal.basic_salary),
            hra=_to_dec(sal.hra),
            allowances_total=allowances,
            gross_earnings=sal.total_earnings,
            total_deductions=sal.total_deductions,
            net_salary=sal.net_salary,
            pf_total=_to_dec(sal.employee_pf) + _to_dec(sal.employer_pf),
            effective_from=sal.effective_from,
        )

    @staticmethod
    def get_all_salaries(db: Session) -> List[Salary]:
        """Retrieve all company salary records."""
        return salary_repo.get_all(db)


salary_service = SalaryService()
