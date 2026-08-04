"""
header_normalizer.py

Normalize CET/DTE table headers into canonical names.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------
# Canonical header aliases
# ---------------------------------------------------------

HEADER_ALIASES = {

    # Choice / Course
    "choice code": "choice code",
    "choice": "choice code",
    "course": "course name",
    "course name": "course name",

    # Intake
    "intake": "intake",
    "sanctioned intake": "intake",

    # HU
    "hu open": "hu open",
    "home university open": "hu open",

    "hu sc": "hu sc",
    "home university sc": "hu sc",

    "hu st": "hu st",
    "home university st": "hu st",

    "hu vj": "hu vjdt",
    "hu vjdt": "hu vjdt",

    "hu nt1": "hu ntb",
    "hu nt2": "hu ntc",
    "hu nt3": "hu ntd",

    "hu obc": "hu obc",
    "hu sebc": "hu sebc",

    # OHU
    "ohu open": "ohu open",
    "other than home university open": "ohu open",

    "ohu sc": "ohu sc",
    "ohu st": "ohu st",

    "ohu vj": "ohu vjdt",
    "ohu vjdt": "ohu vjdt",

    "ohu nt1": "ohu ntb",
    "ohu nt2": "ohu ntc",
    "ohu nt3": "ohu ntd",

    "ohu obc": "ohu obc",
    "ohu sebc": "ohu sebc",

    # Others
    "pwd": "pwd",
    "persons with disability": "pwd",

    "ews": "ews",

    "tfws": "tfws",

    "all india": "all india",

    "minority": "minority",

    "ms seats": "ms seats",

    "si seats": "si seats",
}


# ---------------------------------------------------------
# Cleaning
# ---------------------------------------------------------

MULTISPACE_RE = re.compile(r"\s+")


def clean_header(text: str) -> str:
    """
    Normalize punctuation and spacing.
    """

    text = text.lower()

    text = text.replace("-", " ")

    text = text.replace("_", " ")

    text = text.replace("(", " ")

    text = text.replace(")", " ")

    text = text.replace("/", " ")

    text = MULTISPACE_RE.sub(" ", text)

    return text.strip()


# ---------------------------------------------------------
# Public API
# ---------------------------------------------------------

def normalize_header(text: str) -> str:

    cleaned = clean_header(text)

    return HEADER_ALIASES.get(cleaned, cleaned)