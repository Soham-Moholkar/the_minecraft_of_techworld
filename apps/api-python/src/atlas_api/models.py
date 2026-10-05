"""Relational models for the first ATLAS organization/project vertical slice."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from atlas_api.database import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class Organization(Base):
    __tablename__ = "organizations"
    __table_args__ = (UniqueConstraint("slug"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    projects: Mapped[list["Project"]] = relationship(back_populates="organization")


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (UniqueConstraint("organization_id", "slug", name="uq_project_org_slug"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    slug: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(24), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    organization: Mapped[Organization] = relationship(back_populates="projects")
    notes: Mapped[list["Note"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    author: Mapped[str] = mapped_column(String(120))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    project: Mapped[Project] = relationship(back_populates="notes")


class AuditEvent(Base):
    """Immutable security/administrative evidence for sensitive mutations."""

    __tablename__ = "audit_events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    actor: Mapped[str] = mapped_column(String(160), index=True)
    action: Mapped[str] = mapped_column(String(120), index=True)
    target_type: Mapped[str] = mapped_column(String(80))
    target_id: Mapped[str] = mapped_column(String(64), index=True)
    details: Mapped[dict[str, str]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )


class Dataset(Base):
    """Tenant-owned cleaned operational data and immutable profiling evidence."""

    __tablename__ = "datasets"
    __table_args__ = (
        UniqueConstraint("id", "organization_id", name="uq_datasets_id_organization"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    source_checksum: Mapped[str] = mapped_column(String(64))
    # Raw uploads are deliberately not retained. Only validated rows enter storage.
    rows: Mapped[list[dict[str, str | float | int]]] = mapped_column(JSON)
    report: Mapped[dict[str, object]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ModelExperiment(Base):
    """Tenant-owned, immutable training and evaluation evidence.

    ATLAS stores metrics and interpretation output, not executable estimator
    pickles. This avoids deserializing code-bearing artifacts at the API boundary
    and keeps every experiment reviewable from ordinary JSON.
    """

    __tablename__ = "model_experiments"
    __table_args__ = (
        ForeignKeyConstraint(
            ["dataset_id", "organization_id"],
            ["datasets.id", "datasets.organization_id"],
            name="fk_model_experiments_dataset_tenant",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    dataset_id: Mapped[UUID] = mapped_column(ForeignKey("datasets.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    report: Mapped[dict[str, object]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AppliedAIExperiment(Base):
    """Tenant-owned evidence for fixed, ATLAS-maintained applied-AI tasks.

    These runs use deterministic synthetic fixtures whose generation rules live
    in source control. The JSON report is reviewable and contains no executable
    checkpoint, downloaded model, or tenant-provided code.
    """

    __tablename__ = "applied_ai_experiments"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    report: Mapped[dict[str, object]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AIPromptVersion(Base):
    """Immutable tenant prompt revision used by repository-intelligence runs.

    Versions are append-only: the API exposes create/list operations but no update
    or delete mutation. A unique tenant/key/version constraint also makes races
    fail visibly instead of silently overwriting another author's prompt.
    """

    __tablename__ = "ai_prompt_versions"
    __table_args__ = (
        UniqueConstraint(
            "organization_id", "prompt_key", "version", name="uq_ai_prompt_tenant_key_version"
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    prompt_key: Mapped[str] = mapped_column(String(64))
    version: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(120))
    instruction: Mapped[str] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AgentMemory(Base):
    """Expiring operator notes, never automatically added to model/tool context.

    A unique bounded slot makes the tenant quota a database invariant even when
    concurrent writers pick the same free slot. Deleted text is not copied to audit.
    """

    __tablename__ = "agent_memories"
    __table_args__ = (
        UniqueConstraint("organization_id", "slot", name="uq_agent_memory_tenant_slot"),
        CheckConstraint("slot >= 1 AND slot <= 50", name="ck_agent_memory_slot"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    slot: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(120))
    content: Mapped[str] = mapped_column(Text)
    provenance: Mapped[str] = mapped_column(String(240))
    created_by: Mapped[str] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class AIRetrievalEvaluation(Base):
    """Immutable evidence from the fixed repository retrieval regression suite."""

    __tablename__ = "ai_retrieval_evaluations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    report: Mapped[dict[str, object]] = mapped_column(JSON)
    created_by: Mapped[str] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AIUsageReservation(Base):
    """Durable monthly-budget reservation settled with provider-reported usage."""

    __tablename__ = "ai_usage_reservations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), index=True)
    provider_requested: Mapped[str] = mapped_column(String(20))
    provider_used: Mapped[str | None] = mapped_column(String(20), nullable=True)
    model: Mapped[str | None] = mapped_column(String(160), nullable=True)
    reserved_cost_microusd: Mapped[int] = mapped_column(Integer)
    actual_cost_microusd: Mapped[int] = mapped_column(Integer, default=0)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    created_by: Mapped[str] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AIRepositoryPatchProposal(Base):
    """Immutable bytes and mutable lifecycle evidence for one reviewed patch.

    The original and patched content are captured at proposal time so approval is
    bound to exact bytes and rollback does not depend on an AI provider. They are
    never returned by list endpoints; the UI receives only the bounded unified diff.
    """

    __tablename__ = "ai_repository_patch_proposals"
    __table_args__ = (
        UniqueConstraint("organization_id", "proposal_digest", name="uq_ai_patch_tenant_digest"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    path: Mapped[str] = mapped_column(String(240))
    summary: Mapped[str] = mapped_column(String(200))
    rationale: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(24), index=True, default="pending")
    original_sha256: Mapped[str] = mapped_column(String(64))
    patched_sha256: Mapped[str] = mapped_column(String(64))
    proposal_digest: Mapped[str] = mapped_column(String(64), index=True)
    original_content: Mapped[str] = mapped_column(Text)
    patched_content: Mapped[str] = mapped_column(Text)
    unified_diff: Mapped[str] = mapped_column(Text)
    start_line: Mapped[int] = mapped_column(Integer)
    end_line: Mapped[int] = mapped_column(Integer)
    proposed_by: Mapped[str] = mapped_column(String(160))
    approved_by: Mapped[str | None] = mapped_column(String(160), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rolled_back_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AIRepositoryPatchWorkflow(Base):
    """Persisted deterministic state for a change-plan-to-proposal workflow."""

    __tablename__ = "ai_repository_patch_workflows"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    proposal_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("ai_repository_patch_proposals.id"), nullable=True, index=True
    )
    objective: Mapped[str] = mapped_column(String(500))
    plan: Mapped[dict[str, object]] = mapped_column(JSON)
    graph_version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(32), index=True)
    current_step: Mapped[str] = mapped_column(String(40))
    events: Mapped[list[dict[str, str]]] = mapped_column(JSON, default=list)
    failure_reason: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_by: Mapped[str] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class AIRepositoryTestRun(Base):
    """Durable approval and execution evidence for one fixed test profile."""

    __tablename__ = "ai_repository_test_runs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    proposal_id: Mapped[UUID] = mapped_column(
        ForeignKey("ai_repository_patch_proposals.id"), index=True
    )
    retry_of_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("ai_repository_test_runs.id"), nullable=True, index=True
    )
    attempt: Mapped[int] = mapped_column(Integer, default=1)
    profile_id: Mapped[str] = mapped_column(String(64), index=True)
    profile_version: Mapped[int] = mapped_column(Integer)
    run_digest: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    requested_by: Mapped[str] = mapped_column(String(160))
    approved_by: Mapped[str | None] = mapped_column(String(160), nullable=True)
    container_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    output_excerpt: Mapped[str] = mapped_column(Text, default="")
    output_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    output_truncated: Mapped[bool] = mapped_column(Boolean, default=False)
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(120), nullable=True)
    cancel_requested: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
