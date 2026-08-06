from typing import Optional

from pydantic import BaseModel


class CutoffBase(BaseModel):
    college_id: int
    course_id: int
    year: int
    category: Optional[str] = None
    round: Optional[int] = None
    cutoff_value: float


class CutoffCreate(CutoffBase):
    pass


class CutoffUpdate(BaseModel):
    college_id: Optional[int] = None
    course_id: Optional[int] = None
    year: Optional[int] = None
    category: Optional[str] = None
    round: Optional[int] = None
    cutoff_value: Optional[float] = None


class CutoffRead(CutoffBase):
    id: int

    class Config:
        from_attributes = True
