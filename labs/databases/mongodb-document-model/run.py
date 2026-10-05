"""Lifecycle entry point for the optional MongoDB document-model lab."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import time

from pymongo.errors import PyMongoError

from mongodb_document_lab import connect, prepare_lab, reset_collections, reset_generated_state

LAB_DIR = pathlib.Path(__file__).resolve().parent
REPOSITORY_ROOT = LAB_DIR.parents[2]
STATE_DIR = LAB_DIR / ".lab-state"


def ensure_mongodb() -> None:
    """Reuse the database or start only the optional MongoDB Compose service."""

    try:
        with connect() as client:
            client["atlas_document_lab"].command("ping")
            return
    except (PyMongoError, OSError):
        subprocess.run(  # noqa: S603 - fixed repository-owned Compose arguments
            ["docker", "compose", "--profile", "database", "up", "-d", "mongodb"],
            cwd=REPOSITORY_ROOT,
            check=True,
        )
    for _ in range(30):
        try:
            with connect() as client:
                client["atlas_document_lab"].command("ping")
                return
        except (PyMongoError, OSError):
            time.sleep(1)
    raise RuntimeError("MongoDB did not become ready for the lab")


def start() -> None:
    ensure_mongodb()
    reset_generated_state(STATE_DIR)
    evidence_path = prepare_lab(STATE_DIR)
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    print(f"index: compound selected={evidence['index']['selected_compound_index']}")
    print(f"validation: code={evidence['validation']['error_code']}")
    print("atomic update: stale version rejected; fresh retry applied")
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
    ensure_mongodb()
    reset_collections()
    reset_generated_state(STATE_DIR)
    print("reset: two fixed MongoDB lab collections and generated evidence removed")


def verify() -> None:
    started = False
    try:
        start()
        started = True
        test()
    finally:
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
