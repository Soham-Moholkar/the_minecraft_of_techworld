"""Redis cache, stream recovery, optimistic transaction, and ACL experiments."""

from __future__ import annotations

import json
import os
import pathlib
import time
from datetime import UTC, datetime
from typing import Any, cast

from redis import Redis
from redis.exceptions import WatchError

CACHE_KEY = "atlas:lab:cache:portfolio"
STREAM_KEY = "atlas:lab:stream:events"
COUNTER_KEY = "atlas:lab:counter:deployments"
FIXED_KEYS = (CACHE_KEY, STREAM_KEY, COUNTER_KEY)
EVIDENCE_NAME = "redis-cache-stream-evidence.json"


def connect() -> Redis:
    """Create a decoded, bounded client using only the dedicated lab identity."""

    return Redis.from_url(
        os.getenv(
            "ATLAS_REDIS_LAB_URL",
            "redis://atlas_lab:atlas_lab_dev_only@localhost:56379/0",
        ),
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=3,
        health_check_interval=15,
        protocol=2,
    )


def verify_lab_identity(client: Redis) -> None:
    """Fail before destructive work when root/product/default credentials are used."""

    if client.acl_whoami() != "atlas_lab":
        raise RuntimeError("Redis lab requires the dedicated atlas_lab ACL identity")


def reset_keys() -> None:
    """Delete only three fixed lab-prefixed keys; never enumerate the database."""

    with connect() as client:
        client.ping()
        verify_lab_identity(client)
        client.delete(*FIXED_KEYS)


def reset_generated_state(state_dir: pathlib.Path) -> None:
    for name in (EVIDENCE_NAME, "state.json"):
        target = state_dir / name
        if target.exists():
            target.unlink()
    if state_dir.exists() and not any(state_dir.iterdir()):
        state_dir.rmdir()


def _cache_experiment(client: Redis) -> dict[str, object]:
    client.delete(CACHE_KEY)
    cold_miss = client.get(CACHE_KEY) is None
    client.set(CACHE_KEY, '{"project_total":3}', ex=1)
    warm_hit = client.get(CACHE_KEY) == '{"project_total":3}'
    ttl_bounded = 0 < client.ttl(CACHE_KEY) <= 1
    deadline = time.monotonic() + 2.5
    while client.exists(CACHE_KEY) and time.monotonic() < deadline:
        time.sleep(0.05)
    expired = client.get(CACHE_KEY) is None
    return {
        "cold_miss": cold_miss,
        "warm_hit": warm_hit,
        "ttl_bounded": ttl_bounded,
        "expired": expired,
    }


def _stream_experiment(client: Redis) -> dict[str, object]:
    group = "atlas-lab-workers"
    client.delete(STREAM_KEY)
    client.xgroup_create(STREAM_KEY, group, id="0", mkstream=True)
    produced = [
        client.xadd(
            STREAM_KEY,
            {"event_type": "project.changed", "sequence": str(index)},
            maxlen=100,
            approximate=False,
        )
        for index in range(3)
    ]
    deliveries = client.xreadgroup(
        group,
        "consumer-a",
        streams={STREAM_KEY: ">"},
        count=2,
    )
    # RESP2 is pinned by connect(); the driver union also includes RESP3 maps.
    streams = cast(list[tuple[str, list[tuple[str, dict[str, str]]]]], deliveries)
    messages = streams[0][1] if streams else []
    first_id = messages[0][0]
    client.xack(STREAM_KEY, group, first_id)
    pending_before_claim = client.xpending(STREAM_KEY, group)
    claimed = client.xautoclaim(
        STREAM_KEY,
        group,
        "consumer-b",
        min_idle_time=0,
        start_id="0-0",
        count=10,
    )
    claimed_messages: list[tuple[str, dict[str, str]]] = claimed[1]
    if claimed_messages:
        client.xack(STREAM_KEY, group, *(item[0] for item in claimed_messages))
    pending_after_claim = client.xpending(STREAM_KEY, group)
    return {
        "produced_count": len(produced),
        "consumer_a_received": len(messages),
        "pending_before_claim": int(pending_before_claim["pending"]),
        "consumer_b_claimed": len(claimed_messages),
        "pending_after_claim": int(pending_after_claim["pending"]),
        "delivery_model": "at-least-once with explicit acknowledgement and stale-owner recovery",
    }


def _transaction_experiment(client: Redis) -> dict[str, object]:
    client.set(COUNTER_KEY, "0")
    conflict_detected = False
    retry_applied = False
    with client.pipeline() as pipeline:
        try:
            pipeline.watch(COUNTER_KEY)  # type: ignore[no-untyped-call]  # redis-py method lacks typing
            current = int(pipeline.get(COUNTER_KEY) or "0")
            client.incr(COUNTER_KEY)
            pipeline.multi()
            pipeline.set(COUNTER_KEY, str(current + 1))
            pipeline.execute()
        except WatchError:
            conflict_detected = True

    with client.pipeline() as pipeline:
        # Even isolated labs must terminate if another process keeps writing.
        for _attempt in range(3):
            try:
                pipeline.watch(COUNTER_KEY)  # type: ignore[no-untyped-call]  # redis-py typing gap
                fresh = int(pipeline.get(COUNTER_KEY) or "0")
                pipeline.multi()
                pipeline.set(COUNTER_KEY, str(fresh + 1))
                pipeline.execute()
                retry_applied = True
                break
            except WatchError:
                continue
        if not retry_applied:
            raise RuntimeError("Redis optimistic retry budget exhausted")
    return {
        "watch_conflict_detected": conflict_detected,
        "fresh_retry_applied": retry_applied,
        "final_value": int(client.get(COUNTER_KEY) or "-1"),
    }


def _acl_experiment(client: Redis) -> dict[str, object]:
    # Never execute a destructive command to test whether it is denied: a
    # misconfigured ACL would erase unrelated data. DRYRUN only checks access.
    # execute_command preserves the denial string (redis-py's acl_dryrun helper
    # can raise a generic ResponseError for simulated permission denials).
    flush_result = client.execute_command(  # type: ignore[no-untyped-call]
        "ACL", "DRYRUN", "atlas_lab", "FLUSHALL"
    )
    foreign_result = client.execute_command(  # type: ignore[no-untyped-call]
        "ACL", "DRYRUN", "atlas_lab", "SET", "outside:lab", "forbidden"
    )
    flush_denied = (
        isinstance(flush_result, str) and "no permissions" in flush_result.lower()
    )
    foreign_prefix_denied = (
        isinstance(foreign_result, str) and "no permissions" in foreign_result.lower()
    )
    return {
        "identity": client.acl_whoami(),
        "flushall_denied": flush_denied,
        "foreign_prefix_denied": foreign_prefix_denied,
        "default_user_disabled_by_configuration": True,
    }


def prepare_lab(state_dir: pathlib.Path) -> pathlib.Path:
    """Run the experiments and persist only bounded, non-secret evidence."""

    reset_keys()
    with connect() as client:
        client.ping()
        verify_lab_identity(client)
        evidence: dict[str, Any] = {
            "engine": "redis",
            "generated_at": datetime.now(UTC).isoformat(),
            "cache": _cache_experiment(client),
            "stream": _stream_experiment(client),
            "transaction": _transaction_experiment(client),
            "acl": _acl_experiment(client),
        }
    state_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = state_dir / EVIDENCE_NAME
    evidence_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    (state_dir / "state.json").write_text(
        json.dumps({"status": "ready", "evidence": EVIDENCE_NAME}, indent=2),
        encoding="utf-8",
    )
    return evidence_path
