"""
extractor.py

Extract words and logical lines from PDF pages.
"""

from __future__ import annotations

from collections import defaultdict
from typing import List

import pdfplumber

from models import Word, Line
from logger import logger

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

# Words whose Y coordinates differ by less than this value are considered
# to be on the same visual line.
LINE_Y_TOLERANCE = 3.0

# Gap (in PDF units) above which a space is inserted when reconstructing
# text from words.
WORD_GAP_THRESHOLD = 2.0


# ----------------------------------------------------------------------
# Page cleanup
# ----------------------------------------------------------------------

def dedupe_page(page: pdfplumber.page.Page):
    """
    Remove duplicated characters produced by bold/overprint PDFs.
    """

    try:
        return page.dedupe_chars()
    except Exception:
        return page


# ----------------------------------------------------------------------
# Word Extraction
# ----------------------------------------------------------------------

def extract_words(page: pdfplumber.page.Page) -> List[Word]:
    """
    Extract words with coordinates.
    """

    page = dedupe_page(page)

    raw_words = page.extract_words(
        keep_blank_chars=False,
        use_text_flow=True,
    )

    words: List[Word] = []

    for w in raw_words:

        text = w["text"].strip()

        if not text:
            continue

        words.append(
            Word(
                text=text,
                x0=float(w["x0"]),
                x1=float(w["x1"]),
                top=float(w["top"]),
                bottom=float(w["bottom"]),
            )
        )

    return words


# ----------------------------------------------------------------------
# Line Reconstruction
# ----------------------------------------------------------------------

def group_words_into_lines(words: List[Word]) -> List[Line]:
    """
    Convert positioned words into logical text lines.
    """

    if not words:
        return []

    # Sort top to bottom, then left to right.
    words = sorted(words, key=lambda w: (round(w.top, 1), w.x0))

    buckets = defaultdict(list)

    for word in words:

        matched_key = None

        for key in buckets.keys():

            if abs(key - word.top) <= LINE_Y_TOLERANCE:
                matched_key = key
                break

        if matched_key is None:
            buckets[word.top].append(word)
        else:
            buckets[matched_key].append(word)

    lines: List[Line] = []

    for y in sorted(buckets.keys()):

        row = sorted(buckets[y], key=lambda w: w.x0)

        lines.append(Line(words=row))

    return lines


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def line_text(line: Line) -> str:
    """
    Convert a Line object into readable text while preserving spaces.
    """

    if not line.words:
        return ""

    output = []

    previous = None

    for word in line.words:

        if previous is None:
            output.append(word.text)

        else:

            gap = word.x0 - previous.x1

            if gap > WORD_GAP_THRESHOLD:
                output.append(" ")

            output.append(word.text)

        previous = word

    return "".join(output).strip()


def lines_as_text(lines: List[Line]) -> List[str]:
    """
    Convert Line objects into plain strings.
    """

    return [line_text(line) for line in lines]


# ----------------------------------------------------------------------
# Complete Extraction Pipeline
# ----------------------------------------------------------------------

def extract_page(page: pdfplumber.page.Page) -> List[Line]:
    """
    Complete extraction pipeline.

    PDF Page
        ↓
    dedupe chars
        ↓
    extract words
        ↓
    group into lines
        ↓
    return Line objects
    """

    words = extract_words(page)

    logger.debug(f"Extracted {len(words)} words")

    lines = group_words_into_lines(words)

    logger.debug(f"Built {len(lines)} lines")

    return lines