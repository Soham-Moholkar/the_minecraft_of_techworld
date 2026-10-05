"""Real export validation, tenant receipts, stale evidence and authority gates."""

import hashlib
import importlib.util
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from atlas_api.auth import Principal, require_principal
from atlas_api.config import Settings, get_settings
from atlas_api.main import app
from atlas_api.streaming import LocalBroker, UsageEvent, UsageStream
from atlas_api.streaming_export import export_parquet
from atlas_api.usage_compute import read_receipt


def receipt(digest: str, tenant: str = "northstar") -> dict[str, object]:
    return dict(
        schema_version=1,
        provider="spark",
        version="4.2.0",
        tenant=tenant,
        source_provider="sqlite",
        source_digest=digest,
        rows=1,
        units=4,
        mode="local",
        partitions=1,
        duration_ms=100,
        finished_at=datetime.now(UTC).isoformat(),
    )


def save(root: Path, value: dict[str, object]) -> Path:
    path = root / "northstar" / "sqlite" / "spark.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf8")
    return path


def test_actual_export_receipt_and_staleness(tmp_path: Path) -> None:
    settings = Settings(
        streaming_enabled=True,
        usage_compute_enabled=True,
        streaming_store=str(tmp_path / "stream.db"),
        usage_compute_store=str(tmp_path / "compute"),
    )
    sink = UsageStream(Path(settings.streaming_store), "northstar", "sqlite")
    broker = LocalBroker(sink.db, "northstar")
    broker.publish([UsageEvent(event_id="accepted-one", units=4)])
    sink.consume(broker, 10)
    _, digest = export_parquet(sink)
    save(Path(settings.usage_compute_store), receipt(digest))
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[require_principal] = lambda: Principal(
        subject="operator", organization_slug="northstar", roles=["owner"]
    )
    try:
        with TestClient(app) as client:
            result = client.get("/v1/pipelines/usage/compute")
            assert result.status_code == 200
            assert result.json()["source_current"] is True
            assert result.headers["cache-control"] == "no-store"
            save(Path(settings.usage_compute_store), receipt(digest) | {"units": 3})
            assert client.get("/v1/pipelines/usage/compute").status_code == 503
            save(Path(settings.usage_compute_store), receipt(digest))
            broker.publish([UsageEvent(event_id="accepted-two", units=3)])
            sink.consume(broker, 10)
            assert client.get("/v1/pipelines/usage/compute").json()["source_current"] is False
            assert (
                client.post("/v1/pipelines/usage/compute", json={"sql": "SELECT 1"}).status_code
                == 405
            )
    finally:
        sink.close()
        app.dependency_overrides.clear()


@pytest.mark.parametrize(
    "changed",
    [dict(tenant="other"), dict(units=True), dict(rows=10001), {"private_field": "never-project"}],
)
def test_rejects_namespace_bounds_coercion_and_private_fields(
    tmp_path: Path, changed: dict[str, object]
) -> None:
    save(tmp_path, receipt("a" * 64) | changed)
    with pytest.raises(ValueError):
        read_receipt(tmp_path, "northstar", "sqlite")
    assert read_receipt(tmp_path, "other", "sqlite") is None


def test_empty_and_oversized_receipts(tmp_path: Path) -> None:
    assert read_receipt(tmp_path, "northstar", "sqlite") is None
    path = save(tmp_path, receipt("a" * 64))
    path.write_bytes(b"x" * 8193)
    with pytest.raises(ValueError, match="byte bound"):
        read_receipt(tmp_path, "northstar", "sqlite")


@pytest.mark.parametrize(
    "environment,enabled,roles",
    [
        ("production", True, ["owner"]),
        ("development", False, ["owner"]),
        ("development", True, ["viewer"]),
    ],
)
def test_independent_authority_gate(environment: str, enabled: bool, roles: list[str]) -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(
        environment=environment, usage_compute_enabled=enabled, streaming_enabled=True
    )
    app.dependency_overrides[require_principal] = lambda: Principal(
        subject="operator", organization_slug="northstar", roles=roles
    )
    try:
        with TestClient(app) as client:
            assert client.get("/v1/pipelines/usage/compute").status_code == 403
    finally:
        app.dependency_overrides.clear()


def test_spark_source_validator_uses_real_parquet(tmp_path: Path) -> None:
    path = Path(__file__).resolve().parents[3] / "infra/spark/usage_job.py"
    spec = importlib.util.spec_from_file_location("atlas_usage_spark_job", path)
    assert spec and spec.loader
    worker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(worker)
    sink = UsageStream(tmp_path / "source.db", "northstar", "sqlite")
    try:
        raw, digest = export_parquet(sink)
        assert worker.validate_source(raw, digest, "northstar") == ("sqlite", 0, 0)
        with pytest.raises(ValueError, match="tenant/provider"):
            worker.validate_source(raw, digest, "other")
        with pytest.raises(ValueError, match="digest"):
            worker.validate_source(raw + b"tamper", digest, "northstar")
        assert hashlib.sha256(raw).hexdigest() == digest
    finally:
        sink.close()
