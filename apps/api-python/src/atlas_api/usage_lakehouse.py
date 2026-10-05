"""Local Iceberg projection of accepted usage events.

Each tenant/provider has a fixed table. This is an operator-triggered, bounded
full refresh, not a streaming checkpoint, remote catalog or distributed engine.
Iceberg metadata commits atomically; SQLite-to-Iceberg has no shared transaction.
"""

from pathlib import Path

from pydantic import BaseModel

from atlas_api.streaming import StreamConflict, UsageStream
from atlas_api.streaming_export import export_parquet


class SnapshotRead(BaseModel):
    snapshot_id: str  # IDs exceed JavaScript's exact integer range.
    committed_at_ms: int
    operation: str
    rows: int


class LakehouseRead(BaseModel):
    provider: str = "iceberg-local"
    table: str
    snapshots: list[SnapshotRead]
    rows: int
    units: int
    changed: bool
    source_digest: str


def refresh_lakehouse(sink: UsageStream, root: Path) -> LakehouseRead:
    """Publish at most 32 immutable snapshots, skipping identical source reads.

    Optimistic catalog conflicts fail rather than retrying a stale sink image.
    Snapshot expiration/orphan cleanup is a future explicit maintenance operation;
    no request deletes files or accepts table names, storage URIs or credentials.
    """
    import pyarrow as pa  # type: ignore[import-untyped]
    import pyarrow.parquet as pq  # type: ignore[import-untyped]
    from pyiceberg.catalog.sql import SqlCatalog

    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    catalog = SqlCatalog(
        "atlas-local",
        uri=f"sqlite:///{(root / 'catalog.db').as_posix()}",
        # Our local FileIO decodes canonical URIs and normalizes drive letters
        # and long paths; upstream Arrow FileIO alone fails on this workspace.
        warehouse=root.as_uri(),
        **{"py-io-impl": "atlas_api.local_iceberg_io.LocalIcebergFileIO"},
    )
    try:
        namespace = sink.tenant.replace("-", "_")
        name = (namespace, f"usage_{sink.provider}")
        catalog.create_namespace_if_not_exists(namespace)
        content, digest = export_parquet(sink)
        data = pq.read_table(pa.BufferReader(content)).replace_schema_metadata(None)
        table = catalog.create_table_if_not_exists(name, schema=data.schema)
        current = table.current_snapshot()
        existing_digest = (
            current.summary.additional_properties.get("atlas.source_digest", "")
            if current and current.summary
            else ""
        )
        changed = digest != existing_digest
        if changed:
            # A full overwrite may record a delete and an append snapshot in one
            # metadata commit. Reserve both slots before writing any new files.
            if len(table.metadata.snapshots) > 30:
                raise StreamConflict()
            table.overwrite(
                data,
                snapshot_properties={
                    "atlas.source_digest": digest,
                    "atlas.source": f"atlas.usage.{sink.tenant}",
                    "atlas.transform": "validated-event-id-dedup-v1",
                },
            )
        # Read at the published snapshot, not the next concurrent writer's head.
        current = table.current_snapshot()
        output = table.scan(snapshot_id=current.snapshot_id if current else None).to_arrow()
        snapshots = [
            SnapshotRead(
                snapshot_id=str(snapshot.snapshot_id),
                committed_at_ms=snapshot.timestamp_ms,
                operation=str(snapshot.summary.operation.value) if snapshot.summary else "unknown",
                rows=int(snapshot.summary.additional_properties.get("total-records", "0"))
                if snapshot.summary
                else 0,
            )
            for snapshot in table.metadata.snapshots
        ]
        return LakehouseRead(
            table=".".join(name),
            snapshots=snapshots,
            rows=output.num_rows,
            units=sum(output.column("units").to_pylist()),
            changed=changed,
            source_digest=digest,
        )
    finally:
        catalog.engine.dispose()
