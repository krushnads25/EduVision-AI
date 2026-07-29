from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
