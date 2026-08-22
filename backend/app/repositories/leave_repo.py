from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from backend.app.models.leave import LeaveType, LeaveBalance, TimeOffRequest, LeaveRequestStatus
from backend.app.repositories.base import BaseRepository


class LeaveRepository(BaseRepository[TimeOffRequest]):
    def __init__(self):
        super().__init__(TimeOffRequest)

    # Leave Types
    def get_all_leave_types(self, db: Session) -> List[LeaveType]:
        return db.query(LeaveType).all()

    def get_leave_type_by_id(self, db: Session, leave_type_id: int) -> Optional[LeaveType]:
        return db.query(LeaveType).filter(LeaveType.id == leave_type_id).first()

    def get_leave_type_by_name(self, db: Session, name: str) -> Optional[LeaveType]:
        return db.query(LeaveType).filter(LeaveType.name.ilike(name.strip())).first()

    def create_leave_type(self, db: Session, name: str, default_allocation: int) -> LeaveType:
        lt = LeaveType(name=name.strip(), default_allocation=default_allocation)
        db.add(lt)
        db.commit()
        db.refresh(lt)
        return lt

    # Leave Balances
    def get_balance(
        self, db: Session, employee_id: int, leave_type_id: int, year: int
    ) -> Optional[LeaveBalance]:
        return (
            db.query(LeaveBalance)
            .filter(
                LeaveBalance.employee_id == employee_id,
                LeaveBalance.leave_type_id == leave_type_id,
                LeaveBalance.year == year,
            )
            .first()
        )

    def get_all_balances_by_employee(
        self, db: Session, employee_id: int, year: int
    ) -> List[LeaveBalance]:
        return (
            db.query(LeaveBalance)
            .filter(LeaveBalance.employee_id == employee_id, LeaveBalance.year == year)
            .all()
        )

    def initialize_balances_for_employee(
        self, db: Session, employee_id: int, year: int
    ) -> List[LeaveBalance]:
        leave_types = self.get_all_leave_types(db)
        balances = []
        for lt in leave_types:
            existing = self.get_balance(db, employee_id, lt.id, year)
            if not existing:
                bal = LeaveBalance(
                    employee_id=employee_id,
                    leave_type_id=lt.id,
                    year=year,
                    allocated_days=lt.default_allocation,
                    used_days=0.0,
                    remaining_days=lt.default_allocation,
                )
                db.add(bal)
                balances.append(bal)
            else:
                balances.append(existing)
        db.commit()
        for b in balances:
            db.refresh(b)
        return balances

    # Time-Off Requests
    def get_requests(
        self,
        db: Session,
        employee_id: Optional[int] = None,
        status: Optional[LeaveRequestStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[TimeOffRequest], int]:
        q = db.query(TimeOffRequest)
        if employee_id:
            q = q.filter(TimeOffRequest.employee_id == employee_id)
        if status:
            q = q.filter(TimeOffRequest.status == status)

        total = q.count()
        records = (
            q.order_by(TimeOffRequest.created_at.desc(), TimeOffRequest.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return records, total


leave_repo = LeaveRepository()
