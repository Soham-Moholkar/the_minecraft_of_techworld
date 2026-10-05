"""Persist immutable repository retrieval evaluation evidence."""

import sqlalchemy as sa

from alembic import op

revision = "20260921_0008"
down_revision = "20260921_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_retrieval_evaluations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "organization_id", sa.Uuid(), sa.ForeignKey("organizations.id"), nullable=False
        ),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("report", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.String(160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_ai_retrieval_evaluations_organization_id",
        "ai_retrieval_evaluations",
        ["organization_id"],
    )


def downgrade() -> None:
    op.drop_table("ai_retrieval_evaluations")
