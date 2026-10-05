"""Execute the real source-owned DAG task helpers against the production API."""

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
from fastapi.testclient import TestClient

from atlas_api.config import Settings, get_settings
from atlas_api.main import app


def tasks() -> ModuleType:
    path = Path(__file__).resolve().parents[3] / "infra/airflow/dags/atlas_usage_tasks.py"
    spec = importlib.util.spec_from_file_location("atlas_usage_tasks", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_real_consume_parquet_iceberg_task_chain(
    client: TestClient,
    auth_headers: dict[str, str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("pyarrow")
    pytest.importorskip("pyiceberg")
    app.dependency_overrides[get_settings] = lambda: Settings(
        streaming_enabled=True,
        lakehouse_enabled=True,
        streaming_store=str(tmp_path / "usage.db"),
        lakehouse_store=str(tmp_path / "lakehouse"),
    )
    url = "/v1/streaming/usage"
    assert (
        client.post(
            url + "/events",
            headers=auth_headers,
            json={"events": [{"event_id": "one", "units": 4}, {"event_id": "bad", "units": -1}]},
        ).status_code
        == 200
    )
    module = tasks()

    def call(suffix: str, payload: dict[str, int] | None = None) -> tuple[bytes, str | None]:
        response = (
            client.get(url + suffix, headers=auth_headers)
            if payload is None
            else client.post(url + suffix, headers=auth_headers, json=payload)
        )
        assert response.is_success, response.text
        return response.content, response.headers.get("X-Atlas-Content-SHA256")

    monkeypatch.setattr(module, "call", call)
    assert module.consume() == {"processed": 2}
    evidence = module.validate_parquet()
    assert evidence["rows"] == 1 and evidence["units"] == 4
    assert module.refresh_lakehouse() == {"rows": 1, "changed": True}
    assert module.refresh_lakehouse() == {"rows": 1, "changed": False}
    monkeypatch.setenv("ATLAS_PIPELINE_TENANT", "outsider")
    with pytest.raises(module.PipelineUnavailable, match="invalid Parquet lineage"):
        module.validate_parquet()


def test_tasks_require_operator_opt_in_and_redact_bad_payloads(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = tasks()
    monkeypatch.delenv("ATLAS_PIPELINE_ENABLED", raising=False)
    with pytest.raises(module.PipelineUnavailable, match="disabled"):
        module.consume()

    def bad_call(*_: Any) -> tuple[bytes, str | None]:
        return b'{"processed": true, "secret": "private"}', None

    monkeypatch.setattr(module, "call", bad_call)
    with pytest.raises(module.PipelineUnavailable, match="invalid consume evidence"):
        module.consume()
