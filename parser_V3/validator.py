"""
validator.py

Validation for parsed records.
"""

from __future__ import annotations

from collections import Counter
from typing import List

from logger import logger
from models import Record


class Validator:

    def __init__(self):

        self.errors = []

        self.warnings = []

    # ---------------------------------------------------------

    def reset(self):

        self.errors.clear()

        self.warnings.clear()

    # ---------------------------------------------------------

    def validate(self, records: List[Record]):

        self.reset()

        self._missing_college(records)

        self._missing_course(records)

        self._duplicate_choice(records)

        self._invalid_intake(records)

        self.summary()

        return len(self.errors) == 0

    # ---------------------------------------------------------

    def _missing_college(self, records):

        for r in records:

            if not r.college_code:

                self.errors.append(
                    f"{r.choice_code} : Missing college code"
                )

    # ---------------------------------------------------------

    def _missing_course(self, records):

        for r in records:

            if not r.course:

                self.errors.append(
                    f"{r.choice_code} : Missing course"
                )

    # ---------------------------------------------------------

    def _invalid_intake(self, records):

        for r in records:

            if r.intake < 0:

                self.errors.append(
                    f"{r.choice_code} : Negative intake"
                )

    # ---------------------------------------------------------

    def _duplicate_choice(self, records):

        keys = [
            (
                r.college_code,
                r.choice_code,
            )
            for r in records
        ]

        counts = Counter(keys)

        for key, count in counts.items():

            if count > 1:

                self.errors.append(
                    f"Duplicate Choice Code : {key}"
                )

    # ---------------------------------------------------------

    def summary(self):

        logger.info("")

        logger.info("=" * 40)

        logger.info("Validation Summary")

        logger.info("=" * 40)

        logger.info(
            f"Errors   : {len(self.errors)}"
        )

        logger.info(
            f"Warnings : {len(self.warnings)}"
        )

        if self.errors:

            logger.info("")

            for e in self.errors:

                logger.error(e)

        logger.info("=" * 40)