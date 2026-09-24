# VoxHire AI: Local Voice Interview Coach

Privacy-focused local interview coaching application. Milestone 1 establishes the monorepo foundation only: a FastAPI backend, a Next.js frontend shell, and PostgreSQL infrastructure. AI, authentication, resume processing, voice processing, and interview workflows are intentionally not implemented yet.

## Repository Layout

- `frontend/`: Next.js App Router UI with TypeScript and Tailwind CSS.
- `backend/`: FastAPI service with SQLAlchemy 2, Alembic, Pydantic settings, health routes, and tests.
- `docker-compose.yml`: Local PostgreSQL with a persistent named volume and health check.
- `PROJECT_PLAN.md`: Milestone plan and architecture decisions.

## Prerequisites

Install manually:

- Windows 10 or 11
- Python 3.12
- Node.js LTS and npm
- Docker Desktop with WSL2 integration
- A modern browser

PostgreSQL is supplied by Docker Compose. No cloud or paid service is required.

## Start PostgreSQL

```powershell
Copy-Item .env.example .env
docker compose up -d postgres
docker compose ps
```

## Start the Backend

```powershell
Set-Location backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

## Start the Frontend

In a second PowerShell terminal:

```powershell
Set-Location frontend
Copy-Item .env.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`. The frontend expects the backend at `http://localhost:8000/api/v1`.

## Validate

Backend:

```powershell
Set-Location backend
python -m pytest
```

Frontend:

```powershell
Set-Location frontend
npm run lint
npm run type-check
npm run build
```

Milestone 2 adds the SQLAlchemy 2 model registry, initial application schema, repeatable Alembic workflow, email registration/login/logout, protected current-user access, JWT access tokens, rotating HttpOnly refresh tokens, revocation, and ownership-policy checks. AI integrations, resume upload, speech processing, and interview workflows remain intentionally out of scope.
