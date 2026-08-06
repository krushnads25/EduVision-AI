from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Generic repository providing basic CRUD operations."""

    def __init__(self, model: Type[T]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[T]:
        return db.get(self.model, id)

    def list(self, db: Session, offset: int = 0, limit: int = 100) -> List[T]:
        stmt = select(self.model).offset(offset).limit(limit)
        return db.execute(stmt).scalars().all()

    def create(self, db: Session, obj_in: Dict[str, Any]) -> T:
        obj = self.model(**obj_in)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(self, db: Session, db_obj: T, obj_in: Dict[str, Any]) -> T:
        for k, v in obj_in.items():
            setattr(db_obj, k, v)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> bool:
        obj = self.get(db, id)
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False
