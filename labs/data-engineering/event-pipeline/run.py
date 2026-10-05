"""Offline lifecycle for the durable usage-event pipeline."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from pipeline import write_evidence

LAB = Path(__file__).resolve().parent
STATE = LAB / ".lab-state"


def reset() -> None:
    # Fixed generated filenames only: reset never accepts an operator path or
    # recursively deletes a tree. Unrecognized files prevent directory removal.
    for name in ("pipeline.db", "pipeline.db-journal", "evidence.json"):
        (STATE / name).unlink(missing_ok=True)
    if STATE.exists():
        STATE.rmdir()
    print(json.dumps({"event": "pipeline_reset"}))


def start() -> None:
    reset()
    evidence = write_evidence(STATE)
    print(evidence.read_text(encoding="utf-8"))


def test() -> None:
    if not (STATE / "evidence.json").is_file():
        raise RuntimeError("start the lab before testing")
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(LAB),
                    "-p", "test_*.py"], check=True)


def verify() -> None:
    try:
        start()
        test()
    finally:
        reset()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("start", "test", "reset", "verify"))
    {"start": start, "test": test, "reset": reset, "verify": verify}[parser.parse_args().action]()
