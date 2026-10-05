"""Real local Iceberg snapshots, replay identity, isolation and history."""

from pathlib import Path
from uuid import uuid4

import pytest

from atlas_api.streaming import LocalBroker, UsageEvent, UsageStream
from atlas_api.usage_lakehouse import refresh_lakehouse


def test_iceberg_refresh_replay_and_tenant_isolation() -> None:
    pytest.importorskip("pyiceberg")
    root = Path("output") / f"iceberg-test-{uuid4().hex}"
    root.mkdir()
    sink = UsageStream(root / "sink.db", "northstar", "sqlite")
    other = UsageStream(root / "sink.db", "other", "sqlite")
    try:
        broker = LocalBroker(sink.db, "northstar")
        broker.publish([UsageEvent(event_id="one", units=5)])
        sink.consume(broker, 10)
        first = refresh_lakehouse(sink, root / "warehouse")
        assert (first.rows, first.units, first.changed, len(first.snapshots)) == (1, 5, True, 1)
        replay = refresh_lakehouse(sink, root / "warehouse")
        assert replay.changed is False
        assert len(replay.snapshots) == 1
        broker.publish([UsageEvent(event_id="two", units=3)])
        sink.consume(broker, 10)
        second = refresh_lakehouse(sink, root / "warehouse")
        assert (second.rows, second.units, len(second.snapshots)) == (2, 8, 3)
        foreign = refresh_lakehouse(other, root / "warehouse")
        assert (foreign.rows, foreign.units) == (0, 0)
        assert foreign.table != second.table
        # Verify actual prior snapshot data rather than only counting metadata.
        from pyiceberg.catalog.sql import SqlCatalog

        catalog = SqlCatalog(
            "atlas-local",
            uri=f"sqlite:///{(root.resolve() / 'warehouse/catalog.db').as_posix()}",
            warehouse="file://" + (root.resolve() / "warehouse").as_posix(),
            **{"py-io-impl": "atlas_api.local_iceberg_io.LocalIcebergFileIO"},
        )
        try:
            table = catalog.load_table(("northstar", "usage_sqlite"))
            old = table.scan(snapshot_id=int(first.snapshots[0].snapshot_id)).to_arrow()
            assert old.to_pylist() == [{"event_id": "one", "units": 5}]
        finally:
            catalog.engine.dispose()
    finally:
        other.close()
        sink.close()
        # Verify every resolved generated target before removing this unique fixture.
        for target in sorted(root.rglob("*"), key=lambda item: len(item.parts), reverse=True):
            assert target.resolve().is_relative_to(root.resolve())
            if target.is_file():
                target.unlink()
            else:
                target.rmdir()
        root.rmdir()
