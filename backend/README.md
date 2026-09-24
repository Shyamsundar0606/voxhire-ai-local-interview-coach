# VoxHire AI Backend

FastAPI backend foundation for VoxHire AI. Milestone 2 provides configuration, structured logging, centralized exception responses, CORS, PostgreSQL connectivity, SQLAlchemy 2 models, Alembic migrations, email authentication, JWT access tokens, rotating refresh tokens, and health endpoints.

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
Set `JWT_SECRET_KEY` to a random local value of at least 32 characters. Do not commit the real `.env` file.

## Run

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Health endpoints:

- `GET http://localhost:8000/api/v1/health`
- `GET http://localhost:8000/api/v1/health/database`

The database health endpoint requires PostgreSQL to be running.

## Authentication

`Candidate` is the authenticated identity for the MVP because it already owns resumes, job descriptions, and interview sessions. It now stores a normalized unique email, an Argon2 password hash, and an active flag. No separate `User` table or duplicate ownership relationship is introduced.

Available endpoints:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

Access tokens are short-lived JWTs returned in the response and held in frontend memory only. Refresh tokens are random opaque values stored in an HttpOnly, SameSite cookie. The database stores only a SHA-256 hash of each refresh token. Refresh use rotates the token and revokes the previous record; logout revokes the current record.

Login failures use a process-local, configurable rate limiter. This is suitable for the single-user local deployment and should be replaced with a shared limiter only if the application becomes multi-process or remote.

## Test

```powershell
python -m pytest
```

## Migrations

Alembic is configured for future schema migrations:

```powershell
python -m alembic upgrade head
```

The initial migration creates the candidate, intake, interview, evaluation, and report tables defined in `app/models`. The second migration adds authentication fields and the `refresh_tokens` table without rewriting the foundation migration.

To roll back the latest migration during local development:

```powershell
python -m alembic downgrade -1
```
