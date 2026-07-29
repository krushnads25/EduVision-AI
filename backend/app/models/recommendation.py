from sqlalchemy import Column, Integer, ForeignKey, String, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="SET NULL"), nullable=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="SET NULL"), nullable=True, index=True)
    reason = Column(String(1024), nullable=True)
    recommendation = Column(String(2048), nullable=False)
    score = Column(Float, nullable=True)
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    college = relationship("College")
    course = relationship("Course")
