"""Safe database-isolation introspection for the Data Estate surface.

The provider owns every statement it executes. It intentionally accepts no SQL,
isolation level, or PRAGMA name from an HTTP caller: database metadata endpoints
must not quietly become administrative consoles or mutation primitives.
"""

from datetime import UTC, datetime
from typing import Literal

from sqlalchemy import text
from sqlalchemy.orm import Session

from atlas_api.schemas import (
    DatabaseConcurrencyProfileRead,
    IsolationCapability,
    IsolationLevel,
)

_ISOLATION_LEVELS: frozenset[str] = frozenset(
    {"read_uncommitted", "read_committed", "repeatable_read", "serializable"}
)


class UnsupportedConcurrencyProfileDialect(RuntimeError):
    """Raised when ATLAS has no reviewed isolation adapter for an engine."""


def normalize_isolation_level(value: object) -> IsolationLevel:
    """Normalize engine spellings while rejecting unknown or malformed settings.

    Failing closed matters here: presenting a novel engine value as a familiar
    guarantee could encourage an unsafe transaction design.
    """

    if not isinstance(value, str):
        raise ValueError("database returned a non-text isolation level")
    normalized = "_".join(value.strip().lower().replace("-", " ").split())
    if normalized not in _ISOLATION_LEVELS:
        raise ValueError(f"database returned an unsupported isolation level: {value!r}")
    # The membership check above narrows the runtime value; this explicit literal
    # mapping gives static type checkers the same proof without an unsafe cast.
    mapping: dict[str, IsolationLevel] = {
        "read_uncommitted": "read_uncommitted",
        "read_committed": "read_committed",
        "repeatable_read": "repeatable_read",
        "serializable": "serializable",
    }
    return mapping[normalized]


def _postgresql_capabilities() -> list[IsolationCapability]:
    """Describe PostgreSQL's documented isolation-level compatibility behavior."""

    return [
        IsolationCapability(
            level="read_uncommitted",
            support="mapped",
            effective_level="read_committed",
            detail="Accepted by PostgreSQL but implemented with Read Committed semantics.",
        ),
        IsolationCapability(
            level="read_committed",
            support="native",
            effective_level="read_committed",
            detail="Each statement observes a snapshot taken when that statement begins.",
        ),
        IsolationCapability(
            level="repeatable_read",
            support="native",
            effective_level="repeatable_read",
            detail="A transaction observes one stable snapshot and may need serialization retries.",
        ),
        IsolationCapability(
            level="serializable",
            support="native",
            effective_level="serializable",
            detail="Serializable Snapshot Isolation detects unsafe dependency patterns.",
        ),
    ]


def _sqlite_capabilities() -> list[IsolationCapability]:
    """Describe SQLite behavior without implying unsupported SQL-level choices."""

    return [
        IsolationCapability(
            level="read_uncommitted",
            support="conditional",
            effective_level="read_uncommitted",
            detail=(
                "PRAGMA read_uncommitted is effective only between connections sharing a cache; "
                "ordinary connections remain isolated."
            ),
        ),
        IsolationCapability(
            level="read_committed",
            support="unsupported",
            effective_level=None,
            detail="SQLite does not expose Read Committed as a distinct transaction mode.",
        ),
        IsolationCapability(
            level="repeatable_read",
            support="unsupported",
            effective_level=None,
            detail="SQLite does not expose Repeatable Read as a distinct transaction mode.",
        ),
        IsolationCapability(
            level="serializable",
            support="native",
            effective_level="serializable",
            detail="Separate database connections are serializable by default.",
        ),
    ]


def _mariadb_capabilities() -> list[IsolationCapability]:
    """Describe InnoDB's four native isolation-level choices."""

    details = {
        "read_uncommitted": "Reads may observe changes another transaction has not committed.",
        "read_committed": "Each consistent read receives a fresh committed snapshot.",
        "repeatable_read": "Consistent reads share a transaction snapshot; this is the default.",
        "serializable": "Plain reads become locking reads when autocommit is disabled.",
    }
    levels: list[IsolationLevel] = [
        "read_uncommitted",
        "read_committed",
        "repeatable_read",
        "serializable",
    ]
    return [
        IsolationCapability(
            level=level,
            support="native",
            effective_level=level,
            detail=details[level],
        )
        for level in levels
    ]


def _sqlite_current_isolation(raw_read_uncommitted: object) -> IsolationLevel:
    """Convert SQLite's integer PRAGMA result into the portable vocabulary."""

    if raw_read_uncommitted in (0, False):
        return "serializable"
    if raw_read_uncommitted in (1, True):
        return "read_uncommitted"
    raise ValueError(f"SQLite returned an invalid read_uncommitted value: {raw_read_uncommitted!r}")


class ConcurrencyProfileRepository:
    """Read current/default isolation metadata through a request-scoped session."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def read(self) -> DatabaseConcurrencyProfileRead:
        """Return a normalized snapshot without changing connection or transaction state."""

        dialect = self.session.get_bind().dialect.name
        if dialect == "postgresql":
            # The setting names are source-owned string literals. current_setting is
            # read-only, and combining both reads yields one internally consistent row.
            current, default = self.session.execute(
                text(
                    "SELECT current_setting('transaction_isolation'), "
                    "current_setting('default_transaction_isolation')"
                )
            ).one()
            engine: Literal["postgresql", "sqlite", "mariadb"] = "postgresql"
            current_isolation = normalize_isolation_level(current)
            default_isolation = normalize_isolation_level(default)
            capabilities = _postgresql_capabilities()
            notes = [
                "Read Uncommitted requests use Read Committed semantics on PostgreSQL.",
                "Applications must retry transactions rejected by stricter isolation levels.",
            ]
        elif dialect == "sqlite":
            # Reading this fixed PRAGMA does not alter the connection. Its narrow
            # integer result is normalized before it crosses the API boundary.
            raw_read_uncommitted = self.session.execute(
                text("PRAGMA read_uncommitted")
            ).scalar_one()
            engine = "sqlite"
            current_isolation = _sqlite_current_isolation(raw_read_uncommitted)
            default_isolation = "serializable"
            capabilities = _sqlite_capabilities()
            notes = [
                "SQLite serializes writes; WAL mode changes concurrency, not isolation names.",
                "Read Uncommitted requires shared-cache connections to expose another "
                "writer's data.",
            ]
        elif dialect == "mariadb":
            current, default = self.session.execute(
                text(
                    "SELECT @@session.transaction_isolation, "
                    "@@global.transaction_isolation"
                )
            ).one()
            engine = "mariadb"
            current_isolation = normalize_isolation_level(current)
            default_isolation = normalize_isolation_level(default)
            capabilities = _mariadb_capabilities()
            notes = [
                "InnoDB uses Repeatable Read by default and may use gap locks for locking reads.",
                "Deadlocks and lock waits require whole-transaction retry from fresh reads.",
            ]
        else:
            raise UnsupportedConcurrencyProfileDialect(
                f"concurrency profiling is not configured for database dialect {dialect!r}"
            )

        return DatabaseConcurrencyProfileRead(
            engine=engine,
            current_isolation=current_isolation,
            default_isolation=default_isolation,
            capabilities=capabilities,
            notes=notes,
            generated_at=datetime.now(UTC),
        )
