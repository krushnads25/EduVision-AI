from typing import Any, Dict, Optional

from app.importers.base import BaseImporter, DataImportError
from app.models.vacancy import Vacancy


class VacancyImporter(BaseImporter):
    entity_name = "vacancy"
    required_columns = ("college_name", "choice_code")

    alias_map = {
        "college": "college_name",
        "university": "college_name",
        "institute": "college_name",
        "institute_name": "college_name",
        "course_name": "course",
        "code": "choice_code",
        "vacancies": "total_vacancies",
        "vacant_seats": "total_vacancies",
        "vacant": "total_vacancies",
        "tfws_code": "tfws_choice_code",
        "all_india_seats": "institute_level",
        "minority_seats": "minority",
        "institute_seats": "institute_level",
    }

    integer_columns = (
        "hu_open", "hu_sc", "hu_st", "hu_vjdt", "hu_ntb", "hu_ntc",
        "hu_ntd", "hu_obc", "hu_sebc", "ohu_open", "ohu_sc", "ohu_st",
        "ohu_vjdt", "ohu_ntb", "ohu_ntc", "ohu_ntd", "ohu_obc", "ohu_sebc",
        "pwd_total", "orphan", "institute_level", "minority", "tfws_seats",
        "total_vacancies",
    )

    def process_row(self, row: Dict[str, Any]) -> Optional[str]:
        college_name = self.clean_text(row.get("college_name"))
        choice_code = self.clean_text(row.get("choice_code"))
        if not college_name:
            raise DataImportError("College name is required")
        if not choice_code:
            raise DataImportError("Choice code is required")

        college = self._find_or_create_college(college_name)
        course_name = self.clean_text(row.get("course"))
        course = self._find_or_create_course(college, choice_code, course_name)
        if not course:
            raise DataImportError("Unable to resolve course for vacancy row")

        year = self.get_year()
        if year is None:
            raise DataImportError("Year is required for vacancy import")
        round_value = self.get_round()

        values = {
            "college_id": college.id,
            "course_id": course.id,
            "year": year,
            "round": round_value,
            "choice_code": choice_code,
            "tfws_choice_code": self.clean_text(row.get("tfws_choice_code")),
        }
        for column in self.integer_columns:
            values[column] = self.clean_int(row.get(column))

        category_columns = self.integer_columns[:-1]
        if all(values[column] is None for column in category_columns):
            raise DataImportError("No vacancy values found")

        if values["total_vacancies"] is None:
            values["total_vacancies"] = sum(
                values[column] or 0 for column in category_columns
            )

        query = self.db.query(Vacancy).filter(
            Vacancy.college_id == college.id,
            Vacancy.course_id == course.id,
            Vacancy.year == year,
            Vacancy.choice_code == choice_code,
        )
        query = query.filter(Vacancy.round == round_value)
        existing = query.one_or_none()

        if existing:
            changed = False
            for column, value in values.items():
                if column in {"college_id", "course_id", "year", "choice_code"}:
                    continue
                if getattr(existing, column) != value:
                    setattr(existing, column, value)
                    changed = True
            return "updated" if changed else "duplicate"

        self.db.add(Vacancy(**values))
        return None