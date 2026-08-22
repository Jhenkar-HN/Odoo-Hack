from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.models.user import User, UserRole
from backend.app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def get_by_login_id(self, db: Session, login_id: str) -> Optional[User]:
        return db.query(User).filter(User.login_id == login_id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_login_or_email(self, db: Session, identifier: str) -> Optional[User]:
        return (
            db.query(User)
            .filter((User.login_id == identifier) | (User.email == identifier))
            .first()
        )

    def get_by_employee_id(self, db: Session, employee_id: int) -> Optional[User]:
        return db.query(User).filter(User.employee_id == employee_id).first()

    def get_by_role(self, db: Session, role: UserRole) -> List[User]:
        return db.query(User).filter(User.role == role).all()


user_repo = UserRepository()
