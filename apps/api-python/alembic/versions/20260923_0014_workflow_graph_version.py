"""Pin repository workflow runs to their source-owned graph version."""

import sqlalchemy as sa

from alembic import op

revision = "20260923_0014"
down_revision = "20260923_0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Existing event streams were written by the original deterministic graph,
    # now frozen as version 1. The default makes that compatibility explicit.
    with op.batch_alter_table("ai_repository_patch_workflows") as batch:
        batch.add_column(
            sa.Column("graph_version", sa.Integer(), nullable=False, server_default="1")
        )


def downgrade() -> None:
    with op.batch_alter_table("ai_repository_patch_workflows") as batch:
        batch.drop_column("graph_version")
