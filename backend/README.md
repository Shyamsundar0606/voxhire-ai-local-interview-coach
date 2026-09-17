# VoxHire AI Backend

FastAPI backend foundation for VoxHire AI. Milestone 2 provides configuration, structured logging, centralized exception responses, CORS, PostgreSQL connectivity, SQLAlchemy 2 models, Alembic migrations, and health endpoints.

## Requirements

- Python 3.12
- PostgreSQL from the repository Docker Compose setup

## Setup

From PowerShell in the `backend` directory:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

Update `.env` with the same local database password used by Docker Compose. The default development URL assumes PostgreSQL is exposed on `localhost:5432`.

## Run

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Health endpoints:

- `GET http://localhost:8000/api/v1/health`
- `GET http://localhost:8000/api/v1/health/database`

The database health endpoint requires PostgreSQL to be running.

## Test

```powershell
python -m pytest
```

## Migrations

Alembic is configured for future schema migrations:

```powershell
python -m alembic upgrade head
```

The initial migration creates the candidate, intake, interview, evaluation, and report tables defined in `app/models`.

To roll back the latest migration during local development:

```powershell
python -m alembic downgrade -1
```
