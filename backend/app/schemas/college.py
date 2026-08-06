from typing import Optional

from pydantic import BaseModel


class CollegeBase(BaseModel):
    name: str
    district_id: Optional[int] = None
    address: Optional[str] = None


class CollegeCreate(CollegeBase):
    pass


class CollegeUpdate(BaseModel):
    name: Optional[str] = None
    district_id: Optional[int] = None
    address: Optional[str] = None


class CollegeRead(CollegeBase):
    id: int

    class Config:
        from_attributes = True
