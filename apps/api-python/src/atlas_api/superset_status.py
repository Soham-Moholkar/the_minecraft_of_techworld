"""Read-only metadata for a fixed tenant-owned Superset usage dashboard.

The service JWT never crosses HTTP. No SQL, chart data, owners, dataset URLs or
dashboard JSON/CSS are returned. Publication is metadata, not a data freshness
or runtime-readiness claim; the separate projection job publishes accepted totals.
"""

import json
from datetime import UTC, datetime
from typing import Annotated, Literal

import httpx
import structlog
from fastapi import APIRouter, Depends, HTTPException
from prometheus_client import Counter
from pydantic import BaseModel, ConfigDict, Field

from atlas_api.auth import Principal, require_principal
from atlas_api.config import Settings, get_settings

router = APIRouter(prefix="/v1/pipelines/usage/bi", tags=["pipelines"])
logger = structlog.get_logger()
READS = Counter(
    "atlas_superset_status_reads_total", "Fixed usage dashboard observations", ["status"]
)


class DashboardRead(BaseModel):
    model_config = ConfigDict(strict=True)
    provider: Literal["superset"] = "superset"
    dashboard_id: int = Field(ge=1, le=2147483647)
    title: str = Field(min_length=1, max_length=240)
    published: bool
    checked_at: datetime


def read_dashboard(client: httpx.Client, dashboard_id: int, tenant: str) -> DashboardRead:
    with client.stream(
        "GET",
        f"/api/v1/dashboard/{dashboard_id}",
        params={"q": "(columns:!(id,dashboard_title,published))"},
    ) as response:
        response.raise_for_status()
        raw = bytearray()
        for chunk in response.iter_bytes():
            raw.extend(chunk)
            if len(raw) > 64000:
                raise ValueError("dashboard response bound")
    value = json.loads(raw)["result"]
    if value.get("id") != dashboard_id or value.get("dashboard_title") != f"ATLAS usage {tenant}":
        raise ValueError("dashboard namespace")
    return DashboardRead.model_validate(
        dict(
            dashboard_id=value["id"],
            title=value["dashboard_title"],
            published=value["published"],
            checked_at=datetime.now(UTC),
        )
    )


@router.get("", response_model=DashboardRead)
def dashboard_status(
    principal: Annotated[Principal, Depends(require_principal)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DashboardRead:
    if "owner" not in principal.roles or principal.organization_slug != settings.superset_tenant:
        raise HTTPException(403, "BI tenant access denied")
    if settings.environment != "development" or not settings.superset_enabled:
        raise HTTPException(403, "local BI observation disabled")
    if settings.superset_api_token is None or settings.superset_dashboard_id is None:
        raise HTTPException(503, "BI observation unconfigured")
    try:
        with httpx.Client(
            base_url=settings.superset_api_url,
            headers={"Authorization": "Bearer " + settings.superset_api_token.get_secret_value()},
            timeout=2,
            trust_env=False,
            follow_redirects=False,
        ) as client:
            result = read_dashboard(
                client, settings.superset_dashboard_id, settings.superset_tenant
            )
        READS.labels("ok").inc()
        logger.info("usage_bi_observed", published=result.published)
        return result
    except Exception:
        READS.labels("unavailable").inc()
        logger.warning("usage_bi_unavailable")
        raise HTTPException(503, "BI observation unavailable") from None
