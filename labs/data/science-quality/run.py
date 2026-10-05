"""Resettable dirty-data and three-scale aggregation benchmark using product code."""

from __future__ import annotations

import argparse
import json
import pathlib
import platform
import subprocess
import sys

from atlas_api.data_science import generate_sample, profile_csv

LAB = pathlib.Path(__file__).resolve().parent
STATE = LAB / ".lab-state"


def reset() -> None:
    for name in ("sample.csv", "evidence.json"):
        (STATE / name).unlink(missing_ok=True)
    if STATE.exists() and not any(STATE.iterdir()):
        STATE.rmdir()


def start() -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    reports = []
    for size in (100, 1000, 5000):
        _, profile, checksum = profile_csv(generate_sample(size))
        reports.append(
            {
                "rows": size,
                "checksum": checksum,
                "profile": profile.model_dump(mode="json"),
            }
        )
    (STATE / "sample.csv").write_text(generate_sample(), encoding="utf-8")
    (STATE / "evidence.json").write_text(
        json.dumps(
            {
                "environment": {
                    "python": platform.python_version(),
                    "platform": platform.platform(),
                },
                "scale_reports": reports,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print("ready: 100/1000/5000 rows; three real engines; known dirty-data counts")


def test() -> None:
    subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(LAB)], check=True
    )


def verify() -> None:
    try:
        start()
        test()
    finally:
        reset()
    print(
        "pass: quality counts, cross-engine parity, statistical evidence, and clean reset"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("start", "test", "reset", "verify"))
    {"start": start, "test": test, "reset": reset, "verify": verify}[
        parser.parse_args().action
    ]()
