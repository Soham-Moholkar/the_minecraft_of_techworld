"""Add tenant slug uniqueness and durable audit evidence."""

import sqlalchemy as sa

from alembic import op

revision = "20260827_0002"
down_revision = "20260827_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("projects") as batch:
        batch.create_unique_constraint("uq_project_org_slug", ["organization_id", "slug"])
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("actor", sa.String(160), nullable=False),
        sa.Column("action", sa.String(120), nullable=False),
        sa.Column("target_type", sa.String(80), nullable=False),
        sa.Column("target_id", sa.String(64), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("organization_id", "actor", "action", "target_id", "created_at"):
        op.create_index(f"ix_audit_events_{column}", "audit_events", [column])


def downgrade() -> None:
    op.drop_table("audit_events")
    with op.batch_alter_table("projects") as batch:
        batch.drop_constraint("uq_project_org_slug", type_="unique")
