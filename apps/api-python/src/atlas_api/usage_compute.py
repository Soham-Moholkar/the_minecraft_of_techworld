"""Read an operator-owned Spark receipt; compare it with current accepted data.

Receipts are local operational observations, not remote attestation. The worker
and API must share an operator-owned directory. HTTP callers cannot submit jobs,
choose paths, overwrite observations, or launch Spark/SQL/subprocesses.
"""

import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Annotated, Literal

import structlog
from fastapi import APIRouter, Depends, HTTPException
from prometheus_client import Counter
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from atlas_api.auth import Principal, require_principal
from atlas_api.config import Settings, get_settings
from atlas_api.streaming import UsageStream
from atlas_api.streaming_export import export_parquet

router = APIRouter(prefix="/v1/pipelines/usage/compute", tags=["pipelines"])
logger = structlog.get_logger()
READS = Counter("atlas_usage_compute_reads_total", "Local usage compute observations", ["status"])


class SparkReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal[1]
    provider: Literal["spark"]
    version: Literal["4.2.0"]
    tenant: str = Field(pattern=r"^[a-z][a-z0-9-]{0,47}$")
    source_provider: Literal["sqlite", "kafka"]
    source_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    rows: int = Field(ge=0, le=10000)
    units: int = Field(ge=0, le=10000000)
    mode: Literal["local", "standalone"]
    partitions: int = Field(ge=0, le=10000)
    duration_ms: int = Field(ge=0, le=300000)
    finished_at: datetime

    @model_validator(mode="after")
    def bounded_aggregate(self) -> "SparkReceipt":
        if self.units > self.rows * 1000:
            raise ValueError("aggregate cannot exceed accepted row bounds")
        return self

    @field_validator("finished_at")
    @classmethod
    def timezone_required(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value > datetime.now(UTC) + timedelta(seconds=30):
            raise ValueError("invalid observation time")
        return value


class ComputeRead(BaseModel):
    receipt: SparkReceipt | None
    source_current: bool | None
    checked_at: datetime


def read_receipt(root: Path, tenant: str, provider: str) -> SparkReceipt | None:
    root = root.resolve()
    path = root / tenant / provider / "spark.json"
    if not path.resolve().is_relative_to(root) or path.is_symlink():
        raise ValueError("receipt containment")
    if not path.exists():
        return None
    with path.open("rb") as source:
        raw = source.read(8193)
    if len(raw) > 8192:
        raise ValueError("receipt byte bound")
    result = SparkReceipt.model_validate_json(raw)
    if result.tenant != tenant or result.source_provider != provider:
        raise ValueError("receipt namespace")
    return result


@router.get("", response_model=ComputeRead)
def compute_status(
    principal: Annotated[Principal, Depends(require_principal)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ComputeRead:
    if "owner" not in principal.roles:
        raise HTTPException(403, "owner role required")
    if (
        settings.environment != "development"
        or not settings.usage_compute_enabled
        or not settings.streaming_enabled
    ):
        raise HTTPException(403, "local usage compute disabled")
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,47}", principal.organization_slug):
        raise HTTPException(403, "invalid tenant")
    try:
        result = read_receipt(
            Path(settings.usage_compute_store),
            principal.organization_slug,
            settings.streaming_provider,
        )
        current = None
        if result:
            sink = UsageStream(
                Path(settings.streaming_store),
                principal.organization_slug,
                settings.streaming_provider,
            )
            try:
                content, digest = export_parquet(sink)
                current = digest == result.source_digest
                if current:
                    import pyarrow as pa  # type: ignore[import-untyped]
                    import pyarrow.parquet as pq  # type: ignore[import-untyped]

                    metadata = pq.read_metadata(pa.BufferReader(content)).metadata
                    lineage = json.loads(metadata[b"atlas.lineage"])
                    if (result.rows, result.units) != (lineage["rows"], lineage["units"]):
                        raise ValueError("receipt aggregate disagrees with current source")
            finally:
                sink.close()
        READS.labels("ok").inc()
        logger.info("usage_compute_observed", available=result is not None, current=current)
        return ComputeRead(receipt=result, source_current=current, checked_at=datetime.now(UTC))
    except Exception:
        READS.labels("unavailable").inc()
        logger.warning("usage_compute_unavailable")
        raise HTTPException(503, "usage compute observation unavailable") from None
