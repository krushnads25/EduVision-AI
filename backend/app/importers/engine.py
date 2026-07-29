from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Type

from sqlalchemy.orm import Session

from app.importers.base import ImportSummary, DataImportError
from app.importers.college_importer import CollegeImporter
from app.importers.course_importer import CourseImporter
from app.importers.candidate_importer import CandidateImporter


IMPORTER_TYPES: Dict[str, Type] = {
    "college": CollegeImporter,
    "course": CourseImporter,
    "candidate": CandidateImporter,
}


@dataclass
class EngineReport:
    summaries: Dict[str, ImportSummary] = field(default_factory=dict)
    errors: int = 0

    def add_summary(self, summary: ImportSummary) -> None:
        self.summaries[summary.entity] = summary
        self.errors += summary.errors

    def to_dict(self) -> Dict[str, object]:
        return {
            "summaries": {entity: summary.__dict__ for entity, summary in self.summaries.items()},
            "errors": self.errors,
        }


class ImportEngine:
    def __init__(self, db: Session):
        self.db = db

    def run(self, entity: str, file_path: str, sheet_name: Optional[str] = None) -> EngineReport:
        importer_class = IMPORTER_TYPES.get(entity.lower())
        if importer_class is None:
            raise DataImportError(f"Unknown import entity: {entity}. Supported: {list(IMPORTER_TYPES)}")

        importer = importer_class(self.db)
        summary = importer.run(file_path, sheet_name=sheet_name)
        report = EngineReport()
        report.add_summary(summary)
        return report
