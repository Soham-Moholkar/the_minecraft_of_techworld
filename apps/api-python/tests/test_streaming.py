"""Durability, identity conflict, isolation, fail-closed API and replay contracts."""

import sqlite3
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from atlas_api.auth import Principal, require_principal
from atlas_api.config import Settings, get_settings
from atlas_api.main import app
from atlas_api.streaming import LocalBroker, Record, StreamConflict, UsageEvent, UsageStream


@pytest.fixture
def store() -> Path:
    path = Path("output") / f"stream-test-{uuid4().hex}.db"
    yield path
    path.unlink(missing_ok=True)


def test_sink_replay_crash_conflict_and_quarantine(store: Path) -> None:
    sink = UsageStream(store, "northstar", "sqlite")
    broker = LocalBroker(sink.db, "northstar")
    broker.publish([UsageEvent(event_id="first", units=5), UsageEvent(event_id="bad", units=-1)])
    records = broker.fetch(10)
    with pytest.raises(RuntimeError):
        sink.apply(records, fail_before_commit=True)
    assert sink.snapshot(broker).units == 0
    sink.apply(records)  # Crash after sink commit but before broker acknowledgement.
    sink.close()
    sink = UsageStream(store, "northstar", "sqlite")
    broker = LocalBroker(sink.db, "northstar")
    result = sink.consume(broker, 10)
    assert (result.units, result.accepted, result.quarantined, result.partitions[0].lag) == (
        5,
        1,
        1,
        0,
    )
    sink.apply([Record(2, b'{"event_id":"first","units":9}'), Record(3, b"secret-invalid")])
    assert sink.snapshot(broker).units == 5
    assert sink.snapshot(broker).quarantined == 3
    assert "secret-invalid" not in str(
        sink.db.execute("SELECT * FROM stream_quarantine").fetchall()
    )
    sink.close()


def test_atomic_publish_and_tenant_boundaries(store: Path) -> None:
    sink = UsageStream(store, "northstar", "sqlite")
    broker = LocalBroker(sink.db, "northstar")
    broker.publish([UsageEvent(event_id="one", units=4)])
    with pytest.raises(StreamConflict):
        broker.publish([UsageEvent(event_id="two", units=8), UsageEvent(event_id="one", units=7)])
    assert broker.position().end == 1
    broker.publish([UsageEvent(event_id="one", units=4)])
    assert broker.position().end == 1
    assert sink.consume(broker, 1).units == 4
    other = UsageStream(store, "other-tenant", "sqlite")
    assert other.snapshot(LocalBroker(other.db, "other-tenant")).units == 0
    other.close()
    sink.close()


def test_duplicate_replay_at_quota_and_new_write_rolls_back(store: Path) -> None:
    sink = UsageStream(store, "northstar", "sqlite")
    try:
        with sink.db:
            sink.db.executemany(
                "INSERT INTO stream_effects VALUES (?,?,?,?)",
                [("northstar", "sqlite", f"item-{i}", 1) for i in range(10000)],
            )
        sink.apply([Record(0, b'{"event_id":"item-0","units":1}')])
        with pytest.raises(StreamConflict):
            sink.apply([Record(1, b'{"event_id":"new-event","units":1}')])
        assert sink.db.execute("SELECT COUNT(*) FROM stream_effects").fetchone()[0] == 10000
    finally:
        sink.close()


def test_api_auth_gating_validation_and_real_lag(
    client: TestClient,
    auth_headers: dict[str, str],
    store: Path,
) -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(
        streaming_enabled=True,
        streaming_store=str(store),
    )
    assert client.get("/v1/streaming/usage").status_code == 401
    assert (
        client.post(
            "/v1/streaming/usage/events", headers=auth_headers, content=b" " * 16001
        ).status_code
        == 413
    )
    response = client.post(
        "/v1/streaming/usage/events",
        headers=auth_headers,
        json={"events": [{"event_id": "one", "units": 7}]},
    )
    assert response.status_code == 200
    assert response.json()["partitions"][0]["lag"] == 1
    result = client.post("/v1/streaming/usage/consume", headers=auth_headers, json={"limit": 1})
    assert result.json()["units"] == 7
    assert result.json()["partitions"][0]["lag"] == 0
    assert result.headers["Cache-Control"] == "no-store"
    assert client.post("/v1/streaming/usage/lakehouse", headers=auth_headers).status_code == 403
    for body in ({"limit": 0}, {"limit": True}, {"limit": 101}, {"tenant": "other"}):
        assert (
            client.post("/v1/streaming/usage/consume", headers=auth_headers, json=body).status_code
            == 422
        )
    app.dependency_overrides[require_principal] = lambda: Principal("reader", "other", ("reader",))
    assert client.get("/v1/streaming/usage", headers=auth_headers).status_code == 403
    app.dependency_overrides.pop(require_principal)
    app.dependency_overrides[get_settings] = lambda: Settings(streaming_enabled=False)
    assert client.get("/v1/streaming/usage", headers=auth_headers).status_code == 403
    app.dependency_overrides[get_settings] = lambda: Settings(
        streaming_enabled=True,
        environment="production",
        streaming_store=str(store),
    )
    assert client.get("/v1/streaming/usage", headers=auth_headers).status_code == 403


def test_api_provider_failure_redacted(
    client: TestClient,
    auth_headers: dict[str, str],
    store: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(
        streaming_enabled=True,
        streaming_store=str(store),
        streaming_provider="kafka",
    )

    def unavailable(*args: object) -> None:
        raise RuntimeError("password-secret broker-url")

    monkeypatch.setattr("atlas_api.streaming_routes.KafkaBroker", unavailable)
    response = client.get("/v1/streaming/usage", headers=auth_headers)
    assert response.status_code == 503
    assert "password" not in response.text
    # Closed resources leave the SQLite store available after provider failure.
    db = sqlite3.connect(store)
    try:
        db.execute("BEGIN IMMEDIATE")
    finally:
        db.close()
