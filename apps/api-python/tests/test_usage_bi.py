"""Actual aggregate projection/read-only SQL and fixed-dashboard boundaries."""

import importlib.util
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from atlas_api.auth import Principal, require_principal
from atlas_api.config import Settings, get_settings
from atlas_api.main import app
from atlas_api.streaming import LocalBroker, UsageEvent, UsageStream
from atlas_api.streaming_export import export_parquet
from atlas_api.superset_status import read_dashboard

ROOT = Path(__file__).resolve().parents[3]


def test_real_projection_is_numeric_tenant_scoped_and_read_only(tmp_path: Path) -> None:
    spec = importlib.util.spec_from_file_location(
        "atlas_bi_publisher", ROOT / "scripts/publish_usage_bi.py"
    )
    assert spec and spec.loader
    publisher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(publisher)
    sink = UsageStream(tmp_path / "source.db", "northstar", "sqlite")
    try:
        broker = LocalBroker(sink.db, "northstar")
        broker.publish([UsageEvent(event_id="private-counter-id", units=4)])
        sink.consume(broker, 10)
        raw, digest = export_parquet(sink)
        path = publisher.publish(raw, digest, "northstar", tmp_path / "bi")
        engine = create_engine(f"sqlite:///file:{path.as_posix()}?mode=ro&uri=true")
        try:
            with engine.connect() as db:
                row = db.execute(
                    text("SELECT tenant,rows,units,source_digest FROM usage_rollup")
                ).one()
                assert tuple(row) == ("northstar", 1, 4, digest)
                assert "private-counter-id" not in str(row)
                with pytest.raises(OperationalError, match="readonly"):
                    db.execute(text("UPDATE usage_rollup SET units=0"))
            # Re-publication replaces one aggregate, rather than appending it.
            publisher.publish(raw, digest, "northstar", tmp_path / "bi")
            with engine.connect() as db:
                assert db.execute(text("SELECT COUNT(*) FROM usage_rollup")).scalar() == 1
            with pytest.raises(ValueError, match="tenant/provider"):
                publisher.publish(raw, digest, "other", tmp_path / "bi")
            assert not (tmp_path / "bi/other").exists()
        finally:
            engine.dispose()
    finally:
        sink.close()


def test_dashboard_projection_excludes_private_fields() -> None:
    calls: list[httpx.Request] = []

    def upstream(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(
            200,
            json={
                "result": {
                    "id": 7,
                    "dashboard_title": "ATLAS usage northstar",
                    "published": False,
                    "owners": [{"email": "private"}],
                    "json_metadata": "private",
                }
            },
        )

    with httpx.Client(
        base_url="http://superset", transport=httpx.MockTransport(upstream)
    ) as client:
        result = read_dashboard(client, 7, "northstar")
    assert result.published is False
    assert "private" not in result.model_dump_json()
    assert calls[0].method == "GET" and calls[0].url.path == "/api/v1/dashboard/7"
    assert calls[0].url.params["q"] == "(columns:!(id,dashboard_title,published))"


@pytest.mark.parametrize("failure", ["identity", "tenant", "bytes"])
def test_dashboard_rejects_provider_namespace_and_size(failure: str) -> None:
    def upstream(request: httpx.Request) -> httpx.Response:
        if failure == "bytes":
            return httpx.Response(200, content=b"x" * 64001)
        return httpx.Response(
            200,
            json={
                "result": {
                    "id": 8 if failure == "identity" else 7,
                    "dashboard_title": "ATLAS usage other"
                    if failure == "tenant"
                    else "ATLAS usage northstar",
                    "published": True,
                }
            },
        )

    with (
        httpx.Client(base_url="http://superset", transport=httpx.MockTransport(upstream)) as client,
        pytest.raises(ValueError),
    ):
        read_dashboard(client, 7, "northstar")


@pytest.mark.parametrize(
    "environment,roles,tenant",
    [
        ("production", ["owner"], "northstar"),
        ("development", ["viewer"], "northstar"),
        ("development", ["owner"], "other"),
    ],
)
def test_dashboard_authority_gate(environment: str, roles: list[str], tenant: str) -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(
        environment=environment, superset_enabled=True
    )
    app.dependency_overrides[require_principal] = lambda: Principal(
        subject="operator", organization_slug=tenant, roles=roles
    )
    try:
        with TestClient(app) as client:
            response = client.get("/v1/pipelines/usage/bi")
            assert response.status_code == 403
            assert response.headers["cache-control"] == "no-store"
            assert (
                client.post("/v1/pipelines/usage/bi", json={"sql": "SELECT 1"}).status_code == 405
            )
    finally:
        app.dependency_overrides.clear()


def test_blank_bi_configuration_is_unconfigured() -> None:
    settings = Settings(superset_api_token="", superset_dashboard_id="")
    assert settings.superset_api_token is None and settings.superset_dashboard_id is None
