"""Persist tenant-scoped applied AI evaluation evidence."""

import sqlalchemy as sa

from alembic import op

revision = "20260918_0006"
down_revision = "20260916_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "applied_ai_experiments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "organization_id", sa.Uuid(), sa.ForeignKey("organizations.id"), nullable=False
        ),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("report", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_applied_ai_experiments_organization_id",
        "applied_ai_experiments",
        ["organization_id"],
    )


def downgrade() -> None:
    op.drop_table("applied_ai_experiments")
