"""Fixed identity, privacy, pressure availability and independent authority."""

import httpx
import pytest
from fastapi.testclient import TestClient

from atlas_api.auth import Principal, require_principal
from atlas_api.config import Settings, get_settings
from atlas_api.flink_status import read_status
from atlas_api.main import app

JOB = "a" * 32
VERTEX = "b" * 32


def payload(path: str) -> dict[str, object]:
    if path.endswith("checkpoints"):
        return {
            "counts": {"completed": 2, "failed": 1, "in_progress": 0},
            "latest": {"external_path": "private"},
        }
    if path.endswith("backpressure"):
        return {"status": "deprecated", "backpressure-level": "ok"}
    return {
        "jid": JOB,
        "state": "RUNNING",
        "vertices": [{"id": VERTEX, "name": "private SQL"}],
        "plan": "private",
    }


def test_projection_and_unavailable_pressure() -> None:
    calls: list[httpx.Request] = []

    def upstream(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json=payload(request.url.path))

    with httpx.Client(base_url="http://flink", transport=httpx.MockTransport(upstream)) as client:
        result = read_status(client, JOB)
    assert result.checkpoints.completed == 2
    assert result.vertices[0].level is None
    assert "private" not in result.model_dump_json()
    assert len(calls) == 3 and all(call.method == "GET" for call in calls)


@pytest.mark.parametrize("failure", ["identity", "bytes", "vertex"])
def test_rejects_unsafe_provider(failure: str) -> None:
    def upstream(request: httpx.Request) -> httpx.Response:
        value = payload(request.url.path)
        if failure == "identity":
            value["jid"] = "c" * 32
        if failure == "vertex":
            value["vertices"] = [{"id": "../config"}]
        if failure == "bytes":
            return httpx.Response(200, content=b"x" * 256001)
        return httpx.Response(200, json=value)

    with (
        httpx.Client(base_url="http://flink", transport=httpx.MockTransport(upstream)) as client,
        pytest.raises(ValueError),
    ):
        read_status(client, JOB)


def test_development_tenant_and_blank_job_gates() -> None:
    assert Settings(flink_job_id="").flink_job_id is None
    app.dependency_overrides[get_settings] = lambda: Settings(
        flink_enabled=True, flink_tenant="northstar", flink_job_id=JOB
    )
    app.dependency_overrides[require_principal] = lambda: Principal(
        subject="operator", organization_slug="other", roles=["owner"]
    )
    try:
        with TestClient(app) as client:
            response = client.get("/v1/pipelines/usage/flink")
            assert response.status_code == 403
            assert response.headers["cache-control"] == "no-store"
            assert client.post("/v1/pipelines/usage/flink", json={"job_id": JOB}).status_code == 405
    finally:
        app.dependency_overrides.clear()
