from decimal import Decimal
from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.core.exceptions import NotFoundException, BusinessRuleException
from backend.app.models.salary import Salary
from backend.app.repositories.salary_repo import salary_repo
from backend.app.repositories.employee_repo import employee_repo
from backend.app.schemas.salary import SalaryCreate, SalaryUpdate, SalaryBreakdown


class SalaryService:
    @staticmethod
    def get_employee_salary(db: Session, employee_id: int) -> Optional[Salary]:
        emp = employee_repo.get(db, employee_id)
        if not emp:
            raise NotFoundException("Employee", employee_id)
        return salary_repo.get_current_by_employee(db, employee_id)

    @staticmethod
    def create_or_update_salary(
        db: Session, employee_id: int, salary_in: SalaryCreate
    ) -> Salary:
        emp = employee_repo.get(db, employee_id)
        if not emp:
            raise NotFoundException("Employee", employee_id)

        # Validate non-negative amounts
        salary_data = salary_in.model_dump()
        for k, v in salary_data.items():
            if isinstance(v, (int, float, Decimal)) and v < 0:
                raise BusinessRuleException(f"Salary field '{k}' cannot be negative.")

        # Auto-compute yearly wage if monthly wage provided and yearly wage is 0
        if salary_in.monthly_wage > 0 and salary_in.yearly_wage == 0:
            salary_data["yearly_wage"] = salary_in.monthly_wage * 12

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
    def get_salary_breakdown(db: Session, employee_id: int) -> SalaryBreakdown:
        emp = employee_repo.get(db, employee_id)
        if not emp:
            raise NotFoundException("Employee", employee_id)

        sal = salary_repo.get_current_by_employee(db, employee_id)
        if not sal:
            raise NotFoundException("Salary details for employee", employee_id)

        allowances = (
            (sal.standard_allowance or Decimal(0))
            + (sal.performance_bonus or Decimal(0))
            + (sal.leave_travel_allowance or Decimal(0))
            + (sal.fixed_allowance or Decimal(0))
        )

        return SalaryBreakdown(
            employee_id=emp.id,
            employee_name=emp.full_name,
            monthly_wage=sal.monthly_wage,
            basic_salary=sal.basic_salary,
            hra=sal.hra,
            allowances_total=allowances,
            gross_earnings=sal.total_earnings,
            total_deductions=sal.total_deductions,
            net_salary=sal.net_salary,
            pf_total=(sal.employee_pf or Decimal(0)) + (sal.employer_pf or Decimal(0)),
            effective_from=sal.effective_from,
        )

    @staticmethod
    def get_all_salaries(db: Session) -> List[Salary]:
        return salary_repo.get_all(db)


salary_service = SalaryService()
