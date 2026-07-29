from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.college import College


class CollegeRepository(BaseRepository[College]):
    def __init__(self):
        super().__init__(College)

    def get_by_name(self, db: Session, name: str) -> Optional[College]:
        return db.query(College).filter(College.name == name).one_or_none()
