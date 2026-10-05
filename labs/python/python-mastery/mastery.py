"""Executable Python progression from typed functions to measured concurrency."""

from __future__ import annotations

import asyncio
import cProfile
import functools
import io
import pstats
import time
from collections.abc import Callable, Generator, Iterable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import ParamSpec, Protocol, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


@dataclass(frozen=True, slots=True)
class WorkItem:
    """Immutable value object shared by every example."""

    id: str
    value: float


class WorkSink(Protocol):
    """Structural interface: implementations need no shared base class."""

    def write(self, item: WorkItem) -> None: ...


class MemorySink:
    def __init__(self) -> None:
        self.items: list[WorkItem] = []

    def write(self, item: WorkItem) -> None:
        self.items.append(item)


def normalize(values: Iterable[float]) -> list[float]:
    materialized = list(values)
    total = sum(materialized)
    if total == 0:
        raise ValueError("normalization requires a non-zero total")
    return [value / total for value in materialized]


def batches(items: list[WorkItem], size: int) -> Generator[list[WorkItem]]:
    if size < 1:
        raise ValueError("batch size must be positive")
    for index in range(0, len(items), size):
        yield items[index : index + size]


def profiled(function: Callable[P, R]) -> Callable[P, tuple[R, float]]:
    """Preserve the decorated signature and return elapsed wall time."""

    @functools.wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> tuple[R, float]:
        started = time.perf_counter()
        result = function(*args, **kwargs)
        return result, time.perf_counter() - started

    return wrapper


@profiled
def weighted_total(items: Iterable[WorkItem]) -> float:
    return sum(item.value * 1.25 for item in items)


async def enrich(item: WorkItem) -> WorkItem:
    """Represent an I/O wait without requiring external network access."""

    await asyncio.sleep(0)
    return WorkItem(id=item.id, value=item.value * 2)


async def enrich_all(items: Iterable[WorkItem]) -> list[WorkItem]:
    return list(await asyncio.gather(*(enrich(item) for item in items)))


def cpu_square(value: int) -> int:
    return value * value


def threaded_squares(values: Iterable[int]) -> list[int]:
    with ThreadPoolExecutor(max_workers=2) as executor:
        return list(executor.map(cpu_square, values))


def parallel_squares(values: Iterable[int]) -> list[int]:
    with ProcessPoolExecutor(max_workers=2) as executor:
        return list(executor.map(cpu_square, values))


def profile_workload(destination: Path, count: int = 5_000) -> str:
    profiler = cProfile.Profile()
    profiler.enable()
    weighted_total(WorkItem(str(index), float(index)) for index in range(count))
    profiler.disable()
    stream = io.StringIO()
    pstats.Stats(profiler, stream=stream).sort_stats("cumulative").print_stats(8)
    report = stream.getvalue()
    destination.write_text(report, encoding="utf-8")
    return report
