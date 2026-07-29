from sqlalchemy import inspect
from app.database import session


def main() -> None:
    inspector = inspect(session.engine)
    tables = sorted(inspector.get_table_names())
    print("Database tables:")
    for table in tables:
        print(f"- {table}")


if __name__ == "__main__":
    main()
