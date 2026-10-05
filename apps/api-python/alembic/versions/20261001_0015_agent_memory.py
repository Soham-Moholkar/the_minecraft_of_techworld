"""Add bounded tenant-owned operator memory with explicit expiry."""

import sqlalchemy as sa

from alembic import op

revision = "20261001_0015"
down_revision = "20260923_0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_memories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("slot", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("provenance", sa.String(240), nullable=False),
        sa.Column("created_by", sa.String(160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.UniqueConstraint("organization_id", "slot", name="uq_agent_memory_tenant_slot"),
        sa.CheckConstraint("slot >= 1 AND slot <= 50", name="ck_agent_memory_slot"),
    )
    op.create_index("ix_agent_memories_organization_id", "agent_memories", ["organization_id"])
    op.create_index("ix_agent_memories_expires_at", "agent_memories", ["expires_at"])


def downgrade() -> None:
    # Explicit migration downgrade removes memory text; audit metadata is separate.
    op.drop_index("ix_agent_memories_expires_at", table_name="agent_memories")
    op.drop_index("ix_agent_memories_organization_id", table_name="agent_memories")
    op.drop_table("agent_memories")
