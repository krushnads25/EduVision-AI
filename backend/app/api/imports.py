from __future__ import annotations

import os
import shutil
import tempfile

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.importers.engine import ImportEngine

router = APIRouter(
    prefix="/api/imports",
    tags=["Imports"],
)


@router.post("/upload")
async def upload_csv(
    entity: str = Form(...),
    year: int = Form(...),
    round: int | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a parser CSV and import it into the database.

    Supported entities:
    - college
    - course
    - candidate
    - seat_matrix
    - vacancy
    - cutoff
    """

    filename = file.filename or ""

    if not filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported.",
        )

    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, filename)

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        engine = ImportEngine(db)

        report = engine.run(
            entity=entity,
            file_path=temp_path,
            context={
                "year": year,
                "round": round,
            },
        )

        return {
            "status": "success",
            "entity": entity,
            "report": report.to_dict(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        try:
            os.remove(temp_path)
        except Exception:
            pass

        try:
            os.rmdir(temp_dir)
        except Exception:
            pass