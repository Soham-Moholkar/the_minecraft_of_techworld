"""Persist tenant-scoped machine-learning experiment evidence."""

import sqlalchemy as sa

from alembic import op

revision = "20260915_0004"
down_revision = "20260914_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "model_experiments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("organization_id", sa.Uuid(), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("dataset_id", sa.Uuid(), sa.ForeignKey("datasets.id"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("report", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_model_experiments_organization_id", "model_experiments", ["organization_id"]
    )
    op.create_index("ix_model_experiments_dataset_id", "model_experiments", ["dataset_id"])


def downgrade() -> None:
    op.drop_table("model_experiments")
