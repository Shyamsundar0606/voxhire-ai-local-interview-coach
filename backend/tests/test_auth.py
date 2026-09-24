from datetime import UTC, datetime, timedelta
import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-with-at-least-32-characters")

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_owned_interview_session
from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.candidate import Candidate
from app.models.interview_session import InterviewSession
from app.models.job_description import JobDescription
from app.models.refresh_token import RefreshToken
from app.models.resume import Resume


engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)
def database() -> None:
    Base.metadata.create_all(engine)
    app.dependency_overrides[get_db] = override_get_db
    from app.core.security import login_rate_limiter

    login_rate_limiter._attempts.clear()
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def registration_payload(email: str = "Person@Example.com", password: str = "correct-horse") -> dict[str, str]:
    return {"email": email, "password": password}


def register(client: TestClient, email: str = "Person@Example.com"):
    return client.post("/api/v1/auth/register", json=registration_payload(email))


def test_successful_registration_normalizes_email_and_sets_secure_cookie(client: TestClient) -> None:
    response = register(client)

    assert response.status_code == 201
    assert response.json()["user"]["email"] == "person@example.com"
    assert "httponly" in response.headers["set-cookie"].lower()

    with TestingSessionLocal() as db:
        user = db.scalar(select(Candidate).where(Candidate.email == "person@example.com"))
        refresh_token = db.scalar(select(RefreshToken))
        assert user is not None
        assert user.password_hash != "correct-horse"
        assert user.password_hash.startswith("$argon2")
        assert refresh_token is not None
        assert refresh_token.token_hash != client.cookies.get(get_settings().refresh_cookie_name)


def test_duplicate_email_rejected(client: TestClient) -> None:
    assert register(client).status_code == 201

    response = register(client, " person@example.com ")

    assert response.status_code == 409
    assert "already exists" in response.json()["error"]["message"]


def test_password_validation(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json=registration_payload(password="short"),
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_successful_login_and_invalid_credentials(client: TestClient) -> None:
    assert register(client, "login@example.com").status_code == 201
    client.post("/api/v1/auth/logout")

    success = client.post(
        "/api/v1/auth/login",
        json=registration_payload("LOGIN@example.com"),
    )
    invalid = client.post(
        "/api/v1/auth/login",
        json=registration_payload("LOGIN@example.com", "wrong-password"),
    )

    assert success.status_code == 200
    assert success.json()["token_type"] == "bearer"
    assert invalid.status_code == 401
    assert invalid.json()["error"]["message"] == "Invalid email or password."


def test_current_user_and_access_token_protection(client: TestClient) -> None:
    registration = register(client, "me@example.com")
    access_token = registration.json()["access_token"]

    current_user = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    missing_token = client.get("/api/v1/auth/me")
    malformed_token = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-a-token"},
    )

    assert current_user.status_code == 200
    assert current_user.json()["email"] == "me@example.com"
    assert missing_token.status_code == 401
    assert malformed_token.status_code == 401


def test_expired_access_token_rejected(client: TestClient) -> None:
    register(client, "expired@example.com")
    settings = get_settings()
    expired_token = jwt.encode(
        {
            "sub": "missing-user",
            "type": "access",
            "exp": datetime.now(UTC) - timedelta(minutes=1),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401


def test_refresh_token_rotation_and_old_token_reuse_rejected(client: TestClient) -> None:
    register(client, "rotate@example.com")
    cookie_name = get_settings().refresh_cookie_name
    old_token = client.cookies.get(cookie_name)

    rotated = client.post("/api/v1/auth/refresh")
    new_token = client.cookies.get(cookie_name)

    assert rotated.status_code == 200
    assert old_token != new_token

    client.cookies.set(cookie_name, old_token)
    reused = client.post("/api/v1/auth/refresh")

    assert reused.status_code == 401
    with TestingSessionLocal() as db:
        records = db.scalars(select(RefreshToken)).all()
        assert len(records) == 2
        assert sum(record.revoked_at is not None for record in records) == 1


def test_logout_revokes_refresh_token(client: TestClient) -> None:
    register(client, "logout@example.com")
    cookie_name = get_settings().refresh_cookie_name
    token = client.cookies.get(cookie_name)

    logout_response = client.post("/api/v1/auth/logout")
    client.cookies.set(cookie_name, token)
    refresh_response = client.post("/api/v1/auth/refresh")

    assert logout_response.status_code == 200
    assert refresh_response.status_code == 401
    with TestingSessionLocal() as db:
        record = db.scalar(select(RefreshToken))
        assert record is not None and record.revoked_at is not None


def test_cross_user_interview_session_is_not_owned() -> None:
    with TestingSessionLocal() as db:
        owner = Candidate(email="owner@example.com", password_hash=hash_password("password"))
        other_user = Candidate(email="other@example.com", password_hash=hash_password("password"))
        resume = Resume(
            candidate=owner,
            original_filename="resume.pdf",
            storage_key="owner/resume.pdf",
            content_type="application/pdf",
            byte_size=10,
            checksum_sha256="a" * 64,
        )
        job = JobDescription(candidate=owner, content="A role")
        interview = InterviewSession(
            candidate=owner,
            resume=resume,
            job_description=job,
        )
        db.add_all([owner, other_user, resume, job, interview])
        db.commit()
        db.refresh(interview)

        with pytest.raises(Exception) as error:
            get_owned_interview_session(interview.id, other_user, db)

        assert getattr(error.value, "status_code", None) == 404
