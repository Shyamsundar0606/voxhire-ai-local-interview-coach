from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimestampedEntity

if TYPE_CHECKING:
    from app.models.answer import Answer
    from app.models.interview_session import InterviewSession


class InterviewQuestion(TimestampedEntity):
    __tablename__ = "interview_questions"
    __table_args__ = (
        UniqueConstraint("session_id", "position", name="uq_question_session_position"),
    )

    session_id: Mapped[str] = mapped_column(
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    competencies: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    source_references: Mapped[list[str]] = mapped_column(JSON, nullable=False)

    session: Mapped["InterviewSession"] = relationship(back_populates="questions")
    answers: Mapped[list["Answer"]] = relationship(back_populates="question")