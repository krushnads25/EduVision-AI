# EduVision AI — Backend (Milestone 1)

Lightweight README for getting the backend running for Milestone 1 (project foundation).

## Summary

This backend provides the FastAPI application, SQLAlchemy models, and Alembic migrations for the EduVision AI project. Milestone 1 (foundation) includes configuration, DB session, logging, health endpoint, and initial schema.

## Tech stack

- Python 3.10+
- FastAPI, Uvicorn
- SQLAlchemy 2.x
- PostgreSQL
- Alembic

## Prerequisites

- Install PostgreSQL and create database `eduvision_ai` (or update `DATABASE_URL`).
- Create and activate a Python virtual environment.

## Quick start (development)

1. From project `backend` folder, create and activate venv (example using python -m venv):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Configure environment variables: copy `.env` and update `DATABASE_URL` if needed.

4. Run Alembic migrations (creates tables):

```powershell
python -m alembic -c alembic.ini upgrade head
```

5. Start the app (development):

```powershell
# from backend directory
python -m uvicorn main:app --reload --port 8000
```

6. Health check:

Open: `http://localhost:8000/api/health` (should return `{ "status": "ok" }`)

## PowerShell-safe helper scripts

Use these helper scripts when you want to run project checks safely from PowerShell.

- `python scripts/test_db.py` — tests DB connectivity.
- `python scripts/inspect_tables.py` — lists current database tables.

## Avoid the stuck-terminal issue

PowerShell is not a Unix shell. Do not paste raw Python lines directly into PowerShell like this:

```powershell
from app.database import session
from sqlalchemy import inspect
```

Instead use one of these patterns:

```powershell
# run a helper script
python scripts/test_db.py
python scripts/inspect_tables.py

# or run a one-line Python command
$env:PYTHONPATH = (Get-Location).Path
python -c "from app.database import session; from sqlalchemy import inspect; print(sorted(inspect(session.engine).get_table_names()))"
```

If you start a long-running process, use a separate terminal tab/window and stop it with Ctrl+C when done.

## Useful scripts

- `scripts/test_db.py` — quick DB connectivity test using the project's SQLAlchemy engine.
- `scripts/inspect_tables.py` — list database tables safely from PowerShell.

## Where important code lives

- Config: `app/core/config.py`
- Logging: `app/core/logging_config.py`
- DB session: `app/database/session.py`
- Base model metadata: `app/models/base.py`
- Models: `app/models/` (college, course, candidate)
- API routers: `app/api/` (health endpoint)
- Alembic config: `alembic/` and `alembic.ini`

## Next steps

- Add Pydantic schemas for core models
- Create CRUD APIs for core models
- Implement importers and analytics engines

If you want, I can now add repositories, schemas, and basic CRUD endpoints for `College`, `Course`, and `Candidate`.
