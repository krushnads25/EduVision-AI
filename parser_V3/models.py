from dataclasses import dataclass, field
from typing import List
from columnmap import ColumnMap

@dataclass
class Word:
    text: str
    x0: float
    x1: float
    top: float
    bottom: float


@dataclass
class Line:
    words: List[Word] = field(default_factory=list)

    @property
    def text(self) -> str:
        return " ".join(word.text for word in self.words)



@dataclass
class Row:
    course: str
    choice_code: str
    sponsored_choice_code: str = ""

    regular_numbers: list[int] = field(default_factory=list)
    sponsored_numbers: list[int] = field(default_factory=list)

    raw_lines: list[str] = field(default_factory=list)
    raw_text: str = ""
    line_number: int = 0
@dataclass
class PageData:
    page_number: int

    university: str = ""

    institute_code: str = ""

    institute_name: str = ""

    layout: str = ""

    is_continuation: bool = False

    choice_count: int = 0

    column_map: ColumnMap = field(default_factory=ColumnMap)

    lines: List[Line] = field(default_factory=list)

    rows: List[Row] = field(default_factory=list)

@dataclass
class Record:

    university: str = ""

    college_code: str = ""

    college_name: str = ""

    choice_code: str = ""

    course: str = ""

    intake: int = 0

    cap_seats: int = 0

    si_seats: int = 0

    ms_seats: int = 0

    all_india_seats: int = 0

    minority_seats: int = 0

    institute_seats: int = 0

    hu_open: int = 0
    hu_sc: int = 0
    hu_st: int = 0
    hu_vjdt: int = 0
    hu_ntb: int = 0
    hu_ntc: int = 0
    hu_ntd: int = 0
    hu_obc: int = 0
    hu_sebc: int = 0

    ohu_open: int = 0
    ohu_sc: int = 0
    ohu_st: int = 0
    ohu_vjdt: int = 0
    ohu_ntb: int = 0
    ohu_ntc: int = 0
    ohu_ntd: int = 0
    ohu_obc: int = 0
    ohu_sebc: int = 0

    pwd_total: int = 0

    ews_seats: int = 0

    tfws_choice_code: str = ""

    tfws_seats: int = 0

@dataclass
class ParseResult:
    """
    Result returned by the parser engine.
    """

    records: List[Record] = field(default_factory=list)

    pages: int = 0

    universities: int = 0

    institutes: int = 0

    reconstructed_rows: int = 0

    skipped_rows: int = 0

    validation_errors: int = 0

    validation_warnings: int = 0  

    elapsed_seconds: float = 0.0