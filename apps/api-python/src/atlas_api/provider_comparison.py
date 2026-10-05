"""Safe, normalized comparison of ATLAS database providers.

The optional MariaDB connection is deliberately an observer, not an application
or administrator connection. Every statement is fixed in source and the public
result excludes hosts, users, database names, errors, and connection strings.
"""

from datetime import UTC, datetime
from typing import Any, Literal

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from atlas_api.concurrency_profiles import normalize_isolation_level
from atlas_api.schemas import (
    DatabaseProviderComparisonRead,
    DatabaseProviderRead,
    IsolationLevel,
)


def _bounded_version(value: object) -> str:
    """Return a display-safe, bounded server version without connection metadata."""

    version = " ".join(str(value).split())[:64]
    if not version:
        raise ValueError("database returned an empty version")
    return version


def _primary_provider(session: Session) -> DatabaseProviderRead:
    """Inspect the active request provider through fixed, read-only statements."""

    dialect = session.get_bind().dialect.name
    if dialect == "postgresql":
        version, current, default = session.execute(
            text(
                "SELECT current_setting('server_version'), "
                "current_setting('transaction_isolation'), "
                "current_setting('default_transaction_isolation')"
            )
        ).one()
        return DatabaseProviderRead(
            engine="postgresql",
            role="primary",
            status="available",
            version=_bounded_version(version),
            current_isolation=normalize_isolation_level(current),
            default_isolation=normalize_isolation_level(default),
            query_plan_format="json",
            transaction_model=(
                "MVCC snapshots with row-level locking and Serializable conflict detection."
            ),
            notes=["Authoritative ATLAS metadata store in the Compose environment."],
        )
    if dialect == "sqlite":
        version = session.execute(text("SELECT sqlite_version()")).scalar_one()
        read_uncommitted = session.execute(text("PRAGMA read_uncommitted")).scalar_one()
        isolation: IsolationLevel = (
            "read_uncommitted" if read_uncommitted in (1, True) else "serializable"
        )
        return DatabaseProviderRead(
            engine="sqlite",
            role="primary",
            status="available",
            version=_bounded_version(version),
            current_isolation=isolation,
            default_isolation="serializable",
            query_plan_format="query_plan",
            transaction_model=(
                "File-backed transactions with serialized writes and WAL reader snapshots."
            ),
            notes=["Zero-service development and test adapter."],
        )
    if dialect == "mariadb":
        version, current, default = session.execute(
            text(
                "SELECT VERSION(), @@session.transaction_isolation, "
                "@@global.transaction_isolation"
            )
        ).one()
        return _mariadb_available(version, current, default, role="primary")
    raise ValueError("active database provider is not supported")


def _mariadb_available(
    version: object,
    current: object,
    default: object,
    *,
    role: Literal["primary", "comparison"] = "comparison",
) -> DatabaseProviderRead:
    """Normalize MariaDB metadata returned by the least-privileged observer."""

    return DatabaseProviderRead(
        engine="mariadb",
        role=role,
        status="available",
        version=_bounded_version(version),
        current_isolation=normalize_isolation_level(current),
        default_isolation=normalize_isolation_level(default),
        query_plan_format="json",
        transaction_model="InnoDB MVCC with row and gap locks; Repeatable Read is the default.",
        notes=["Observed through a dedicated account with no product-table privileges."],
    )


def _mariadb_unavailable() -> DatabaseProviderRead:
    """Represent absence honestly without reflecting infrastructure errors."""

    return DatabaseProviderRead(
        engine="mariadb",
        role="comparison",
        status="unavailable",
        query_plan_format="json",
        transaction_model="InnoDB MVCC with row and gap locks; Repeatable Read is the default.",
        notes=["Start the optional MariaDB profile to collect live comparison evidence."],
    )


class ProviderComparisonRepository:
    """Compose the primary provider with an optional MariaDB observer."""

    def __init__(self, session: Session, mariadb_observer_url: str | None) -> None:
        self.session = session
        self.mariadb_observer_url = mariadb_observer_url

    def _read_mariadb(self) -> DatabaseProviderRead:
        if not self.mariadb_observer_url:
            return _mariadb_unavailable()

        engine: Engine | None = None
        try:
            # NullPool ensures the optional observer does not retain idle database
            # sessions. The short driver timeout bounds an unavailable comparison.
            engine = create_engine(
                self.mariadb_observer_url,
                poolclass=NullPool,
                connect_args={"connect_timeout": 2},
            )
            with engine.connect() as connection:
                row: tuple[Any, ...] = tuple(
                    connection.execute(
                        text(
                            "SELECT VERSION(), @@session.transaction_isolation, "
                            "@@global.transaction_isolation"
                        )
                    ).one()
                )
            return _mariadb_available(row[0], row[1], row[2])
        except (SQLAlchemyError, ValueError, IndexError):
            # Intentionally suppress raw driver text: it commonly contains host,
            # user, port, or database details that ordinary tenants do not need.
            return _mariadb_unavailable()
        finally:
            if engine is not None:
                engine.dispose()

    def read(self) -> DatabaseProviderComparisonRead:
        """Return one primary and one optional provider in a stable order."""

        primary = _primary_provider(self.session)
        providers = [primary]
        if primary.engine != "mariadb":
            providers.append(self._read_mariadb())
        return DatabaseProviderComparisonRead(
            providers=providers,
            generated_at=datetime.now(UTC),
        )
