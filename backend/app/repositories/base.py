from typing import TypeVar, Generic, Type, Optional, List, Any
from sqlalchemy.orm import Session
from backend.app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def count(self, db: Session) -> int:
        return db.query(self.model).count()

    def create(self, db: Session, obj_in: Any) -> ModelType:
        if isinstance(obj_in, dict):
            db_obj = self.model(**obj_in)
        else:
            db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: Any) -> bool:
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False
