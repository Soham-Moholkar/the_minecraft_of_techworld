"""Bounded read-only Flink job/checkpoint/backpressure observations.

Only an operator-configured job ID and tenant are visible. Job plans, names,
exception text, configuration and checkpoint storage paths are never projected.
The Flink development REST listener must remain private/loopback: it has job
submission capabilities that this API deliberately does not expose.
"""

import json
import re
from datetime import UTC, datetime
from typing import Annotated, Literal

import httpx
import structlog
from fastapi import APIRouter, Depends, HTTPException
from prometheus_client import Counter
from pydantic import BaseModel, ConfigDict, Field

from atlas_api.auth import Principal, require_principal
from atlas_api.config import Settings, get_settings

router = APIRouter(prefix="/v1/pipelines/usage/flink", tags=["pipelines"])
logger = structlog.get_logger()
READS = Counter("atlas_flink_status_reads_total", "Fixed Flink job observations", ["status"])


class CheckpointCounts(BaseModel):
    model_config = ConfigDict(strict=True)
    completed: int = Field(ge=0, le=10000000)
    failed: int = Field(ge=0, le=10000000)
    in_progress: int = Field(ge=0, le=1000)


class VertexPressure(BaseModel):
    vertex_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    level: Literal["ok", "low", "high"] | None


class FlinkRead(BaseModel):
    provider: Literal["flink"] = "flink"
    job_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    state: Literal[
        "INITIALIZING",
        "CREATED",
        "RUNNING",
        "FAILING",
        "FAILED",
        "CANCELLING",
        "CANCELED",
        "FINISHED",
        "RESTARTING",
        "SUSPENDED",
        "RECONCILING",
    ]
    checkpoints: CheckpointCounts
    vertices: list[VertexPressure] = Field(max_length=3)
    checked_at: datetime


def read_json(client: httpx.Client, path: str) -> dict[str, object]:
    with client.stream("GET", path) as response:
        response.raise_for_status()
        content = bytearray()
        for chunk in response.iter_bytes():
            content.extend(chunk)
            if len(content) > 256000:
                raise ValueError("Flink byte limit")
    value: object = json.loads(content)
    if not isinstance(value, dict):
        raise ValueError("Flink contract")
    return value


def read_status(client: httpx.Client, job_id: str) -> FlinkRead:
    if not re.fullmatch(r"[a-f0-9]{32}", job_id):
        raise ValueError("configured job identity")
    # Pydantic validates all response identities before they enter another path.
    job = read_json(client, f"/jobs/{job_id}")
    if job.get("jid") != job_id:
        raise ValueError("job identity")
    checkpoint_data = read_json(client, f"/jobs/{job_id}/checkpoints")
    counts = CheckpointCounts.model_validate(checkpoint_data.get("counts"))
    raw_vertices = job.get("vertices")
    if not isinstance(raw_vertices, list) or len(raw_vertices) > 20:
        raise ValueError("vertex bound")
    vertices: list[VertexPressure] = []
    for raw in raw_vertices[:3]:
        if not isinstance(raw, dict):
            raise ValueError("vertex contract")
        vertex = VertexPressure.model_validate({"vertex_id": raw.get("id"), "level": None})
        pressure = read_json(client, f"/jobs/{job_id}/vertices/{vertex.vertex_id}/backpressure")
        status = pressure.get("status")
        if status not in ("ok", "deprecated"):
            raise ValueError("pressure observation")
        # Deprecated/missing samples aren't evidence of zero backpressure.
        level = (
            pressure.get("backpressure-level", pressure.get("backpressureLevel"))
            if status == "ok"
            else None
        )
        vertices.append(
            VertexPressure.model_validate({"vertex_id": vertex.vertex_id, "level": level})
        )
    if len({value.vertex_id for value in vertices}) != len(vertices):
        raise ValueError("duplicate vertex")
    return FlinkRead.model_validate(
        dict(
            job_id=job_id,
            state=job.get("state"),
            checkpoints=counts,
            vertices=vertices,
            checked_at=datetime.now(UTC),
        )
    )


@router.get("", response_model=FlinkRead)
def flink_status(
    principal: Annotated[Principal, Depends(require_principal)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> FlinkRead:
    if "owner" not in principal.roles or principal.organization_slug != settings.flink_tenant:
        raise HTTPException(403, "Flink tenant access denied")
    if settings.environment != "development" or not settings.flink_enabled:
        raise HTTPException(403, "local Flink observation disabled")
    if settings.flink_job_id is None:
        raise HTTPException(503, "Flink job unconfigured")
    try:
        with httpx.Client(
            base_url=settings.flink_api_url, trust_env=False, follow_redirects=False, timeout=0.5
        ) as client:
            result = read_status(client, settings.flink_job_id)
        READS.labels("ok").inc()
        logger.info(
            "usage_flink_observed",
            vertices=len(result.vertices),
            completed=result.checkpoints.completed,
        )
        return result
    except Exception:
        READS.labels("unavailable").inc()
        logger.warning("usage_flink_unavailable")
        raise HTTPException(503, "Flink observation unavailable") from None
