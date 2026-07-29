from sqlalchemy import Column, Integer, ForeignKey, Float, String
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base


class Cutoff(Base):
    __tablename__ = "cutoffs"

    id = Column(Integer, primary_key=True, index=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    category = Column(String(64), nullable=True, index=True)
    round = Column(Integer, nullable=True)
    cutoff_value = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    college = relationship("College")
    course = relationship("Course")
