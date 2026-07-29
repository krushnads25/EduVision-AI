import re
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple

import pandas as pd
import pdfplumber


PDF = "mca_after_cap4_vacancy_2025_26.pdf"
OUTPUT_CSV = os.path.join("output", "mca_after_cap4_vacancy_2025_26.csv")
EXPECTED_INSTITUTES = 190


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


def _collect_choice_entries(block_lines: List[str]) -> List[Tuple[int, List[str]]]:
    # Returns list of (index_in_block, lines_for_choice_entry)
    entries = []
    n = len(block_lines)
    for i, line in enumerate(block_lines):
        if not _is_choice_code_line(line):
            continue
        j = i + 1
        chunk = [line.strip()]
        while j < n and not _is_choice_code_line(block_lines[j]):
            # stop chunk if new college header encountered
            if re.match(r"^\s*\d{3,}\s*-\s*.+", block_lines[j]):
                break
            chunk.append(block_lines[j].strip())
            j += 1
        entries.append((i, chunk))
    return entries


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
            result["course"] = " ".join(tokens[1:intake_pos])
            # remaining numeric tokens are seats
            seats_tokens = tokens[intake_pos + 1: intake_pos + 1 + 10]
            seats = [ _to_int(t) for t in seats_tokens if re.search(r"\d+", t) ]
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


def parse_page(page_text: str, current_university: Optional[str], page_number: int) -> Tuple[List[Record], Optional[str], int]:
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
            continue
        institute_count += 1
        print(f"Page {page_number}")
        print(f"Institute: {college_name}")
        cap_seats = extract_cap_seats(block_text)

        choice_entries = _collect_choice_entries(block_lines)
        if not choice_entries:
            continue

        for _, chunk in choice_entries:
            choice = extract_choice(chunk)
            if not choice.get("choice_code"):
                continue
            print(f"Choice Code: {choice.get('choice_code')}")

            rec = Record()
            rec.university = uni or ""
            rec.college_code = college_code
            rec.college_name = college_name
            rec.choice_code = choice.get("choice_code", "")
            rec.course = choice.get("course", "")
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


def parse_pdf(pdf_path: str) -> List[Record]:
    all_records: List[Record] = []
    page_counts = {}
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        current_university: Optional[str] = None
        for i, page in enumerate(pdf.pages, start=1):
            print(f"Parsing page {i}/{total}")
            text = page.extract_text()
            if not text or not text.strip():
                continue
            records, current_university, institute_count = parse_page(text, current_university, i)
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

    print(f"Expected Institutes : {EXPECTED_INSTITUTES}")
    print(f"Parsed Institutes : {len(unique)}")
    print(f"Missing : {EXPECTED_INSTITUTES - len(unique)}")
    print(f"Unique Universities : {len({r.university for r in unique})}")

    if len(unique) != EXPECTED_INSTITUTES:
        for page_num, count in sorted(page_counts.items()):
            if count < 1:
                print(f"Page {page_num}: fewer institutes detected ({count})")

    return unique


def write_csv(records: List[Record], out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    rows = [asdict(r) for r in records]
    df = pd.DataFrame(rows)
    df.to_csv(out_path, index=False)


def main() -> None:
    print("Starting PDF parse...")
    records = parse_pdf(PDF)
    print(f"Parsed {len(records)} records")
    if len(records) != EXPECTED_INSTITUTES:
        raise SystemExit(f"Expected {EXPECTED_INSTITUTES} institutes but parsed {len(records)}")
    write_csv(records, OUTPUT_CSV)
    print("Wrote:", OUTPUT_CSV)


if __name__ == "__main__":
    main()