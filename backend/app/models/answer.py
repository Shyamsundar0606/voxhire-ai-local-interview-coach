from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimestampedEntity

if TYPE_CHECKING:
    from app.models.evaluation import Evaluation
    from app.models.interview_question import InterviewQuestion
    from app.models.interview_session import InterviewSession


class Answer(TimestampedEntity):
    __tablename__ = "answers"

    session_id: Mapped[str] = mapped_column(
        ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question_id: Mapped[str] = mapped_column(
        ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=False
    )
    audio_storage_key: Mapped[str | None] = mapped_column(String(512), unique=True)
    audio_checksum_sha256: Mapped[str | None] = mapped_column(String(64))
    audio_content_type: Mapped[str | None] = mapped_column(String(128))
    audio_duration_ms: Mapped[int | None] = mapped_column(Integer)
    transcription_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending", server_default="pending"
    )
    transcript: Mapped[str | None] = mapped_column(Text)

    session: Mapped["InterviewSession"] = relationship(back_populates="answers")
    question: Mapped["InterviewQuestion"] = relationship(back_populates="answers")
    evaluation: Mapped["Evaluation | None"] = relationship(
        back_populates="answer", cascade="all, delete-orphan", uselist=False
    )