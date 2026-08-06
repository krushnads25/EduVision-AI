from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.vacancy_repository import VacancyRepository
from app.schemas.vacancy import VacancyCreate, VacancyRead, VacancyUpdate

router = APIRouter()
vacancy_repo = VacancyRepository()


@router.get("/vacancies", response_model=List[VacancyRead])
def list_vacancies(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    return vacancy_repo.list(db, offset=skip, limit=limit)


@router.post("/vacancies", response_model=VacancyRead, status_code=201)
def create_vacancy(vacancy_in: VacancyCreate, db: Session = Depends(get_db)):
    return vacancy_repo.create(db, vacancy_in.dict())


@router.get("/vacancies/{vacancy_id}", response_model=VacancyRead)
def get_vacancy(vacancy_id: int, db: Session = Depends(get_db)):
    vacancy = vacancy_repo.get(db, vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    return vacancy


@router.patch("/vacancies/{vacancy_id}", response_model=VacancyRead)
def update_vacancy(
    vacancy_id: int,
    vacancy_in: VacancyUpdate,
    db: Session = Depends(get_db),
):
    vacancy = vacancy_repo.get(db, vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    return vacancy_repo.update(db, vacancy, vacancy_in.dict(exclude_unset=True))


@router.delete("/vacancies/{vacancy_id}")
def delete_vacancy(vacancy_id: int, db: Session = Depends(get_db)):
    deleted = vacancy_repo.delete(db, vacancy_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    return {"status": "deleted", "id": vacancy_id}
