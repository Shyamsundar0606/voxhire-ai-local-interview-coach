from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimestampedEntity

if TYPE_CHECKING:
    from app.models.interview_session import InterviewSession


class Report(TimestampedEntity):
    __tablename__ = "reports"
    __table_args__ = (
        UniqueConstraint("session_id", name="uq_report_session"),
    )

    session_id: Mapped[str] = mapped_column(
        ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False
    )
    aggregate_components: Mapped[dict] = mapped_column(JSON, nullable=False)
    final_score: Mapped[int] = mapped_column(Integer, nullable=False)
    strengths: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    improvement_areas: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    recommendations: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    generation_version: Mapped[str] = mapped_column(String(32), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)

    session: Mapped["InterviewSession"] = relationship(back_populates="report")