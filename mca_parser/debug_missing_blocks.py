import os
import re
import pdfplumber
import parser as p

PDF = 'mca_after_cap4_vacancy_2025_26.pdf'

with pdfplumber.open(PDF) as pdf:
    for i, page in enumerate(pdf.pages, start=1):
        text = page.extract_text() or ''
        normalized_text = p.normalize_page_text(text)
        lines = [ln.rstrip() for ln in normalized_text.split('\n') if ln.strip()]
        starts = p._find_college_starts(lines)
        if not starts:
            continue
        starts.append(len(lines))
        for s_idx in range(len(starts) - 1):
            start = starts[s_idx]
            end = starts[s_idx + 1]
            block_lines = lines[start:end]
            if not block_lines:
                continue
            college_code, college_name = p.extract_college(block_lines)
            if not college_code:
                continue
            choice_entries = p._collect_choice_entries(block_lines)
            if not choice_entries:
                print(f'Page {i}: missing choice entries for {college_code} - {college_name}')
                print('\n'.join(block_lines[:20]))
                print('---')
