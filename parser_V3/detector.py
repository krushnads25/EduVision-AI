"""
detector.py

Detect page metadata:
- University
- Institute
- Layout
- Continuation pages
"""

from __future__ import annotations

import re
from typing import Optional

from models import PageData
from columnmap import ColumnMap
from header_normalizer import normalize_header
from logger import logger
# ------------------------------------------------------------
# Regular Expressions
# ------------------------------------------------------------

UNIVERSITY_RE = re.compile(
    r".*University.*",
    re.IGNORECASE,
)

INSTITUTE_RE = re.compile(
    r"^\s*(\d{5})\s*[-:]\s*(.+)$"
)

CHOICE_CODE_RE = re.compile(
    r"\d{10}[A-Z]?$"
)

COURSE_HEADER_RE = re.compile(
    r"Course\s*Name",
    re.IGNORECASE,
)

CHOICE_HEADER_RE = re.compile(
    r"Choice\s*Code",
    re.IGNORECASE,
)

INTAKE_HEADER_RE = re.compile(
    r"Intake",
    re.IGNORECASE,
)
HEADER_SPLIT_RE = re.compile(r"\s{2,}")

# ------------------------------------------------------------
# University
# ------------------------------------------------------------


def detect_university(lines: list[str]) -> Optional[str]:

    for line in lines:

        if UNIVERSITY_RE.search(line):

            return line.strip()

    return None


# ------------------------------------------------------------
# Institute
# ------------------------------------------------------------


def detect_institute(lines: list[str]):

    STOP_WORDS = (
        "Non-Sponsored",
        "Sponsored",
        "PWD",
        "Total",
        "Choice Code",
        "Open",
        "Seat",
    )

    for line in lines:

        m = INSTITUTE_RE.match(line)

        if not m:
            continue

        code = m.group(1)

        name = m.group(2).strip()

        #
        # Remove everything after the real institute name
        #

        cut = len(name)

        for word in STOP_WORDS:

            idx = name.find(word)

            if idx != -1:
                cut = min(cut, idx)

        name = name[:cut].strip(" -")

        return code, name

    return None, None
# ------------------------------------------------------------
# Header Detection
# ------------------------------------------------------------


def has_course_header(lines: list[str]) -> bool:

    for line in lines:

        if COURSE_HEADER_RE.search(line):

            return True

    return False


def has_choice_header(lines: list[str]) -> bool:

    for line in lines:

        if CHOICE_HEADER_RE.search(line):

            return True

    return False


def has_intake_header(lines: list[str]) -> bool:

    for line in lines:

        if INTAKE_HEADER_RE.search(line):

            return True

    return False


# ------------------------------------------------------------
# Layout Detection
# ------------------------------------------------------------


def detect_layout(lines: list[str]) -> str:
    """
    Detect CET layout from header text.
    """

    text = "\n".join(lines).lower()

    # -----------------------------
    # M.Tech
    # -----------------------------
    if (
        "vacant course name" in text
        and "non-sponsored" in text
    ):
        return "MTECH"

    # -----------------------------
    # MBA
    # -----------------------------
    if (
        "all india" in text
        and "minority" in text
    ):
        return "MBA"

    # -----------------------------
    # MCA
    # -----------------------------
    if (
        "ms seats" in text
        or "si seats" in text
    ):
        return "MCA"

    return "UNKNOWN"
# ------------------------------------------------------------
# Continuation Page
# ------------------------------------------------------------


def is_continuation_page(
    lines: list[str]
) -> bool:

    institute, _ = detect_institute(lines)

    if institute:

        return False

    return has_course_header(lines)


# ------------------------------------------------------------
# Choice Code Count
# ------------------------------------------------------------


def count_choice_codes(lines: list[str]) -> int:

    count = 0

    for line in lines:

        if CHOICE_CODE_RE.search(line):

            count += 1

    return count

#detect column
def detect_column_map(lines: list[str]) -> ColumnMap:

    cmap = ColumnMap()

    cmap.add("course_name", 0)
    cmap.add("choice_code", 1)
    cmap.add("open", 2)
    cmap.add("sc", 3)
    cmap.add("st", 4)
    cmap.add("vjdt", 5)
    cmap.add("ntb", 6)
    cmap.add("ntc", 7)
    cmap.add("ntd", 8)
    cmap.add("obc", 9)
    cmap.add("sebc", 10)
    cmap.add("pwd", 11)
    cmap.add("orphan", 12)
    cmap.add("il", 13)
    cmap.add("mi", 14)

    return cmap
# ------------------------------------------------------------
# Build PageData
# ------------------------------------------------------------


def build_page_data(
    page_number: int,
    lines: list[str],
) -> PageData:

    university = detect_university(lines)

    institute_code, institute_name = detect_institute(lines)

    layout = detect_layout(lines)

    logger.debug(
        f"Page {page_number}: "
        f"layout={layout}, "
        f"university='{university}', "
        f"institute='{institute_code}'"
    )
    return PageData(
        page_number=page_number,
        university=university or "",
        institute_code=institute_code or "",
        institute_name=institute_name or "",
        layout=layout,
        is_continuation=is_continuation_page(lines),
        choice_count=count_choice_codes(lines),
        column_map=detect_column_map(lines),
    )