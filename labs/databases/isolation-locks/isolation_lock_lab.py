"""Deterministic two-connection SQLite isolation and writer-lock experiments.

The experiments use a file-backed database because separate connections to an
ordinary ``:memory:`` database would not share state.  WAL mode is intentional:
it lets one connection keep a stable read snapshot while another commits, which
makes the snapshot boundary directly observable without threads or sleeps.
"""

from __future__ import annotations

import json
import pathlib
import sqlite3
from contextlib import ExitStack, closing
from dataclasses import asdict, dataclass
from typing import Final

BUSY_TIMEOUT_MS: Final = 75
DATABASE_FILENAME: Final = "isolation-locks.sqlite3"
EVIDENCE_FILENAME: Final = "isolation-evidence.json"
STATE_FILENAME: Final = "state.json"

# SQLite can leave WAL/shared-memory sidecars next to a database.  They are
# allowlisted explicitly so reset cannot delete unrelated learner files.
GENERATED_FILENAMES: Final = (
    DATABASE_FILENAME,
    f"{DATABASE_FILENAME}-wal",
    f"{DATABASE_FILENAME}-shm",
    EVIDENCE_FILENAME,
    STATE_FILENAME,
)


@dataclass(frozen=True, slots=True)
class SnapshotEvidence:
    """Values observed before, during, and after a reader transaction."""

    initial_value: str
    value_inside_original_snapshot: str
    value_after_reader_commit: str
    writer_committed_value: str


@dataclass(frozen=True, slots=True)
class WriterLockEvidence:
    """Stable observations from two writers contending for one SQLite database."""

    configured_busy_timeout_ms: int
    busy_error_code: int
    busy_error_name: str
    committed_value_visible_during_lock: str
    holder_uncommitted_value: str
    final_committed_value: str
    retry_succeeded: bool


def connect(
    database_path: pathlib.Path, *, busy_timeout_ms: int = 0
) -> sqlite3.Connection:
    """Open one manually controlled connection with explicit safety settings."""

    connection = sqlite3.connect(database_path, isolation_level=None)
    connection.execute("PRAGMA foreign_keys = ON")
    # The timeout is an integer controlled by this module, never caller-supplied
    # SQL.  Setting it explicitly keeps behavior independent of Python defaults.
    connection.execute(f"PRAGMA busy_timeout = {busy_timeout_ms}")
    return connection


def initialize_database(database_path: pathlib.Path) -> None:
    """Create deterministic seed rows for the two independent experiments."""

    database_path.unlink(missing_ok=True)
    with closing(connect(database_path)) as connection:
        journal_mode = str(
            connection.execute("PRAGMA journal_mode = WAL").fetchone()[0]
        )
        if journal_mode.casefold() != "wal":
            raise RuntimeError(f"SQLite did not enable WAL mode: {journal_mode}")
        connection.executescript(
            """
            CREATE TABLE configuration (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                revision INTEGER NOT NULL CHECK (revision > 0)
            );

            INSERT INTO configuration (key, value, revision)
            VALUES
                ('feature-mode', 'disabled', 1),
                ('deployment-slot', 'blue', 1);
            """
        )


def read_value(connection: sqlite3.Connection, key: str) -> str:
    """Read one seed value through a bound parameter and fail on schema drift."""

    row = connection.execute(
        "SELECT value FROM configuration WHERE key = ?", (key,)
    ).fetchone()
    if row is None:
        raise RuntimeError(f"missing deterministic configuration row: {key}")
    return str(row[0])


def rollback_if_active(connection: sqlite3.Connection) -> None:
    """Release locks when an experiment fails before its normal boundary."""

    if connection.in_transaction:
        connection.rollback()


def run_reader_snapshot(database_path: pathlib.Path) -> SnapshotEvidence:
    """Show that a reader retains its snapshot across another connection's commit."""

    with ExitStack() as stack:
        reader = stack.enter_context(closing(connect(database_path)))
        writer = stack.enter_context(closing(connect(database_path)))
        try:
            reader.execute("BEGIN")
            initial_value = read_value(reader, "feature-mode")

            # WAL permits this writer to commit while the earlier reader remains
            # open.  The reader must still see the version fixed by its first read.
            writer.execute("BEGIN IMMEDIATE")
            writer.execute(
                """
                UPDATE configuration
                SET value = ?, revision = revision + 1
                WHERE key = ?
                """,
                ("enabled", "feature-mode"),
            )
            writer.commit()

            value_inside_original_snapshot = read_value(reader, "feature-mode")
            reader.commit()
            value_after_reader_commit = read_value(reader, "feature-mode")
        finally:
            rollback_if_active(writer)
            rollback_if_active(reader)

    return SnapshotEvidence(
        initial_value=initial_value,
        value_inside_original_snapshot=value_inside_original_snapshot,
        value_after_reader_commit=value_after_reader_commit,
        writer_committed_value="enabled",
    )


def run_writer_lock(database_path: pathlib.Path) -> WriterLockEvidence:
    """Hold a write lock, observe ``SQLITE_BUSY``, release it, and retry safely."""

    with ExitStack() as stack:
        holder = stack.enter_context(closing(connect(database_path)))
        contender = stack.enter_context(
            closing(connect(database_path, busy_timeout_ms=BUSY_TIMEOUT_MS))
        )
        try:
            holder.execute("BEGIN IMMEDIATE")
            holder.execute(
                """
                UPDATE configuration
                SET value = ?, revision = revision + 1
                WHERE key = ?
                """,
                ("green-pending", "deployment-slot"),
            )

            configured_timeout = int(
                contender.execute("PRAGMA busy_timeout").fetchone()[0]
            )
            committed_value_visible_during_lock = read_value(
                contender, "deployment-slot"
            )

            try:
                contender.execute("BEGIN IMMEDIATE")
            except sqlite3.OperationalError as error:
                # We gate on SQLite's machine-readable BUSY code, not message text
                # or elapsed wall time, both of which vary by platform/runtime.
                busy_error_code = int(getattr(error, "sqlite_errorcode", -1))
                busy_error_name = str(getattr(error, "sqlite_errorname", "UNKNOWN"))
            else:
                contender.rollback()
                raise RuntimeError("second writer unexpectedly acquired the held lock")

            # Rolling back the holder proves that the pending value was never
            # committed.  The same contender can then retry successfully.
            holder.rollback()
            contender.execute("BEGIN IMMEDIATE")
            contender.execute(
                """
                UPDATE configuration
                SET value = ?, revision = revision + 1
                WHERE key = ?
                """,
                ("green", "deployment-slot"),
            )
            contender.commit()
            final_committed_value = read_value(contender, "deployment-slot")
        finally:
            rollback_if_active(contender)
            rollback_if_active(holder)

    return WriterLockEvidence(
        configured_busy_timeout_ms=configured_timeout,
        busy_error_code=busy_error_code,
        busy_error_name=busy_error_name,
        committed_value_visible_during_lock=committed_value_visible_during_lock,
        holder_uncommitted_value="green-pending",
        final_committed_value=final_committed_value,
        retry_succeeded=final_committed_value == "green",
    )


def ensure_valid_evidence(
    snapshot: SnapshotEvidence, writer_lock: WriterLockEvidence
) -> None:
    """Enforce only deterministic transaction and lock invariants."""

    if snapshot.initial_value != "disabled":
        raise RuntimeError("snapshot experiment did not start from the seed value")
    if snapshot.value_inside_original_snapshot != snapshot.initial_value:
        raise RuntimeError("reader snapshot changed before its transaction ended")
    if snapshot.value_after_reader_commit != snapshot.writer_committed_value:
        raise RuntimeError(
            "reader did not observe the writer after ending its snapshot"
        )
    if writer_lock.configured_busy_timeout_ms != BUSY_TIMEOUT_MS:
        raise RuntimeError("contender busy timeout does not match lab configuration")
    if writer_lock.busy_error_code != sqlite3.SQLITE_BUSY:
        raise RuntimeError("writer contention did not produce SQLITE_BUSY")
    if writer_lock.committed_value_visible_during_lock != "blue":
        raise RuntimeError("contender observed another writer's uncommitted value")
    if not writer_lock.retry_succeeded:
        raise RuntimeError("contender could not commit after the lock was released")


def write_json(path: pathlib.Path, payload: object) -> None:
    """Persist inspectable, stable evidence with a trailing newline."""

    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def prepare_lab(state_dir: pathlib.Path) -> pathlib.Path:
    """Run both experiments and leave the database plus JSON evidence inspectable."""

    state_dir.mkdir(parents=True, exist_ok=True)
    database_path = state_dir / DATABASE_FILENAME
    initialize_database(database_path)
    snapshot = run_reader_snapshot(database_path)
    writer_lock = run_writer_lock(database_path)
    ensure_valid_evidence(snapshot, writer_lock)

    evidence_path = state_dir / EVIDENCE_FILENAME
    write_json(
        evidence_path,
        {
            "experiment": "sqlite-reader-snapshot-and-writer-lock",
            "provider": "sqlite",
            "sqlite_version": sqlite3.sqlite_version,
            "journal_mode": "wal",
            "dataset": {
                "generator": "deterministic-synthetic",
                "row_count": 2,
                "sensitivity": "none",
            },
            "reader_snapshot": asdict(snapshot),
            "writer_lock": asdict(writer_lock),
            "assertion_policy": (
                "Gate on values, transaction boundaries, PRAGMA configuration, "
                "and SQLITE_BUSY; never on elapsed time."
            ),
        },
    )
    write_json(
        state_dir / STATE_FILENAME,
        {
            "status": "ready",
            "database": DATABASE_FILENAME,
            "evidence": EVIDENCE_FILENAME,
        },
    )
    return evidence_path


def reset_generated_state(state_dir: pathlib.Path) -> None:
    """Delete only allowlisted artifacts after all connections have been closed."""

    for filename in GENERATED_FILENAMES:
        (state_dir / filename).unlink(missing_ok=True)
    if state_dir.exists() and not any(state_dir.iterdir()):
        state_dir.rmdir()
