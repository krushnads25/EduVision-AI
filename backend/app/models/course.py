from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(64), nullable=False)
    name = Column(String(255), nullable=False)
    degree_level = Column(String(64), nullable=True)
    intake = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    college = relationship("College", backref="courses")
