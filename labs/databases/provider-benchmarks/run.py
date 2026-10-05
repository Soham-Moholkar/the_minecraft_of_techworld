"""Lifecycle entry point for the Phase 4 provider benchmark suite."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

from provider_benchmark_lab import reset_generated_state, write_evidence

LAB_DIR = pathlib.Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[2]
STATE_DIR = LAB_DIR / ".lab-state"


def start() -> None:
    reset_generated_state(STATE_DIR)
    report_path = write_evidence(STATE_DIR)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    print(f"ready: {len(report['results'])} read patterns measured")
    for result in report["results"]:
        print(
            f"{result['implementation']}: p50={result['p50_ms']} ms; "
            f"p95={result['p95_ms']} ms"
        )
    print(f"evidence: {report_path.relative_to(ROOT)}")


def test() -> None:
    if not (STATE_DIR / "state.json").exists():
        raise RuntimeError("start the lab before testing")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            str(LAB_DIR),
            "-p",
            "test_*.py",
        ],
        cwd=ROOT,
        check=True,
    )
    print("pass: metadata, percentiles, and cross-implementation correctness verified")


def reset() -> None:
    reset_generated_state(STATE_DIR)
    print("reset: benchmark report and lifecycle state removed")


def verify() -> None:
    try:
        start()
        test()
    finally:
        reset()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("start", "test", "reset", "verify"))
    action = parser.parse_args().action
    {"start": start, "test": test, "reset": reset, "verify": verify}[action]()


if __name__ == "__main__":
    main()
