import os
import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, inspect

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-with-at-least-32-characters")

from app.core.config import Settings
from app.db.base import Base
from app.db import session as database_session
from app import models  # noqa: F401


def test_settings_requires_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file="__missing__.env")


def test_metadata_contains_initial_tables() -> None:
    expected = {
        "candidates",
        "resumes",
        "job_descriptions",
        "interview_sessions",
        "interview_questions",
        "answers",
        "evaluations",
        "reports",
    }

    assert expected.issubset(Base.metadata.tables)


def test_session_dependency_closes_session(monkeypatch: pytest.MonkeyPatch) -> None:
    class TrackingSession:
        close_called = False

        def close(self) -> None:
            self.close_called = True

    tracked_session = TrackingSession()
    monkeypatch.setattr(database_session, "SessionLocal", lambda: tracked_session)

    dependency = database_session.get_db()
    next(dependency)

    dependency.close()
    assert tracked_session.close_called


def test_sqlite_can_create_initial_metadata() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    assert "interview_sessions" in inspect(engine).get_table_names()