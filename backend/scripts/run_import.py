from argparse import ArgumentParser
from pathlib import Path

from app.database.session import SessionLocal, engine
from app.importers.engine import ImportEngine
from app.models import Base  # noqa: F401, imports all models so metadata is populated


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description="Run an EduVision import job")
    parser.add_argument(
        "entity",
        choices=["college", "course", "candidate", "seat_matrix", "vacancy", "cutoff"],
        help="Entity type to import",
    )
    parser.add_argument("file", help="Input CSV or Excel file path")
    parser.add_argument("--sheet", default=None, help="Excel sheet name or index")
    parser.add_argument("--year", default=None, help="Year associated with imported data")
    parser.add_argument("--round", default=None, help="Round number associated with imported data")
    return parser


def main() -> None:
    parser = parse_args()
    args = parser.parse_args()
    file_path = Path(args.file)
    if not file_path.exists():
        raise SystemExit(f"File not found: {file_path}")

    # Ensure all models are imported and metadata is registered before any import runs.
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        importer = ImportEngine(db)
        report = importer.run(
            args.entity,
            str(file_path),
            sheet_name=args.sheet,
            context={"year": args.year, "round": args.round},
        )

        print("Import report")
        for entity, summary in report.summaries.items():
            print(f"- entity: {entity}")
            print(f"  imported: {summary.imported}")
            print(f"  updated: {summary.updated}")
            print(f"  duplicates: {summary.duplicates}")
            print(f"  errors: {summary.errors}")
            print(f"  warnings: {summary.warnings}")
            if summary.details:
                print("  details:")
                for detail in summary.details:
                    print(f"    - {detail}")


if __name__ == "__main__":
    main()
