"""Linux Airflow acceptance: parse the actual DAG and check scheduler policy.

A successful parse is not a live scheduler run. The API task-chain integration
is a separate required test; full acceptance still requires an Airflow run.
"""
from pathlib import Path

from airflow.models import DagBag

root = Path(__file__).resolve().parents[1]
bag = DagBag(dag_folder=str(root / "infra/airflow/dags"), include_examples=False)
assert not bag.import_errors, bag.import_errors
workflow = bag.get_dag("atlas_usage_rollup")
assert workflow is not None
assert workflow.max_active_runs == 1 and not workflow.catchup
assert set(workflow.task_ids) == {"consume", "validate_parquet", "refresh_lakehouse"}
assert workflow.get_task("consume").retries == 0
assert workflow.get_task("consume").downstream_task_ids == {"validate_parquet"}
assert workflow.get_task("validate_parquet").downstream_task_ids == {"refresh_lakehouse"}
assert workflow.get_task("refresh_lakehouse").retries == 1
print("Airflow DAG parsed: 3 tasks, 2 dependencies, bounded manual execution")
