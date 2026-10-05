"""Read-only Airflow adapter for one source-owned, tenant-bound usage DAG.

The server chooses URL, bearer credential, tenant and DAG. Bounded projections
exclude conf, notes, logs and XCom. The API cannot trigger or modify Airflow runs.
"""

import json
from datetime import datetime
from typing import Annotated, Literal
from urllib.parse import quote

import httpx
import structlog
from fastapi import APIRouter, Depends, HTTPException, Response
from prometheus_client import Counter
from pydantic import BaseModel, Field

from atlas_api.auth import Principal, require_principal
from atlas_api.config import Settings, get_settings

DAG_ID = "atlas_usage_rollup"
TASK_IDS = ("consume", "validate_parquet", "refresh_lakehouse")
RunState = Literal["queued", "running", "success", "failed"]
TaskState = Literal[
    "none",
    "scheduled",
    "queued",
    "running",
    "success",
    "failed",
    "up_for_retry",
    "up_for_reschedule",
    "upstream_failed",
    "skipped",
    "deferred",
    "removed",
    "restarting",
]
logger = structlog.get_logger()
READS = Counter("atlas_airflow_status_reads_total", "Fixed DAG status reads", ["status"])
router = APIRouter(prefix="/v1/pipelines/usage", tags=["pipelines"])


class DagRun(BaseModel):
    dag_run_id: str = Field(min_length=1, max_length=240)
    state: RunState
    start_date: datetime | None = None
    end_date: datetime | None = None


class TaskStatus(BaseModel):
    task_id: Literal["consume", "validate_parquet", "refresh_lakehouse"]
    state: TaskState = "none"
    try_number: int = Field(ge=0, le=1000)


class UsageDagStatus(BaseModel):
    provider: Literal["airflow"] = "airflow"
    dag_id: Literal["atlas_usage_rollup"] = "atlas_usage_rollup"
    runs: list[DagRun] = Field(max_length=5)
    latest_tasks: list[TaskStatus] = Field(max_length=3)
    checked_at: datetime


class AirflowStatusUnavailable(RuntimeError):
    """Redacted provider or schema failure."""


def _read(client: httpx.Client, path: str) -> dict[str, object]:
    # A malicious/misconfigured upstream cannot redirect credentials or allocate
    # unlimited JSON. This limit applies while reading, not after parsing.
    with client.stream("GET", path) as response:
        response.raise_for_status()
        data = bytearray()
        for chunk in response.iter_bytes():
            data.extend(chunk)
            if len(data) > 256_000:
                raise AirflowStatusUnavailable("provider response limit")
    value: object = json.loads(data)
    if not isinstance(value, dict):
        raise AirflowStatusUnavailable("provider contract")
    return value


def read_status(client: httpx.Client) -> UsageDagStatus:
    from datetime import UTC

    try:
        result = _read(client, f"/api/v2/dags/{DAG_ID}/dagRuns?limit=5&order_by=-run_after")
        values = result.get("dag_runs")
        if not isinstance(values, list) or len(values) > 5:
            raise AirflowStatusUnavailable("run limit")
        runs: list[DagRun] = []
        for value in values:
            if not isinstance(value, dict) or value.get("dag_id") != DAG_ID:
                raise AirflowStatusUnavailable("DAG identity")
            runs.append(DagRun.model_validate(value))
        tasks: list[TaskStatus] = []
        if runs:
            run_id = quote(runs[0].dag_run_id, safe="")
            result = _read(client, f"/api/v2/dags/{DAG_ID}/dagRuns/{run_id}/taskInstances?limit=20")
            values = result.get("task_instances")
            if not isinstance(values, list) or len(values) > 20:
                raise AirflowStatusUnavailable("task limit")
            for value in values:
                if (
                    not isinstance(value, dict)
                    or value.get("dag_id") != DAG_ID
                    or value.get("dag_run_id") != runs[0].dag_run_id
                ):
                    raise AirflowStatusUnavailable("task identity")
                if value.get("task_id") not in TASK_IDS:
                    continue
                data = dict(value)
                data["state"] = data.get("state") or "none"
                tasks.append(TaskStatus.model_validate(data))
            if len(tasks) > 3 or len({item.task_id for item in tasks}) != len(tasks):
                raise AirflowStatusUnavailable("task identity duplication")
        return UsageDagStatus(runs=runs, latest_tasks=tasks, checked_at=datetime.now(UTC))
    except Exception:
        raise AirflowStatusUnavailable("Airflow status unavailable") from None


@router.get("", response_model=UsageDagStatus)
def usage_dag(
    principal: Annotated[Principal, Depends(require_principal)],
    settings: Annotated[Settings, Depends(get_settings)],
    response: Response,
) -> UsageDagStatus:
    response.headers["Cache-Control"] = "no-store"
    if "owner" not in principal.roles or principal.organization_slug != settings.airflow_tenant:
        raise HTTPException(403, "pipeline tenant access denied")
    if settings.environment != "development" or not settings.airflow_enabled:
        raise HTTPException(403, "local Airflow status disabled")
    if not settings.airflow_api_token:
        raise HTTPException(503, "Airflow credential unconfigured")
    try:
        with httpx.Client(
            base_url=settings.airflow_api_url,
            headers={"Authorization": f"Bearer {settings.airflow_api_token.get_secret_value()}"},
            timeout=3,
            follow_redirects=False,
            trust_env=False,
        ) as client:
            result = read_status(client)
        READS.labels("ok").inc()
        logger.info("usage_dag_status", runs=len(result.runs), tasks=len(result.latest_tasks))
        return result
    except Exception:
        READS.labels("unavailable").inc()
        logger.warning("usage_dag_unavailable")
        raise HTTPException(503, "Airflow status unavailable") from None
