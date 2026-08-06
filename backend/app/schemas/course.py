from typing import Optional

from pydantic import BaseModel


class CourseBase(BaseModel):
    college_id: int
    code: str
    name: str
    degree_level: Optional[str] = None
    intake: Optional[int] = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    college_id: Optional[int] = None
    code: Optional[str] = None
    name: Optional[str] = None
    degree_level: Optional[str] = None
    intake: Optional[int] = None


class CourseRead(CourseBase):
    id: int

    class Config:
        from_attributes = True
