from typing import Optional

from pydantic import BaseModel


class VacancyBase(BaseModel):
    college_id: int
    course_id: int
    year: int
    round: Optional[int] = None
    vacancies: int


class VacancyCreate(VacancyBase):
    pass


class VacancyUpdate(BaseModel):
    college_id: Optional[int] = None
    course_id: Optional[int] = None
    year: Optional[int] = None
    round: Optional[int] = None
    vacancies: Optional[int] = None


class VacancyRead(VacancyBase):
    id: int

    class Config:
        from_attributes = True
