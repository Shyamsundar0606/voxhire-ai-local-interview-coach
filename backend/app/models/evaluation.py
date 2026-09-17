from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimestampedEntity

if TYPE_CHECKING:
    from app.models.answer import Answer
    from app.models.interview_session import InterviewSession


class Evaluation(TimestampedEntity):
    __tablename__ = "evaluations"
    __table_args__ = (
        UniqueConstraint("answer_id", name="uq_evaluation_answer"),
    )

    session_id: Mapped[str] = mapped_column(
        ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    answer_id: Mapped[str] = mapped_column(
        ForeignKey("answers.id", ondelete="CASCADE"), nullable=False
    )
    evidence: Mapped[dict] = mapped_column(JSON, nullable=False)
    dimension_scores: Mapped[dict] = mapped_column(JSON, nullable=False)
    weighted_score: Mapped[int] = mapped_column(Integer, nullable=False)
    feedback: Mapped[str] = mapped_column(Text, nullable=False)
    rubric_version: Mapped[str] = mapped_column(String(32), nullable=False)

    session: Mapped["InterviewSession"] = relationship(back_populates="evaluations")
    answer: Mapped["Answer"] = relationship(back_populates="evaluation")