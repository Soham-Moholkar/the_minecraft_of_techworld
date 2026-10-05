"""Authenticated experiment tracking over saved tenant datasets."""

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException
from prometheus_client import Counter, Histogram
from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas_api.auth import Principal, require_principal
from atlas_api.database import get_session
from atlas_api.machine_learning import (
    ExperimentCreate,
    ExperimentRead,
    ExperimentReport,
    ExperimentSummary,
    train_experiment,
)
from atlas_api.models import AuditEvent, Dataset, ModelExperiment, Organization
from atlas_api.neural_training import (
    TrainingBusyError,
    TrainingFailedError,
    train_neural_isolated,
)

router = APIRouter(prefix="/v1/ml/experiments", tags=["machine-learning"])
logger = structlog.get_logger()
TRAINING = Counter("atlas_ml_training_total", "Bounded model training runs", ["outcome"])
TRAINING_TIME = Histogram("atlas_ml_training_seconds", "Model comparison training duration")
Db = Annotated[Session, Depends(get_session)]
Identity = Annotated[Principal, Depends(require_principal)]


def _summary(experiment: ModelExperiment, dataset_name: str) -> ExperimentSummary:
    report = ExperimentReport.model_validate(experiment.report)
    best = max(report.models, key=lambda item: item.metrics.balanced_accuracy)
    return ExperimentSummary(
        id=experiment.id,
        dataset_id=experiment.dataset_id,
        dataset_name=dataset_name,
        name=experiment.name,
        created_at=_as_utc(experiment.created_at),
        best_model=best.model,
        best_balanced_accuracy=best.metrics.balanced_accuracy,
    )


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


@router.get("")
def list_experiments(session: Db, principal: Identity) -> list[ExperimentSummary]:
    records = session.execute(
        select(ModelExperiment, Dataset.name)
        .join(Dataset, ModelExperiment.dataset_id == Dataset.id)
        .join(Organization, ModelExperiment.organization_id == Organization.id)
        .where(
            Organization.slug == principal.organization_slug,
            Dataset.organization_id == ModelExperiment.organization_id,
        )
        .order_by(ModelExperiment.created_at.desc())
        .limit(100)
    ).all()
    return [_summary(experiment, dataset_name) for experiment, dataset_name in records]


@router.get("/{experiment_id}")
def read_experiment(experiment_id: UUID, session: Db, principal: Identity) -> ExperimentRead:
    record = session.execute(
        select(ModelExperiment, Dataset.name)
        .join(Dataset, ModelExperiment.dataset_id == Dataset.id)
        .join(Organization, ModelExperiment.organization_id == Organization.id)
        .where(
            Organization.slug == principal.organization_slug,
            ModelExperiment.id == experiment_id,
            Dataset.organization_id == ModelExperiment.organization_id,
        )
    ).one_or_none()
    if record is None:
        raise HTTPException(404, "experiment not found")
    experiment, dataset_name = record
    return ExperimentRead(
        **_summary(experiment, dataset_name).model_dump(),
        report=ExperimentReport.model_validate(experiment.report),
    )


@router.post("", status_code=201)
def create_experiment(
    request: ExperimentCreate, session: Db, principal: Identity
) -> ExperimentRead:
    if "owner" not in principal.roles:
        raise HTTPException(403, "owner role required")
    dataset = session.scalar(
        select(Dataset)
        .join(Organization)
        .where(
            Organization.slug == principal.organization_slug,
            Dataset.id == request.dataset_id,
        )
    )
    if dataset is None:
        raise HTTPException(404, "dataset not found")
    # Refuse a full catalog before spending CPU; the locked check below remains
    # authoritative when concurrent requests race for the last available slot.
    existing = session.scalars(
        select(ModelExperiment.id)
        .where(ModelExperiment.organization_id == dataset.organization_id)
        .limit(100)
    ).all()
    if len(existing) >= 100:
        raise HTTPException(409, "experiment catalog limit reached")
    try:
        with TRAINING_TIME.time():
            report = (
                train_neural_isolated(dataset.rows, include_keras=request.suite == "frameworks")
                if request.suite != "classical"
                else train_experiment(dataset.rows)
            )
    except TrainingBusyError as error:
        TRAINING.labels("busy").inc()
        raise HTTPException(429, str(error), headers={"Retry-After": "10"}) from error
    except TrainingFailedError as error:
        TRAINING.labels("failed").inc()
        logger.warning("neural_training_failed", dataset_id=str(dataset.id))
        raise HTTPException(503, str(error)) from error
    except ImportError as error:
        TRAINING.labels("unavailable").inc()
        raise HTTPException(503, "install the API data and requested neural extras") from error
    except ValueError as error:
        TRAINING.labels("invalid").inc()
        raise HTTPException(422, str(error)) from error
    # Training happens before this short quota transaction. Dataset rows are
    # immutable, so holding the tenant row lock during CPU work adds no safety.
    organization = session.scalar(
        select(Organization)
        .where(Organization.slug == principal.organization_slug)
        .with_for_update()
    )
    if organization is None:
        raise HTTPException(404, "organization not found")
    count = len(
        session.scalars(
            select(ModelExperiment.id)
            .where(ModelExperiment.organization_id == organization.id)
            .limit(100)
        ).all()
    )
    if count >= 100:
        raise HTTPException(409, "experiment catalog limit reached")
    experiment = ModelExperiment(
        organization_id=organization.id,
        dataset_id=dataset.id,
        name=request.name,
        report=report.model_dump(mode="json"),
    )
    session.add(experiment)
    session.flush()
    session.add(
        AuditEvent(
            organization_id=organization.id,
            actor=principal.subject,
            action="model.experiment.created",
            target_type="model_experiment",
            target_id=str(experiment.id),
            details={
                "dataset_id": str(dataset.id),
                "training_rows": str(report.training_rows),
                "suite": request.suite,
            },
        )
    )
    session.commit()
    TRAINING.labels("success").inc()
    logger.info(
        "ml_experiment_completed",
        experiment_id=str(experiment.id),
        dataset_id=str(dataset.id),
        training_rows=report.training_rows,
        test_rows=report.test_rows,
        suite=request.suite,
    )
    return ExperimentRead(**_summary(experiment, dataset.name).model_dump(), report=report)
