from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.importers.base import BaseImporter, DataImportError
from app.models.course import Course
from app.models.college import College


class CourseImporter(BaseImporter):
    entity_name = "course"
    required_columns = ("college_name", "code", "name")
    alias_map = {
        "college": "college_name",
        "college_name": "college_name",
        "college_id": "college_id",
        "code": "code",
        "course_code": "code",
        "name": "name",
        "course_name": "name",
        "degree_level": "degree_level",
        "intake": "intake",
    }

    def process_row(self, row: Dict[str, Any]) -> Optional[str]:
        code = self.clean_text(row.get("code"))
        name = self.clean_text(row.get("name"))
        if not code or not name:
            raise DataImportError("Course code and name are required")

        college = self._resolve_college(row)
        if not college:
            raise DataImportError("Unable to resolve college for course")

        existing = (
            self.db.query(Course)
            .filter(Course.code == code, Course.college_id == college.id)
            .one_or_none()
        )
        if existing:
            return "duplicate"

        degree_level = self.clean_text(row.get("degree_level"))
        intake = self.clean_int(row.get("intake"))

        course = Course(
            college_id=college.id,
            code=code,
            name=name,
            degree_level=degree_level,
            intake=intake,
        )
        self.db.add(course)
        return None

    def _resolve_college(self, row: Dict[str, Any]) -> Optional[College]:
        college_id = self.clean_int(row.get("college_id"))
        college_name = self.clean_text(row.get("college_name"))

        if college_id:
            college = self.db.get(College, college_id)
            if college:
                return college

        if college_name:
            college = self.db.query(College).filter(College.name == college_name).one_or_none()
            if college:
                return college

        if college_name:
            college = College(name=college_name)
            self.db.add(college)
            self.db.flush()
            return college

        return None
