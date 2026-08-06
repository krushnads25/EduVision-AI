from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.base import Base


class SeatMatrix(Base):
    __tablename__ = "seat_matrices"

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

    round = Column(Integer, nullable=True, index=True)

    choice_code = Column(String(20), nullable=False, index=True)

    tfws_choice_code = Column(String(20), nullable=True)

    intake = Column(Integer, default=0)

    hu_open = Column(Integer, default=0)
    hu_sc = Column(Integer, default=0)
    hu_st = Column(Integer, default=0)
    hu_vjdt = Column(Integer, default=0)
    hu_ntb = Column(Integer, default=0)
    hu_ntc = Column(Integer, default=0)
    hu_ntd = Column(Integer, default=0)
    hu_obc = Column(Integer, default=0)
    hu_sebc = Column(Integer, default=0)

    ohu_open = Column(Integer, default=0)
    ohu_sc = Column(Integer, default=0)
    ohu_st = Column(Integer, default=0)
    ohu_vjdt = Column(Integer, default=0)
    ohu_ntb = Column(Integer, default=0)
    ohu_ntc = Column(Integer, default=0)
    ohu_ntd = Column(Integer, default=0)
    ohu_obc = Column(Integer, default=0)
    ohu_sebc = Column(Integer, default=0)

    pwd_total = Column(Integer, default=0)

    orphan = Column(Integer, default=0)

    institute_level = Column(Integer, default=0)

    minority = Column(Integer, default=0)

    tfws_seats = Column(Integer, default=0)

    total_seats = Column(Integer, default=0)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    college = relationship("College")
    course = relationship("Course")