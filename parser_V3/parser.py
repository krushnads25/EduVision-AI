"""
parser.py

Main parser engine.
"""

from __future__ import annotations

from pathlib import Path
import traceback
from typing import List

import pdfplumber

from cleaner import clean_lines
from detector import build_page_data
from extractor import extract_page, lines_as_text
from layouts import LAYOUTS
from logger import logger
from models import PageData, Record
from rowbuilder import RowBuilder


class Parser:

    def __init__(self):

        self.records: List[Record] = []

        self.current_university = ""

        self.current_institute_code = ""

        self.current_institute_name = ""

        self.row_builder = RowBuilder()

        self.page_count = 0
        self.row_count = 0
        self.skipped_rows = 0

    # ---------------------------------------------------------

    def reset(self):

        self.records.clear()

        self.current_university = ""

        self.current_institute_code = ""

        self.current_institute_name = ""

        self.page_count = 0
        self.row_count = 0
        self.skipped_rows = 0
    # ---------------------------------------------------------

    def parse_pdf(
        self,
        pdf_path: str | Path,
    ) -> List[Record]:

        self.reset()

        pdf_path = Path(pdf_path)

        logger.info(f"Opening {pdf_path}")

        with pdfplumber.open(pdf_path) as pdf:
            self.page_count = len(pdf.pages)

            logger.info(f"{len(pdf.pages)} pages found")

            for index, page in enumerate(pdf.pages, start=1):

                self.parse_page(index, page)

        logger.info(
            f"Finished : {len(self.records)} records"
        )

        return self.records
    # ---------------------------------------------------------

    def parse_page(
        self,
        page_number: int,
        page,
    ):

        logger.info(f"Page {page_number}")

        #
        # Extract lines
        #

        line_objects = extract_page(page)

        text_lines = lines_as_text(line_objects)

        text_lines = clean_lines(text_lines)
        if page_number == 1:
            logger.info("===== PAGE 1 CLEANED LINES =====")
            for line in text_lines[:25]:
                logger.info(line)

        #
        # Detect metadata
        #

        page_data = build_page_data(
            page_number,
            text_lines,
        )
        if page_number == 1:
            logger.info(f"Detected layout: {page_data.layout}")
            logger.info(f"University: {page_data.university}")
            logger.info(f"Institute: {page_data.institute_code}")
            logger.info(f"Columns: {page_data.column_map}")

        page_data.lines = line_objects

        #
        # Remember university
        #

        if page_data.university:

            self.current_university = page_data.university

        else:

            page_data.university = self.current_university

        #
        # Remember institute
        #

        if page_data.institute_code:

            self.current_institute_code = page_data.institute_code

            self.current_institute_name = page_data.institute_name

        else:

            page_data.institute_code = self.current_institute_code

            page_data.institute_name = self.current_institute_name

        #
        # Build rows
        #

        rows = self.row_builder.build(text_lines)
        self.row_count += len(rows)
        filtered_rows = []

        for row in rows:

            if not row.choice_code:
                self.skipped_rows += 1
                continue

            filtered_rows.append(row)

        rows = filtered_rows

        logger.debug(
            f"{len(rows)} rows reconstructed"
        )

        #
        # Select layout
        #

        layout = LAYOUTS.get(page_data.layout)

        if layout is None:

            logger.warn(
                f"No parser for layout '{page_data.layout}'"
            )

            return

        #
        # Parse rows
        #

        for row in rows:

            try:

                record = layout.parse(
                    row,
                    page_data,
                )

                self.records.append(record)

            except Exception:

                logger.error(
                    f"Page {page_number} "
                    f"Choice {row.choice_code}"
                )

                logger.debug(traceback.format_exc())