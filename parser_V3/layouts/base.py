"""
layouts/base.py

Base class for all layout parsers.

Each layout parser receives a generic Row and converts it into a Record.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from models import Record, Row


class BaseLayoutParser(ABC):
    """
    Base class for all CET layout parsers.
    """

    name = "BASE"

    @abstractmethod
    def parse(
        self,
        row: Row,
        university: str,
        college_code: str,
        college_name: str,
    ) -> Record:
        """
        Convert one Row into one Record.
        """
        raise NotImplementedError

    # ----------------------------------------------------------

    def build_record(
        self,
        row: Row,
        university: str,
        college_code: str,
        college_name: str,
    ) -> Record:
        """
        Populate fields common to every layout.
        """

        r = Record()

        r.university = university

        r.college_code = str(college_code).zfill(5)

        r.college_name = college_name

        r.choice_code = str(row.choice_code).zfill(10)

        r.course = row.course

        return r
    #-----------------------------------------------
    def column(
        self,
        row,
        page,
        name,
        default=0,
    ):
        """
        Return a value using the detected column map.
        """

        values = row.regular_numbers

        # Sponsored columns come from sponsored_numbers
        if name.lower() in {
            "tfws",
            "il",
            "mi",
            "sponsored",
        }:
            values = row.sponsored_numbers

        return page.column_map.value(
            values,
            name,
            default,
        )
    #---------------------------------------------------------
    def value(
        self,
        values,
        index,
        default=0,
    ):
        """
        Safe positional lookup.
        """

        if values is None:
            return default

        if index >= len(values):
            return default

        return values[index]

    # ----------------------------------------------------------

    @staticmethod
    def text(value) -> str:

        if value is None:
            return ""

        return str(value).strip()

    # ----------------------------------------------------------

    @staticmethod
    def safe_choice(code: str) -> str:

        if not code:
            return ""

        return code.strip().upper()