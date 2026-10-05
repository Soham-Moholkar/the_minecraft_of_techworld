"""Deterministic SQLite query-plan experiment for a real ATLAS access pattern.

The production API retrieves projects inside an authenticated tenant and often
filters those projects by status.  This lab isolates the same relational shape
so a learner can see why a composite index is materially different from merely
having primary-key indexes on the two tables.
"""

from __future__ import annotations

import json
import math
import pathlib
import platform
import sqlite3
import sys
import time
from collections.abc import Sequence
from contextlib import closing
from dataclasses import asdict, dataclass
from typing import Final

ROW_COUNT: Final = 20_000
TENANT_COUNT: Final = 20
STATUSES: Final = ("active", "paused", "archived", "draft")
TARGET_TENANT: Final = "tenant-07"
TARGET_STATUS: Final = "active"
RESULT_LIMIT: Final = 50
COMPOSITE_INDEX: Final = "idx_projects_tenant_status_created_at"

# This is deliberately fixed SQL, not caller-provided text.  Besides making the
# experiment reproducible, it mirrors the API's security rule: users choose an
# allowlisted query and validated parameters, never arbitrary SQL to EXPLAIN.
TENANT_STATUS_QUERY: Final = """
SELECT p.id, p.slug, p.name, p.status, p.created_at
FROM projects AS p
JOIN organizations AS o ON o.id = p.organization_id
WHERE o.slug = ? AND p.status = ?
ORDER BY p.created_at DESC
LIMIT ?
""".strip()

GENERATED_FILENAMES: Final = (
    "query-plans.sqlite3",
    "plan-evidence.json",
    "benchmark.json",
    "state.json",
)


@dataclass(frozen=True, slots=True)
class PlanStep:
    """One normalized row returned by SQLite's ``EXPLAIN QUERY PLAN``."""

    select_id: int
    parent_id: int
    detail: str


@dataclass(frozen=True, slots=True)
class TimingSummary:
    """Illustrative latency samples; correctness never depends on these values."""

    repetitions: int
    warmup_runs: int
    median_ms: float
    p95_ms: float
    minimum_ms: float
    maximum_ms: float


@dataclass(frozen=True, slots=True)
class ExperimentResult:
    """Evidence proving that indexing preserves results and changes the plan."""

    before_plan: tuple[PlanStep, ...]
    after_plan: tuple[PlanStep, ...]
    before_rows: tuple[tuple[object, ...], ...]
    after_rows: tuple[tuple[object, ...], ...]


def connect(database_path: pathlib.Path) -> sqlite3.Connection:
    """Open the disposable database with explicit, reproducible lab settings."""

    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    # SQLite may otherwise create a transient index for the join.  Disabling
    # that optimizer convenience exposes the true baseline before our durable
    # composite index is introduced, which is the behavior this lab examines.
    connection.execute("PRAGMA automatic_index = OFF")
    return connection


def create_and_seed(connection: sqlite3.Connection, *, row_count: int = ROW_COUNT) -> None:
    """Create a fresh schema and deterministically seed ``row_count`` projects."""

    if row_count < TENANT_COUNT:
        raise ValueError(f"row_count must be at least {TENANT_COUNT}")

    connection.executescript(
        """
        DROP TABLE IF EXISTS projects;
        DROP TABLE IF EXISTS organizations;

        CREATE TABLE organizations (
            id INTEGER PRIMARY KEY,
            slug TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL
        );

        CREATE TABLE projects (
            id INTEGER PRIMARY KEY,
            organization_id INTEGER NOT NULL REFERENCES organizations(id),
            slug TEXT NOT NULL,
            name TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            UNIQUE (organization_id, slug)
        );
        """
    )

    organizations = [
        (tenant_id, f"tenant-{tenant_id:02d}", f"Tenant {tenant_id:02d}")
        for tenant_id in range(TENANT_COUNT)
    ]
    projects = [
        (
            project_id,
            project_id % TENANT_COUNT,
            f"project-{project_id:05d}",
            f"Project {project_id:05d}",
            STATUSES[(project_id // TENANT_COUNT) % len(STATUSES)],
            1_700_000_000 + project_id,
        )
        for project_id in range(row_count)
    ]
    with connection:
        connection.executemany(
            "INSERT INTO organizations (id, slug, name) VALUES (?, ?, ?)", organizations
        )
        connection.executemany(
            """
            INSERT INTO projects (id, organization_id, slug, name, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            projects,
        )
        connection.execute("ANALYZE")


def query_parameters() -> tuple[str, str, int]:
    """Return the fixed, non-sensitive parameters used by every lab run."""

    return TARGET_TENANT, TARGET_STATUS, RESULT_LIMIT


def explain_query(connection: sqlite3.Connection) -> tuple[PlanStep, ...]:
    """Normalize SQLite's provider-specific plan rows for stable JSON evidence."""

    rows = connection.execute(
        f"EXPLAIN QUERY PLAN {TENANT_STATUS_QUERY}", query_parameters()
    ).fetchall()
    return tuple(PlanStep(int(row[0]), int(row[1]), str(row[3])) for row in rows)


def execute_query(connection: sqlite3.Connection) -> tuple[tuple[object, ...], ...]:
    """Execute the allowlisted tenant/status query and return immutable results."""

    return tuple(connection.execute(TENANT_STATUS_QUERY, query_parameters()).fetchall())


def add_composite_index(connection: sqlite3.Connection) -> None:
    """Add the index matching equality predicates followed by the sort column."""

    # Equality columns lead the index and created_at follows in DESC order, so
    # SQLite can both locate the tenant/status slice and satisfy ORDER BY without
    # scanning every project or constructing a temporary sorting B-tree.
    with connection:
        connection.execute(
            f"""
            CREATE INDEX {COMPOSITE_INDEX}
            ON projects (organization_id, status, created_at DESC)
            """
        )
        connection.execute("ANALYZE")


def drop_composite_index(connection: sqlite3.Connection) -> None:
    """Restore the baseline schema for repeatable benchmark runs."""

    with connection:
        connection.execute(f"DROP INDEX IF EXISTS {COMPOSITE_INDEX}")
        connection.execute("ANALYZE")


def plan_uses_index(plan: Sequence[PlanStep], index_name: str = COMPOSITE_INDEX) -> bool:
    """Return whether a normalized plan explicitly uses ``index_name``."""

    expected = index_name.casefold()
    return any(expected in step.detail.casefold() for step in plan)


def run_experiment(connection: sqlite3.Connection) -> ExperimentResult:
    """Capture comparable plans and results before and after indexing."""

    drop_composite_index(connection)
    before_plan = explain_query(connection)
    before_rows = execute_query(connection)
    add_composite_index(connection)
    after_plan = explain_query(connection)
    after_rows = execute_query(connection)
    return ExperimentResult(before_plan, after_plan, before_rows, after_rows)


def time_query(
    connection: sqlite3.Connection, *, repetitions: int = 120, warmup_runs: int = 10
) -> TimingSummary:
    """Measure local latency without turning noisy timings into pass/fail gates."""

    for _ in range(warmup_runs):
        execute_query(connection)

    samples_ms: list[float] = []
    for _ in range(repetitions):
        started_ns = time.perf_counter_ns()
        execute_query(connection)
        samples_ms.append((time.perf_counter_ns() - started_ns) / 1_000_000)

    ordered = sorted(samples_ms)
    p95_index = min(len(ordered) - 1, math.ceil(len(ordered) * 0.95) - 1)
    middle = len(ordered) // 2
    median = (
        ordered[middle]
        if len(ordered) % 2
        else (ordered[middle - 1] + ordered[middle]) / 2
    )
    return TimingSummary(
        repetitions=repetitions,
        warmup_runs=warmup_runs,
        median_ms=round(median, 6),
        p95_ms=round(ordered[p95_index], 6),
        minimum_ms=round(ordered[0], 6),
        maximum_ms=round(ordered[-1], 6),
    )


def write_json(path: pathlib.Path, payload: object) -> None:
    """Write human-readable, deterministic evidence for inspection in the IDE."""

    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def plan_payload(result: ExperimentResult, *, row_count: int) -> dict[str, object]:
    """Build the persistent correctness and plan-comparison artifact."""

    return {
        "experiment": "tenant-projects-by-status",
        "provider": "sqlite",
        "sqlite_version": sqlite3.sqlite_version,
        "dataset": {
            "generator": "deterministic-synthetic",
            "row_count": row_count,
            "tenant_count": TENANT_COUNT,
            "sensitivity": "none",
        },
        "query": TENANT_STATUS_QUERY,
        "parameters": {
            "tenant_slug": TARGET_TENANT,
            "status": TARGET_STATUS,
            "limit": RESULT_LIMIT,
        },
        "before": {
            "uses_composite_index": plan_uses_index(result.before_plan),
            "plan": [asdict(step) for step in result.before_plan],
        },
        "after": {
            "uses_composite_index": plan_uses_index(result.after_plan),
            "plan": [asdict(step) for step in result.after_plan],
        },
        "correctness": {
            "identical_results": result.before_rows == result.after_rows,
            "result_count": len(result.after_rows),
        },
    }


def benchmark_payload(
    before: TimingSummary, after: TimingSummary, result: ExperimentResult
) -> dict[str, object]:
    """Build benchmark evidence with the caveats needed for honest interpretation."""

    return {
        "benchmark_id": "sqlite-tenant-status-index",
        "input_rows": ROW_COUNT,
        "environment": {
            "python": platform.python_version(),
            "sqlite": sqlite3.sqlite_version,
            "platform": platform.platform(),
        },
        "configuration": {
            "automatic_index": False,
            "composite_index": COMPOSITE_INDEX,
        },
        "before": asdict(before),
        "after": asdict(after),
        "correctness": {"identical_results": result.before_rows == result.after_rows},
        "plan": {
            "before_uses_composite_index": plan_uses_index(result.before_plan),
            "after_uses_composite_index": plan_uses_index(result.after_plan),
        },
        "notes": [
            "Timing is illustrative and is never a test assertion.",
            "The synthetic 20k-row workload is smaller and more uniform than production data.",
            "OS scheduling, CPU frequency, filesystem, and warm-cache effects vary by machine.",
            "Use the structural EXPLAIN evidence and identical-result check as the stable proof.",
        ],
    }


def ensure_valid_result(result: ExperimentResult) -> None:
    """Fail fast if the experiment no longer proves its intended invariant."""

    if result.before_rows != result.after_rows:
        raise RuntimeError("the index changed query results")
    if plan_uses_index(result.before_plan):
        raise RuntimeError("baseline unexpectedly uses the composite index")
    if not plan_uses_index(result.after_plan):
        raise RuntimeError("indexed plan does not use the composite index")
    if not result.after_rows:
        raise RuntimeError("deterministic query returned no rows")


def prepare_lab(state_dir: pathlib.Path, *, row_count: int = ROW_COUNT) -> pathlib.Path:
    """Create database and plan artifacts, leaving the indexed state inspectable."""

    state_dir.mkdir(parents=True, exist_ok=True)
    database_path = state_dir / GENERATED_FILENAMES[0]
    database_path.unlink(missing_ok=True)
    # sqlite3.Connection's context manager commits/rolls back but does not close.
    # ``closing`` is required so Windows releases the file before reset/cleanup.
    with closing(connect(database_path)) as connection:
        create_and_seed(connection, row_count=row_count)
        result = run_experiment(connection)
    ensure_valid_result(result)
    evidence_path = state_dir / GENERATED_FILENAMES[1]
    write_json(evidence_path, plan_payload(result, row_count=row_count))
    write_json(
        state_dir / GENERATED_FILENAMES[3],
        {
            "status": "ready",
            "database": database_path.name,
            "plan_evidence": evidence_path.name,
            "row_count": row_count,
        },
    )
    return evidence_path


def benchmark_lab(state_dir: pathlib.Path) -> pathlib.Path:
    """Rebuild, time both schemas, and leave the indexed database for inspection."""

    state_path = state_dir / GENERATED_FILENAMES[3]
    if not state_path.exists():
        raise RuntimeError("start the lab before benchmarking")

    database_path = state_dir / GENERATED_FILENAMES[0]
    with closing(connect(database_path)) as connection:
        create_and_seed(connection, row_count=ROW_COUNT)
        before_plan = explain_query(connection)
        before_rows = execute_query(connection)
        before_timing = time_query(connection)
        add_composite_index(connection)
        after_plan = explain_query(connection)
        after_rows = execute_query(connection)
        after_timing = time_query(connection)

    result = ExperimentResult(before_plan, after_plan, before_rows, after_rows)
    ensure_valid_result(result)
    report_path = state_dir / GENERATED_FILENAMES[2]
    write_json(report_path, benchmark_payload(before_timing, after_timing, result))
    return report_path


def reset_generated_state(state_dir: pathlib.Path) -> None:
    """Remove only known generated files, preserving any learner-created work."""

    for filename in GENERATED_FILENAMES:
        (state_dir / filename).unlink(missing_ok=True)
    if state_dir.exists() and not any(state_dir.iterdir()):
        state_dir.rmdir()


def display_plan(plan: Sequence[PlanStep]) -> str:
    """Render compact terminal evidence without hiding the raw JSON artifact."""

    return " | ".join(step.detail for step in plan)


def main() -> None:
    """Offer a small direct smoke command for contributors editing this module."""

    if len(sys.argv) != 2 or sys.argv[1] != "smoke":
        raise SystemExit("usage: query_plan_lab.py smoke")
    with closing(sqlite3.connect(":memory:")) as connection:
        connection.execute("PRAGMA automatic_index = OFF")
        create_and_seed(connection, row_count=2_000)
        result = run_experiment(connection)
    ensure_valid_result(result)
    print(f"before: {display_plan(result.before_plan)}")
    print(f"after:  {display_plan(result.after_plan)}")


if __name__ == "__main__":
    main()
