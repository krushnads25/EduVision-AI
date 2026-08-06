from typing import Optional

from pydantic import BaseModel


class CandidateBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    course_id: Optional[int] = None
    year: Optional[int] = None
    category: Optional[str] = None
    rank: Optional[int] = None


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    course_id: Optional[int] = None
    year: Optional[int] = None
    category: Optional[str] = None
    rank: Optional[int] = None


class CandidateRead(CandidateBase):
    id: int

    class Config:
        from_attributes = True
