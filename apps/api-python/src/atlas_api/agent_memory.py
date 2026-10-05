"""Bounded operator memory and privacy lifecycle, independent of inference.

These notes are untrusted plain text, not prompts, commands, approvals or secrets.
Expiry hides data immediately; physical cleanup happens on save or explicit purge.
No reader in the inference/tool stack imports this module.
"""

import re
from datetime import UTC, datetime, timedelta
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from atlas_api.models import AgentMemory, AuditEvent, Organization

CAPACITY = 50
# Conservative guardrails, not a complete DLP system: operators must review text.
# Digests are rejected too, so an approval cannot be cached/reused as "memory".
SENSITIVE_TEXT = re.compile(
    r"\bBearer\s+\S+|\bsk-[A-Za-z0-9_-]{8,}|\bAKIA[A-Z0-9]{16}\b|"
    r"-----BEGIN[^\n]*PRIVATE KEY-----|"
    r"\b(?:password|passwd|secret|api[_ -]?key|access[_ -]?token)\s*[=:]\s*\S+|"
    r"\b[0-9a-f]{64}\b|APPLY EXACT PATCH|ROLL BACK EXACT PATCH|"
    r"RUN ISOLATED TEST PROFILE|proposal_digest|run_digest|"
    r"\b(?:postgres(?:ql)?|mysql|https?)://[^\s/]+:[^\s/]+@",
    re.IGNORECASE,
)


class MemoryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(min_length=3, max_length=120)
    content: str = Field(min_length=10, max_length=2_000)
    provenance: str = Field(min_length=3, max_length=240)
    retention_days: Literal[1, 7, 30] = 7
    confirmation: Literal["NO SECRETS OR APPROVALS"]


class MemoryDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")
    confirmation: Literal["DELETE MEMORY"]


class MemoryPurge(BaseModel):
    model_config = ConfigDict(extra="forbid")
    confirmation: Literal["REMOVE EXPIRED MEMORY"]


class MemoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    id: UUID
    title: str
    content: str
    provenance: str
    created_by: str
    created_at: datetime
    expires_at: datetime


class MemorySnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: list[MemoryRead]
    expired_count: int
    capacity: Literal[50] = 50
    mode: Literal["operator-managed"] = "operator-managed"
    automatic_context: Literal[False] = False


class MemoryRemoval(BaseModel):
    model_config = ConfigDict(extra="forbid")
    removed_count: int


class MemoryPolicyError(ValueError):
    """Reject without quoting potentially sensitive input."""


def validate_memory(data: MemoryCreate) -> None:
    if any(SENSITIVE_TEXT.search(value) for value in (data.title, data.content, data.provenance)):
        raise MemoryPolicyError(
            "Memory cannot contain recognizable credentials or approval material."
        )


def memory_read(record: AgentMemory) -> MemoryRead:
    # SQLite returns naive timestamps; normalize known UTC storage without using
    # the host timezone. The browser contract always receives explicit offsets.
    return MemoryRead(
        id=record.id,
        title=record.title,
        content=record.content,
        provenance=record.provenance,
        created_by=record.created_by,
        created_at=record.created_at.replace(tzinfo=UTC)
        if record.created_at.tzinfo is None
        else record.created_at,
        expires_at=record.expires_at.replace(tzinfo=UTC)
        if record.expires_at.tzinfo is None
        else record.expires_at,
    )


def snapshot(session: Session, organization_id: UUID, *, now: datetime) -> MemorySnapshot:
    active = session.scalars(
        select(AgentMemory)
        .where(
            AgentMemory.organization_id == organization_id,
            AgentMemory.expires_at > now,
        )
        .order_by(AgentMemory.created_at.desc(), AgentMemory.id)
        .limit(CAPACITY)
    ).all()
    expired = (
        session.scalar(
            select(func.count(AgentMemory.id)).where(
                AgentMemory.organization_id == organization_id,
                AgentMemory.expires_at <= now,
            )
        )
        or 0
    )
    return MemorySnapshot(items=[memory_read(item) for item in active], expired_count=expired)


def audit(session: Session, record: AgentMemory, actor: str, action: str) -> None:
    # Only identity/lifecycle metadata survives physical deletion; no title,
    # content, provenance or content hash belongs in the immutable audit trail.
    session.add(
        AuditEvent(
            organization_id=record.organization_id,
            actor=actor,
            action=f"ai.memory.{action}",
            target_type="agent_memory",
            target_id=str(record.id),
            details={},
        )
    )


def purge_expired(session: Session, organization_id: UUID, actor: str, *, now: datetime) -> int:
    # Serialize cleanup with tenant saves on PostgreSQL; SQLite remains bounded
    # by slot constraints and transaction conflicts rather than a pretend row lock.
    session.execute(
        select(Organization.id)
        .where(
            Organization.id == organization_id,
        )
        .with_for_update()
    ).scalar_one()
    expired = session.scalars(
        select(AgentMemory).where(
            AgentMemory.organization_id == organization_id,
            AgentMemory.expires_at <= now,
        )
    ).all()
    for record in expired:
        audit(session, record, actor, "expired")
        session.delete(record)
    session.flush()
    return len(expired)


def create_memory(
    session: Session,
    organization_id: UUID,
    data: MemoryCreate,
    actor: str,
    *,
    now: datetime,
) -> AgentMemory:
    validate_memory(data)
    # PostgreSQL serializes writers on the parent; SQLite races still fail closed
    # through unique bounded slots. Never trust a count-only quota check.
    # Cleanup retains the parent lock through the caller's eventual commit.
    purge_expired(session, organization_id, actor, now=now)
    occupied = set(
        session.scalars(
            select(AgentMemory.slot).where(
                AgentMemory.organization_id == organization_id,
            )
        ).all()
    )
    slot = next((value for value in range(1, CAPACITY + 1) if value not in occupied), None)
    if slot is None:
        raise MemoryPolicyError("Memory capacity reached; delete a note before saving another.")
    record = AgentMemory(
        organization_id=organization_id,
        slot=slot,
        title=data.title,
        content=data.content,
        provenance=data.provenance,
        created_by=actor,
        created_at=now,
        expires_at=now + timedelta(days=data.retention_days),
    )
    session.add(record)
    session.flush()
    audit(session, record, actor, "created")
    return record
