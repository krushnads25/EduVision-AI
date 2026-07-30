import argparse
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import pdfplumber


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


def _to_int(value: Optional[str]) -> int:
    if value is None:
        return 0
    s = str(value).strip()
    if s == "":
        return 0
    m = re.search(r"(\d+)", s.replace(",", ""))
    return int(m.group(1)) if m else 0


def is_footer_line(line: str) -> bool:
    lower = line.lower().strip()
    if not lower:
        return False
    return any(token in lower for token in ["state cet cell", "page ", "important note", "f:only for female", "only for female", "published on"])


def normalize_page_text(page_text: str) -> str:
    lines = []
    for raw_line in page_text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if is_footer_line(stripped):
            continue
        lines.append(stripped)
    return "\n".join(lines)


def extract_university(lines: List[str], current_university: Optional[str]) -> Optional[str]:
    invalid_markers = [
        "cap seats",
        "choice code",
        "course name",
        "category",
        "pwd",
        "economically weaker section",
        "tfws",
        "government",
        "un-aided",
        "autonomous",
        "university department",
        "home university",
        "only for female",
        "state cet cell",
        "page ",
    ]

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r"^\d{4,5}\s*-", stripped):
            continue
        if ":" in stripped:
            continue
        lower = stripped.lower()
        if "university" not in lower:
            continue
        if any(marker in lower for marker in invalid_markers):
            continue
        if re.search(r"\d", stripped):
            continue
        if len(stripped.split()) < 2:
            continue
        return stripped

    return current_university


def _find_college_starts(lines: List[str]) -> List[int]:
    starts = []
    for idx, line in enumerate(lines):
        if re.match(r"^\s*\d{4,5}\s*-\s*.+", line):
            starts.append(idx)
    return starts


def extract_college(block_lines: List[str]) -> Tuple[str, str]:
    for line in block_lines:
        m = re.match(r"^\s*(\d{4,5})\s*-\s*(.+)$", line)
        if m:
            return m.group(1).strip(), m.group(2).strip()
    return "", ""


def extract_cap_seats(block_text: str) -> int:
    m = re.search(r"CAP\s*Seats[:\s]*([0-9,]+)", block_text, re.IGNORECASE)
    if m:
        return _to_int(m.group(1))
    # alternative phrases
    m = re.search(r"CAP[:\s]*([0-9,]+)", block_text, re.IGNORECASE)
    if m:
        return _to_int(m.group(1))
    return 0


def _is_choice_code_line(line: str) -> bool:
    return bool(re.match(r"^\s*\d{9,}[A-Za-z]*\b", line))


def _extract_choice_code(line: str) -> str:
    match = re.match(r"^\s*(\d{9,}[A-Za-z]*)", line)
    return match.group(1).strip() if match else ""


# --- FIX 1: table-marker detection, used to stop the course-name fallback ---
# from swallowing the Category/HU/OHU/PWD/TFWS seat-matrix lines that follow
# a choice-code entry.
_TABLE_MARKER_RE = re.compile(
    r"^(category\b|hu\b|ohu\b|pwd\b|state level\b|economically weaker section\b|tfws\b)",
    re.IGNORECASE,
)


def _is_table_marker_line(line: str) -> bool:
    return bool(_TABLE_MARKER_RE.match(line.strip()))


# --- FIX 2: recover course-name fragments that pdfplumber prints on the line(s)
# immediately BEFORE the choice-code line (instead of after it), which happens
# when a multi-word course name wraps and the choice-code + seat numbers get
# interleaved in between the wrapped fragments. We walk backward from each
# choice-code line, grabbing any orphan lines not already consumed by the
# previous entry and not matching a header/college-start pattern.
def _collect_choice_entries(block_lines: List[str]) -> List[Tuple[int, List[str], str]]:
    # Returns list of (index_in_block, lines_for_choice_entry, prefix_text)
    entries = []
    n = len(block_lines)
    consumed_until = 0
    header_markers = ("choice code", "course name")

    for i, line in enumerate(block_lines):
        if not _is_choice_code_line(line):
            continue

        # Walk backward to recover an orphaned course-name prefix fragment,
        # without stepping into lines already consumed by a previous entry,
        # a college header line, another choice-code line, or the table header.
        prefix_parts: List[str] = []
        k = i - 1
        while k >= consumed_until:
            candidate = block_lines[k].strip()
            if not candidate:
                break
            lower = candidate.lower()
            if any(marker in lower for marker in header_markers):
                break
            if re.match(r"^\s*\d{4,5}\s*-\s*.+", candidate):
                break
            if _is_choice_code_line(candidate):
                break
            if _is_table_marker_line(candidate):
                break
            prefix_parts.insert(0, candidate)
            k -= 1
        prefix_text = " ".join(prefix_parts).strip()

        j = i + 1
        chunk = [line.strip()]
        while j < n and not _is_choice_code_line(block_lines[j]):
            # stop chunk if new college header encountered
            if re.match(r"^\s*\d{3,}\s*-\s*.+", block_lines[j]):
                break
            chunk.append(block_lines[j].strip())
            j += 1
        consumed_until = j
        entries.append((i, chunk, prefix_text))
    return entries


def infer_course(choice_code: str, course_name: Optional[str], fallback_text: Optional[str] = "") -> str:
    if course_name and str(course_name).strip():
        return str(course_name).strip()

    combined = " ".join(part for part in [choice_code or "", fallback_text or ""] if part)
    if not combined:
        return ""

    match = re.search(r"\b(?:Master|Bachelor|MBA|MTech|M\.Tech|BTech|B\.Tech|MSc|BSc|Pharm|Management|Technology|Administration)\b", combined, re.IGNORECASE)
    if match:
        return re.sub(r"\s+", " ", combined[match.start():match.end()]).strip()

    return ""


def extract_choice(chunk_lines: List[str]) -> Dict:
    # chunk_lines starts with choice_code then course name lines then intake and seats
    result = {
        "choice_code": "",
        "course": "",
        "intake": 0,
        "si_seats": 0,
        "ms_seats": 0,
        "all_india_seats": 0,
        "minority_seats": 0,
        "institute_seats": 0,
    }
    if not chunk_lines:
        return result

    joined_lines = []
    for line in chunk_lines:
        text = str(line).strip()
        if not text:
            continue
        # Never merge a table-marker line (Category/HU/OHU/PWD/TFWS/EWS) into
        # the preceding text line, even if the preceding line ends in a letter.
        # Without this guard, a wrapped course-name fragment like "Systems
        # Management" gets glued straight onto "Category OPEN SC ST ..." and
        # the whole seat-matrix table ends up inside the course name.
        if (
            joined_lines
            and not _is_table_marker_line(text)
            and re.search(r"[A-Za-z]$", joined_lines[-1])
            and re.search(r"^[A-Za-z]", text)
        ):
            joined_lines[-1] = f"{joined_lines[-1]} {text}"
        else:
            joined_lines.append(text)
    chunk_lines = joined_lines
    if not chunk_lines:
        return result

    line0 = chunk_lines[0]
    # If the first line contains the choice code and other tokens (inline), split tokens
    tokens = line0.split()
    choice_code = _extract_choice_code(line0)
    if tokens and choice_code:
        result["choice_code"] = choice_code
        # look for first numeric token after choice code -> intake
        intake_pos = None
        for i_tok in range(1, len(tokens)):
            if re.match(r"^\d{1,3}$", tokens[i_tok]):
                intake_pos = i_tok
                break
        if intake_pos is not None:
            result["intake"] = _to_int(tokens[intake_pos])
            course_tokens = tokens[1:intake_pos]
            if not course_tokens and len(chunk_lines) > 1:
                # FIX 1 applied here: stop at the first table-marker line
                # (Category / HU / OHU / PWD / TFWS / Economically Weaker Section)
                # instead of grabbing every remaining line in the chunk.
                trailing = []
                for part in chunk_lines[1:]:
                    if _is_table_marker_line(part):
                        break
                    if str(part).strip():
                        trailing.append(part)
                course_tokens = trailing
            result["course"] = re.sub(r"\s+", " ", " ".join(course_tokens)).strip()
            # remaining numeric tokens are seats
            seats_tokens = tokens[intake_pos + 1: intake_pos + 1 + 10]
            seats = [_to_int(t) for t in seats_tokens if re.search(r"\d+", t)]
        else:
            # no numeric found on first line, take remainder as course and try subsequent lines for intake
            result["course"] = " ".join(tokens[1:])
            seats = []
            intake_pos = None
            for idx in range(1, len(chunk_lines)):
                if re.match(r"^\s*\d+\s*$", chunk_lines[idx]):
                    result["intake"] = _to_int(chunk_lines[idx])
                    intake_pos = idx
                    break
            if intake_pos is not None:
                for k in range(intake_pos + 1, min(len(chunk_lines), intake_pos + 6)):
                    seats.extend([_to_int(tok) for tok in re.findall(r"\d+", chunk_lines[k])])
            else:
                # try to extract any numeric tokens in subsequent lines
                for idx in range(1, len(chunk_lines)):
                    seats.extend([_to_int(tok) for tok in re.findall(r"\d+", chunk_lines[idx])])
    else:
        # fallback: previous logic for multi-line chunks
        result["choice_code"] = chunk_lines[0].strip()
        intake_idx = None
        for idx in range(1, len(chunk_lines)):
            if re.match(r"^\s*\d+\s*$", chunk_lines[idx]):
                intake_idx = idx
                break
        if intake_idx is None:
            for idx in range(1, len(chunk_lines)):
                if re.search(r"\b\d{1,3}\b", chunk_lines[idx]):
                    intake_idx = idx
                    break
        if intake_idx is None:
            result["course"] = " ".join(chunk_lines[1:]).strip()
            seats = []
        else:
            course_name = " ".join(chunk_lines[1:intake_idx]).strip()
            result["course"] = re.sub(r"\s+", " ", course_name)
            result["intake"] = _to_int(chunk_lines[intake_idx])
            seats = []
            for k in range(intake_idx + 1, min(len(chunk_lines), intake_idx + 6)):
                seats.extend([_to_int(tok) for tok in re.findall(r"\d+", chunk_lines[k])])
    # assign in order
    if len(seats) >= 1:
        result["si_seats"] = seats[0]
    if len(seats) >= 2:
        result["ms_seats"] = seats[1]
    if len(seats) >= 3:
        result["all_india_seats"] = seats[2]
    if len(seats) >= 4:
        result["minority_seats"] = seats[3]
    if len(seats) >= 5:
        result["institute_seats"] = seats[4]

    return result


def _extract_category_block(block_text: str, heading_pattern: str) -> Dict[str, int]:
    # Not used; retained for compatibility
    cats = ["OPEN", "SC", "ST", "VJDT", "NTB", "NTC", "NTD", "OBC", "SEBC"]
    return {c.lower(): 0 for c in cats}


def extract_category(block_text: str) -> Tuple[Dict[str, int], Dict[str, int]]:
    cats = ["OPEN", "SC", "ST", "VJDT", "NTB", "NTC", "NTD", "OBC", "SEBC"]
    hu_out = {c.lower(): 0 for c in cats}
    ohu_out = {c.lower(): 0 for c in cats}

    # split into lines and search for HU / OHU lines
    for line in block_text.split("\n"):
        line_stripped = line.strip()
        if not line_stripped:
            continue
        # HU can appear as 'HU 2 1 0 ...' or 'State Level ...'
        if re.match(r"^(HU|State Level|STATE LEVEL)\b", line_stripped, re.IGNORECASE):
            nums = re.findall(r"\d+", line_stripped)
            # map first 9 numbers to categories
            for i, cat in enumerate(cats):
                if i < len(nums):
                    hu_out[cat.lower()] = _to_int(nums[i])
            continue
        if re.match(r"^OHU\b", line_stripped, re.IGNORECASE):
            nums = re.findall(r"\d+", line_stripped)
            for i, cat in enumerate(cats):
                if i < len(nums):
                    ohu_out[cat.lower()] = _to_int(nums[i])
            continue

    return hu_out, ohu_out


def extract_pwd(block_text: str) -> int:
    m = re.search(r"\bPWD\b[^0-9\n]*([0-9,]+)", block_text, re.IGNORECASE)
    if m:
        return _to_int(m.group(1))
    # sometimes 'PWD Total X' or 'PWD : X'
    m = re.search(r"PWD[:\s]*([0-9,]+)", block_text, re.IGNORECASE)
    if m:
        return _to_int(m.group(1))
    return 0


def extract_ews(block_text: str) -> int:
    m = re.search(r"Economically\s+Weaker\s+Section.*?:\s*([0-9,]+)", block_text, re.IGNORECASE)
    if m:
        return _to_int(m.group(1))
    m = re.search(r"EWS\s*Seats[:\s]*([0-9,]+)", block_text, re.IGNORECASE)
    if m:
        return _to_int(m.group(1))
    return 0


def extract_tfws(block_text: str) -> Tuple[str, int]:
    m = re.search(r"TFWS\s*Choice\s*Code\s*[:\s]*([0-9]+).*?Seats\s*[:\s]*([0-9,]+)", block_text, re.IGNORECASE)
    if m:
        return m.group(1).strip(), _to_int(m.group(2))
    # alternate: 'TFWS Choice Code : XXXXX Seats: Y' with variations
    m = re.search(r"TFWS[:\s]*([0-9]+)\s*Seats[:\s]*([0-9,]+)", block_text, re.IGNORECASE)
    if m:
        return m.group(1).strip(), _to_int(m.group(2))
    return "", 0



COLLEGE_RE = re.compile(r"^\s*(\d{4,5})\s*-\s*(.+?)\s*$")
CHOICE_CODE_RE = re.compile(r"^\s*(\d{9}[A-Za-z]{0,2})\b", re.IGNORECASE)

FOOTER_PATTERNS = [
    r"State CET Cell",
    r"Published On",
    r"Page\s+\d+",
    r"Only for Female",
    r"Important Note",
    r"Government of Maharashtra",
]

def extract_clean_text(page):
    try:
        page = page.dedupe_chars(tolerance=1)
    except Exception:
        pass
    try:
        words = page.extract_words(x_tolerance=2, y_tolerance=2, keep_blank_chars=False, use_text_flow=True)
        if words:
            rows = {}
            for w in words:
                rows.setdefault(round(w["top"],1), []).append(w)
            return "\n".join(" ".join(x["text"] for x in sorted(v,key=lambda z:z["x0"])) for _,v in sorted(rows.items()))
    except Exception:
        pass
    return page.extract_text() or ""


def parse_page(
    page_text: str,
    current_university: Optional[str],
    page_number: int,
    current_college_code: Optional[str] = None,
    current_college_name: Optional[str] = None,
) -> Tuple[List[Record], Optional[str], int]:
    records: List[Record] = []
    if not page_text:
        return records, current_university, 0

    normalized_text = normalize_page_text(page_text)
    lines = [ln.rstrip() for ln in normalized_text.split("\n") if ln.strip()]

    uni = extract_university(lines, current_university)
    if uni:
        print(f"Page {page_number}")
        print(f"University: {uni}")

    starts = _find_college_starts(lines)
    if not starts:
        if current_college_code and current_college_name:
            block_lines = lines
            block_text = "\n".join(block_lines)
            choice_entries = _collect_choice_entries(block_lines)
            if choice_entries:
                for _, chunk, prefix_text in choice_entries:
                    choice = extract_choice(chunk)
                    if not choice.get("choice_code"):
                        continue
                    if prefix_text:
                        choice["course"] = (prefix_text + " " + choice.get("course", "")).strip()
                    rec = Record()
                    rec.university = uni or current_university or ""
                    rec.college_code = current_college_code
                    rec.college_name = current_college_name
                    rec.choice_code = choice.get("choice_code", "")
                    rec.course = infer_course(
                        choice.get("choice_code", ""),
                        choice.get("course", ""),
                        block_text,
                    )
                    rec.intake = choice.get("intake", 0)
                    rec.cap_seats = extract_cap_seats(block_text)
                    rec.si_seats = choice.get("si_seats", 0)
                    rec.ms_seats = choice.get("ms_seats", 0)
                    rec.all_india_seats = choice.get("all_india_seats", 0)
                    rec.minority_seats = choice.get("minority_seats", 0)
                    rec.institute_seats = choice.get("institute_seats", 0)

                    hu, ohu = extract_category(block_text)
                    rec.hu_open = hu.get("open", 0)
                    rec.hu_sc = hu.get("sc", 0)
                    rec.hu_st = hu.get("st", 0)
                    rec.hu_vjdt = hu.get("vjdt", 0)
                    rec.hu_ntb = hu.get("ntb", 0)
                    rec.hu_ntc = hu.get("ntc", 0)
                    rec.hu_ntd = hu.get("ntd", 0)
                    rec.hu_obc = hu.get("obc", 0)
                    rec.hu_sebc = hu.get("sebc", 0)

                    rec.ohu_open = ohu.get("open", 0)
                    rec.ohu_sc = ohu.get("sc", 0)
                    rec.ohu_st = ohu.get("st", 0)
                    rec.ohu_vjdt = ohu.get("vjdt", 0)
                    rec.ohu_ntb = ohu.get("ntb", 0)
                    rec.ohu_ntc = ohu.get("ntc", 0)
                    rec.ohu_ntd = ohu.get("ntd", 0)
                    rec.ohu_obc = ohu.get("obc", 0)
                    rec.ohu_sebc = ohu.get("sebc", 0)

                    rec.pwd_total = extract_pwd(block_text)
                    rec.ews_seats = extract_ews(block_text)
                    tfws_code, tfws_seats = extract_tfws(block_text)
                    rec.tfws_choice_code = tfws_code
                    rec.tfws_seats = tfws_seats

                    records.append(rec)
            return records, uni, 1
        return records, uni, 0

    starts.append(len(lines))
    institute_count = 0
    for s_idx in range(len(starts) - 1):
        start = starts[s_idx]
        end = starts[s_idx + 1]
        block_lines = lines[start:end]
        if not block_lines:
            continue
        block_text = "\n".join(block_lines)

        college_code, college_name = extract_college(block_lines)
        if not college_code:
            college_code, college_name = current_college_code, current_college_name
            if not college_code:
                continue
        else:
            current_college_code = college_code
            current_college_name = college_name
        institute_count += 1
        print(f"Page {page_number}")
        print(f"Institute: {college_name}")
        cap_seats = extract_cap_seats(block_text)

        choice_entries = _collect_choice_entries(block_lines)
        if not choice_entries:
            continue

        for _, chunk, prefix_text in choice_entries:
            choice = extract_choice(chunk)
            if not choice.get("choice_code"):
                continue
            if prefix_text:
                choice["course"] = (prefix_text + " " + choice.get("course", "")).strip()
            print(f"Choice Code: {choice.get('choice_code')}")

            rec = Record()
            rec.university = uni or ""
            rec.college_code = college_code
            rec.college_name = college_name
            rec.choice_code = choice.get("choice_code", "")
            rec.course = infer_course(
                choice.get("choice_code", ""),
                choice.get("course", ""),
                block_text,
            )
            rec.intake = choice.get("intake", 0)
            rec.cap_seats = cap_seats
            rec.si_seats = choice.get("si_seats", 0)
            rec.ms_seats = choice.get("ms_seats", 0)
            rec.all_india_seats = choice.get("all_india_seats", 0)
            rec.minority_seats = choice.get("minority_seats", 0)
            rec.institute_seats = choice.get("institute_seats", 0)

            window_text = block_text
            hu, ohu = extract_category(window_text)
            rec.hu_open = hu.get("open", 0)
            rec.hu_sc = hu.get("sc", 0)
            rec.hu_st = hu.get("st", 0)
            rec.hu_vjdt = hu.get("vjdt", 0)
            rec.hu_ntb = hu.get("ntb", 0)
            rec.hu_ntc = hu.get("ntc", 0)
            rec.hu_ntd = hu.get("ntd", 0)
            rec.hu_obc = hu.get("obc", 0)
            rec.hu_sebc = hu.get("sebc", 0)

            rec.ohu_open = ohu.get("open", 0)
            rec.ohu_sc = ohu.get("sc", 0)
            rec.ohu_st = ohu.get("st", 0)
            rec.ohu_vjdt = ohu.get("vjdt", 0)
            rec.ohu_ntb = ohu.get("ntb", 0)
            rec.ohu_ntc = ohu.get("ntc", 0)
            rec.ohu_ntd = ohu.get("ntd", 0)
            rec.ohu_obc = ohu.get("obc", 0)
            rec.ohu_sebc = ohu.get("sebc", 0)

            rec.pwd_total = extract_pwd(window_text)
            rec.ews_seats = extract_ews(window_text)
            tfws_code, tfws_seats = extract_tfws(window_text)
            rec.tfws_choice_code = tfws_code
            rec.tfws_seats = tfws_seats

            records.append(rec)

    return records, uni, institute_count


def parse_pdf(pdf_path: str, expected_institutes: Optional[int] = None) -> List[Record]:
    all_records: List[Record] = []
    page_counts = {}
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        current_university: Optional[str] = None
        current_college_code: Optional[str] = None
        current_college_name: Optional[str] = None
        for i, page in enumerate(pdf.pages, start=1):
            print(f"Parsing page {i}/{total}")
            text = extract_clean_text(page)
            if not text or not text.strip():
                continue
            records, current_university, institute_count = parse_page(
                text,
                current_university,
                i,
                current_college_code=current_college_code,
                current_college_name=current_college_name,
            )
            if records:
                current_college_code = records[-1].college_code or current_college_code
                current_college_name = records[-1].college_name or current_college_name
            page_counts[i] = institute_count
            all_records.extend(records)

    seen = set()
    unique: List[Record] = []
    for r in all_records:
        key = (r.college_code, r.choice_code, r.course)
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)

    print(f"Parsed Institutes : {len(unique)}")
    if expected_institutes is not None:
        print(f"Expected Institutes : {expected_institutes}")
        print(f"Missing : {expected_institutes - len(unique)}")
    print(f"Unique Universities : {len({r.university for r in unique})}")

    if expected_institutes is not None and len(unique) != expected_institutes:
        for page_num, count in sorted(page_counts.items()):
            if count < 1:
                print(f"Page {page_num}: fewer institutes detected ({count})")

    missing_pages = [page_num for page_num, count in sorted(page_counts.items()) if count < 1]
    if missing_pages:
        print("Pages without institute detection:", ", ".join(str(page) for page in missing_pages))

    return unique


def write_csv(records: List[Record], out_path: str) -> None:
    out_path_obj = Path(out_path)
    out_path_obj.parent.mkdir(parents=True, exist_ok=True)
    rows = [asdict(r) for r in records]
    df = pd.DataFrame(rows)
    df.to_csv(out_path_obj, index=False)


def build_output_path(pdf_path: str, output_dir: str = "output") -> str:
    pdf_name = Path(pdf_path).stem
    output_path = Path(output_dir) / f"{pdf_name}.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path.as_posix()


def validate_dataframe(df: pd.DataFrame, expected_columns: Optional[List[str]] = None) -> Dict[str, List[str]]:
    report: Dict[str, List[str]] = {
        "missing_columns": [],
        "empty_rows": [],
    }

    expected_columns = expected_columns or [
        "college_code",
        "college_name",
        "choice_code",
        "course",
    ]

    missing = [col for col in expected_columns if col not in df.columns]
    report["missing_columns"] = missing

    for idx, row in df.iterrows():
        values = [str(row.get(col, "")).strip() for col in expected_columns]
        if any(value == "" for value in values):
            report["empty_rows"].append(str(idx))

    return report


def parse_file(pdf_path: str, output_path: Optional[str] = None, expected_institutes: Optional[int] = None) -> Dict[str, object]:
    records = parse_pdf(pdf_path, expected_institutes=expected_institutes)
    destination = output_path or build_output_path(pdf_path)
    write_csv(records, destination)

    df = pd.read_csv(destination)
    validation = validate_dataframe(df)
    return {
        "records": records,
        "output_path": destination,
        "validation": validation,
    }


def parse_many(pdf_paths: List[str], output_dir: str = "output") -> List[Dict[str, object]]:
    results = []
    for pdf_path in pdf_paths:
        output_path = build_output_path(pdf_path, output_dir=output_dir)
        results.append(parse_file(pdf_path, output_path=output_path))
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Parse a CET vacancy PDF into a CSV")
    parser.add_argument("pdf_path", nargs="?", help="Path to the CET vacancy PDF")
    parser.add_argument("-o", "--output", dest="output", help="Output CSV path")
    parser.add_argument("--output-dir", default="output", help="Directory for generated CSV files")
    parser.add_argument("--expected-institutes", type=int, default=None, help="Optional expected institute count")
    parser.add_argument("--bulk", action="store_true", help="Parse all PDFs in the current directory")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.bulk:
        pdf_paths = sorted(Path.cwd().glob("*.pdf"))
        if not pdf_paths:
            raise SystemExit("No PDFs found in current directory")
        results = parse_many([str(path) for path in pdf_paths], output_dir=args.output_dir)
        for result in results:
            print("Wrote:", result["output_path"])
            print("Validation:", result["validation"])
        return

    pdf_path = args.pdf_path
    if not pdf_path:
        candidates = sorted(Path.cwd().glob("*.pdf"))
        if not candidates:
            raise SystemExit("Please provide a PDF path")
        if len(candidates) > 1:
            raise SystemExit(f"Multiple PDFs found in {Path.cwd()}: {', '.join(str(path.name) for path in candidates)}")
        pdf_path = str(candidates[0])

    print("Starting PDF parse...")
    result = parse_file(pdf_path, output_path=args.output, expected_institutes=args.expected_institutes)
    print(f"Parsed {len(result['records'])} records")
    print("Wrote:", result["output_path"])
    print("Validation:", result["validation"])


if __name__ == "__main__":
    main()