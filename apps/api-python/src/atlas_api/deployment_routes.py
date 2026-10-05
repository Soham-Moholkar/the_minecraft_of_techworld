"""Owner-only offline deployment observation; no apply/delete/upload endpoints."""

from pathlib import Path
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException
from prometheus_client import Counter

from atlas_api.auth import Principal, require_principal
from atlas_api.config import Settings, get_settings
from atlas_api.deployment_policy import DeploymentReview, read_manifest, review

router = APIRouter(prefix="/v1/infrastructure/deployment", tags=["infrastructure"])
logger = structlog.get_logger()
READS = Counter("atlas_deployment_reviews_total", "Offline deployment policy reviews", ["status"])


@router.get("", response_model=DeploymentReview)
def deployment_review(
    principal: Annotated[Principal, Depends(require_principal)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DeploymentReview:
    if (
        settings.environment != "development"
        or not settings.deployment_review_enabled
        or "owner" not in principal.roles
        or principal.organization_slug != "northstar"
    ):
        raise HTTPException(403, "local deployment review disabled or denied")
    try:
        result = review(read_manifest(Path(settings.repository_root)))
    except Exception:
        READS.labels("unavailable").inc()
        logger.warning("deployment_review_unavailable")
        raise HTTPException(503, "deployment manifest unavailable") from None
    READS.labels(result.status).inc()
    logger.info("deployment_review_observed", status=result.status, resources=len(result.resources))
    return result
