"""Lifecycle entry point for the disposable PostgreSQL concurrency lab."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import time

import psycopg

from postgresql_concurrency_lab import (
    connect,
    prepare_lab,
    reset_generated_state,
    reset_schema,
)

LAB_DIR = pathlib.Path(__file__).resolve().parent
REPOSITORY_ROOT = LAB_DIR.parents[2]
STATE_DIR = LAB_DIR / ".lab-state"


def ensure_postgres() -> None:
    """Reuse a healthy server or start the repository-owned Compose service."""

    try:
        with connect():
            return
    except psycopg.OperationalError:
        subprocess.run(  # noqa: S603 - fixed repository-owned Compose arguments
            ["docker", "compose", "up", "-d", "postgres"],
            cwd=REPOSITORY_ROOT,
            check=True,
        )

    # This is service-readiness polling, not a correctness assertion. Experiment
    # results never depend on how quickly the container starts.
    for _ in range(20):
        try:
            with connect():
                return
        except psycopg.OperationalError:
            time.sleep(1)
    raise RuntimeError("PostgreSQL did not become ready for the lab")


def start() -> None:
    """Run all three experiments and leave their evidence inspectable."""

    ensure_postgres()
    reset_generated_state(STATE_DIR)
    evidence_path = prepare_lab(STATE_DIR)
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    print(
        "row lock: "
        f"SQLSTATE {evidence['row_lock']['first_attempt_sqlstate']}; retry committed"
    )
    print(
        "deadlock: "
        f"{evidence['deadlock']['deadlock_count']} victim; "
        f"{evidence['deadlock']['committed_count']} commit"
    )
    print(
        "serializable: "
        f"{evidence['serializable']['serialization_failure_count']} retryable failure; "
        f"final on-call count={evidence['serializable']['final_on_call_count']}"
    )
    print(f"evidence: {evidence_path.relative_to(REPOSITORY_ROOT)}")


def test() -> None:
    """Run regression tests after the lab lifecycle has been started."""

    if not (STATE_DIR / "state.json").exists():
        raise RuntimeError("start the lab before testing")
    subprocess.run(  # noqa: S603 - fixed interpreter and repository-owned test path
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
        cwd=REPOSITORY_ROOT,
        check=True,
    )
    print("pass: row lock, deadlock, Serializable retry, evidence, and reset")


def reset() -> None:
    """Remove the fixed lab schema and only this lab's generated files."""

    ensure_postgres()
    reset_schema()
    reset_generated_state(STATE_DIR)
    print("reset: atlas_concurrency_lab schema and generated evidence removed")


def verify() -> None:
    """Exercise the full lifecycle and guarantee cleanup after failures."""

    try:
        start()
        test()
    finally:
        reset()


def parse_args() -> argparse.Namespace:
    """Parse the deliberately allowlisted lifecycle commands."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("start", "test", "reset", "verify"))
    return parser.parse_args()


def main() -> None:
    """Dispatch exactly one lifecycle action."""

    actions = {"start": start, "test": test, "reset": reset, "verify": verify}
    actions[parse_args().action]()


if __name__ == "__main__":
    main()
