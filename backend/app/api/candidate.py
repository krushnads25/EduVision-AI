from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.candidate_repository import CandidateRepository
from app.schemas.candidate import CandidateCreate, CandidateRead, CandidateUpdate

router = APIRouter()
candidate_repo = CandidateRepository()


@router.get("/candidates", response_model=List[CandidateRead])
def list_candidates(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    return candidate_repo.list(db, offset=skip, limit=limit)


@router.post("/candidates", response_model=CandidateRead, status_code=201)
def create_candidate(candidate_in: CandidateCreate, db: Session = Depends(get_db)):
    return candidate_repo.create(db, candidate_in.dict())


@router.get("/candidates/{candidate_id}", response_model=CandidateRead)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = candidate_repo.get(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.patch("/candidates/{candidate_id}", response_model=CandidateRead)
def update_candidate(
    candidate_id: int,
    candidate_in: CandidateUpdate,
    db: Session = Depends(get_db),
):
    candidate = candidate_repo.get(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate_repo.update(db, candidate, candidate_in.dict(exclude_unset=True))


@router.delete("/candidates/{candidate_id}")
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    deleted = candidate_repo.delete(db, candidate_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"status": "deleted", "id": candidate_id}
