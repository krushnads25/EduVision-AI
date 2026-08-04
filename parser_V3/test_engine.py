from engine import ParserEngine

engine = ParserEngine()

result = engine.parse("mtech_vacancy_after_capIV_2025_26.pdf")

engine.export_csv(
    result,
    "output.csv",
)

print()

print("===== PARSE SUMMARY =====")
print(f"Pages                 : {result.pages}")
print(f"Records               : {len(result.records)}")
print(f"Rows reconstructed    : {result.reconstructed_rows}")
print(f"Rows skipped          : {result.skipped_rows}")
print(f"Universities          : {result.universities}")
print(f"Institutes            : {result.institutes}")
print(f"Validation Errors     : {result.validation_errors}")
print(f"Validation Warnings   : {result.validation_warnings}")
print(f"Elapsed               : {result.elapsed_seconds:.2f}s")