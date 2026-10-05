"""Resettable experiment that exercises the product's model comparison code."""

from __future__ import annotations

import argparse
import json
import pathlib
import platform
import subprocess
import sys

from atlas_api.data_science import clean_csv, generate_sample
from atlas_api.machine_learning import train_experiment

LAB = pathlib.Path(__file__).resolve().parent
STATE = LAB / ".lab-state"


def reset() -> None:
    (STATE / "evidence.json").unlink(missing_ok=True)
    if STATE.exists() and not any(STATE.iterdir()):
        STATE.rmdir()


def start() -> None:
    rows, _, _, _ = clean_csv(generate_sample(120))
    report = train_experiment(rows)
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / "evidence.json").write_text(
        json.dumps(
            {
                "environment": {"python": platform.python_version(), "platform": platform.platform()},
                "features": ["requests", "day", "service"],
                "excluded_target_source": "cost",
                "report": report.model_dump(mode="json"),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print("ready: deterministic split; two sklearn pipelines; NumPy baseline; permutation effects")


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
    print("pass: shared holdout, bounded metrics, target exclusion, interpretation, and clean reset")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("start", "test", "reset", "verify"))
    {"start": start, "test": test, "reset": reset, "verify": verify}[
        parser.parse_args().action
    ]()
