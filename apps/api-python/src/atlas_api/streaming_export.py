"""Bounded Parquet snapshots with embedded lineage and a content digest.

Only accepted tenant-owned counters are exported. No arbitrary path, URL, SQL,
schema or uploaded Parquet reader is exposed. Buffers live for one request and
are not written to shared storage. Broker observations are deliberately omitted:
they cannot define a transactional cutoff for an independent SQLite sink.
"""

import hashlib
import json

from atlas_api.streaming import UsageStream


def export_parquet(sink: UsageStream) -> tuple[bytes, str]:
    import pyarrow as pa  # type: ignore[import-untyped]
    import pyarrow.parquet as pq  # type: ignore[import-untyped]

    rows = sink.db.execute(
        "SELECT event_id,units FROM stream_effects WHERE tenant=? AND provider=? "
        "ORDER BY event_id LIMIT 10001",
        (sink.tenant, sink.provider),
    ).fetchall()
    if len(rows) > 10000:
        raise ValueError("export quota exceeded")
    # Fixed Arrow types preserve an empty export's schema and prevent inference
    # from widening strings or changing integer types when data happens to vary.
    schema = pa.schema([("event_id", pa.string()), ("units", pa.int64())])
    lineage = {
        "schema_version": 1,
        "tenant": sink.tenant,
        "provider": sink.provider,
        "source": f"atlas.usage.{sink.tenant}",
        "transform": "validated-event-id-dedup-v1",
        "sink": "stream_effects",
        "rows": len(rows),
        "units": sum(int(row[1]) for row in rows),
        "cutoff": "consistent accepted-sink read; not a broker offset snapshot",
    }
    schema = schema.with_metadata({b"atlas.lineage": json.dumps(lineage, sort_keys=True).encode()})
    table = pa.Table.from_arrays(
        [
            pa.array([row[0] for row in rows], type=pa.string()),
            pa.array([row[1] for row in rows], type=pa.int64()),
        ],
        schema=schema,
    )
    output = pa.BufferOutputStream()
    pq.write_table(table, output, compression="snappy", row_group_size=1000, version="2.6")
    content: bytes = output.getvalue().to_pybytes()
    return content, hashlib.sha256(content).hexdigest()
