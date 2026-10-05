"""Source-owned bounded PyFlink batch alternative for accepted usage exports.

Flink's Table planner executes the aggregate; Arrow is only the bounded input
decoder. Batch completion is not checkpoint/recovery acceptance. Observe the
returned actual job ID through the separate read-only status adapter.
"""

import io
import json
import os


def main() -> None:
    import pyarrow.parquet as pq
    from atlas_usage_tasks import call
    from pyflink.common import RuntimeExecutionMode
    from pyflink.datastream import StreamExecutionEnvironment
    from pyflink.table import DataTypes, StreamTableEnvironment
    from pyflink.table.expressions import col, lit
    from usage_job_input import validate_source

    tenant = os.environ.get("ATLAS_PIPELINE_TENANT", "northstar")
    raw, digest = call("/export")
    _, expected_rows, expected_units = validate_source(raw, digest, tenant)
    table = pq.read_table(io.BytesIO(raw))
    rows = [(row["event_id"], row["units"]) for row in table.to_pylist()]
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_runtime_mode(RuntimeExecutionMode.BATCH)
    env.set_parallelism(2)
    tables = StreamTableEnvironment.create(env)
    tables.get_config().set("pipeline.name", "atlas-usage-rollup")
    source = tables.from_elements(
        rows,
        DataTypes.ROW(
            [
                DataTypes.FIELD("event_id", DataTypes.STRING()),
                DataTypes.FIELD("units", DataTypes.BIGINT()),
            ]
        ),
    )
    aggregate = source.select(
        col("event_id").count.alias("rows"),
        col("units").sum.if_null(lit(0)).alias("units"),
    )
    result = aggregate.execute()
    client = result.get_job_client()
    if client is None:
        raise ValueError("Flink job identity unavailable")
    with result.collect() as values:
        output = list(values)
    if len(output) != 1 or tuple(output[0]) != (expected_rows, expected_units):
        raise ValueError("Flink aggregate disagrees with source lineage")
    print(
        json.dumps(
            {
                "operation": "usage_flink_rollup",
                "job_id": str(client.get_job_id()),
                "rows": expected_rows,
                "units": expected_units,
                "source_digest": digest,
                "mode": "batch",
            }
        )
    )


if __name__ == "__main__":
    main()
