"""Tenant-isolated usage stream and durable sink, independent of broker delivery.

Only bounded synthetic counters belong here. SQLite sink commits BEFORE broker
acknowledgement; a lost acknowledgement causes replay, handled by event identity.
This is at-least-once delivery with idempotent effects, never distributed exactly-once.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

Identifier = str


class UsageEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    event_id: str = Field(pattern=r"^[a-z][a-z0-9-]{0,47}$")
    units: int = Field(ge=-1000, le=1000)


class IngestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    events: list[UsageEvent] = Field(min_length=1, max_length=100)


class ConsumeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    limit: int = Field(default=10, ge=1, le=100)


class PartitionRead(BaseModel):
    partition: int
    earliest: int
    end: int
    checkpoint: int
    lag: int
    retention_gap: bool = False


class StreamRead(BaseModel):
    provider: Literal["sqlite", "kafka"]
    topic: str
    consumer: str = "usage-rollup"
    partitions: list[PartitionRead]
    units: int
    accepted: int
    quarantined: int
    processed: int = 0
    delivery: str = "at-least-once with durable event-id deduplication"


@dataclass(frozen=True)
class Record:
    offset: int
    payload: bytes


class Broker(Protocol):
    """One tenant-owned topic/partition; offsets denote the NEXT record to read.

    Providers must bound I/O, refuse retention gaps and release resources. Topic
    and group selection come from the authenticated tenant, never request input.
    The initial Kafka slice uses manual assignment, not distributed group balancing.
    """

    def publish(self, events: list[UsageEvent]) -> None: ...
    def fetch(self, limit: int) -> list[Record]: ...
    def commit(self, next_offset: int) -> None: ...
    def position(self) -> PartitionRead: ...
    def close(self) -> None: ...


class StreamUnavailable(Exception):
    """Redacted broker failure, including unsafe automatic retention recovery."""


class StreamConflict(Exception):
    """An event identity was reused with a different counter."""


class LocalBroker:
    """Actual durable local source; intentionally not presented as Kafka."""

    def __init__(self, db: sqlite3.Connection, tenant: str) -> None:
        self.db, self.tenant = db, tenant

    def publish(self, events: list[UsageEvent]) -> None:
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            for event in events:
                existing = self.db.execute(
                    "SELECT payload FROM stream_source WHERE tenant=? AND event_id=?",
                    (self.tenant, event.event_id),
                ).fetchone()
                payload = event.model_dump_json().encode()
                if existing:
                    if existing[0] != payload:
                        raise StreamConflict()
                    continue
                end = self.db.execute(
                    "SELECT COUNT(*) FROM stream_source WHERE tenant=?", (self.tenant,)
                ).fetchone()[0]
                if end >= 10000:
                    raise StreamConflict()  # Local profile has an explicit storage quota.
                self.db.execute(
                    "INSERT INTO stream_source VALUES (?, ?, ?, ?)",
                    (self.tenant, end, event.event_id, payload),
                )

    def fetch(self, limit: int) -> list[Record]:
        position = self.position()
        return [
            Record(int(row[0]), bytes(row[1]))
            for row in self.db.execute(
                "SELECT offset,payload FROM stream_source WHERE tenant=? AND offset>=? "
                "ORDER BY offset LIMIT ?",
                (self.tenant, position.checkpoint, limit),
            ).fetchall()
        ]

    def commit(self, next_offset: int) -> None:
        with self.db:
            self.db.execute(
                "INSERT INTO stream_offsets VALUES (?, ?) ON CONFLICT(tenant) "
                "DO UPDATE SET offset=MAX(offset,excluded.offset)",
                (self.tenant, next_offset),
            )

    def position(self) -> PartitionRead:
        row = self.db.execute(
            "SELECT (SELECT COUNT(*) FROM stream_source WHERE tenant=?), "
            "COALESCE((SELECT offset FROM stream_offsets WHERE tenant=?),0)",
            (self.tenant, self.tenant),
        ).fetchone()
        return PartitionRead(
            partition=0, earliest=0, end=row[0], checkpoint=row[1], lag=max(0, row[0] - row[1])
        )

    def close(self) -> None:
        pass  # Connection lifetime belongs to the enclosing sink.


class UsageStream:
    """Single-machine durable sink. BEGIN IMMEDIATE serializes concurrent effects.

    Provider namespaces prevent switching brokers from suppressing valid events.
    Quarantine stores only identity/offset/reason, never rejected payload bytes.
    The local quota bounds both source and deduplication retention; operators must
    explicitly archive/reset this development store before it reaches capacity.
    """

    def __init__(self, path: Path, tenant: str, provider: Literal["sqlite", "kafka"]) -> None:
        self.tenant, self.provider = tenant, provider
        self.db = sqlite3.connect(path, timeout=2)
        self.db.executescript("""
          CREATE TABLE IF NOT EXISTS stream_source (
            tenant TEXT, offset INTEGER, event_id TEXT, payload BLOB,
            PRIMARY KEY(tenant,offset), UNIQUE(tenant,event_id));
          CREATE TABLE IF NOT EXISTS stream_offsets (tenant TEXT PRIMARY KEY, offset INTEGER);
          CREATE TABLE IF NOT EXISTS stream_effects (
            tenant TEXT, provider TEXT, event_id TEXT, units INTEGER,
            PRIMARY KEY(tenant,provider,event_id));
          CREATE TABLE IF NOT EXISTS stream_quarantine (
            tenant TEXT, provider TEXT, offset INTEGER, reason TEXT,
            PRIMARY KEY(tenant,provider,offset));
        """)

    def apply(self, records: list[Record], *, fail_before_commit: bool = False) -> None:
        """Apply or quarantine each delivery atomically before broker commit.

        Conflicting duplicate IDs are evidence, not permission to overwrite a
        previously accepted counter. Injected crashes are test-only, never HTTP input.
        """
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            for record in records:
                reason = ""
                try:
                    if len(record.payload) > 512:
                        raise ValueError("oversized")
                    event = UsageEvent.model_validate(json.loads(record.payload))
                    if event.units < 0:
                        reason = "negative_units"
                    else:
                        existing = self.db.execute(
                            "SELECT units FROM stream_effects "
                            "WHERE tenant=? AND provider=? AND event_id=?",
                            (self.tenant, self.provider, event.event_id),
                        ).fetchone()
                        if existing and existing[0] != event.units:
                            reason = "conflicting_identity"
                        else:
                            self.db.execute(
                                "INSERT OR IGNORE INTO stream_effects VALUES (?,?,?,?)",
                                (self.tenant, self.provider, event.event_id, event.units),
                            )
                except (ValueError, UnicodeError):
                    reason = "invalid_schema"
                if reason:
                    self.db.execute(
                        "INSERT OR IGNORE INTO stream_quarantine VALUES (?,?,?,?)",
                        (self.tenant, self.provider, record.offset, reason),
                    )
            # Count actual new identities AFTER deduplication but BEFORE commit.
            # A lost broker acknowledgement must remain replayable at the quota.
            count = self.db.execute(
                "SELECT (SELECT COUNT(*) FROM stream_effects WHERE tenant=? AND provider=?) + "
                "(SELECT COUNT(*) FROM stream_quarantine WHERE tenant=? AND provider=?)",
                (self.tenant, self.provider, self.tenant, self.provider),
            ).fetchone()[0]
            if count > 10000:
                raise StreamConflict()
            if fail_before_commit:
                raise RuntimeError("injected sink failure")

    def snapshot(self, broker: Broker, processed: int = 0) -> StreamRead:
        row = self.db.execute(
            "SELECT COALESCE(SUM(units),0),COUNT(*) FROM stream_effects "
            "WHERE tenant=? AND provider=?",
            (self.tenant, self.provider),
        ).fetchone()
        rejected = self.db.execute(
            "SELECT COUNT(*) FROM stream_quarantine WHERE tenant=? AND provider=?",
            (self.tenant, self.provider),
        ).fetchone()[0]
        return StreamRead(
            provider=self.provider,
            topic=f"atlas.usage.{self.tenant}",
            partitions=[broker.position()],
            units=row[0],
            accepted=row[1],
            quarantined=rejected,
            processed=processed,
        )

    def consume(self, broker: Broker, limit: int) -> StreamRead:
        records = broker.fetch(limit)
        self.apply(records)
        if records:
            broker.commit(records[-1].offset + 1)
        return self.snapshot(broker, len(records))

    def close(self) -> None:
        self.db.close()
