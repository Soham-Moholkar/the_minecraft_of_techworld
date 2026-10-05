"""Resettable lifecycle for the Python mastery evidence lab."""

import asyncio
import json
import pathlib
import subprocess
import sys

from failure_modes import (
    build_zipapp,
    measure_generator_memory,
    parallel_squares_resilient,
)
from mastery import (
    WorkItem,
    enrich_all,
    profile_workload,
    threaded_squares,
    weighted_total,
)

ROOT = pathlib.Path(__file__).resolve().parents[3]
STATE = pathlib.Path(__file__).with_name(".state.json")
PROFILE = pathlib.Path(__file__).with_name("profile.txt")
PACKAGE = pathlib.Path(__file__).with_name("dist") / "atlas-python-mastery.pyz"


def run(action: str) -> None:
    if action == "start":
        items = [WorkItem("alpha", 2.0), WorkItem("beta", 3.0)]
        enriched = asyncio.run(enrich_all(items))
        total, elapsed = weighted_total(enriched)
        profile_workload(PROFILE, count=1_000)
        memory = measure_generator_memory(5_000)
        processes = parallel_squares_resilient([2, -1, 3])
        build_zipapp(PACKAGE)
        STATE.write_text(
            json.dumps(
                {
                    "status": "ready",
                    "total": total,
                    "elapsed_seconds": elapsed,
                    "peak_bytes": memory.peak_bytes,
                    "process_failures": processes.failed,
                    "package": str(PACKAGE.relative_to(ROOT)),
                }
            ),
            encoding="utf-8",
        )
        print(
            f"ready: total={total:.2f}; threaded={threaded_squares([2, 3, 4])}; "
            f"isolated_failures={len(processes.failed)}; peak_bytes={memory.peak_bytes}"
        )
    elif action == "test":
        if not STATE.exists():
            raise RuntimeError("start the lab before testing")
        subprocess.run(  # noqa: S603 - fixed interpreter and allowlisted local test path
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                str(pathlib.Path(__file__).parent),
                "-p",
                "test_*.py",
            ],
            cwd=ROOT,
            check=True,
        )
        print(
            "pass: functions, OOP, typing, generators, decorators, async, "
            "threads, processes, randomized invariants, memory, packaging, "
            "and profiling"
        )
    elif action == "reset":
        STATE.unlink(missing_ok=True)
        PROFILE.unlink(missing_ok=True)
        PACKAGE.unlink(missing_ok=True)
        # Preserve the directory if a learner has placed any of their own files in it.
        if PACKAGE.parent.exists() and not any(PACKAGE.parent.iterdir()):
            PACKAGE.parent.rmdir()
        print("reset: generated state, profile, and package evidence removed")
    elif action == "verify":
        try:
            run("start")
            run("test")
            subprocess.run(  # noqa: S603 - fixed interpreter and repository-owned script
                [sys.executable, str(pathlib.Path(__file__).with_name("benchmark.py"))],
                cwd=ROOT,
                check=True,
            )
        finally:
            run("reset")
    else:
        raise ValueError(f"unsupported action: {action}")


if __name__ == "__main__":
    run(sys.argv[1])
