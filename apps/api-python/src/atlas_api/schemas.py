"""Public HTTP schemas; ORM objects never leak across the API boundary directly."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    organization_id: UUID
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", min_length=2, max_length=64)
    name: str = Field(min_length=2, max_length=160)
    description: str = Field(default="", max_length=2000)


class ProjectRead(ProjectCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    status: str
    created_at: datetime


class NoteCreate(BaseModel):
    author: str = Field(min_length=2, max_length=120)
    body: str = Field(min_length=1, max_length=4000)


class NoteRead(NoteCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID
    created_at: datetime


class Page(BaseModel):
    items: list[ProjectRead]
    total: int
    limit: int
    offset: int


class AuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    actor: str
    action: str
    target_type: str
    target_id: str
    details: dict[str, str]
    created_at: datetime


class CurrentIdentity(BaseModel):
    subject: str
    organization_id: UUID
    organization_slug: str
    roles: list[str]


class RealtimeTicketRead(BaseModel):
    ticket: str
    expires_in_seconds: int


class PresencePing(BaseModel):
    type: Literal["presence.ping"]
    request_id: UUID


class PresencePong(BaseModel):
    type: Literal["presence.pong"] = "presence.pong"
    request_id: UUID
    organization_slug: str
    subject: str
    server_time: datetime


class RealtimeError(BaseModel):
    type: Literal["protocol.error"] = "protocol.error"
    code: str
    detail: str


class QueryPlanParameters(BaseModel):
    """Public parameters for the allowlisted project-status diagnostic."""

    status: Literal["active", "paused", "archived"]


class QueryPlanNode(BaseModel):
    """A portable planner node shared by PostgreSQL and SQLite adapters."""

    operation: str
    relation: str | None = None
    detail: str
    estimated_rows: float | None = None
    estimated_cost: float | None = None


class QueryPlanRead(BaseModel):
    """Stable API contract for a database-specific query plan."""

    engine: Literal["postgresql", "sqlite", "mariadb"]
    query_name: Literal["tenant_projects_by_status"]
    parameters: QueryPlanParameters
    nodes: list[QueryPlanNode]
    recommendations: list[str]
    generated_at: datetime


IsolationLevel = Literal[
    "read_uncommitted",
    "read_committed",
    "repeatable_read",
    "serializable",
]


class IsolationCapability(BaseModel):
    """One engine's behavior for a normalized SQL isolation level."""

    level: IsolationLevel
    support: Literal["native", "mapped", "conditional", "unsupported"]
    effective_level: IsolationLevel | None
    detail: str


class DatabaseConcurrencyProfileRead(BaseModel):
    """Portable, read-only snapshot of the active database isolation contract."""

    engine: Literal["postgresql", "sqlite", "mariadb"]
    current_isolation: IsolationLevel
    default_isolation: IsolationLevel
    capabilities: list[IsolationCapability]
    notes: list[str]
    generated_at: datetime


class LockActivityBucket(BaseModel):
    """One privacy-bounded aggregate from the active database lock catalog."""

    mode: str = Field(min_length=1, max_length=64)
    granted: bool
    count: int = Field(ge=0)


class DatabaseLockActivityRead(BaseModel):
    """Portable snapshot used by the Data Estate lock-activity viewer."""

    engine: Literal["postgresql", "sqlite", "mariadb"]
    available: bool
    total_locks: int = Field(ge=0)
    waiting_locks: int = Field(ge=0)
    buckets: list[LockActivityBucket]
    notes: list[str]
    generated_at: datetime


class DatabaseProviderRead(BaseModel):
    """One normalized primary or optional comparison database provider."""

    engine: Literal["postgresql", "sqlite", "mariadb"]
    role: Literal["primary", "comparison"]
    status: Literal["available", "unavailable"]
    version: str | None = Field(default=None, max_length=64)
    current_isolation: IsolationLevel | None = None
    default_isolation: IsolationLevel | None = None
    query_plan_format: Literal["json", "query_plan"]
    transaction_model: str = Field(min_length=1, max_length=160)
    notes: list[str]


class DatabaseProviderComparisonRead(BaseModel):
    """Bounded provider comparison rendered by the Data Estate."""

    providers: list[DatabaseProviderRead]
    generated_at: datetime


class DocumentProjectionItem(BaseModel):
    """Bounded project fields materialized in the document read model."""

    project_slug: str = Field(min_length=2, max_length=64)
    status: str = Field(min_length=1, max_length=24)
    note_count: int = Field(ge=0)
    created_at: datetime


class DocumentProjectionSnapshotRead(BaseModel):
    """Tenant-scoped status of the optional MongoDB project projection."""

    engine: Literal["mongodb"] = "mongodb"
    status: Literal["available", "empty", "unavailable"]
    document_count: int = Field(ge=0)
    published_at: datetime | None = None
    items: list[DocumentProjectionItem] = Field(max_length=25)
    index_strategy: str
    consistency_model: str
    notes: list[str]
    generated_at: datetime


class DocumentProjectionPublishRead(BaseModel):
    """Result of explicitly refreshing one tenant's derived document projection."""

    engine: Literal["mongodb"] = "mongodb"
    published_count: int = Field(ge=0)
    removed_count: int = Field(ge=0)
    published_at: datetime


class CacheStatusCount(BaseModel):
    """One bounded status bucket from the relational project portfolio."""

    status: str = Field(min_length=1, max_length=24)
    count: int = Field(ge=0)


class DatabaseCacheProfileRead(BaseModel):
    """Resilient cache-aside result; relational data is always authoritative."""

    engine: Literal["redis"] = "redis"
    status: Literal["available", "unavailable"]
    cache_state: Literal["hit", "miss", "bypass"]
    project_total: int = Field(ge=0)
    status_counts: list[CacheStatusCount] = Field(max_length=12)
    ttl_seconds: int = Field(ge=0, le=300)
    consistency_model: str
    notes: list[str] = Field(max_length=8)
    generated_at: datetime


class DatabaseWorkbenchRequest(BaseModel):
    """Allowlisted parameters for the read-only database workbench."""

    model_config = ConfigDict(extra="forbid")

    query_name: Literal["tenant_projects_by_status"] = "tenant_projects_by_status"
    status: Literal["active", "paused", "archived"] = "active"
    limit: int = Field(default=10, ge=1, le=25)


class DatabaseWorkbenchItem(BaseModel):
    """Public row shape for the reviewed tenant project query."""

    project_slug: str = Field(min_length=2, max_length=64)
    status: str = Field(min_length=1, max_length=24)
    note_count: int = Field(ge=0)
    created_at: datetime


class DatabaseWorkbenchRead(BaseModel):
    """Bounded result from one source-reviewed query template."""

    engine: Literal["postgresql", "sqlite"]
    query_name: Literal["tenant_projects_by_status"]
    parameters: DatabaseWorkbenchRequest
    items: list[DatabaseWorkbenchItem] = Field(max_length=25)
    returned_count: int = Field(ge=0, le=25)
    safety_model: str
    generated_at: datetime
