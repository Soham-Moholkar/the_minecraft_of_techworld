"""Operator-run Spark Parquet rollup, with a bounded, content-bound receipt.

This job never consumes broker offsets or accepts SQL/paths from an HTTP request.
The source is the owner's authenticated accepted-sink export. Executors read a
shared, validated Parquet file; a single operator job owns that file until Spark
finishes. No raw identifiers are copied into the receipt consumed by the UI.
"""

import hashlib
import io
import json
import os
import re
import time
from datetime import UTC, datetime
from pathlib import Path


def validate_source(
    raw: bytes, digest: str | None, tenant: str
) -> tuple[str, int, int]:
    import pyarrow as pa
    import pyarrow.parquet as pq

    if len(raw) > 2_000_000 or hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError("source digest or byte limit")
    parquet = pq.ParquetFile(io.BytesIO(raw))
    # Inspect the footer before decoding rows, including an untrusted compressed
    # file. The format comes from ATLAS, but the credential alone isn't a schema.
    if (
        parquet.metadata.num_rows > 10000
        or sum(
            parquet.metadata.row_group(index).total_byte_size
            for index in range(parquet.metadata.num_row_groups)
        )
        > 4_000_000
    ):
        raise ValueError("source row limit")
    table = parquet.read()
    schema = table.schema
    if (
        schema.names != ["event_id", "units"]
        or schema.field(0).type != pa.string()
        or schema.field(1).type != pa.int64()
    ):
        raise ValueError("source schema")
    lineage = json.loads((schema.metadata or {})[b"atlas.lineage"])
    ids = table.column(0).to_pylist()
    units = table.column(1).to_pylist()
    if any(
        not isinstance(value, str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,47}", value)
        for value in ids
    ):
        raise ValueError("source identity")
    if len(set(ids)) != len(ids) or any(
        type(unit) is not int or not 0 <= unit <= 1000 for unit in units
    ):
        raise ValueError("source effects")
    if (
        lineage.get("schema_version") != 1
        or lineage.get("tenant") != tenant
        or lineage.get("provider") not in ("sqlite", "kafka")
    ):
        raise ValueError("source tenant/provider")
    if lineage.get("rows") != len(ids) or lineage.get("units") != sum(units):
        raise ValueError("source aggregate lineage")
    return lineage["provider"], len(ids), sum(units)


def write_atomic(path: Path, content: bytes) -> None:
    if path.is_symlink() or path.with_suffix(".tmp").is_symlink():
        raise ValueError("symlink output denied")
    temporary = path.with_suffix(".tmp")
    with temporary.open("wb") as output:
        output.write(content)
        output.flush()
        os.fsync(output.fileno())
    temporary.replace(path)


def main() -> None:
    # Reuse only the environment-selected bounded HTTP transport, not consume or
    # Airflow state. It disables redirects/proxies and redacts credentials/errors.
    from atlas_usage_tasks import call
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as f
    from pyspark.sql.types import LongType, StringType, StructField, StructType

    tenant = os.environ.get("ATLAS_PIPELINE_TENANT", "northstar")
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,47}", tenant):
        raise ValueError("tenant")
    raw, digest = call("/export")
    provider, expected_rows, expected_units = validate_source(raw, digest, tenant)
    root = Path(
        os.environ.get("ATLAS_USAGE_COMPUTE_STORE", "/var/lib/atlas-compute")
    ).resolve()
    folder = root / tenant / provider
    folder.mkdir(parents=True, exist_ok=True)
    if not folder.resolve().is_relative_to(root) or folder.is_symlink():
        raise ValueError("output containment")
    # O_EXCL prevents two operator runs from replacing input underneath a job.
    # An interrupted run leaves this lock for explicit operator investigation.
    lock = folder / "spark.lock"
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    spark = None
    started = time.monotonic()
    try:
        write_atomic(folder / "source.parquet", raw)
        spark = SparkSession.builder.appName("atlas-usage-rollup").getOrCreate()
        if spark.version != "4.2.0":
            raise ValueError("Spark runtime version differs from the pinned contract")
        spark.sparkContext.setLogLevel("WARN")
        schema = StructType(
            [
                StructField("event_id", StringType(), False),
                StructField("units", LongType(), False),
            ]
        )
        # Hadoop's Path constructor escapes spaces itself. Passing Path.as_uri()
        # here double-encodes %20 and breaks real Windows workspaces with spaces.
        frame = spark.read.schema(schema).parquet(
            (folder / "source.parquet").as_posix()
        )
        result = frame.agg(
            f.count("*").alias("rows"),
            f.countDistinct("event_id").alias("identities"),
            f.coalesce(f.sum("units"), f.lit(0)).alias("units"),
        ).first()
        if (
            result is None
            or result.rows != expected_rows
            or result.identities != expected_rows
            or result.units != expected_units
        ):
            raise ValueError("Spark aggregate disagrees with source lineage")
        mode = (
            "local" if spark.sparkContext.master.startswith("local") else "standalone"
        )
        if mode == "standalone" and not spark.sparkContext.master.startswith(
            "spark://"
        ):
            raise ValueError("unsupported Spark deployment mode")
        receipt = {
            "schema_version": 1,
            "provider": "spark",
            "version": "4.2.0",
            "tenant": tenant,
            "source_provider": provider,
            "source_digest": digest,
            "rows": int(result.rows),
            "units": int(result.units),
            "mode": mode,
            "partitions": frame.rdd.getNumPartitions(),
            "duration_ms": round((time.monotonic() - started) * 1000),
            "finished_at": datetime.now(UTC).isoformat(),
        }
        write_atomic(
            folder / "spark.json", json.dumps(receipt, sort_keys=True).encode()
        )
        print(
            json.dumps(
                {
                    "operation": "usage_spark_rollup",
                    "rows": receipt["rows"],
                    "units": receipt["units"],
                    "mode": mode,
                }
            )
        )
    finally:
        try:
            if spark is not None:
                spark.stop()
        finally:
            os.close(descriptor)
            lock.unlink()


if __name__ == "__main__":
    main()
