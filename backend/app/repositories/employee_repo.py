from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from backend.app.models.employee import (
    Employee,
    EmployeePrivateInfo,
    Skill,
    EmployeeSkill,
    Certification,
    Resume,
)
from backend.app.repositories.base import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    def __init__(self):
        super().__init__(Employee)

    def get_by_code(self, db: Session, employee_code: str) -> Optional[Employee]:
        return db.query(Employee).filter(Employee.employee_code == employee_code).first()

    def get_by_email(self, db: Session, email: str) -> Optional[Employee]:
        return db.query(Employee).filter(Employee.email == email).first()

    def search_employees(
        self,
        db: Session,
        query_str: Optional[str] = None,
        department: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Employee], int]:
        q = db.query(Employee)
        if department:
            q = q.filter(Employee.department.ilike(f"%{department}%"))
        if query_str:
            term = f"%{query_str}%"
            q = q.filter(
                (Employee.first_name.ilike(term))
                | (Employee.last_name.ilike(term))
                | (Employee.email.ilike(term))
                | (Employee.employee_code.ilike(term))
                | (Employee.job_position.ilike(term))
            )
        total = q.count()
        items = q.order_by(Employee.id.desc()).offset(skip).limit(limit).all()
        return items, total

    # Private info
    def get_private_info(self, db: Session, employee_id: int) -> Optional[EmployeePrivateInfo]:
        return db.query(EmployeePrivateInfo).filter(EmployeePrivateInfo.employee_id == employee_id).first()

    def set_private_info(self, db: Session, employee_id: int, info_data: dict) -> EmployeePrivateInfo:
        info = self.get_private_info(db, employee_id)
        if not info:
            info = EmployeePrivateInfo(employee_id=employee_id, **info_data)
            db.add(info)
        else:
            for k, v in info_data.items():
                if v is not None:
                    setattr(info, k, v)
        db.commit()
        db.refresh(info)
        return info

    # Skills
    def get_or_create_skill(self, db: Session, name: str) -> Skill:
        clean_name = name.strip()
        skill = db.query(Skill).filter(Skill.name.ilike(clean_name)).first()
        if not skill:
            skill = Skill(name=clean_name)
            db.add(skill)
            db.commit()
            db.refresh(skill)
        return skill

    def add_employee_skill(self, db: Session, employee_id: int, skill_id: int) -> EmployeeSkill:
        emp_skill = (
            db.query(EmployeeSkill)
            .filter(EmployeeSkill.employee_id == employee_id, EmployeeSkill.skill_id == skill_id)
            .first()
        )
        if not emp_skill:
            emp_skill = EmployeeSkill(employee_id=employee_id, skill_id=skill_id)
            db.add(emp_skill)
            db.commit()
            db.refresh(emp_skill)
        return emp_skill

    def remove_employee_skill(self, db: Session, employee_id: int, skill_id: int) -> bool:
        emp_skill = (
            db.query(EmployeeSkill)
            .filter(EmployeeSkill.employee_id == employee_id, EmployeeSkill.skill_id == skill_id)
            .first()
        )
        if emp_skill:
            db.delete(emp_skill)
            db.commit()
            return True
        return False

    # Certifications
    def add_certification(self, db: Session, employee_id: int, cert_data: dict) -> Certification:
        cert = Certification(employee_id=employee_id, **cert_data)
        db.add(cert)
        db.commit()
        db.refresh(cert)
        return cert

    def delete_certification(self, db: Session, cert_id: int) -> bool:
        cert = db.query(Certification).filter(Certification.id == cert_id).first()
        if cert:
            db.delete(cert)
            db.commit()
            return True
        return False


employee_repo = EmployeeRepository()
