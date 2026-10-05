"""Manual source-owned usage DAG; no caller-controlled configuration or commands."""

from datetime import UTC, datetime, timedelta

from airflow.sdk import dag, task


@dag(
    dag_id="atlas_usage_rollup",
    schedule=None,
    start_date=datetime(2026, 1, 1, tzinfo=UTC),
    catchup=False,
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=5),
    tags=["atlas", "usage"],
    default_args={"execution_timeout": timedelta(seconds=60)},
)
def usage_rollup():
    @task(task_id="consume", retries=0)
    def consume_batch():
        from atlas_usage_tasks import consume

        return consume()

    @task(task_id="validate_parquet", retries=1, retry_delay=timedelta(seconds=5))
    def validate_export():
        from atlas_usage_tasks import validate_parquet

        return validate_parquet()

    @task(task_id="refresh_lakehouse", retries=1, retry_delay=timedelta(seconds=5))
    def publish_snapshot():
        from atlas_usage_tasks import refresh_lakehouse

        return refresh_lakehouse()

    consume_batch() >> validate_export() >> publish_snapshot()


atlas_usage_rollup = usage_rollup()
