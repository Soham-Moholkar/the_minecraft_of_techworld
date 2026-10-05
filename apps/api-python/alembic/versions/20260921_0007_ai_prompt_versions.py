"""Add immutable tenant-scoped AI prompt versions."""

import sqlalchemy as sa

from alembic import op

revision = "20260921_0007"
down_revision = "20260918_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_prompt_versions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "organization_id", sa.Uuid(), sa.ForeignKey("organizations.id"), nullable=False
        ),
        sa.Column("prompt_key", sa.String(64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("instruction", sa.Text(), nullable=False),
        sa.Column("created_by", sa.String(160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "organization_id",
            "prompt_key",
            "version",
            name="uq_ai_prompt_tenant_key_version",
        ),
    )
    op.create_index(
        "ix_ai_prompt_versions_organization_id", "ai_prompt_versions", ["organization_id"]
    )


def downgrade() -> None:
    op.drop_table("ai_prompt_versions")
