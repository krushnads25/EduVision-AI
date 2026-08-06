from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.cutoff_repository import CutoffRepository
from app.schemas.cutoff import CutoffCreate, CutoffRead, CutoffUpdate

router = APIRouter()
cutoff_repo = CutoffRepository()


@router.get("/cutoffs", response_model=List[CutoffRead])
def list_cutoffs(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    college_id: Optional[int] = Query(None),
    course_id: Optional[int] = Query(None),
):
    if college_id:
        return cutoff_repo.list_by_college(db, college_id)
    if course_id:
        return cutoff_repo.list_by_course(db, course_id)
    return cutoff_repo.list(db, offset=skip, limit=limit)


@router.post("/cutoffs", response_model=CutoffRead, status_code=201)
def create_cutoff(cutoff_in: CutoffCreate, db: Session = Depends(get_db)):
    return cutoff_repo.create(db, cutoff_in.dict())


@router.get("/cutoffs/{cutoff_id}", response_model=CutoffRead)
def get_cutoff(cutoff_id: int, db: Session = Depends(get_db)):
    cutoff = cutoff_repo.get(db, cutoff_id)
    if not cutoff:
        raise HTTPException(status_code=404, detail="Cutoff not found")
    return cutoff


@router.patch("/cutoffs/{cutoff_id}", response_model=CutoffRead)
def update_cutoff(
    cutoff_id: int,
    cutoff_in: CutoffUpdate,
    db: Session = Depends(get_db),
):
    cutoff = cutoff_repo.get(db, cutoff_id)
    if not cutoff:
        raise HTTPException(status_code=404, detail="Cutoff not found")
    return cutoff_repo.update(db, cutoff, cutoff_in.dict(exclude_unset=True))


@router.delete("/cutoffs/{cutoff_id}")
def delete_cutoff(cutoff_id: int, db: Session = Depends(get_db)):
    deleted = cutoff_repo.delete(db, cutoff_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Cutoff not found")
    return {"status": "deleted", "id": cutoff_id}
