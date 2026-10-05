"""Read-only observation of fixed source-bound local infrastructure plan receipts."""

from pathlib import Path
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException
from prometheus_client import Counter

from atlas_api.auth import Principal, require_principal
from atlas_api.config import Settings, get_settings
from atlas_api.infrastructure_plan import PlanObservation, observe_plan

router = APIRouter(prefix="/v1/infrastructure/plan", tags=["infrastructure"])
logger = structlog.get_logger()
READS = Counter("atlas_infrastructure_plan_reads_total", "Local plan observations", ["status"])


@router.get("", response_model=PlanObservation)
def plan_observation(
    principal: Annotated[Principal, Depends(require_principal)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> PlanObservation:
    if (
        settings.environment != "development"
        or not settings.infrastructure_plan_enabled
        or "owner" not in principal.roles
        or principal.organization_slug != "northstar"
    ):
        raise HTTPException(403, "local plan observation disabled or denied")
    try:
        result = observe_plan(Path(settings.repository_root))
    except Exception:
        READS.labels("unavailable").inc()
        logger.warning("infrastructure_plan_unavailable")
        raise HTTPException(503, "local plan observation unavailable") from None
    status = (
        "missing" if result.receipt is None else "current" if result.source_current else "older"
    )
    READS.labels(status).inc()
    logger.info("infrastructure_plan_observed", status=status)
    return result
