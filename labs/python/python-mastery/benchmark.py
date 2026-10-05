"""Repeatable compute, memory, thread, and process-pool comparison evidence."""

import statistics
import time
import timeit
from collections.abc import Callable

from failure_modes import measure_generator_memory, parallel_squares_resilient
from mastery import WorkItem, threaded_squares, weighted_total

ITEMS = [WorkItem(str(index), float(index)) for index in range(10_000)]
CONCURRENT_VALUES = list(range(2_000))


def elapsed(function: Callable[[], object]) -> float:
    started = time.perf_counter()
    function()
    return time.perf_counter() - started


def main() -> None:
    samples = timeit.repeat(lambda: weighted_total(ITEMS), number=20, repeat=5)
    thread_seconds = elapsed(lambda: threaded_squares(CONCURRENT_VALUES))
    process_seconds = elapsed(lambda: parallel_squares_resilient(CONCURRENT_VALUES))
    memory = measure_generator_memory(10_000)
    print(f"weighted_median_seconds={statistics.median(samples):.6f}")
    print(f"weighted_min_seconds={min(samples):.6f}")
    print(f"thread_seconds={thread_seconds:.6f}")
    print(f"process_seconds={process_seconds:.6f}")
    print(f"generator_peak_bytes={memory.peak_bytes}")
    print("iterations_per_weighted_sample=20")


if __name__ == "__main__":
    main()
