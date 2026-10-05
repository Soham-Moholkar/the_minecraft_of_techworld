"""Add immutable retry lineage for isolated repository tests."""

import sqlalchemy as sa

from alembic import op

revision = "20260923_0013"
down_revision = "20260923_0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("ai_repository_test_runs") as batch:
        batch.add_column(sa.Column("retry_of_id", sa.Uuid(), nullable=True))
        batch.add_column(sa.Column("attempt", sa.Integer(), nullable=False, server_default="1"))
        batch.create_foreign_key(
            "fk_ai_repository_test_runs_retry_of_id",
            "ai_repository_test_runs",
            ["retry_of_id"],
            ["id"],
        )
        batch.create_index("ix_ai_repository_test_runs_retry_of_id", ["retry_of_id"])


def downgrade() -> None:
    with op.batch_alter_table("ai_repository_test_runs") as batch:
        batch.drop_index("ix_ai_repository_test_runs_retry_of_id")
        batch.drop_constraint("fk_ai_repository_test_runs_retry_of_id", type_="foreignkey")
        batch.drop_column("attempt")
        batch.drop_column("retry_of_id")
