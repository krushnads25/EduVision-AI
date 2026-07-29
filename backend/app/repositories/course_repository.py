from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.course import Course


class CourseRepository(BaseRepository[Course]):
    def __init__(self):
        super().__init__(Course)

    def list_by_college(self, db: Session, college_id: int) -> List[Course]:
        return db.query(Course).filter(Course.college_id == college_id).all()
