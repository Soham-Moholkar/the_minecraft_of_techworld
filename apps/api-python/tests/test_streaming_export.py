"""Real Parquet round-trip and embedded lineage isolation."""

import hashlib
import json
from pathlib import Path
from uuid import uuid4

import pytest

from atlas_api.streaming import LocalBroker, UsageEvent, UsageStream
from atlas_api.streaming_export import export_parquet


def test_parquet_roundtrip_and_tenant_lineage() -> None:
    pa = pytest.importorskip("pyarrow")
    pq = pytest.importorskip("pyarrow.parquet")
    path = Path("output") / f"parquet-test-{uuid4().hex}.db"
    sink = UsageStream(path, "northstar", "sqlite")
    other = UsageStream(path, "other", "sqlite")
    try:
        broker = LocalBroker(sink.db, "northstar")
        broker.publish([UsageEvent(event_id="one", units=5), UsageEvent(event_id="bad", units=-1)])
        sink.consume(broker, 10)
        foreign = LocalBroker(other.db, "other")
        foreign.publish([UsageEvent(event_id="foreign", units=999)])
        other.consume(foreign, 10)
        data, digest = export_parquet(sink)
        assert digest == hashlib.sha256(data).hexdigest()
        assert data[:4] == b"PAR1"
        table = pq.read_table(pa.BufferReader(data))
        assert table.to_pylist() == [{"event_id": "one", "units": 5}]
        lineage = json.loads(table.schema.metadata[b"atlas.lineage"])
        assert (lineage["tenant"], lineage["rows"], lineage["units"]) == ("northstar", 1, 5)
        assert lineage["source"] == "atlas.usage.northstar"
    finally:
        other.close()
        sink.close()
        path.unlink(missing_ok=True)


def test_empty_parquet_retains_schema() -> None:
    pa = pytest.importorskip("pyarrow")
    pq = pytest.importorskip("pyarrow.parquet")
    sink = UsageStream(Path(":memory:"), "empty", "sqlite")
    try:
        data, _ = export_parquet(sink)
        table = pq.read_table(pa.BufferReader(data))
        assert table.num_rows == 0
        assert table.schema.field("units").type == pa.int64()
    finally:
        sink.close()
