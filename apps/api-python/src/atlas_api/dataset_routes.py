"""Authenticated dataset catalog with atomic data/profile/audit persistence."""

from datetime import UTC
from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException
from prometheus_client import Counter, Histogram
from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas_api.auth import Principal, require_principal
from atlas_api.data_science import (
    DatasetImport,
    DatasetProfile,
    DatasetRead,
    DatasetSummary,
    profile_csv,
)
from atlas_api.database import get_session
from atlas_api.models import AuditEvent, Dataset, Organization

router = APIRouter(prefix="/v1/datasets", tags=["datasets"])
logger = structlog.get_logger()
IMPORTS = Counter("atlas_dataset_imports_total", "Bounded dataset imports", ["outcome"])
PROFILE_TIME = Histogram("atlas_dataset_profile_seconds", "Dataset cleaning and profile duration")
Db = Annotated[Session, Depends(get_session)]
Identity = Annotated[Principal, Depends(require_principal)]


def _summary(dataset: Dataset) -> DatasetSummary:
    report = DatasetProfile.model_validate(dataset.report)
    return DatasetSummary(
        id=dataset.id,
        name=dataset.name,
        source_checksum=dataset.source_checksum,
        created_at=dataset.created_at.replace(tzinfo=UTC),
        valid_rows=report.valid_rows,
    )


@router.get("")
def list_datasets(session: Db, principal: Identity) -> list[DatasetSummary]:
    datasets = session.scalars(
        select(Dataset)
        .join(Organization)
        .where(Organization.slug == principal.organization_slug)
        .order_by(Dataset.created_at.desc())
        .limit(100)
    ).all()
    return [_summary(dataset) for dataset in datasets]


@router.get("/{dataset_id}")
def read_dataset(dataset_id: UUID, session: Db, principal: Identity) -> DatasetRead:
    dataset = session.scalar(
        select(Dataset)
        .join(Organization)
        .where(Organization.slug == principal.organization_slug, Dataset.id == dataset_id)
    )
    if dataset is None:
        raise HTTPException(404, "dataset not found")
    return DatasetRead(
        **_summary(dataset).model_dump(), profile=DatasetProfile.model_validate(dataset.report)
    )


@router.post("", status_code=201)
def import_dataset(request: DatasetImport, session: Db, principal: Identity) -> DatasetRead:
    if "owner" not in principal.roles:
        raise HTTPException(403, "owner role required")
    try:
        with PROFILE_TIME.time():
            rows, profile, checksum = profile_csv(request.csv_text)
    except ImportError as error:
        IMPORTS.labels("unavailable").inc()
        raise HTTPException(503, "install the API data extra to enable profiling") from error
    except ValueError as error:
        IMPORTS.labels("invalid").inc()
        # Cleaning errors are source-owned strings. Never echo the uploaded CSV.
        raise HTTPException(422, str(error)) from error
    # Lock the organization before checking the catalog quota. PostgreSQL writers
    # for the same tenant serialize here; the SQLite single-writer fallback remains
    # useful for development. Profile work is done before taking this short lock.
    organization = session.scalar(
        select(Organization)
        .where(Organization.slug == principal.organization_slug)
        .with_for_update()
    )
    if organization is None:
        raise HTTPException(404, "organization not found")
    existing = session.scalars(
        select(Dataset.id).where(Dataset.organization_id == organization.id).limit(100)
    ).all()
    if len(existing) >= 100:
        raise HTTPException(409, "dataset catalog limit reached")
    dataset = Dataset(
        organization_id=organization.id,
        name=request.name,
        source_checksum=checksum,
        rows=rows,
        report=profile.model_dump(mode="json"),
    )
    session.add(dataset)
    session.flush()
    session.add(
        AuditEvent(
            organization_id=organization.id,
            actor=principal.subject,
            action="dataset.imported",
            target_type="dataset",
            target_id=str(dataset.id),
            details={
                "valid_rows": str(profile.valid_rows),
                "invalid_rows": str(profile.invalid_rows),
            },
        )
    )
    session.commit()
    IMPORTS.labels("success").inc()
    logger.info(
        "dataset_import_completed",
        dataset_id=str(dataset.id),
        valid_rows=profile.valid_rows,
        invalid_rows=profile.invalid_rows,
        duplicate_rows=profile.duplicate_rows,
    )
    return DatasetRead(**_summary(dataset).model_dump(), profile=profile)
