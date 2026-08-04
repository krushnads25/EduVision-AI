"""
exporter.py

Export parsed records to CSV.
"""

from __future__ import annotations

import csv
from pathlib import Path
from dataclasses import fields

from logger import logger
from models import Record


class Exporter:

    def __init__(self):

        pass

    # ---------------------------------------------------------

    def headers(self):

        """
        Return Record field names in declared order.
        """

        return [f.name for f in fields(Record)]

    # ---------------------------------------------------------

    def row(self, record: Record):
        """
        Convert a Record into a CSV row.

        None values are written as empty strings.
        """

        values = []

        for field in self.headers():

            value = getattr(record, field)

            if value is None:
                value = ""

            values.append(value)

        return values
    # ---------------------------------------------------------

    def to_csv(
        self,
        records,
        output_file,
    ):

        output_file = Path(output_file)

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        logger.info(
            f"Writing CSV -> {output_file}"
        )

        with open(
            output_file,
            "w",
            newline="",
            encoding="utf-8",
        ) as fp:

            writer = csv.writer(fp)

            writer.writerow(self.headers())

            for record in records:

                writer.writerow(
                    self.row(record)
                )

        logger.info(
            f"CSV written ({len(records)} rows)"
        )