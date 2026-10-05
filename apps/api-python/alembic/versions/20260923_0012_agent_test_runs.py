"""Add separately approved isolated repository test runs."""

import sqlalchemy as sa

from alembic import op

revision = "20260923_0012"
down_revision = "20260923_0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_repository_test_runs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("organization_id", sa.Uuid(), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column(
            "proposal_id",
            sa.Uuid(),
            sa.ForeignKey("ai_repository_patch_proposals.id"),
            nullable=False,
        ),
        sa.Column("profile_id", sa.String(64), nullable=False),
        sa.Column("profile_version", sa.Integer(), nullable=False),
        sa.Column("run_digest", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("requested_by", sa.String(160), nullable=False),
        sa.Column("approved_by", sa.String(160), nullable=True),
        sa.Column("container_name", sa.String(80), nullable=True),
        sa.Column("output_excerpt", sa.Text(), nullable=False),
        sa.Column("output_sha256", sa.String(64), nullable=True),
        sa.Column("output_truncated", sa.Boolean(), nullable=False),
        sa.Column("exit_code", sa.Integer(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("failure_reason", sa.String(120), nullable=True),
        sa.Column("cancel_requested", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("heartbeat_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )
    for column in ("organization_id", "proposal_id", "profile_id", "run_digest", "status"):
        op.create_index(
            f"ix_ai_repository_test_runs_{column}",
            "ai_repository_test_runs",
            [column],
        )


def downgrade() -> None:
    op.drop_table("ai_repository_test_runs")
