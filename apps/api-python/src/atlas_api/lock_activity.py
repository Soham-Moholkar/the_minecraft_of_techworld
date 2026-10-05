"""Read-only, privacy-bounded lock activity for the Data Estate surface.

The product endpoint intentionally exposes aggregate lock modes rather than query
text, relation names, process identifiers, or transaction identifiers. Those raw
fields are invaluable to an administrator, but they would turn an ordinary tenant
API into an unnecessary cross-workload information channel.
"""

from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from typing import Literal

from sqlalchemy import text
from sqlalchemy.orm import Session

from atlas_api.schemas import DatabaseLockActivityRead, LockActivityBucket


class UnsupportedLockActivityDialect(RuntimeError):
    """Raised when the active provider has no reviewed activity adapter."""


def normalize_lock_rows(rows: Iterable[Mapping[str, object]]) -> list[LockActivityBucket]:
    """Validate database aggregates before they cross the public API boundary."""

    buckets: list[LockActivityBucket] = []
    for row in rows:
        mode = row.get("mode")
        granted = row.get("granted")
        count = row.get("lock_count")
        if not isinstance(mode, str) or not mode or len(mode) > 64:
            raise ValueError("database returned an invalid lock mode")
        if not isinstance(granted, bool):
            raise ValueError("database returned an invalid granted flag")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError("database returned an invalid lock count")
        buckets.append(LockActivityBucket(mode=mode, granted=granted, count=count))
    return buckets


class LockActivityRepository:
    """Inspect aggregate lock state through a request-scoped SQLAlchemy session."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def read(self) -> DatabaseLockActivityRead:
        """Return one bounded lock snapshot without changing database state."""

        dialect = self.session.get_bind().dialect.name
        if dialect == "postgresql":
            # Restrict the snapshot to the current database and aggregate before it
            # leaves PostgreSQL. No PID, relation OID, query text, or tenant data is
            # returned, and callers cannot alter this source-owned statement.
            rows = self.session.execute(
                text(
                    """
                    SELECT mode, granted, count(*)::bigint AS lock_count
                    FROM pg_catalog.pg_locks
                    WHERE database = (
                        SELECT oid FROM pg_catalog.pg_database
                        WHERE datname = current_database()
                    )
                    GROUP BY mode, granted
                    ORDER BY granted, mode
                    """
                )
            ).mappings()
            # Project SQLAlchemy's broad RowMapping into the narrow public fields
            # accepted by the normalizer; catalog identifiers cannot leak here.
            normalized_rows = (
                {
                    "mode": row["mode"],
                    "granted": row["granted"],
                    "lock_count": row["lock_count"],
                }
                for row in rows
            )
            buckets = normalize_lock_rows(normalized_rows)
            engine: Literal["postgresql", "sqlite", "mariadb"] = "postgresql"
            available = True
            notes = [
                "Counts are an instantaneous database-wide aggregate, not a historical trace.",
                "Waiting locks can disappear before investigation; correlate sustained waits "
                "with logs and metrics.",
            ]
        elif dialect == "sqlite":
            # SQLite coordinates locks through the database file and does not expose
            # a pg_locks-style activity view. Returning an explicit unsupported state
            # is more honest than manufacturing an empty operational snapshot.
            engine = "sqlite"
            available = False
            buckets = []
            notes = [
                "SQLite does not expose a portable live lock-activity catalog.",
                "Use the two-connection isolation lab for deterministic SQLite lock evidence.",
            ]
        elif dialect == "mariadb":
            # MariaDB lock-wait views expose process/table metadata and require
            # broader catalog privileges. The ordinary product endpoint therefore
            # reports the capability boundary rather than elevating its account.
            engine = "mariadb"
            available = False
            buckets = []
            notes = [
                "The least-privileged MariaDB provider cannot read administrative lock views.",
                "Use the isolated MariaDB transaction lab for deterministic lock evidence.",
            ]
        else:
            raise UnsupportedLockActivityDialect(
                f"lock activity is not configured for database dialect {dialect!r}"
            )

        total_locks = sum(bucket.count for bucket in buckets)
        waiting_locks = sum(bucket.count for bucket in buckets if not bucket.granted)
        return DatabaseLockActivityRead(
            engine=engine,
            available=available,
            total_locks=total_locks,
            waiting_locks=waiting_locks,
            buckets=buckets,
            notes=notes,
            generated_at=datetime.now(UTC),
        )
