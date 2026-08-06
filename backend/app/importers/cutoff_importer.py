from typing import Any, Dict, Optional
from pathlib import Path
import csv

import pandas as pd
from pandas import DataFrame

from app.importers.base import BaseImporter, DataImportError
from app.models.cutoff import Cutoff


class CutoffImporter(BaseImporter):
    entity_name = "cutoff"
    required_columns = ("college_name", "choice_code")

    alias_map = {
        "college": "college_name",
        "university": "college_name",
        "institute": "college_name",
        "institute_name": "college_name",
        "course_name": "course",
        "code": "choice_code",
        "tfws_code": "tfws_choice_code",
        "merit": "hu_open",
        "score": "hu_open",
        "cutoff": "hu_open",
        "institute_level_cutoff": "institute_level",
        "minority_cutoff": "minority",
        "pwd_cutoff": "pwd",
        "orphan_cutoff": "orphan",
        "tfws_cutoff": "tfws",
    }

    cutoff_columns = (
        "hu_open", "hu_sc", "hu_st", "hu_vjdt", "hu_ntb", "hu_ntc",
        "hu_ntd", "hu_obc", "hu_sebc", "ohu_open", "ohu_sc", "ohu_st",
        "ohu_vjdt", "ohu_ntb", "ohu_ntc", "ohu_ntd", "ohu_obc", "ohu_sebc",
        "ews", "tfws", "orphan", "pwd", "institute_level", "minority",
    )

    @classmethod
    def load_file(cls, file_path: str, sheet_name: Optional[str] = None) -> DataFrame:
        path = Path(file_path)
        if path.suffix.lower() != ".csv":
            return super().load_file(file_path, sheet_name=sheet_name)

        with path.open(encoding="utf-8-sig", newline="") as file:
            rows = list(csv.reader(file))

        if not rows:
            raise DataImportError("Cutoff CSV is empty")

        header_index = cls._find_header_index(rows)
        if header_index is None:
            raise DataImportError(
                "Unable to determine Parser V3 cutoff CSV header row"
            )

        header = [str(value).strip() for value in rows[header_index]]
        width = len(header)
        data_rows = []
        for row in rows[header_index + 1:]:
            if not any(str(value).strip() for value in row):
                continue
            if len(row) < width:
                row = row + [""] * (width - len(row))
            data_rows.append(row[:width])

        return cls.normalize_columns(
            pd.DataFrame(data_rows, columns=header)
        )

    @classmethod
    def _find_header_index(cls, rows: list[list[str]]) -> Optional[int]:
        identity_names = {
            "college", "college_name", "university", "institute",
            "institute_name", "course", "course_name", "code", "choice_code",
        }
        cutoff_names = set(cls.cutoff_columns)

        best_index = None
        best_score = 0
        for index, row in enumerate(rows):
            normalized = {
                cls.normalize_header(value)
                for value in row
                if str(value).strip()
            }
            identity_score = len(normalized & identity_names)
            cutoff_score = len(normalized & cutoff_names)
            score = identity_score * 3 + cutoff_score
            if identity_score >= 1 and cutoff_score >= 1 and score > best_score:
                best_index = index
                best_score = score
        return best_index

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
            raise DataImportError("Unable to resolve course for cutoff row")

        year = self.get_year()
        if year is None:
            raise DataImportError("Year is required for cutoff import")
        round_value = self.get_round()

        values = {
            "college_id": college.id,
            "course_id": course.id,
            "year": year,
            "round": round_value,
            "choice_code": choice_code,
        }
        for column in self.cutoff_columns:
            values[column] = self.clean_float(row.get(column))

        if all(values[column] is None for column in self.cutoff_columns):
            raise DataImportError("No cutoff values found")

        query = self.db.query(Cutoff).filter(
            Cutoff.college_id == college.id,
            Cutoff.course_id == course.id,
            Cutoff.year == year,
            Cutoff.choice_code == choice_code,
        )
        query = query.filter(Cutoff.round == round_value)
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

        self.db.add(Cutoff(**values))
        return None