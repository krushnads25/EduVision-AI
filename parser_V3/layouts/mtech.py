"""
layouts/mtech.py

Parser for M.Tech vacancy PDFs.
"""

from __future__ import annotations

from models import Record
from models import Row
from models import PageData

from layouts.base import BaseLayoutParser


class MTechLayoutParser(BaseLayoutParser):

    name = "MTECH"

    def parse(
        self,
        row: Row,
        page: PageData,
    ) -> Record:

        r = self.build_record(
            row,
            page.university,
            page.institute_code,
            page.institute_name,
        )

        #
        # Basic fields
        #

        r.intake = self.column(
            row,
            page,
            "intake",
        )

        #
        # Reservation Columns
        #
        regular = row.regular_numbers
        sponsored = row.sponsored_numbers

        #
        # Regular seat columns
        #

        r.hu_open = self.value(regular, 0)
        r.hu_sc = self.value(regular, 1)
        r.hu_st = self.value(regular, 2)
        r.hu_vjdt = self.value(regular, 3)
        r.hu_ntb = self.value(regular, 4)
        r.hu_ntc = self.value(regular, 5)
        r.hu_ntd = self.value(regular, 6)
        r.hu_obc = self.value(regular, 7)
        r.hu_sebc = self.value(regular, 8)

        r.ohu_open = self.value(regular, 9)
        r.ohu_sc = self.value(regular, 10)
        r.ohu_st = self.value(regular, 11)
        r.ohu_vjdt = self.value(regular, 12)
        r.ohu_ntb = self.value(regular, 13)
        r.ohu_ntc = self.value(regular, 14)
        r.ohu_ntd = self.value(regular, 15)
        r.ohu_obc = self.value(regular, 16)
        r.ohu_sebc = self.value(regular, 17)

        r.pwd_total = self.value(regular, 18)
        r.ews_seats = self.value(regular, 19)

        #
        # Sponsored / Institute Level
        #

        r.tfws_choice_code = (
            str(row.sponsored_choice_code).zfill(11)
            if row.sponsored_choice_code
            else ""
        )

        r.tfws_seats = self.value(sponsored, 0)

        if row.choice_code == "0100239210":
            print("Regular :", regular)
            print("Sponsored :", sponsored)
        return r