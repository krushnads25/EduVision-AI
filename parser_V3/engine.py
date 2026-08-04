"""
engine.py

Coordinates parsing, validation and exporting.
"""

from __future__ import annotations

from pathlib import Path
import time

from logger import logger
from models import ParseResult
from parser import Parser
from validator import Validator
from exporter import Exporter

class ParserEngine:

    def __init__(self):

        self.parser = Parser()

        self.validator = Validator()

        self.exporter = Exporter()

    # -----------------------------------------------------

    def parse(
        self,
        pdf_path: str | Path,
    ) -> ParseResult:

        start = time.perf_counter()

        records = self.parser.parse_pdf(pdf_path)

        self.validator.validate(records)

        return ParseResult(
            records=records,
            pages=self.parser.page_count,
            universities=len({
                r.university
                for r in records
                if r.university
            }),
            institutes=len({
                (r.college_code, r.college_name)
                for r in records
            }),
            reconstructed_rows=self.parser.row_count,
            skipped_rows=self.parser.skipped_rows,
            validation_errors=len(self.validator.errors),
            elapsed_seconds=time.perf_counter() - start,
        )

    # -----------------------------------------------------
    def export_csv(
        self,
        result: ParseResult,
        output_file,
    ):

        self.exporter.to_csv(
            result.records,
            output_file,
        )