"""Lifecycle entry point for the defensive database-boundary exercise."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

from database_security_lab import reset_generated_state, write_evidence

LAB_DIR = pathlib.Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[2]
STATE_DIR = LAB_DIR / ".lab-state"


def start() -> None:
    reset_generated_state(STATE_DIR)
    path = write_evidence(STATE_DIR)
    evidence = json.loads(path.read_text(encoding="utf-8"))
    print(
        f"vulnerable baseline crossed tenant: {evidence['vulnerable_baseline']['cross_tenant_exposed']}"
    )
    print(
        f"secure attack result count: {evidence['remediation']['attack_result_count']}"
    )
    print(
        f"least-privilege mutation denied: {evidence['least_privilege']['mutation_denied']}"
    )
    print(f"evidence: {path.relative_to(ROOT)}")


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
    print(
        "pass: exploit, parameterization, tenant scope, redaction, and read-only role verified"
    )


def reset() -> None:
    reset_generated_state(STATE_DIR)
    print("reset: disposable database and evidence removed")


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
