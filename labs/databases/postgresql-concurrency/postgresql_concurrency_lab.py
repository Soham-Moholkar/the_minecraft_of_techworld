"""Disposable PostgreSQL row-lock, deadlock, and Serializable experiments.

Every statement targets the source-owned ``atlas_concurrency_lab`` schema. The
experiments use separate physical connections because lock and MVCC behavior
cannot be demonstrated honestly inside one session.
"""

from __future__ import annotations

import json
import os
import pathlib
import threading
from dataclasses import asdict, dataclass
from typing import Final

import psycopg
from psycopg import Connection

DEFAULT_DATABASE_URL: Final = "postgresql://atlas:atlas_dev_only@localhost:55432/atlas"
LAB_SCHEMA: Final = "atlas_concurrency_lab"
EVIDENCE_FILENAME: Final = "postgresql-concurrency-evidence.json"
STATE_FILENAME: Final = "state.json"
LOCK_TIMEOUT_SQLSTATE: Final = "55P03"
DEADLOCK_SQLSTATE: Final = "40P01"
SERIALIZATION_SQLSTATE: Final = "40001"


@dataclass(frozen=True, slots=True)
class RowLockEvidence:
    """Stable results from a blocked row update and a safe retry."""

    first_attempt_sqlstate: str
    retry_succeeded: bool
    final_balance: int


@dataclass(frozen=True, slots=True)
class ConcurrentOutcome:
    """One worker's machine-readable result, independent of message wording."""

    worker: str
    outcome: str
    sqlstate: str | None


@dataclass(frozen=True, slots=True)
class DeadlockEvidence:
    """Outcomes from two transactions that create a real wait cycle."""

    outcomes: list[ConcurrentOutcome]
    committed_count: int
    deadlock_count: int


@dataclass(frozen=True, slots=True)
class SerializableEvidence:
    """First-attempt conflict plus the failed transaction's safe retry."""

    first_attempt_outcomes: list[ConcurrentOutcome]
    serialization_failure_count: int
    retry_worker: str
    retry_succeeded: bool
    final_on_call_count: int


def database_url() -> str:
    """Return the opt-in lab connection URL without ever logging its contents."""

    return os.environ.get("ATLAS_POSTGRES_LAB_URL", DEFAULT_DATABASE_URL)


def connect() -> Connection[tuple[object, ...]]:
    """Open a manually controlled connection with a bounded connect attempt."""

    return psycopg.connect(database_url(), connect_timeout=3)


def require_int(row: tuple[object, ...] | None) -> int:
    """Validate one integer scalar returned by the fixed lab queries."""

    if row is None or isinstance(row[0], bool) or not isinstance(row[0], int):
        raise RuntimeError("PostgreSQL returned an invalid integer scalar")
    return row[0]


def require_str(row: tuple[object, ...] | None) -> str:
    """Validate one text scalar returned by the fixed lab queries."""

    if row is None or not isinstance(row[0], str):
        raise RuntimeError("PostgreSQL returned an invalid text scalar")
    return row[0]


def initialize_schema() -> None:
    """Replace only the fixed lab schema and seed deterministic synthetic rows."""

    with connect() as connection:
        with connection.cursor() as cursor:
            # The schema name is a source-owned constant. Keeping reset's target
            # literal makes the destructive boundary easy to audit.
            cursor.execute("DROP SCHEMA IF EXISTS atlas_concurrency_lab CASCADE")
            cursor.execute("CREATE SCHEMA atlas_concurrency_lab")
            cursor.execute(
                """
                CREATE TABLE atlas_concurrency_lab.accounts (
                    id integer PRIMARY KEY,
                    balance integer NOT NULL CHECK (balance >= 0)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE atlas_concurrency_lab.on_call (
                    doctor text PRIMARY KEY,
                    is_on_call boolean NOT NULL
                )
                """
            )
            cursor.executemany(
                "INSERT INTO atlas_concurrency_lab.accounts (id, balance) VALUES (%s, %s)",
                [(1, 100), (2, 100)],
            )
            cursor.executemany(
                "INSERT INTO atlas_concurrency_lab.on_call (doctor, is_on_call) VALUES (%s, %s)",
                [("alice", True), ("bob", True)],
            )


def reset_schema() -> None:
    """Remove exactly the source-owned lab schema after connections are closed."""

    with connect() as connection:
        connection.execute("DROP SCHEMA IF EXISTS atlas_concurrency_lab CASCADE")


def run_row_lock_timeout() -> RowLockEvidence:
    """Hold one row lock, classify the bounded failure, release, then retry."""

    with connect() as holder, connect() as contender:
        holder.execute("BEGIN")
        holder.execute(
            "UPDATE atlas_concurrency_lab.accounts SET balance = balance + 10 WHERE id = 1"
        )

        try:
            with contender.transaction():
                # A transaction-local timeout bounds the exercise without relying
                # on elapsed time as a correctness signal.
                contender.execute("SET LOCAL lock_timeout = '150ms'")
                contender.execute(
                    "UPDATE atlas_concurrency_lab.accounts "
                    "SET balance = balance + 5 WHERE id = 1"
                )
        except psycopg.Error as error:
            first_attempt_sqlstate = error.sqlstate or ""
        else:
            raise RuntimeError("contender unexpectedly acquired the held row lock")

        holder.rollback()
        with contender.transaction():
            contender.execute(
                "UPDATE atlas_concurrency_lab.accounts "
                "SET balance = balance + 5 WHERE id = 1"
            )
        final_balance = require_int(
            contender.execute(
                "SELECT balance FROM atlas_concurrency_lab.accounts WHERE id = 1"
            ).fetchone()
        )

    return RowLockEvidence(
        first_attempt_sqlstate=first_attempt_sqlstate,
        retry_succeeded=final_balance == 105,
        final_balance=final_balance,
    )


def _join_workers(threads: list[threading.Thread]) -> None:
    """Bound worker completion so a broken experiment cannot hang verification."""

    for thread in threads:
        thread.join(timeout=8)
    if any(thread.is_alive() for thread in threads):
        raise RuntimeError("PostgreSQL concurrency worker did not finish")


def run_deadlock() -> DeadlockEvidence:
    """Create opposite row-lock order and let PostgreSQL break the wait cycle."""

    barrier = threading.Barrier(2, timeout=5)
    outcomes: list[ConcurrentOutcome] = []
    outcome_lock = threading.Lock()

    def worker(name: str, first_id: int, second_id: int) -> None:
        try:
            with connect() as connection:
                with connection.transaction():
                    connection.execute("SET LOCAL statement_timeout = '6s'")
                    connection.execute(
                        "UPDATE atlas_concurrency_lab.accounts "
                        "SET balance = balance + 1 WHERE id = %s",
                        (first_id,),
                    )
                    barrier.wait()
                    connection.execute(
                        "UPDATE atlas_concurrency_lab.accounts "
                        "SET balance = balance + 1 WHERE id = %s",
                        (second_id,),
                    )
            result = ConcurrentOutcome(name, "committed", None)
        except psycopg.Error as error:
            result = ConcurrentOutcome(name, "database_error", error.sqlstate)
        except threading.BrokenBarrierError:
            result = ConcurrentOutcome(name, "coordination_error", None)
        with outcome_lock:
            outcomes.append(result)

    threads = [
        threading.Thread(target=worker, args=("left", 1, 2), daemon=True),
        threading.Thread(target=worker, args=("right", 2, 1), daemon=True),
    ]
    for thread in threads:
        thread.start()
    _join_workers(threads)
    outcomes.sort(key=lambda item: item.worker)
    return DeadlockEvidence(
        outcomes=outcomes,
        committed_count=sum(item.outcome == "committed" for item in outcomes),
        deadlock_count=sum(item.sqlstate == DEADLOCK_SQLSTATE for item in outcomes),
    )


def run_serializable_retry() -> SerializableEvidence:
    """Trigger write skew under Serializable, then retry the rejected worker."""

    barrier = threading.Barrier(2, timeout=5)
    outcomes: list[ConcurrentOutcome] = []
    outcome_lock = threading.Lock()

    def first_attempt(doctor: str) -> None:
        try:
            with connect() as connection:
                with connection.transaction():
                    connection.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
                    connection.execute("SET LOCAL statement_timeout = '6s'")
                    on_call_count = require_int(
                        connection.execute(
                            "SELECT count(*) FROM atlas_concurrency_lab.on_call "
                            "WHERE is_on_call"
                        ).fetchone()
                    )
                    barrier.wait()
                    if on_call_count > 1:
                        connection.execute(
                            "UPDATE atlas_concurrency_lab.on_call "
                            "SET is_on_call = false WHERE doctor = %s",
                            (doctor,),
                        )
            result = ConcurrentOutcome(doctor, "committed", None)
        except psycopg.Error as error:
            result = ConcurrentOutcome(doctor, "database_error", error.sqlstate)
        except threading.BrokenBarrierError:
            result = ConcurrentOutcome(doctor, "coordination_error", None)
        with outcome_lock:
            outcomes.append(result)

    threads = [
        threading.Thread(target=first_attempt, args=("alice",), daemon=True),
        threading.Thread(target=first_attempt, args=("bob",), daemon=True),
    ]
    for thread in threads:
        thread.start()
    _join_workers(threads)
    outcomes.sort(key=lambda item: item.worker)

    failed_workers = [
        item.worker for item in outcomes if item.sqlstate == SERIALIZATION_SQLSTATE
    ]
    if len(failed_workers) != 1:
        retry_worker = "not-applicable"
        retry_succeeded = False
    else:
        retry_worker = failed_workers[0]
        with connect() as retry_connection:
            with retry_connection.transaction():
                retry_connection.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
                remaining = require_int(
                    retry_connection.execute(
                        "SELECT count(*) FROM atlas_concurrency_lab.on_call "
                        "WHERE is_on_call"
                    ).fetchone()
                )
                # A correct retry re-runs the decision. It must not blindly replay
                # the rejected write after the database state has changed.
                if remaining > 1:
                    retry_connection.execute(
                        "UPDATE atlas_concurrency_lab.on_call "
                        "SET is_on_call = false WHERE doctor = %s",
                        (retry_worker,),
                    )
            retry_succeeded = True

    with connect() as observer:
        final_on_call_count = require_int(
            observer.execute(
                "SELECT count(*) FROM atlas_concurrency_lab.on_call WHERE is_on_call"
            ).fetchone()
        )
    return SerializableEvidence(
        first_attempt_outcomes=outcomes,
        serialization_failure_count=len(failed_workers),
        retry_worker=retry_worker,
        retry_succeeded=retry_succeeded,
        final_on_call_count=final_on_call_count,
    )


def ensure_valid_evidence(
    row_lock: RowLockEvidence,
    deadlock: DeadlockEvidence,
    serializable: SerializableEvidence,
) -> None:
    """Gate on SQLSTATEs, commits, retries, and final invariants only."""

    if row_lock.first_attempt_sqlstate != LOCK_TIMEOUT_SQLSTATE:
        raise RuntimeError("row-lock contention did not return lock_not_available")
    if not row_lock.retry_succeeded or row_lock.final_balance != 105:
        raise RuntimeError("row-lock retry did not commit the expected value")
    if deadlock.committed_count != 1 or deadlock.deadlock_count != 1:
        raise RuntimeError(
            "deadlock experiment did not produce one victim and one commit"
        )
    if serializable.serialization_failure_count != 1:
        raise RuntimeError("Serializable write skew did not reject one transaction")
    if not serializable.retry_succeeded or serializable.final_on_call_count != 1:
        raise RuntimeError("Serializable retry did not preserve the on-call invariant")


def write_json(path: pathlib.Path, payload: object) -> None:
    """Persist inspectable evidence without leaking SQL or connection details."""

    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def prepare_lab(state_dir: pathlib.Path) -> pathlib.Path:
    """Reset, run all experiments, and leave machine-readable evidence."""

    initialize_schema()
    row_lock = run_row_lock_timeout()
    deadlock = run_deadlock()
    # Deadlock changes both account rows but does not affect the independent
    # on-call dataset used by the Serializable experiment.
    serializable = run_serializable_retry()
    ensure_valid_evidence(row_lock, deadlock, serializable)

    with connect() as connection:
        server_version = require_str(
            connection.execute("SHOW server_version").fetchone()
        )

    state_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = state_dir / EVIDENCE_FILENAME
    write_json(
        evidence_path,
        {
            "experiment": "postgresql-locks-deadlocks-and-serializable-retry",
            "provider": "postgresql",
            "server_version": server_version,
            "schema": LAB_SCHEMA,
            "dataset": {
                "generator": "deterministic-synthetic",
                "row_count": 4,
                "sensitivity": "none",
            },
            "row_lock": asdict(row_lock),
            "deadlock": asdict(deadlock),
            "serializable": asdict(serializable),
            "assertion_policy": (
                "Gate on SQLSTATEs, committed values, transaction outcomes, and "
                "the final invariant; never on elapsed time or message text."
            ),
        },
    )
    write_json(
        state_dir / STATE_FILENAME,
        {"status": "ready", "schema": LAB_SCHEMA, "evidence": EVIDENCE_FILENAME},
    )
    return evidence_path


def reset_generated_state(state_dir: pathlib.Path) -> None:
    """Delete only allowlisted generated files while preserving learner notes."""

    for filename in (EVIDENCE_FILENAME, STATE_FILENAME):
        (state_dir / filename).unlink(missing_ok=True)
    if state_dir.exists() and not any(state_dir.iterdir()):
        state_dir.rmdir()
