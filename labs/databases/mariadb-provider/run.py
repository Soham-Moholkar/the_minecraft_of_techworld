"""Lifecycle entry point for the optional MariaDB provider lab."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import time

import pymysql  # type: ignore[import-untyped]

from mariadb_provider_lab import connect, prepare_lab, reset_generated_state, reset_tables

LAB_DIR = pathlib.Path(__file__).resolve().parent
REPOSITORY_ROOT = LAB_DIR.parents[2]
STATE_DIR = LAB_DIR / ".lab-state"


def ensure_mariadb() -> None:
    """Reuse a live lab service or start only the optional Compose profile."""

    try:
        with connect(autocommit=True):
            return
    except (pymysql.MySQLError, OSError):
        subprocess.run(  # noqa: S603 - fixed repository-owned Compose arguments
            ["docker", "compose", "--profile", "database", "up", "-d", "mariadb"],
            cwd=REPOSITORY_ROOT,
            check=True,
        )
    for _ in range(30):
        try:
            with connect(autocommit=True):
                return
        except (pymysql.MySQLError, OSError):
            time.sleep(1)
    raise RuntimeError("MariaDB did not become ready for the lab")


def start() -> None:
    ensure_mariadb()
    reset_generated_state(STATE_DIR)
    evidence_path = prepare_lab(STATE_DIR)
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    print(f"index: selected={evidence['index']['selected_index']}; results equal")
    print("repeatable read: stable snapshot; fresh transaction observed commit")
    print(
        "lock recovery: "
        f"error {evidence['lock_recovery']['first_attempt_error_code']}; retry committed"
    )
    print(f"evidence: {evidence_path.relative_to(REPOSITORY_ROOT)}")


def test() -> None:
    if not (STATE_DIR / "state.json").exists():
        raise RuntimeError("start the lab before testing")
    subprocess.run(  # noqa: S603 - fixed interpreter and repository-owned test path
        [sys.executable, "-m", "unittest", "discover", "-s", str(LAB_DIR), "-p", "test_*.py"],
        cwd=REPOSITORY_ROOT,
        check=True,
    )


def reset() -> None:
    ensure_mariadb()
    reset_tables()
    reset_generated_state(STATE_DIR)
    print("reset: two fixed atlas_provider tables and generated evidence removed")


def verify() -> None:
    started = False
    try:
        start()
        started = True
        test()
    finally:
        # If service startup itself fails, there are no database objects to clean.
        # Avoid a second startup attempt obscuring the original infrastructure error.
        if started:
            reset()
        else:
            reset_generated_state(STATE_DIR)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("start", "test", "reset", "verify"))
    actions = {"start": start, "test": test, "reset": reset, "verify": verify}
    actions[parser.parse_args().action]()


if __name__ == "__main__":
    main()
