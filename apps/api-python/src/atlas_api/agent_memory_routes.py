"""Local, owner-only operator memory boundary; inference never reads these notes."""

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Response
from prometheus_client import Counter
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from atlas_api.agent_memory import (
    MemoryCreate,
    MemoryDelete,
    MemoryPolicyError,
    MemoryPurge,
    MemoryRead,
    MemoryRemoval,
    MemorySnapshot,
    audit,
    create_memory,
    memory_read,
    purge_expired,
    snapshot,
)
from atlas_api.auth import Principal, require_principal
from atlas_api.config import Settings, get_settings
from atlas_api.database import get_session
from atlas_api.models import AgentMemory, Organization

router = APIRouter(prefix="/v1/ai/repository/memory", tags=["agent-memory"])
logger = structlog.get_logger()
ACTIONS = Counter("atlas_agent_memory_actions_total", "Operator memory lifecycle", ["action"])
Db = Annotated[Session, Depends(get_session)]
Identity = Annotated[Principal, Depends(require_principal)]
Configuration = Annotated[Settings, Depends(get_settings)]


def organization(session: Session, principal: Principal, settings: Settings) -> Organization:
    if "owner" not in principal.roles:
        raise HTTPException(403, "owner role required")
    if settings.environment != "development":
        raise HTTPException(503, "local operator memory is disabled")
    record = session.scalar(
        select(Organization).where(
            Organization.slug == principal.organization_slug,
        )
    )
    if record is None:
        raise HTTPException(404, "organization not found")
    return record


def observed(action: str, organization_id: UUID) -> None:
    ACTIONS.labels(action).inc()
    logger.info("agent_memory_action", action=action, organization_id=str(organization_id))


def commit_memory(session: Session) -> None:
    """Surface lifecycle write races without leaking SQL parameters or partial audit."""
    try:
        session.commit()
    except (IntegrityError, OperationalError) as error:
        session.rollback()
        raise HTTPException(409, "memory write conflicted; refresh before retrying") from error


@router.get("")
def list_memory(
    session: Db,
    principal: Identity,
    settings: Configuration,
    response: Response,
) -> MemorySnapshot:
    tenant = organization(session, principal, settings)
    response.headers["Cache-Control"] = "no-store"
    result = snapshot(session, tenant.id, now=datetime.now(UTC))
    observed("read", tenant.id)
    return result


@router.post("", status_code=201)
def save_memory(
    data: MemoryCreate,
    session: Db,
    principal: Identity,
    settings: Configuration,
    response: Response,
) -> MemoryRead:
    tenant = organization(session, principal, settings)
    try:
        record = create_memory(session, tenant.id, data, principal.subject, now=datetime.now(UTC))
        commit_memory(session)  # Note and content-free audit commit as one transaction.
    except MemoryPolicyError as error:
        session.rollback()
        observed("rejected", tenant.id)
        raise HTTPException(409 if "capacity" in str(error) else 400, str(error)) from error
    except (IntegrityError, OperationalError) as error:
        session.rollback()
        raise HTTPException(409, "memory write conflicted; refresh before retrying") from error
    response.headers["Cache-Control"] = "no-store"
    observed("created", tenant.id)
    return memory_read(record)


@router.delete("/{memory_id}")
def remove_memory(
    memory_id: UUID,
    data: MemoryDelete,
    session: Db,
    principal: Identity,
    settings: Configuration,
    response: Response,
) -> MemoryRemoval:
    tenant = organization(session, principal, settings)
    record = session.scalar(
        select(AgentMemory)
        .where(
            AgentMemory.id == memory_id,
            AgentMemory.organization_id == tenant.id,
        )
        .with_for_update()
    )
    if record is None:
        raise HTTPException(404, "memory not found")
    audit(session, record, principal.subject, "deleted")
    session.delete(record)
    commit_memory(session)  # Physical deletion; audit never retains the removed text.
    response.headers["Cache-Control"] = "no-store"
    observed("deleted", tenant.id)
    return MemoryRemoval(removed_count=1)


@router.post("/purge-expired")
def clean_memory(
    data: MemoryPurge,
    session: Db,
    principal: Identity,
    settings: Configuration,
    response: Response,
) -> MemoryRemoval:
    tenant = organization(session, principal, settings)
    count = purge_expired(session, tenant.id, principal.subject, now=datetime.now(UTC))
    commit_memory(session)
    response.headers["Cache-Control"] = "no-store"
    observed("purged", tenant.id)
    return MemoryRemoval(removed_count=count)
