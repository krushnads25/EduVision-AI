from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.base import Base


class Cutoff(Base):
    __tablename__ = "cutoffs"

    id = Column(Integer, primary_key=True, index=True)

    college_id = Column(
        Integer,
        ForeignKey("colleges.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    course_id = Column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    year = Column(Integer, nullable=False, index=True)

    round = Column(Integer, nullable=False, index=True)

    choice_code = Column(String(20), nullable=False, index=True)

    hu_open = Column(Float)
    hu_sc = Column(Float)
    hu_st = Column(Float)
    hu_vjdt = Column(Float)
    hu_ntb = Column(Float)
    hu_ntc = Column(Float)
    hu_ntd = Column(Float)
    hu_obc = Column(Float)
    hu_sebc = Column(Float)

    ohu_open = Column(Float)
    ohu_sc = Column(Float)
    ohu_st = Column(Float)
    ohu_vjdt = Column(Float)
    ohu_ntb = Column(Float)
    ohu_ntc = Column(Float)
    ohu_ntd = Column(Float)
    ohu_obc = Column(Float)
    ohu_sebc = Column(Float)

    ews = Column(Float)

    tfws = Column(Float)

    orphan = Column(Float)

    pwd = Column(Float)

    institute_level = Column(Float)

    minority = Column(Float)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    college = relationship("College")
    course = relationship("Course")