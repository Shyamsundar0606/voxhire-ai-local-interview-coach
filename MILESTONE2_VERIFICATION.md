# Milestone 2 Verification

## Scope

Milestone 2 adds the backend authentication and authorization boundary while preserving the Milestone 1 foundation. `Candidate` is the authenticated identity because existing resume, job-description, and interview-session records already reference `candidates.id`; adding a separate `User` table would duplicate ownership and require unnecessary migration changes.

Resume processing, Ollama, Whisper, Piper, question generation, and interview workflow APIs are not included.

## Automated Checks

Latest implementation run: backend `14 passed`; frontend lint, type-check, and production build passed; Alembic upgrade, drift check, and downgrade passed.

Run from the repository root:

```powershell
Set-Location backend
py -3.12 -m pytest
```

The suite covers:

- Successful registration and normalized email persistence.
- Duplicate email rejection.
- Password length validation and Argon2 hashing.
- Successful login and uniform invalid-credential errors.
- Current-user access and protected-route rejection.
- Malformed and expired JWT rejection.
- Refresh-token rotation and old-token reuse rejection.
- Logout revocation.
- Cross-user interview-session ownership rejection.
- Settings, metadata, session lifecycle, and schema creation.

Migration verification uses an ephemeral SQLite database and an ephemeral JWT secret. It does not alter the repository `.env` file:

```powershell
Set-Location backend
$env:DATABASE_URL = "sqlite+pysqlite:///milestone2-validation.db"
$env:JWT_SECRET_KEY = "test-secret-key-with-at-least-32-characters"
py -3.12 -m alembic upgrade head
py -3.12 -m alembic check
py -3.12 -m alembic downgrade base
Remove-Item Env:DATABASE_URL
Remove-Item Env:JWT_SECRET_KEY
Remove-Item milestone2-validation.db -ErrorAction SilentlyContinue
```

Expected migration result: `No new upgrade operations detected.`

Frontend checks:

```powershell
Set-Location frontend
npm run lint
npm run type-check
npm run build
```

## Token Storage and Protection

- Access tokens are held in React state/module memory only and are sent in the `Authorization: Bearer` header.
- Access tokens are not written to `localStorage`, `sessionStorage`, cookies, or IndexedDB.
- Refresh tokens are random opaque values in an HttpOnly, SameSite cookie scoped to `/api/v1/auth`.
- The database stores only a SHA-256 refresh-token hash, expiration, revocation timestamp, replacement relationship, and non-sensitive user-agent metadata.
- Refresh-token rotation revokes the previous token before the new session continues.
- Logout revokes the current refresh token and clears the cookie.
- Production-like deployments must set `REFRESH_COOKIE_SECURE=true` when served over HTTPS.

## Manual Checks

1. Start PostgreSQL with Docker Compose and apply `alembic upgrade head`.
2. Start FastAPI and verify `GET /api/v1/health/database` returns a reachable status.
3. Open the frontend and verify unauthenticated access to `/` redirects to `/login`.
4. Register using mixed-case email and verify the account is shown with normalized lowercase email.
5. Reload the browser and verify the HttpOnly refresh cookie restores the session without local storage entries.
6. Log out, reload `/`, and verify the dashboard redirects to `/login`.
7. Attempt to reuse a captured refresh cookie after rotation and verify a 401 response.
8. Inspect browser storage and confirm no access or refresh token is stored in local storage.

## Environmental Limitations

The automated migration checks use SQLite because Docker Desktop PostgreSQL was not available during implementation. The migration uses PostgreSQL-compatible SQLAlchemy types and was designed for PostgreSQL; live PostgreSQL startup and the database health endpoint should be rerun when the Docker Linux engine is running.