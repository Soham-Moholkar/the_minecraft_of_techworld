"""Add durable AI usage reservations for tenant budget enforcement."""

import sqlalchemy as sa

from alembic import op

revision = "20260921_0009"
down_revision = "20260921_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_usage_reservations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "organization_id", sa.Uuid(), sa.ForeignKey("organizations.id"), nullable=False
        ),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("provider_requested", sa.String(20), nullable=False),
        sa.Column("provider_used", sa.String(20), nullable=True),
        sa.Column("model", sa.String(160), nullable=True),
        sa.Column("reserved_cost_microusd", sa.Integer(), nullable=False),
        sa.Column("actual_cost_microusd", sa.Integer(), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=False),
        sa.Column("output_tokens", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.String(160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_ai_usage_reservations_organization_id",
        "ai_usage_reservations",
        ["organization_id"],
    )
    op.create_index(
        "ix_ai_usage_reservations_status", "ai_usage_reservations", ["status"]
    )


def downgrade() -> None:
    op.drop_table("ai_usage_reservations")
