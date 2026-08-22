from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.models.salary import Salary
from backend.app.repositories.base import BaseRepository


class SalaryRepository(BaseRepository[Salary]):
    def __init__(self):
        super().__init__(Salary)

    def get_current_by_employee(self, db: Session, employee_id: int) -> Optional[Salary]:
        return (
            db.query(Salary)
            .filter(Salary.employee_id == employee_id)
            .order_by(Salary.effective_from.desc(), Salary.id.desc())
            .first()
        )

    def get_all_by_employee(self, db: Session, employee_id: int) -> List[Salary]:
        return (
            db.query(Salary)
            .filter(Salary.employee_id == employee_id)
            .order_by(Salary.effective_from.desc())
            .all()
        )


salary_repo = SalaryRepository()
