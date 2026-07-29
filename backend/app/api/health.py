from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.database import session

router = APIRouter()


@router.get("/health")
def health_check():
    """Basic health check with DB ping."""
    # check DB connectivity
    try:
        with session.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(status_code=503, content={"status": "db_unavailable"})

    return {"status": "ok"}
