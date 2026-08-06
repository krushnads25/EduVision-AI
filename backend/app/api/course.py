from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.course_repository import CourseRepository
from app.schemas.course import CourseCreate, CourseRead, CourseUpdate

router = APIRouter()
course_repo = CourseRepository()


@router.get("/courses", response_model=List[CourseRead])
def list_courses(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    return course_repo.list(db, offset=skip, limit=limit)


@router.post("/courses", response_model=CourseRead, status_code=201)
def create_course(course_in: CourseCreate, db: Session = Depends(get_db)):
    return course_repo.create(db, course_in.dict())


@router.get("/courses/{course_id}", response_model=CourseRead)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = course_repo.get(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.patch("/courses/{course_id}", response_model=CourseRead)
def update_course(
    course_id: int,
    course_in: CourseUpdate,
    db: Session = Depends(get_db),
):
    course = course_repo.get(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course_repo.update(db, course, course_in.dict(exclude_unset=True))


@router.delete("/courses/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    deleted = course_repo.delete(db, course_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"status": "deleted", "id": course_id}
