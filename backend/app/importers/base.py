from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence
import re

import pandas as pd
from pandas import DataFrame
from sqlalchemy.orm import Session


class DataImportError(Exception):
    pass


@dataclass
class ImportSummary:
    entity: str
    imported: int = 0
    updated: int = 0
    duplicates: int = 0
    errors: int = 0
    warnings: int = 0
    details: List[str] = field(default_factory=list)


class BaseImporter:
    entity_name: str = "base"
    required_columns: Sequence[str] = ()
    alias_map: Dict[str, str] = {}
    optional_columns: Sequence[str] = ()

    def __init__(self, db: Session, context: Optional[Dict[str, Any]] = None):
        self.db = db
        self.context = context or {}
        self.file_path: Optional[str] = None

    @classmethod
    def normalize_header(cls, header: Any) -> str:
        name = str(header).strip().lower()
        name = name.replace(" ", "_")
        name = name.replace("-", "_")
        name = name.replace("/", "_")
        return name

    @classmethod
    def normalize_columns(cls, df: DataFrame) -> DataFrame:
        alias_map = {cls.normalize_header(alias): canonical for alias, canonical in cls.alias_map.items()}

        canonical_sources: Dict[str, list[str]] = {}
        normalized_headers: Dict[str, str] = {}
        for col in df.columns:
            normalized = cls.normalize_header(col)
            canonical = alias_map.get(normalized, normalized)
            canonical_sources.setdefault(canonical, []).append(col)
            normalized_headers[col] = normalized

        transformed = pd.DataFrame(index=df.index)
        for canonical, sources in canonical_sources.items():
            preferred_source = None
            for source in sources:
                if normalized_headers[source] == canonical:
                    preferred_source = source
                    break
            preferred_source = preferred_source or sources[0]

            transformed[canonical] = df[preferred_source]
            for source in sources:
                if source == preferred_source:
                    continue
                transformed[canonical] = transformed[canonical].combine_first(df[source])

        return transformed

    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        return [".csv", ".xls", ".xlsx"]

    @classmethod
    def load_file(cls, file_path: str, sheet_name: Optional[str] = None) -> DataFrame:
        path = Path(file_path)
        if not path.exists():
            raise DataImportError(f"Import file does not exist: {file_path}")

        suffix = path.suffix.lower()
        if suffix == ".csv":
            return pd.read_csv(path, dtype=str, keep_default_na=False)

        if suffix in {".xls", ".xlsx"}:
            try:
                return pd.read_excel(path, sheet_name=sheet_name or 0, engine="openpyxl", dtype=str)
            except ImportError as exc:
                raise DataImportError("Excel import requires openpyxl. Install it with `pip install openpyxl`.") from exc

        raise DataImportError(f"Unsupported import format: {suffix}. Supported: {cls.get_supported_extensions()}")

    @classmethod
    def validate_dataframe(cls, df: DataFrame) -> None:
        missing = [col for col in cls.required_columns if col not in df.columns]
        if missing:
            raise DataImportError(f"Missing required columns for {cls.entity_name}: {missing}")

    def run(self, file_path: str, sheet_name: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> ImportSummary:
        df = self.load_file(file_path, sheet_name=sheet_name)
        df = self.normalize_columns(df)
        self.validate_dataframe(df)

        self.context = context or {}
        self.file_path = file_path

        summary = ImportSummary(entity=self.entity_name)
        records = df.to_dict(orient="records")
        for row_number, raw_row in enumerate(records, start=1):
            try:
                row = {self.normalize_header(key): value for key, value in raw_row.items()}
                result = self.process_row(row)
                if result == "duplicate":
                    summary.duplicates += 1
                    summary.details.append(f"Row {row_number}: duplicate skipped")
                    self.db.rollback()
                    continue
                if result == "updated":
                    summary.updated += 1
                    summary.details.append(f"Row {row_number}: existing record updated")
                    self.db.commit()
                    continue

                summary.imported += 1
                self.db.commit()
            except DataImportError as exc:
                summary.errors += 1
                summary.details.append(f"Row {row_number}: {exc}")
                self.db.rollback()
            except Exception as exc:
                summary.errors += 1
                summary.details.append(f"Row {row_number}: unexpected error: {exc}")
                self.db.rollback()

        return summary

    def process_row(self, row: Dict[str, Any]) -> Optional[str]:
        raise NotImplementedError("Must implement process_row in subclass")

    @staticmethod
    def clean_text(value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text if text != "" else None

    @staticmethod
    def clean_int(value: Any) -> Optional[int]:
        if value is None:
            return None
        try:
            value_str = str(value).strip()
            if value_str == "":
                return None
            return int(float(value_str))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def clean_float(value: Any) -> Optional[float]:
        if value is None:
            return None
        value_str = str(value).strip()
        if value_str == "":
            return None

        numbers = re.findall(r"-?\d+(?:\.\d+)?", value_str)
        if not numbers:
            return None

        try:
            return float(numbers[-1])
        except ValueError:
            return None

    def infer_year_from_path(self) -> Optional[int]:
        if not self.file_path:
            return None
        match = re.search(r"(20\d{2})", str(self.file_path))
        return self.clean_int(match.group(1)) if match else None

    def infer_round_from_path(self) -> Optional[int]:
        if not self.file_path:
            return None
        match = re.search(r"(?:cap|round)[_\- ]*([0-9]+)", str(self.file_path), re.IGNORECASE)
        return self.clean_int(match.group(1)) if match else None

    def get_year(self) -> Optional[int]:
        year = self.context.get("year")
        return self.clean_int(year) or self.infer_year_from_path()

    def get_round(self) -> Optional[int]:
        round_value = self.context.get("round")
        return self.clean_int(round_value) or self.infer_round_from_path()

    def _resolve_college(self, row: Dict[str, Any]) -> Optional["College"]:
        from app.models.college import College

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

        return None

    def _find_or_create_college(self, college_name: Optional[str]) -> Optional["College"]:
        from app.models.college import College

        if not college_name:
            return None
        college = self.db.query(College).filter(College.name == college_name).one_or_none()
        if college:
            return college
        college = College(name=college_name)
        self.db.add(college)
        self.db.flush()
        return college

    def _resolve_course(self, row: Dict[str, Any]) -> Optional["Course"]:
        from app.models.course import Course

        course_id = self.clean_int(row.get("course_id"))
        course_code = self.clean_text(row.get("course_code") or row.get("code") or row.get("course"))
        college = self._resolve_college(row)

        if course_id:
            course = self.db.get(Course, course_id)
            if course:
                return course

        query = self.db.query(Course)
        if course_code:
            query = query.filter(Course.code == course_code)
        if college:
            query = query.filter(Course.college_id == college.id)

        courses = query.all()
        if len(courses) == 1:
            return courses[0]

        return None

    def _find_or_create_course(self, college: "College", course_code: Optional[str], course_name: Optional[str]) -> Optional["Course"]:
        from app.models.course import Course

        if not college or not course_code:
            return None
        course = (
            self.db.query(Course)
            .filter(Course.college_id == college.id, Course.code == course_code)
            .one_or_none()
        )
        if course:
            return course
        course = Course(college_id=college.id, code=course_code, name=course_name or course_code)
        self.db.add(course)
        self.db.flush()
        return course
