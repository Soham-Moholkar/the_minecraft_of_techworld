"""Lifecycle entry point for the optional Redis cache and streams lab."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import time

from redis.exceptions import RedisError

from redis_cache_stream_lab import (
    connect,
    prepare_lab,
    reset_generated_state,
    reset_keys,
    verify_lab_identity,
)

LAB_DIR = pathlib.Path(__file__).resolve().parent
REPOSITORY_ROOT = LAB_DIR.parents[2]
STATE_DIR = LAB_DIR / ".lab-state"


def ensure_redis() -> None:
    """Reuse a healthy lab endpoint or start only the optional Redis service."""

    try:
        with connect() as client:
            client.ping()
            verify_lab_identity(client)
            return
    except (RedisError, OSError):
        subprocess.run(  # noqa: S603 - fixed repository-owned Compose arguments
            ["docker", "compose", "--profile", "database", "up", "-d", "redis"],
            cwd=REPOSITORY_ROOT,
            check=True,
        )
    for _ in range(30):
        try:
            with connect() as client:
                client.ping()
                verify_lab_identity(client)
                return
        except (RedisError, OSError):
            time.sleep(1)
    raise RuntimeError("Redis did not become ready for the lab")


def start() -> None:
    ensure_redis()
    reset_generated_state(STATE_DIR)
    evidence_path = prepare_lab(STATE_DIR)
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    print(
        f"cache: warm_hit={evidence['cache']['warm_hit']} expired={evidence['cache']['expired']}"
    )
    print(f"stream: recovered={evidence['stream']['consumer_b_claimed']}")
    print(f"transaction: final={evidence['transaction']['final_value']}")
    print(f"evidence: {evidence_path.relative_to(REPOSITORY_ROOT)}")


def test() -> None:
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


def reset() -> None:
    ensure_redis()
    reset_keys()
    reset_generated_state(STATE_DIR)
    print("reset: three fixed Redis lab keys and generated evidence removed")


def verify() -> None:
    # Confirm the endpoint and identity before entering cleanup. Once experiments
    # can write, reset must run even if a mid-experiment assertion/command fails.
    ensure_redis()
    try:
        start()
        test()
    finally:
        try:
            reset_keys()
        finally:
            reset_generated_state(STATE_DIR)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("start", "test", "reset", "verify"))
    actions = {"start": start, "test": test, "reset": reset, "verify": verify}
    actions[parser.parse_args().action]()


if __name__ == "__main__":
    main()
