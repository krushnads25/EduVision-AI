"""
cleaner.py

Utilities for cleaning and normalizing PDF content before parsing.
"""

from __future__ import annotations

import re
from typing import List

# ----------------------------------------------------------------------
# Regex
# ----------------------------------------------------------------------

MULTISPACE_RE = re.compile(r"\s+")

PAGE_NO_RE = re.compile(r"^\s*\d+\s*$")

FOOTER_PATTERNS = [
    re.compile(r"^State Common Entrance Test Cell", re.I),
    re.compile(r"^Government of Maharashtra", re.I),
    re.compile(r"^Page\s+\d+", re.I),
    re.compile(r"^Printed On", re.I),
    re.compile(r"^Cut[- ]?off", re.I),
]

HEADER_PATTERNS = [
    re.compile(r"Admission Regulating Authority", re.I),
]

# ----------------------------------------------------------------------
# Text Normalization
# ----------------------------------------------------------------------


def normalize_spaces(text: str) -> str:
    """
    Collapse multiple spaces/tabs into one.
    """

    text = text.replace("\t", " ")
    text = MULTISPACE_RE.sub(" ", text)

    return text.strip()


def normalize_quotes(text: str) -> str:

    return (
        text.replace("“", '"')
        .replace("”", '"')
        .replace("’", "'")
        .replace("‘", "'")
    )


def normalize_dashes(text: str) -> str:

    return (
        text.replace("–", "-")
        .replace("—", "-")
        .replace("−", "-")
    )


def normalize_unicode(text: str) -> str:

    text = normalize_quotes(text)

    text = normalize_dashes(text)

    text = normalize_spaces(text)

    return text


# ----------------------------------------------------------------------
# Line Cleaning
# ----------------------------------------------------------------------


def remove_blank_lines(lines: List[str]) -> List[str]:

    return [line for line in lines if line.strip()]


def remove_page_numbers(lines: List[str]) -> List[str]:

    cleaned = []

    for line in lines:

        if PAGE_NO_RE.match(line):

            continue

        cleaned.append(line)

    return cleaned


def remove_headers(lines: List[str]) -> List[str]:

    output = []

    for line in lines:

        skip = False

        for pattern in HEADER_PATTERNS:

            if pattern.search(line):
                skip = True
                break

        if not skip:
            output.append(line)

    return output


def remove_footers(lines: List[str]) -> List[str]:

    output = []

    for line in lines:

        skip = False

        for pattern in FOOTER_PATTERNS:

            if pattern.search(line):
                skip = True
                break

        if not skip:
            output.append(line)

    return output


# ----------------------------------------------------------------------
# Wrapped Text Repair
# ----------------------------------------------------------------------


def merge_wrapped_lines(lines: List[str]) -> List[str]:
    """
    Merge wrapped course names.

    Example

    Artificial Intelligence and
    Machine Learning

    becomes

    Artificial Intelligence and Machine Learning
    """

    merged = []

    i = 0

    while i < len(lines):

        current = lines[i].strip()

        if i + 1 < len(lines):

            nxt = lines[i + 1].strip()

            if (
                current
                and nxt
                and not current.endswith(":")
                and not re.search(r"\d{10}[A-Z]*$", current)
                and not re.match(r"^\d", nxt)
            ):

                current += " " + nxt

                i += 1

        merged.append(current)

        i += 1

    return merged

#overall
def is_empty(line: str) -> bool:
    return not line or not line.strip()
# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------


def clean_lines(lines: List[str]) -> List[str]:
    """
    Complete cleaning pipeline.
    """

    lines = [normalize_unicode(line) for line in lines]

    lines = remove_blank_lines(lines)

    lines = remove_headers(lines)

    lines = remove_footers(lines)

    lines = remove_page_numbers(lines)

    lines = merge_wrapped_lines(lines)

    return lines