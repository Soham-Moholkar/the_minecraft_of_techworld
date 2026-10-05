"""Reproducible comparison of relational, document, and cache read patterns."""

from __future__ import annotations

import hashlib
import json
import math
import pathlib
import platform
import sqlite3
import time
from collections.abc import Callable
from contextlib import closing
from dataclasses import asdict, dataclass
from typing import Final

ROW_COUNT: Final = 12_000
REPETITIONS: Final = 120
WARMUPS: Final = 12
TARGET_TENANT: Final = "tenant-07"
TARGET_STATUS: Final = "active"
GENERATED_FILES: Final = ("benchmark.json", "state.json")


@dataclass(frozen=True, slots=True)
class SampleSummary:
    """Portable latency and throughput fields for one implementation."""

    implementation: str
    repetitions: int
    warmup_runs: int
    p50_ms: float
    p95_ms: float
    operations_per_second: float
    result_count: int
    result_checksum: str


def records(row_count: int = ROW_COUNT) -> list[tuple[int, str, str, str]]:
    """Build a deterministic, non-sensitive workload shared by all adapters."""

    statuses = ("active", "paused", "archived")
    return [
        (index, f"tenant-{index % 20:02d}", statuses[index % 3], f"project-{index:05d}")
        for index in range(row_count)
    ]


def checksum(values: list[str]) -> str:
    """Create stable correctness evidence without storing the complete dataset."""

    return hashlib.sha256("\n".join(values).encode("utf-8")).hexdigest()


def percentile(ordered: list[float], fraction: float) -> float:
    """Return a nearest-rank percentile suitable for a small local benchmark."""

    index = min(len(ordered) - 1, max(0, math.ceil(len(ordered) * fraction) - 1))
    return ordered[index]


def measure(name: str, operation: Callable[[], list[str]]) -> SampleSummary:
    """Warm an implementation, measure it, and retain a correctness digest."""

    for _ in range(WARMUPS):
        operation()
    samples: list[float] = []
    result: list[str] = []
    for _ in range(REPETITIONS):
        started = time.perf_counter_ns()
        result = operation()
        samples.append((time.perf_counter_ns() - started) / 1_000_000)
    ordered = sorted(samples)
    total_seconds = sum(samples) / 1_000
    return SampleSummary(
        implementation=name,
        repetitions=REPETITIONS,
        warmup_runs=WARMUPS,
        p50_ms=round(percentile(ordered, 0.50), 6),
        p95_ms=round(percentile(ordered, 0.95), 6),
        operations_per_second=round(REPETITIONS / total_seconds, 2),
        result_count=len(result),
        result_checksum=checksum(result),
    )


def prepare_sqlite(rows: list[tuple[int, str, str, str]]) -> sqlite3.Connection:
    """Create the indexed relational implementation entirely in memory."""

    connection = sqlite3.connect(":memory:")
    connection.execute(
        "CREATE TABLE projects (id INTEGER, tenant TEXT, status TEXT, slug TEXT)"
    )
    connection.executemany("INSERT INTO projects VALUES (?, ?, ?, ?)", rows)
    connection.execute(
        "CREATE INDEX idx_projects_tenant_status ON projects (tenant, status, id)"
    )
    return connection


def run_suite(*, row_count: int = ROW_COUNT) -> dict[str, object]:
    """Measure distinct read models and prove they return identical content."""

    rows = records(row_count)
    documents = [
        {"id": row[0], "tenant": row[1], "status": row[2], "slug": row[3]}
        for row in rows
    ]
    expected = [
        row[3] for row in rows if row[1] == TARGET_TENANT and row[2] == TARGET_STATUS
    ]
    cache = {(TARGET_TENANT, TARGET_STATUS): expected}

    with closing(prepare_sqlite(rows)) as connection:
        # Values are bound parameters and the query is source-owned. The
        # benchmark must not accidentally teach arbitrary SQL execution.
        relational = measure(
            "sqlite-indexed-query",
            lambda: [
                str(row[0])
                for row in connection.execute(
                    "SELECT slug FROM projects WHERE tenant = ? AND status = ? ORDER BY id",
                    (TARGET_TENANT, TARGET_STATUS),
                )
            ],
        )
        document = measure(
            "document-projection-filter",
            lambda: [
                str(item["slug"])
                for item in documents
                if item["tenant"] == TARGET_TENANT and item["status"] == TARGET_STATUS
            ],
        )
        cached = measure(
            "cache-snapshot-hit",
            lambda: list(cache[(TARGET_TENANT, TARGET_STATUS)]),
        )

    results = [relational, document, cached]
    checksums = {result.result_checksum for result in results}
    counts = {result.result_count for result in results}
    if len(checksums) != 1 or len(counts) != 1 or not expected:
        raise RuntimeError("provider implementations returned different results")
    return {
        "benchmark_id": "phase-four-provider-read-patterns",
        "workload": {
            "generator": "deterministic-synthetic",
            "input_rows": row_count,
            "tenant_count": 20,
            "filter": {"tenant": TARGET_TENANT, "status": TARGET_STATUS},
            "sensitivity": "none",
        },
        "environment": {
            "python": platform.python_version(),
            "sqlite": sqlite3.sqlite_version,
            "platform": platform.platform(),
        },
        "results": [asdict(result) for result in results],
        "correctness": {
            "identical_result_counts": True,
            "identical_checksums": True,
            "expected_result_count": len(expected),
        },
        "caveats": [
            "These implementations serve different responsibilities and are not substitutes.",
            "The cache result assumes a hit; invalidation and miss cost are measured in the Redis lab.",
            "The document projection is an in-process representation, not a MongoDB latency claim.",
            "Local synthetic timings do not predict production performance or a universal winner.",
            "Correctness checks, workload metadata, percentiles, and environment are the stable evidence.",
        ],
    }


def write_evidence(state_dir: pathlib.Path) -> pathlib.Path:
    """Persist one inspectable report and a minimal lifecycle marker."""

    state_dir.mkdir(parents=True, exist_ok=True)
    report_path = state_dir / GENERATED_FILES[0]
    report_path.write_text(
        json.dumps(run_suite(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (state_dir / GENERATED_FILES[1]).write_text(
        json.dumps({"status": "ready", "report": report_path.name}, indent=2) + "\n",
        encoding="utf-8",
    )
    return report_path


def reset_generated_state(state_dir: pathlib.Path) -> None:
    """Remove only known generated artifacts, never learner-authored files."""

    for filename in GENERATED_FILES:
        (state_dir / filename).unlink(missing_ok=True)
    if state_dir.exists() and not any(state_dir.iterdir()):
        state_dir.rmdir()
