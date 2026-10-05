"""Lakehouse opt-in, authorization and real snapshot API round-trip."""

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from atlas_api.config import Settings, get_settings
from atlas_api.main import app


def test_real_snapshot_and_export_api(client: TestClient, auth_headers: dict[str, str]) -> None:
    pytest.importorskip("pyiceberg")
    root = Path("output") / f"lake-api-test-{uuid4().hex}"
    root.mkdir()
    app.dependency_overrides[get_settings] = lambda: Settings(
        streaming_enabled=True,
        lakehouse_enabled=True,
        streaming_store=str(root / "source.db"),
        lakehouse_store=str(root / "warehouse"),
    )
    try:
        assert client.post("/v1/streaming/usage/lakehouse").status_code == 401
        client.post(
            "/v1/streaming/usage/events",
            headers=auth_headers,
            json={"events": [{"event_id": "api-one", "units": 6}]},
        )
        client.post("/v1/streaming/usage/consume", headers=auth_headers, json={"limit": 10})
        response = client.post("/v1/streaming/usage/lakehouse", headers=auth_headers)
        assert response.status_code == 200
        assert (response.json()["rows"], response.json()["units"]) == (1, 6)
        assert (
            client.post("/v1/streaming/usage/lakehouse", headers=auth_headers).json()["changed"]
            is False
        )
        exported = client.get("/v1/streaming/usage/export", headers=auth_headers)
        assert exported.status_code == 200
        assert exported.content[:4] == b"PAR1"
        assert len(exported.headers["X-Atlas-Content-SHA256"]) == 64
    finally:
        for target in sorted(root.rglob("*"), key=lambda item: len(item.parts), reverse=True):
            assert target.resolve().is_relative_to(root.resolve())
            target.unlink() if target.is_file() else target.rmdir()
        root.rmdir()
