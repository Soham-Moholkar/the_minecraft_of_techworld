"""Local durable usage pipeline. This provider is not a Kafka emulator.

Offsets are tenant-local SQLite sequence numbers. Effects, rejection evidence and
the consumer checkpoint commit together; a crash before commit can safely replay.
Only synthetic usage counters belong here, never credentials or arbitrary payloads.
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

IDENTIFIER = re.compile(r"[a-z][a-z0-9-]{0,47}\Z")


def identifier(value: str) -> str:
    """Bound identifiers before accepting any storage mutation."""
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise ValueError("invalid identifier")
    return value


class Pipeline:
    """Single-machine provider with transactional replay and bounded batches."""

    def __init__(self, path: Path) -> None:
        self.db = sqlite3.connect(path)
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                tenant TEXT NOT NULL, offset INTEGER NOT NULL,
                event_id TEXT NOT NULL, units INTEGER NOT NULL,
                PRIMARY KEY (tenant, offset), UNIQUE (tenant, event_id));
            CREATE TABLE IF NOT EXISTS checkpoints (
                tenant TEXT NOT NULL, consumer TEXT NOT NULL, offset INTEGER NOT NULL,
                PRIMARY KEY (tenant, consumer));
            CREATE TABLE IF NOT EXISTS totals (
                tenant TEXT NOT NULL, consumer TEXT NOT NULL, units INTEGER NOT NULL,
                PRIMARY KEY (tenant, consumer));
            CREATE TABLE IF NOT EXISTS rejected (
                tenant TEXT NOT NULL, consumer TEXT NOT NULL, offset INTEGER NOT NULL,
                reason TEXT NOT NULL, PRIMARY KEY (tenant, consumer, offset));
        """)

    def close(self) -> None:
        self.db.close()

    def publish(self, tenant: str, event_id: str, units: int) -> int:
        """Idempotent source delivery; conflicting retries fail without mutation.

        Negative units are intentionally accepted into the source for the quality
        exercise. The consumer quarantines them without retaining arbitrary text.
        BEGIN IMMEDIATE serializes offset allocation across local writers.
        """
        identifier(tenant)
        identifier(event_id)
        if type(units) is not int or not -1000 <= units <= 1000:
            raise ValueError("units must be a bounded integer")
        try:
            self.db.execute("BEGIN IMMEDIATE")
            existing = self.db.execute(
                "SELECT offset, units FROM events WHERE tenant=? AND event_id=?",
                (tenant, event_id),
            ).fetchone()
            if existing:
                if existing[1] != units:
                    raise ValueError("conflicting duplicate event")
                self.db.commit()
                return int(existing[0])
            offset = self.db.execute(
                "SELECT COALESCE(MAX(offset), 0)+1 FROM events WHERE tenant=?", (tenant,)
            ).fetchone()[0]
            self.db.execute("INSERT INTO events VALUES (?, ?, ?, ?)",
                            (tenant, offset, event_id, units))
            self.db.commit()
            return int(offset)
        except BaseException:
            self.db.rollback()
            raise

    def consume(self, tenant: str, consumer: str, limit: int = 10,
                *, fail_before_commit: bool = False) -> dict[str, int]:
        """Advance a bounded batch or roll back every effect on injected failure.

        This is atomic local processing, not an exactly-once guarantee across
        independent external sinks. Future brokers need stable event IDs and a
        sink deduplication strategy, rather than copying these offset semantics.
        """
        identifier(tenant)
        identifier(consumer)
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError("batch size must be between 1 and 100")
        try:
            self.db.execute("BEGIN IMMEDIATE")
            current = self.db.execute(
                "SELECT offset FROM checkpoints WHERE tenant=? AND consumer=?",
                (tenant, consumer),
            ).fetchone()
            offset = int(current[0]) if current else 0
            rows = self.db.execute(
                "SELECT offset, units FROM events WHERE tenant=? AND offset>? "
                "ORDER BY offset LIMIT ?", (tenant, offset, limit),
            ).fetchall()
            accepted = rejected = 0
            for offset, units in rows:
                if units < 0:
                    self.db.execute("INSERT INTO rejected VALUES (?, ?, ?, ?)",
                                    (tenant, consumer, offset, "negative_units"))
                    rejected += 1
                else:
                    self.db.execute(
                        "INSERT INTO totals VALUES (?, ?, ?) ON CONFLICT(tenant, consumer) "
                        "DO UPDATE SET units=units+excluded.units", (tenant, consumer, units),
                    )
                    accepted += 1
            self.db.execute(
                "INSERT INTO checkpoints VALUES (?, ?, ?) ON CONFLICT(tenant, consumer) "
                "DO UPDATE SET offset=excluded.offset", (tenant, consumer, offset),
            )
            if fail_before_commit:
                raise RuntimeError("injected pre-commit failure")
            self.db.commit()
        except BaseException:
            self.db.rollback()
            raise
        return {"accepted": accepted, "rejected": rejected, **self.snapshot(tenant, consumer)}

    def snapshot(self, tenant: str, consumer: str) -> dict[str, int]:
        """Read a consistent tenant-scoped lag, checkpoint and sink summary."""
        identifier(tenant)
        identifier(consumer)
        row = self.db.execute("""
            SELECT COALESCE((SELECT MAX(offset) FROM events WHERE tenant=?), 0),
                COALESCE((SELECT offset FROM checkpoints WHERE tenant=? AND consumer=?), 0),
                COALESCE((SELECT units FROM totals WHERE tenant=? AND consumer=?), 0),
                (SELECT COUNT(*) FROM rejected WHERE tenant=? AND consumer=?)
        """, (tenant, tenant, consumer, tenant, consumer, tenant, consumer)).fetchone()
        return {"source_offset": row[0], "checkpoint": row[1], "lag": row[0] - row[1],
                "units": row[2], "quarantined": row[3]}


def exercise(path: Path) -> dict[str, object]:
    """Execute real crash/recovery work and return content-free numeric evidence."""
    pipeline = Pipeline(path)
    try:
        for event_id, units in (("one", 4), ("two", -1), ("three", 6)):
            pipeline.publish("atlas", event_id, units)
        pipeline.publish("other", "one", 99)
        pipeline.publish("atlas", "one", 4)
        before = pipeline.snapshot("atlas", "usage")
        try:
            pipeline.consume("atlas", "usage", fail_before_commit=True)
        except RuntimeError:
            pass
        after_failure = pipeline.snapshot("atlas", "usage")
        first = pipeline.consume("atlas", "usage", 2)
        recovered = pipeline.consume("atlas", "usage", 2)
        replay = pipeline.consume("atlas", "usage")
        return {"schema_version": 1, "provider": "sqlite-local",
                "crash_rolled_back": before == after_failure,
                "first_batch": first, "recovered": recovered, "replay": replay,
                "other_tenant": pipeline.snapshot("other", "usage")}
    finally:
        pipeline.close()


def write_evidence(directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    evidence = exercise(directory / "pipeline.db")
    target = directory / "evidence.json"
    target.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    return target
