"""Failure, memory, and packaging evidence for the Python mastery vertical."""

from __future__ import annotations

import shutil
import tempfile
import tracemalloc
import zipapp
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Final

LAB_ROOT: Final = Path(__file__).resolve().parent


@dataclass(frozen=True, slots=True)
class ProcessBatchResult:
    """Keep successful values useful even when an independent item fails."""

    succeeded: dict[int, int]
    failed: dict[int, str]


@dataclass(frozen=True, slots=True)
class MemoryEvidence:
    total: int
    peak_bytes: int
    item_count: int


def square_or_fail(value: int) -> int:
    """A picklable worker demonstrates how process failures cross the boundary."""

    if value < 0:
        raise ValueError("negative work item")
    return value * value


def parallel_squares_resilient(values: list[int]) -> ProcessBatchResult:
    """Collect failures per item instead of discarding the whole process batch."""

    succeeded: dict[int, int] = {}
    failed: dict[int, str] = {}
    with ProcessPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(square_or_fail, value): value for value in values}
        for future in as_completed(futures):
            value = futures[future]
            try:
                succeeded[value] = future.result()
            except ValueError as exc:
                failed[value] = str(exc)
    return ProcessBatchResult(succeeded=succeeded, failed=failed)


def measure_generator_memory(count: int = 10_000) -> MemoryEvidence:
    """Measure a lazy numeric workload with Python's built-in allocator tracer."""

    if count < 0:
        raise ValueError("count must be non-negative")
    tracemalloc.start()
    try:
        total = sum(value * value for value in range(count))
        _, peak_bytes = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return MemoryEvidence(total=total, peak_bytes=peak_bytes, item_count=count)


def build_zipapp(destination: Path) -> Path:
    """Build an executable, dependency-free Python archive from owned sources."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        staging = Path(directory)
        shutil.copy2(LAB_ROOT / "mastery.py", staging / "mastery.py")
        (staging / "__main__.py").write_text(
            "from mastery import WorkItem, weighted_total\n"
            "items = [WorkItem('packaged', 8.0)]\n"
            "total, _ = weighted_total(items)\n"
            "print(f'atlas-python-mastery total={total:.2f}')\n",
            encoding="utf-8",
        )
        zipapp.create_archive(staging, destination, interpreter="/usr/bin/env python3")
    return destination
