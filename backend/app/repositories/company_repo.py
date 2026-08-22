import re
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.app.models.company import Company, CompanySequence
from backend.app.models.user import User
from backend.app.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    def __init__(self):
        super().__init__(Company)

    def get_by_code(self, db: Session, code: str) -> Optional[Company]:
        return db.query(Company).filter(Company.code.ilike(code.strip())).first()

    def get_by_name(self, db: Session, name: str) -> Optional[Company]:
        return db.query(Company).filter(Company.name.ilike(name.strip())).first()

    def get_by_name_or_code(self, db: Session, identifier: str) -> Optional[Company]:
        if not identifier:
            return None
        cleaned = identifier.strip()
        return (
            db.query(Company)
            .filter(or_(Company.code.ilike(cleaned), Company.name.ilike(cleaned)))
            .first()
        )

    def get_or_create_default(
        self, db: Session, name: str = "HRMS Corp", code: str = "CE"
    ) -> Company:
        comp = self.get_by_name_or_code(db, code) or self.get_by_name_or_code(db, name)
        if not comp:
            comp = Company(name=name, code=code.upper())
            db.add(comp)
            db.flush()
        return comp

    def get_next_serial_transactional(
        self, db: Session, company_code: str, year: int
    ) -> int:
        """
        Atomically look up and increment the next serial number for a company and year.
        Uses database row-level locking (with_for_update) where supported to prevent race conditions.
        Cross-checks existing users to guarantee unique assignment.
        """
        code_upper = company_code.strip().upper()

        # 1. Attempt row-locked sequence retrieval
        query = db.query(CompanySequence).filter(
            CompanySequence.company_code == code_upper,
            CompanySequence.year == year,
        )

        try:
            seq = query.with_for_update().first()
        except Exception:
            # Fallback for storage engines / SQLite configurations without row lock support
            seq = query.first()

        # 2. Check existing user login IDs in the database for that company and year
        # Pattern: [CompanyCode]...[Year][4-digit serial]
        matching_users = (
            db.query(User.login_id)
            .filter(User.login_id.like(f"{code_upper}%{year}%"))
            .all()
        )

        max_existing_serial = 0
        for (lid,) in matching_users:
            # Extract trailing 4 digits if present
            match = re.search(r"(\d{4})$", lid or "")
            if match:
                max_existing_serial = max(max_existing_serial, int(match.group(1)))

        if not seq:
            # First allocation for this company & year
            next_serial = max(max_existing_serial, 0) + 1
            seq = CompanySequence(
                company_code=code_upper,
                year=year,
                last_serial=next_serial,
            )
            db.add(seq)
        else:
            next_serial = max(seq.last_serial, max_existing_serial) + 1
            seq.last_serial = next_serial

        db.flush()
        return next_serial


company_repo = CompanyRepository()
