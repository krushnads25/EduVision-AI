from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base


class Vacancy(Base):
    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True, index=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    round = Column(Integer, nullable=True)
    vacancies = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    college = relationship("College")
    course = relationship("Course")
