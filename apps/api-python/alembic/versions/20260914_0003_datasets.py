"""Persist tenant dataset catalog, cleaned rows, and reproducible profile evidence."""

import sqlalchemy as sa

from alembic import op

revision = "20260914_0003"
down_revision = "20260827_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "datasets",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("organization_id", sa.Uuid(), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("source_checksum", sa.String(64), nullable=False),
        sa.Column("rows", sa.JSON(), nullable=False),
        sa.Column("report", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_datasets_organization_id", "datasets", ["organization_id"])


def downgrade() -> None:
    op.drop_table("datasets")
