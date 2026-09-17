from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from app.db.base import TimestampedEntity

if TYPE_CHECKING:
    from app.models.job_description import JobDescription
    from app.models.resume import Resume
    from app.models.interview_session import InterviewSession


class Candidate(TimestampedEntity):
    __tablename__ = "candidates"

    resumes: Mapped[list["Resume"]] = relationship(
        back_populates="candidate", cascade="all, delete-orphan"
    )
    job_descriptions: Mapped[list["JobDescription"]] = relationship(
        back_populates="candidate", cascade="all, delete-orphan"
    )
    interview_sessions: Mapped[list["InterviewSession"]] = relationship(
        back_populates="candidate", cascade="all, delete-orphan"
    )