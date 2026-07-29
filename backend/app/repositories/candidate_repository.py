from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.candidate import Candidate


class CandidateRepository(BaseRepository[Candidate]):
    def __init__(self):
        super().__init__(Candidate)

    def list_by_course(self, db: Session, course_id: int) -> List[Candidate]:
        return db.query(Candidate).filter(Candidate.course_id == course_id).all()

    def list_by_college(self, db: Session, college_id: int) -> List[Candidate]:
        return db.query(Candidate).filter(Candidate.college_id == college_id).all()
