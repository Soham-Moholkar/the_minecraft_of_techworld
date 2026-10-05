"""Resettable Phase 7 compatibility suite for four applied model families."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

from atlas_api.applied_training import run_applied_isolated

LAB = pathlib.Path(__file__).resolve().parent
STATE = LAB / ".lab-state"


def reset() -> None:
    (STATE / "evidence.json").unlink(missing_ok=True)
    if STATE.exists() and not any(STATE.iterdir()):
        STATE.rmdir()


def start() -> None:
    report = run_applied_isolated()
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / "evidence.json").write_text(
        json.dumps(report.model_dump(mode="json"), indent=2) + "\n", encoding="utf-8"
    )
    print("ready: CNN, GRU, Transformer, and recommendation evidence")


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
    print("pass: four model families improve on fixed baselines and reset cleanly")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("start", "test", "reset", "verify"))
    {"start": start, "test": test, "reset": reset, "verify": verify}[
        parser.parse_args().action
    ]()
