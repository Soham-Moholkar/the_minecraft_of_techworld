"""Add persisted deterministic repository patch workflows."""

import sqlalchemy as sa

from alembic import op

revision = "20260923_0011"
down_revision = "20260923_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_repository_patch_workflows",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("organization_id", sa.Uuid(), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column(
            "proposal_id",
            sa.Uuid(),
            sa.ForeignKey("ai_repository_patch_proposals.id"),
            nullable=True,
        ),
        sa.Column("objective", sa.String(500), nullable=False),
        sa.Column("plan", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("current_step", sa.String(40), nullable=False),
        sa.Column("events", sa.JSON(), nullable=False),
        sa.Column("failure_reason", sa.String(120), nullable=True),
        sa.Column("created_by", sa.String(160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_ai_repository_patch_workflows_organization_id",
        "ai_repository_patch_workflows",
        ["organization_id"],
    )
    op.create_index(
        "ix_ai_repository_patch_workflows_proposal_id",
        "ai_repository_patch_workflows",
        ["proposal_id"],
    )
    op.create_index(
        "ix_ai_repository_patch_workflows_status",
        "ai_repository_patch_workflows",
        ["status"],
    )


def downgrade() -> None:
    op.drop_table("ai_repository_patch_workflows")
