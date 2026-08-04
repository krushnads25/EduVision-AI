"""
rowbuilder.py

Reconstruct logical rows from CET vacancy PDF text.

A row is reconstructed using Choice Codes instead of line boundaries.

Supports:
- Multiple records on one physical line
- Sponsored choice codes
- Regular and sponsored seat values
"""

from __future__ import annotations

import re
from enum import Enum
from typing import List

from logger import logger
from models import Row

# ---------------------------------------------------------
# Regex
# ---------------------------------------------------------

CHOICE_RE = re.compile(r"^\d{10}$")
SPONSORED_RE = re.compile(r"^\d{10}S$")
NUMBER_RE = re.compile(r"^\d+$")
INSTITUTE_RE = re.compile(r"^\d{5}\s*[-:]")


# ---------------------------------------------------------
# Token Types
# ---------------------------------------------------------

class TokenType(Enum):
    WORD = 1
    NUMBER = 2
    CHOICE = 3
    SPONSORED = 4


def classify(token: str) -> TokenType:

    if SPONSORED_RE.fullmatch(token):
        return TokenType.SPONSORED

    if CHOICE_RE.fullmatch(token):
        return TokenType.CHOICE

    if NUMBER_RE.fullmatch(token):
        return TokenType.NUMBER

    return TokenType.WORD


# ---------------------------------------------------------
# Row Builder
# ---------------------------------------------------------

class RowBuilder:

    def __init__(self):
        self.reset()

    # -----------------------------------------------------

    def reset(self):

        self.course_words: List[str] = []

        self.choice_code = ""

        self.sponsored_choice_code = ""

        self.regular_numbers: List[int] = []

        self.sponsored_numbers: List[int] = []

        self.rows: List[Row] = []

    # -----------------------------------------------------

    def tokenize(self, lines: List[str]) -> List[str]:

        tokens: List[str] = []

        #
        # Ignore everything before the institute header.
        #
        seen_institute = False

        for line in lines:

            line = line.strip()

            if not line:
                continue

            #
            # Wait until:
            # 01002 - Government College...
            #
            if not seen_institute:

                if INSTITUTE_RE.match(line):
                    seen_institute = True
                else:
                    continue

            #
            # Skip institute header itself
            #
            if INSTITUTE_RE.match(line):
                continue

            lower = line.lower()

            #
            # Skip obvious non-data lines
            #
            if (
                "published on" in lower
                or "vacant seats" in lower
                or "vacant course name" in lower
                or "seat reserved" in lower
                or "note :-" in lower
                or "institute level seats" in lower
                or "sponsored pwd" in lower
                or lower.startswith("sponsored")
                or lower.startswith("non-sponsored")
                or lower.startswith("choice code")
                or lower.startswith("open sc")
            ):
                continue

            tokens.extend(line.split())

        return tokens

    # -----------------------------------------------------

    def emit(self):

        if not self.choice_code:
            return

        # Build course name
        course = " ".join(self.course_words).strip()

        if not course:
            course = "<UNKNOWN>"

        row = Row(
            course=course,
            choice_code=self.choice_code,
            sponsored_choice_code=self.sponsored_choice_code,
            regular_numbers=self.regular_numbers.copy(),
            sponsored_numbers=self.sponsored_numbers.copy(),
            raw_lines=[],
            raw_text="",
            line_number=0,
        )

        logger.debug(
            f"{row.choice_code} | "
            f"{row.course} | "
            f"regular={len(row.regular_numbers)} "
            f"sponsored={len(row.sponsored_numbers)}"
        )

        self.rows.append(row)

        self.course_words = []
        self.choice_code = ""
        self.sponsored_choice_code = ""
        self.regular_numbers = []
        self.sponsored_numbers = []
    # -----------------------------------------------------

    def build(self, lines: List[str]) -> List[Row]:

        self.reset()

        tokens = self.tokenize(lines)

        next_course: List[str] = []

        reading_sponsored = False

        for token in tokens:

            token_type = classify(token)

            #
            # New row starts
            #
            if token_type == TokenType.CHOICE:

                if self.choice_code:

                    #
                    # Preserve previous course if the next one hasn't started yet.
                    #
                    previous_course = self.course_words.copy()

                    self.emit()

                    if next_course:
                        self.course_words = next_course
                    else:
                        self.course_words = previous_course

                    next_course = []

                self.choice_code = token
                reading_sponsored = False
                continue

            #
            # Sponsored code
            #
            if token_type == TokenType.SPONSORED:

                self.sponsored_choice_code = token
                reading_sponsored = True
                continue

            #
            # Numeric values
            #
            if token_type == TokenType.NUMBER:

                if not self.choice_code:
                    continue

                value = int(token)

                if reading_sponsored:
                    self.sponsored_numbers.append(value)
                else:
                    self.regular_numbers.append(value)

                continue

            #
            # Course words
            #
            if not self.choice_code:
                self.course_words.append(token)
            else:
                next_course.append(token)

        self.emit()

        return self.rows