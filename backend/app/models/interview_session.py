from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimestampedEntity

if TYPE_CHECKING:
    from app.models.answer import Answer
    from app.models.candidate import Candidate
    from app.models.evaluation import Evaluation
    from app.models.interview_question import InterviewQuestion
    from app.models.job_description import JobDescription
    from app.models.report import Report
    from app.models.resume import Resume


class InterviewSession(TimestampedEntity):
    __tablename__ = "interview_sessions"

    candidate_id: Mapped[str] = mapped_column(
        ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True
    )
    resume_id: Mapped[str] = mapped_column(
        ForeignKey("resumes.id", ondelete="RESTRICT"), nullable=False
    )
    job_description_id: Mapped[str] = mapped_column(
        ForeignKey("job_descriptions.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="draft", server_default="draft"
    )
    model_name: Mapped[str | None] = mapped_column(String(128))
    rubric_version: Mapped[str] = mapped_column(
        String(32), nullable=False, default="v1", server_default="v1"
    )
    current_question_position: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    candidate: Mapped["Candidate"] = relationship(back_populates="interview_sessions")
    resume: Mapped["Resume"] = relationship(back_populates="interview_sessions")
    job_description: Mapped["JobDescription"] = relationship(
        back_populates="interview_sessions"
    )
    questions: Mapped[list["InterviewQuestion"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    answers: Mapped[list["Answer"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    evaluations: Mapped[list["Evaluation"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    report: Mapped["Report | None"] = relationship(
        back_populates="session", cascade="all, delete-orphan", uselist=False
    )