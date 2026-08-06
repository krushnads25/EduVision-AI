from typing import Optional, List
from app.models.cutoff import Cutoff
from app.repositories.base import BaseRepository
from sqlalchemy.orm import Session


class CutoffRepository(BaseRepository[Cutoff]):
    def __init__(self):
        super().__init__(Cutoff)

    def list_by_college(self, db: Session, college_id: int) -> List[Cutoff]:
        return db.query(Cutoff).filter(Cutoff.college_id == college_id).all()

    def list_by_course(self, db: Session, course_id: int) -> List[Cutoff]:
        return db.query(Cutoff).filter(Cutoff.course_id == course_id).all()

    def get_latest_for_course(self, db: Session, course_id: int, category: Optional[str] = None):
        q = db.query(Cutoff).filter(Cutoff.course_id == course_id)
        if category:
            q = q.filter(Cutoff.category == category)
        return q.order_by(Cutoff.year.desc()).first()
