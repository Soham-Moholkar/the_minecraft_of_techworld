"""Add exact-diff approval evidence for local repository patching."""

import sqlalchemy as sa

from alembic import op

revision = "20260923_0010"
down_revision = "20260921_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_repository_patch_proposals",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("organization_id", sa.Uuid(), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("path", sa.String(240), nullable=False),
        sa.Column("summary", sa.String(200), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("original_sha256", sa.String(64), nullable=False),
        sa.Column("patched_sha256", sa.String(64), nullable=False),
        sa.Column("proposal_digest", sa.String(64), nullable=False),
        sa.Column("original_content", sa.Text(), nullable=False),
        sa.Column("patched_content", sa.Text(), nullable=False),
        sa.Column("unified_diff", sa.Text(), nullable=False),
        sa.Column("start_line", sa.Integer(), nullable=False),
        sa.Column("end_line", sa.Integer(), nullable=False),
        sa.Column("proposed_by", sa.String(160), nullable=False),
        sa.Column("approved_by", sa.String(160), nullable=True),
        sa.Column("failure_reason", sa.String(120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rolled_back_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint(
            "organization_id", "proposal_digest", name="uq_ai_patch_tenant_digest"
        ),
    )
    op.create_index(
        "ix_ai_repository_patch_proposals_organization_id",
        "ai_repository_patch_proposals",
        ["organization_id"],
    )
    op.create_index(
        "ix_ai_repository_patch_proposals_status",
        "ai_repository_patch_proposals",
        ["status"],
    )
    op.create_index(
        "ix_ai_repository_patch_proposals_proposal_digest",
        "ai_repository_patch_proposals",
        ["proposal_digest"],
    )


def downgrade() -> None:
    op.drop_table("ai_repository_patch_proposals")
