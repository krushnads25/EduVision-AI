from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.college_repository import CollegeRepository
from app.schemas.college import CollegeCreate, CollegeRead, CollegeUpdate

router = APIRouter()
college_repo = CollegeRepository()


@router.get("/colleges", response_model=List[CollegeRead])
def list_colleges(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    return college_repo.list(db, offset=skip, limit=limit)


@router.post("/colleges", response_model=CollegeRead, status_code=201)
def create_college(college_in: CollegeCreate, db: Session = Depends(get_db)):
    return college_repo.create(db, college_in.dict())


@router.get("/colleges/{college_id}", response_model=CollegeRead)
def get_college(college_id: int, db: Session = Depends(get_db)):
    college = college_repo.get(db, college_id)
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    return college


@router.patch("/colleges/{college_id}", response_model=CollegeRead)
def update_college(
    college_id: int,
    college_in: CollegeUpdate,
    db: Session = Depends(get_db),
):
    college = college_repo.get(db, college_id)
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    return college_repo.update(db, college, college_in.dict(exclude_unset=True))


@router.delete("/colleges/{college_id}")
def delete_college(college_id: int, db: Session = Depends(get_db)):
    deleted = college_repo.delete(db, college_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="College not found")
    return {"status": "deleted", "id": college_id}
