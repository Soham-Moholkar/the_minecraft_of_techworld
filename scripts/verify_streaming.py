"""Exercise the installed local Phase 10 runtimes without touching product data.

Requires streaming/lakehouse extras and an isolated generated workspace directory.
Numeric evidence includes replay, Parquet roundtrip and Iceberg history; Kafka
live acceptance remains a separate gate requiring a running broker.
"""

import json
import os
from pathlib import Path
from uuid import uuid4

from atlas_api.streaming import LocalBroker, UsageEvent, UsageStream
from atlas_api.streaming_export import export_parquet
from atlas_api.usage_lakehouse import refresh_lakehouse


def verify() -> None:
    import pyarrow as pa
    import pyarrow.parquet as pq

    root = Path("output") / f"phase10-verification-{uuid4().hex}"
    root.mkdir()
    sink = UsageStream(root / "sink.db", "verification", "sqlite")
    try:
        broker = LocalBroker(sink.db, "verification")
        broker.publish(
            [UsageEvent(event_id="one", units=4), UsageEvent(event_id="bad", units=-1)]
        )
        sink.apply(broker.fetch(10))  # Simulate losing the acknowledgement.
        summary = sink.consume(broker, 10)
        assert (summary.units, summary.quarantined, summary.partitions[0].lag) == (
            4,
            1,
            0,
        )
        content, digest = export_parquet(sink)
        table = pq.read_table(pa.BufferReader(content))
        assert table.num_rows == 1
        lake = refresh_lakehouse(sink, root / "warehouse")
        replay = refresh_lakehouse(sink, root / "warehouse")
        assert lake.rows == 1 and not replay.changed
        print(
            json.dumps(
                {
                    "event": "phase10_local_verified",
                    "units": summary.units,
                    "quarantined": summary.quarantined,
                    "lag": summary.partitions[0].lag,
                    "parquet_rows": table.num_rows,
                    "parquet_sha256": digest,
                    "iceberg_snapshots": len(lake.snapshots),
                    "replay_changed": replay.changed,
                }
            )
        )
    finally:
        sink.close()
        # Every target is resolved and checked inside this unique workspace fixture.
        for target in sorted(
            root.rglob("*"), key=lambda item: len(item.parts), reverse=True
        ):
            if not target.resolve().is_relative_to(root.resolve()):
                raise RuntimeError("refusing cleanup outside verification fixture")
            native = Path("\\\\?\\" + str(target.resolve())) if os.name == "nt" else target
            native.unlink() if native.is_file() else native.rmdir()
        root.rmdir()


if __name__ == "__main__":
    verify()
