"""Bind every model experiment to a dataset owned by the same tenant."""

from alembic import op

revision = "20260916_0005"
down_revision = "20260915_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Batch mode recreates the table for SQLite and emits ordinary ALTER
    # statements on PostgreSQL. The composite key prevents a corrupt or manually
    # inserted experiment from crossing the independent tenant columns.
    with op.batch_alter_table("datasets") as batch:
        batch.create_unique_constraint(
            "uq_datasets_id_organization", ["id", "organization_id"]
        )
    with op.batch_alter_table("model_experiments") as batch:
        batch.create_foreign_key(
            "fk_model_experiments_dataset_tenant",
            "datasets",
            ["dataset_id", "organization_id"],
            ["id", "organization_id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("model_experiments") as batch:
        batch.drop_constraint("fk_model_experiments_dataset_tenant", type_="foreignkey")
    with op.batch_alter_table("datasets") as batch:
        batch.drop_constraint("uq_datasets_id_organization", type_="unique")
