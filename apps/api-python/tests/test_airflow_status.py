"""Provider schema, privacy, bounded I/O and tenant/opt-in regression coverage."""

from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from atlas_api.airflow_status import AirflowStatusUnavailable, read_status
from atlas_api.auth import Principal, require_principal
from atlas_api.config import Settings, get_settings
from atlas_api.main import app

DAG = "atlas_usage_rollup"
RUN = "manual__2026-10-03T00:00:00+00:00"


def provider(request: httpx.Request) -> httpx.Response:
    if request.url.path.endswith("taskInstances"):
        return httpx.Response(
            200,
            json={
                "task_instances": [
                    {
                        "dag_id": DAG,
                        "dag_run_id": RUN,
                        "task_id": "consume",
                        "state": "success",
                        "try_number": 1,
                        "rendered_map_index": "private",
                    }
                ]
            },
        )
    return httpx.Response(
        200,
        json={
            "dag_runs": [
                {
                    "dag_id": DAG,
                    "dag_run_id": RUN,
                    "state": "success",
                    "conf": {"secret": "private"},
                    "note": "private",
                }
            ]
        },
    )


def test_status_projects_only_safe_fixed_dag_fields() -> None:
    calls: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return provider(request)

    with httpx.Client(base_url="http://airflow", transport=httpx.MockTransport(handle)) as client:
        result = read_status(client)
    assert result.runs[0].state == "success"
    assert result.latest_tasks[0].task_id == "consume"
    assert "private" not in result.model_dump_json()
    assert calls[0].url.params["limit"] == "5"
    assert calls[1].url.params["limit"] == "20"
    assert all(call.method == "GET" for call in calls)


@pytest.mark.parametrize(
    "value", [{"dag_runs": [None]}, {"dag_runs": [{"dag_id": "other"}]}, {"dag_runs": [{}] * 6}]
)
def test_provider_contract_fails_closed(value: dict[str, Any]) -> None:
    with (
        httpx.Client(
            base_url="http://airflow",
            transport=httpx.MockTransport(lambda _: httpx.Response(200, json=value)),
        ) as client,
        pytest.raises(AirflowStatusUnavailable, match="status unavailable"),
    ):
        read_status(client)


def test_bounded_response_and_redacted_failure() -> None:
    with (
        httpx.Client(
            base_url="http://airflow",
            transport=httpx.MockTransport(lambda _: httpx.Response(200, content=b"x" * 256001)),
        ) as client,
        pytest.raises(AirflowStatusUnavailable),
    ):
        read_status(client)


def test_no_runs_is_a_real_empty_result() -> None:
    with httpx.Client(
        base_url="http://airflow",
        transport=httpx.MockTransport(lambda _: httpx.Response(200, json={"dag_runs": []})),
    ) as client:
        assert read_status(client).runs == []


def test_status_auth_tenant_and_opt_in(client: TestClient, auth_headers: dict[str, str]) -> None:
    url = "/v1/pipelines/usage"
    assert client.get(url).status_code == 401
    assert client.get(url, headers=auth_headers).status_code == 403
    app.dependency_overrides[get_settings] = lambda: Settings(airflow_enabled=True)
    assert client.get(url, headers=auth_headers).status_code == 503
    app.dependency_overrides[require_principal] = lambda: Principal(
        "outsider", "other-tenant", ("owner",)
    )
    assert client.get(url, headers=auth_headers).status_code == 403
    app.dependency_overrides[require_principal] = lambda: Principal(
        "reader", "northstar", ("reader",)
    )
    assert client.get(url, headers=auth_headers).status_code == 403
