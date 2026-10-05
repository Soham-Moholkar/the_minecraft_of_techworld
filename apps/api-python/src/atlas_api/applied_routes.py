"""Authenticated persistence for the fixed Phase 7 applied-AI suite."""

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException
from prometheus_client import Counter, Histogram
from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas_api.applied_ai import (
    AppliedExperimentCreate,
    AppliedExperimentRead,
    AppliedExperimentSummary,
    AppliedReport,
)
from atlas_api.applied_training import run_applied_isolated
from atlas_api.auth import Principal, require_principal
from atlas_api.database import get_session
from atlas_api.models import AppliedAIExperiment, AuditEvent, Organization
from atlas_api.neural_training import TrainingBusyError, TrainingFailedError

router = APIRouter(prefix="/v1/ml/applied-experiments", tags=["applied-ai"])
logger = structlog.get_logger()
RUNS = Counter("atlas_applied_ai_runs_total", "Applied AI suite runs", ["outcome"])
RUN_TIME = Histogram("atlas_applied_ai_run_seconds", "Applied AI suite duration")
Db = Annotated[Session, Depends(get_session)]
Identity = Annotated[Principal, Depends(require_principal)]


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


def _summary(experiment: AppliedAIExperiment) -> AppliedExperimentSummary:
    report = AppliedReport.model_validate(experiment.report)
    improved = sum(
        (task.model_score > task.baseline_score)
        if task.higher_is_better
        else (task.model_score < task.baseline_score)
        for task in report.tasks
    )
    return AppliedExperimentSummary(
        id=experiment.id,
        name=experiment.name,
        created_at=_as_utc(experiment.created_at),
        tasks=len(report.tasks),
        improved_tasks=improved,
    )


@router.get("")
def list_applied_experiments(session: Db, principal: Identity) -> list[AppliedExperimentSummary]:
    records = session.scalars(
        select(AppliedAIExperiment)
        .join(Organization)
        .where(Organization.slug == principal.organization_slug)
        .order_by(AppliedAIExperiment.created_at.desc())
        .limit(50)
    ).all()
    return [_summary(record) for record in records]


@router.get("/{experiment_id}")
def read_applied_experiment(
    experiment_id: UUID, session: Db, principal: Identity
) -> AppliedExperimentRead:
    record = session.scalar(
        select(AppliedAIExperiment)
        .join(Organization)
        .where(
            Organization.slug == principal.organization_slug,
            AppliedAIExperiment.id == experiment_id,
        )
    )
    if record is None:
        raise HTTPException(404, "applied AI experiment not found")
    return AppliedExperimentRead(
        **_summary(record).model_dump(), report=AppliedReport.model_validate(record.report)
    )


@router.post("", status_code=201)
def create_applied_experiment(
    request: AppliedExperimentCreate, session: Db, principal: Identity
) -> AppliedExperimentRead:
    if "owner" not in principal.roles:
        raise HTTPException(403, "owner role required")
    organization = session.scalar(
        select(Organization).where(Organization.slug == principal.organization_slug)
    )
    if organization is None:
        raise HTTPException(404, "organization not found")
    existing = session.scalars(
        select(AppliedAIExperiment.id)
        .where(AppliedAIExperiment.organization_id == organization.id)
        .limit(50)
    ).all()
    if len(existing) >= 50:
        raise HTTPException(409, "applied experiment catalog limit reached")
    try:
        with RUN_TIME.time():
            report = run_applied_isolated()
    except TrainingBusyError as error:
        RUNS.labels("busy").inc()
        raise HTTPException(429, str(error), headers={"Retry-After": "10"}) from error
    except ImportError as error:
        RUNS.labels("unavailable").inc()
        raise HTTPException(503, "install the API neural extra") from error
    except TrainingFailedError as error:
        RUNS.labels("failed").inc()
        logger.warning("applied_ai_training_failed")
        raise HTTPException(503, str(error)) from error
    # Serialize catalog allocation under the tenant row after CPU work. The
    # fixed fixtures have no mutable tenant input that needs a long-held lock.
    organization = session.scalar(
        select(Organization)
        .where(Organization.slug == principal.organization_slug)
        .with_for_update()
    )
    if organization is None:
        raise HTTPException(404, "organization not found")
    count = len(
        session.scalars(
            select(AppliedAIExperiment.id)
            .where(AppliedAIExperiment.organization_id == organization.id)
            .limit(50)
        ).all()
    )
    if count >= 50:
        raise HTTPException(409, "applied experiment catalog limit reached")
    experiment = AppliedAIExperiment(
        organization_id=organization.id,
        name=request.name,
        report=report.model_dump(mode="json"),
    )
    session.add(experiment)
    session.flush()
    session.add(
        AuditEvent(
            organization_id=organization.id,
            actor=principal.subject,
            action="model.applied_experiment.created",
            target_type="applied_ai_experiment",
            target_id=str(experiment.id),
            details={"tasks": str(len(report.tasks)), "runtime": "pytorch-cpu"},
        )
    )
    session.commit()
    RUNS.labels("success").inc()
    logger.info(
        "applied_ai_experiment_completed",
        experiment_id=str(experiment.id),
        tasks=len(report.tasks),
    )
    return AppliedExperimentRead(**_summary(experiment).model_dump(), report=report)
