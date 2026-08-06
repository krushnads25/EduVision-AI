from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.college import College
from app.models.course import Course
from app.models.seat_matrix import SeatMatrix
from app.models.vacancy import Vacancy

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/seats")
def seat_analytics(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    round: Optional[int] = Query(None),
    college_id: Optional[int] = Query(None),
    course_id: Optional[int] = Query(None),
    choice_code: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    query = db.query(SeatMatrix, College.name.label("college_name"), Course.name.label("course_name")).join(College, SeatMatrix.college_id == College.id).join(Course, SeatMatrix.course_id == Course.id)
    if year is not None:
        query = query.filter(SeatMatrix.year == year)
    if round is not None:
        query = query.filter(SeatMatrix.round == round)
    if college_id is not None:
        query = query.filter(SeatMatrix.college_id == college_id)
    if course_id is not None:
        query = query.filter(SeatMatrix.course_id == course_id)
    if choice_code:
        query = query.filter(SeatMatrix.choice_code == choice_code)
    if search:
        term = f"%{search}%"
        query = query.filter((College.name.ilike(term)) | (Course.name.ilike(term)) | (SeatMatrix.choice_code.ilike(term)))

    rows = query.order_by(College.name, Course.name).all()
    return {
        "count": len(rows),
        "items": [
            {
                "id": r.SeatMatrix.id,
                "college_id": r.SeatMatrix.college_id,
                "college_name": r.college_name,
                "course_id": r.SeatMatrix.course_id,
                "course_name": r.course_name,
                "year": r.SeatMatrix.year,
                "round": r.SeatMatrix.round,
                "choice_code": r.SeatMatrix.choice_code,
                "tfws_choice_code": r.SeatMatrix.tfws_choice_code,
                "intake": r.SeatMatrix.intake,
                "hu_open": r.SeatMatrix.hu_open,
                "hu_sc": r.SeatMatrix.hu_sc,
                "hu_st": r.SeatMatrix.hu_st,
                "hu_vjdt": r.SeatMatrix.hu_vjdt,
                "hu_ntb": r.SeatMatrix.hu_ntb,
                "hu_ntc": r.SeatMatrix.hu_ntc,
                "hu_ntd": r.SeatMatrix.hu_ntd,
                "hu_obc": r.SeatMatrix.hu_obc,
                "hu_sebc": r.SeatMatrix.hu_sebc,
                "ohu_open": r.SeatMatrix.ohu_open,
                "ohu_sc": r.SeatMatrix.ohu_sc,
                "ohu_st": r.SeatMatrix.ohu_st,
                "ohu_vjdt": r.SeatMatrix.ohu_vjdt,
                "ohu_ntb": r.SeatMatrix.ohu_ntb,
                "ohu_ntc": r.SeatMatrix.ohu_ntc,
                "ohu_ntd": r.SeatMatrix.ohu_ntd,
                "ohu_obc": r.SeatMatrix.ohu_obc,
                "ohu_sebc": r.SeatMatrix.ohu_sebc,
                "pwd_total": r.SeatMatrix.pwd_total,
                "orphan": r.SeatMatrix.orphan,
                "institute_level": r.SeatMatrix.institute_level,
                "minority": r.SeatMatrix.minority,
                "tfws_seats": r.SeatMatrix.tfws_seats,
                "total_seats": r.SeatMatrix.total_seats,
            }
            for r in rows
        ],
    }


@router.get("/vacancies")
def vacancy_analytics(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None),
    round: Optional[int] = Query(None),
    college_id: Optional[int] = Query(None),
    course_id: Optional[int] = Query(None),
    choice_code: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    query = db.query(Vacancy, College.name.label("college_name"), Course.name.label("course_name")).join(College, Vacancy.college_id == College.id).join(Course, Vacancy.course_id == Course.id)
    if year is not None:
        query = query.filter(Vacancy.year == year)
    if round is not None:
        query = query.filter(Vacancy.round == round)
    if college_id is not None:
        query = query.filter(Vacancy.college_id == college_id)
    if course_id is not None:
        query = query.filter(Vacancy.course_id == course_id)
    if choice_code:
        query = query.filter(Vacancy.choice_code == choice_code)
    if search:
        term = f"%{search}%"
        query = query.filter((College.name.ilike(term)) | (Course.name.ilike(term)) | (Vacancy.choice_code.ilike(term)))

    rows = query.order_by(College.name, Course.name).all()
    return {
        "count": len(rows),
        "items": [
            {
                "id": r.Vacancy.id,
                "college_id": r.Vacancy.college_id,
                "college_name": r.college_name,
                "course_id": r.Vacancy.course_id,
                "course_name": r.course_name,
                "year": r.Vacancy.year,
                "round": r.Vacancy.round,
                "choice_code": r.Vacancy.choice_code,
                "tfws_choice_code": r.Vacancy.tfws_choice_code,
                "hu_open": r.Vacancy.hu_open,
                "hu_sc": r.Vacancy.hu_sc,
                "hu_st": r.Vacancy.hu_st,
                "hu_vjdt": r.Vacancy.hu_vjdt,
                "hu_ntb": r.Vacancy.hu_ntb,
                "hu_ntc": r.Vacancy.hu_ntc,
                "hu_ntd": r.Vacancy.hu_ntd,
                "hu_obc": r.Vacancy.hu_obc,
                "hu_sebc": r.Vacancy.hu_sebc,
                "ohu_open": r.Vacancy.ohu_open,
                "ohu_sc": r.Vacancy.ohu_sc,
                "ohu_st": r.Vacancy.ohu_st,
                "ohu_vjdt": r.Vacancy.ohu_vjdt,
                "ohu_ntb": r.Vacancy.ohu_ntb,
                "ohu_ntc": r.Vacancy.ohu_ntc,
                "ohu_ntd": r.Vacancy.ohu_ntd,
                "ohu_obc": r.Vacancy.ohu_obc,
                "ohu_sebc": r.Vacancy.ohu_sebc,
                "pwd_total": r.Vacancy.pwd_total,
                "orphan": r.Vacancy.orphan,
                "institute_level": r.Vacancy.institute_level,
                "minority": r.Vacancy.minority,
                "tfws_seats": r.Vacancy.tfws_seats,
                "total_vacancies": r.Vacancy.total_vacancies,
            }
            for r in rows
        ],
    }