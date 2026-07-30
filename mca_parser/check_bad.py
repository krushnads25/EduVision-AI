import parser as p

records = p.parse_pdf("mba_After_cap4_Vacancy_2025_26.pdf", expected_institutes=405)

bad_codes = ["0256916410","0510264710","0130216410","0130264110","0511362810","0619962810"]
for r in records:
    if r.choice_code in bad_codes:
        print(r.choice_code, "|", r.course)