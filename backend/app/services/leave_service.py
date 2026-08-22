from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.core.exceptions import (
    NotFoundException,
    BusinessRuleException,
)
from backend.app.models.leave import (
    LeaveType,
    LeaveBalance,
    TimeOffRequest,
    LeaveRequestStatus,
)
from backend.app.repositories.leave_repo import leave_repo
from backend.app.repositories.employee_repo import employee_repo
from backend.app.schemas.leave import TimeOffRequestCreate, TimeOffReviewRequest


class LeaveService:
    @staticmethod
    def calculate_requested_days(start_date, end_date) -> Decimal:
        delta = (end_date - start_date).days + 1
        return Decimal(str(delta))

    @staticmethod
    def apply_for_time_off(
        db: Session, employee_id: int, request_in: TimeOffRequestCreate
    ) -> TimeOffRequest:
        emp = employee_repo.get(db, employee_id)
        if not emp:
            raise NotFoundException("Employee", employee_id)

        lt = leave_repo.get_leave_type_by_id(db, request_in.leave_type_id)
        if not lt:
            raise NotFoundException("Leave Type", request_in.leave_type_id)

        num_days = LeaveService.calculate_requested_days(request_in.start_date, request_in.end_date)
        req_year = request_in.start_date.year

        # Check balance
        bal = leave_repo.get_balance(db, employee_id, request_in.leave_type_id, req_year)
        if not bal:
            # Initialize balance if missing
            leave_repo.initialize_balances_for_employee(db, employee_id, req_year)
            bal = leave_repo.get_balance(db, employee_id, request_in.leave_type_id, req_year)

        if bal and bal.remaining_days < num_days:
            raise BusinessRuleException(
                f"Insufficient leave balance. Requested: {num_days} days, Remaining: {bal.remaining_days} days."
            )

        req = TimeOffRequest(
            employee_id=employee_id,
            leave_type_id=request_in.leave_type_id,
            start_date=request_in.start_date,
            end_date=request_in.end_date,
            number_of_days=num_days,
            reason=request_in.reason,
            attachment_path=request_in.attachment_path,
            status=LeaveRequestStatus.PENDING,
        )
        db.add(req)
        db.commit()
        db.refresh(req)
        return req

    @staticmethod
    def review_request(
        db: Session, request_id: int, reviewer_user_id: int, review_data: TimeOffReviewRequest
    ) -> TimeOffRequest:
        req = leave_repo.get(db, request_id)
        if not req:
            raise NotFoundException("Time Off Request", request_id)

        if req.status != LeaveRequestStatus.PENDING:
            raise BusinessRuleException(f"Cannot review request that is already in '{req.status.value}' status.")

        now = datetime.now(timezone.utc)
        req.reviewed_by = reviewer_user_id
        req.reviewed_at = now
        req.status = review_data.status
        req.rejection_reason = review_data.rejection_reason

        if review_data.status == LeaveRequestStatus.APPROVED:
            req_year = req.start_date.year
            bal = leave_repo.get_balance(db, req.employee_id, req.leave_type_id, req_year)
            if bal:
                bal.used_days += req.number_of_days
                bal.remaining_days = max(Decimal("0.0"), bal.allocated_days - bal.used_days)

        db.commit()
        db.refresh(req)
        return req

    @staticmethod
    def cancel_request(db: Session, request_id: int, employee_id: int) -> TimeOffRequest:
        req = leave_repo.get(db, request_id)
        if not req:
            raise NotFoundException("Time Off Request", request_id)

        if req.employee_id != employee_id:
            raise BusinessRuleException("You can only cancel your own time-off requests.")

        if req.status == LeaveRequestStatus.CANCELLED:
            return req

        if req.status == LeaveRequestStatus.APPROVED:
            # Revert deducted balance
            req_year = req.start_date.year
            bal = leave_repo.get_balance(db, req.employee_id, req.leave_type_id, req_year)
            if bal:
                bal.used_days = max(Decimal("0.0"), bal.used_days - req.number_of_days)
                bal.remaining_days = max(Decimal("0.0"), bal.allocated_days - bal.used_days)

        req.status = LeaveRequestStatus.CANCELLED
        db.commit()
        db.refresh(req)
        return req


leave_service = LeaveService()
