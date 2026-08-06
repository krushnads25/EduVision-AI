from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base


class Vacancy(Base):
    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True)

    college_id = Column(Integer, ForeignKey("colleges.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))

    choice_code = Column(String(20), index=True)
    tfws_choice_code = Column(String(20), nullable=True)

    year = Column(Integer, index=True)
    round = Column(Integer)

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

    total_vacancies = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())