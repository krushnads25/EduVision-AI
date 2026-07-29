from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.importers.base import BaseImporter, DataImportError
from app.models.candidate import Candidate
from app.models.course import Course
from app.models.college import College


class CandidateImporter(BaseImporter):
    entity_name = "candidate"
    required_columns = ("name", "course_code")
    alias_map = {
        "candidate_name": "name",
        "name": "name",
        "email": "email",
        "phone": "phone",
        "course_code": "course_code",
        "course": "course_code",
        "course_name": "course_name",
        "course_id": "course_id",
        "college_name": "college_name",
        "year": "year",
        "category": "category",
        "rank": "rank",
    }

    def process_row(self, row: Dict[str, Any]) -> Optional[str]:
        name = self.clean_text(row.get("name"))
        if not name:
            raise DataImportError("Candidate name is required")

        course = self._resolve_course(row)
        if not course:
            raise DataImportError("Unable to resolve course for candidate")

        existing = (
            self.db.query(Candidate)
            .filter(Candidate.name == name, Candidate.course_id == course.id)
            .one_or_none()
        )
        if existing:
            return "duplicate"

        email = self.clean_text(row.get("email"))
        phone = self.clean_text(row.get("phone"))
        year = self.clean_int(row.get("year"))
        category = self.clean_text(row.get("category"))
        rank = self.clean_int(row.get("rank"))

        candidate = Candidate(
            name=name,
            email=email,
            phone=phone,
            course_id=course.id,
            year=year,
            category=category,
            rank=rank,
        )
        self.db.add(candidate)
        return None

    def _resolve_course(self, row: Dict[str, Any]) -> Optional[Course]:
        course_id = self.clean_int(row.get("course_id"))
        course_code = self.clean_text(row.get("course_code"))
        college_name = self.clean_text(row.get("college_name"))

        if course_id:
            course = self.db.get(Course, course_id)
            if course:
                return course

        query = self.db.query(Course)
        if course_code:
            query = query.filter(Course.code == course_code)
        if college_name:
            query = query.join(College).filter(College.name == college_name)

        courses = query.all()
        if len(courses) == 1:
            return courses[0]
        if len(courses) > 1:
            raise DataImportError("Ambiguous course lookup; supply course_id or college_name")

        return None
