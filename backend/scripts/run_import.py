from argparse import ArgumentParser
from pathlib import Path

from app.database.session import SessionLocal
from app.importers.engine import ImportEngine


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description="Run an EduVision import job")
    parser.add_argument("entity", choices=["college", "course", "candidate"], help="Entity type to import")
    parser.add_argument("file", help="Input CSV or Excel file path")
    parser.add_argument("--sheet", default=None, help="Excel sheet name or index")
    return parser


def main() -> None:
    parser = parse_args()
    args = parser.parse_args()
    file_path = Path(args.file)
    if not file_path.exists():
        raise SystemExit(f"File not found: {file_path}")

    with SessionLocal() as db:
        engine = ImportEngine(db)
        report = engine.run(args.entity, str(file_path), sheet_name=args.sheet)

        print("Import report")
        for entity, summary in report.summaries.items():
            print(f"- entity: {entity}")
            print(f"  imported: {summary.imported}")
            print(f"  duplicates: {summary.duplicates}")
            print(f"  errors: {summary.errors}")
            print(f"  warnings: {summary.warnings}")
            if summary.details:
                print("  details:")
                for detail in summary.details:
                    print(f"    - {detail}")


if __name__ == "__main__":
    main()
