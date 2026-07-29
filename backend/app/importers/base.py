from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

import pandas as pd
from pandas import DataFrame
from sqlalchemy.orm import Session


class DataImportError(Exception):
    pass


@dataclass
class ImportSummary:
    entity: str
    imported: int = 0
    duplicates: int = 0
    errors: int = 0
    warnings: int = 0
    details: List[str] = field(default_factory=list)


class BaseImporter:
    entity_name: str = "base"
    required_columns: Sequence[str] = ()
    alias_map: Dict[str, str] = {}
    optional_columns: Sequence[str] = ()

    def __init__(self, db: Session):
        self.db = db

    @classmethod
    def normalize_header(cls, header: Any) -> str:
        name = str(header).strip().lower()
        name = name.replace(" ", "_")
        name = name.replace("-", "_")
        name = name.replace("/", "_")
        return name

    @classmethod
    def normalize_columns(cls, df: DataFrame) -> DataFrame:
        renamed = {col: cls.normalize_header(col) for col in df.columns}
        df = df.rename(columns=renamed)

        alias_map = {cls.normalize_header(alias): canonical for alias, canonical in cls.alias_map.items()}
        rename_columns = {alias: canonical for alias, canonical in alias_map.items() if alias in df.columns}
        df = df.rename(columns=rename_columns)

        return df

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

    def run(self, file_path: str, sheet_name: Optional[str] = None) -> ImportSummary:
        df = self.load_file(file_path, sheet_name=sheet_name)
        df = self.normalize_columns(df)
        self.validate_dataframe(df)

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
