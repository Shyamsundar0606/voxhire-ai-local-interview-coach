"""add candidate authentication and refresh tokens

Revision ID: 20260917_0002
Revises: 20260917_0001
Create Date: 2026-09-17

The pre-authentication development schema has no API that creates candidates,
so this revision safely adds required identity fields to the empty candidates
table before authentication is enabled.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260917_0002"
down_revision: str | None = "20260917_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("candidates", sa.Column("email", sa.String(length=320), nullable=False))
    op.add_column("candidates", sa.Column("password_hash", sa.String(length=255), nullable=False))
    op.add_column(
        "candidates",
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    )
    op.create_index("ix_candidates_email", "candidates", ["email"], unique=True)

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("candidate_id", sa.String(length=36), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("replaced_by_token_id", sa.String(length=36), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["replaced_by_token_id"],
            ["refresh_tokens.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_refresh_tokens_candidate_id", "refresh_tokens", ["candidate_id"])


def downgrade() -> None:
    op.drop_index("ix_refresh_tokens_candidate_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
    op.drop_index("ix_candidates_email", table_name="candidates")
    op.drop_column("candidates", "is_active")
    op.drop_column("candidates", "password_hash")
    op.drop_column("candidates", "email")