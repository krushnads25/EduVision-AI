import os
import pdfplumber

PDF = "mca_after_cap4_vacancy_2025_26.pdf"
OUT_DIR = "debug_output"

os.makedirs(OUT_DIR, exist_ok=True)
with pdfplumber.open(PDF) as pdf:
    for i in range(1):
        page = pdf.pages[i]
        text = page.extract_text()
        with open(os.path.join(OUT_DIR, f"page_{i+1}.txt"), "w", encoding="utf-8") as f:
            f.write(text or "")
        print(f"Wrote debug_output/page_{i+1}.txt")
