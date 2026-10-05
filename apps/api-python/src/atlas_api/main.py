"""FastAPI composition root for the ATLAS control plane."""

import asyncio
import time
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID, uuid4

import structlog
from fastapi import (
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from pydantic import ValidationError
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from atlas_api import __version__
from atlas_api.applied_routes import router as applied_router
from atlas_api.auth import Principal, require_principal
from atlas_api.cache_profile import RedisProjectCacheRepository
from atlas_api.concurrency_profiles import ConcurrencyProfileRepository
from atlas_api.config import Settings, get_settings
from atlas_api.database import get_session
from atlas_api.database_workbench import DatabaseWorkbenchRepository
from atlas_api.document_projection import (
    DocumentProjectionUnavailable,
    MongoProjectProjectionRepository,
)
from atlas_api.lock_activity import LockActivityRepository
from atlas_api.models import Organization
from atlas_api.provider_comparison import ProviderComparisonRepository
from atlas_api.query_plans import ProjectStatus, QueryName, QueryPlanRepository
from atlas_api.realtime import ConnectionCapacity, RealtimeTicketStore, SlidingWindowRateLimiter
from atlas_api.repository import ProjectRepository
from atlas_api.schemas import (
    AuditEventRead,
    CurrentIdentity,
    DatabaseCacheProfileRead,
    DatabaseConcurrencyProfileRead,
    DatabaseLockActivityRead,
    DatabaseProviderComparisonRead,
    DatabaseWorkbenchRead,
    DatabaseWorkbenchRequest,
    DocumentProjectionPublishRead,
    DocumentProjectionSnapshotRead,
    NoteCreate,
    NoteRead,
    Page,
    PresencePing,
    PresencePong,
    ProjectCreate,
    ProjectRead,
    QueryPlanRead,
    RealtimeError,
    RealtimeTicketRead,
)

logger = structlog.get_logger()
REQUESTS = Counter("atlas_http_requests_total", "HTTP requests", ["method", "route", "status"])
LATENCY = Histogram("atlas_http_request_duration_seconds", "HTTP latency", ["method", "route"])
WEBSOCKET_CONNECTIONS = Gauge(
    "atlas_websocket_active_connections",
    "Active authenticated realtime connections",
    ["tenant"],
)
WEBSOCKET_MESSAGES = Counter(
    "atlas_websocket_messages_total",
    "Realtime messages by direction and bounded protocol type",
    ["direction", "message_type"],
)
WEBSOCKET_REJECTIONS = Counter(
    "atlas_websocket_rejections_total",
    "Rejected realtime handshakes or messages",
    ["reason"],
)
WEBSOCKET_MESSAGE_DURATION = Histogram(
    "atlas_websocket_message_duration_seconds",
    "Server-side realtime message handling latency",
    ["message_type"],
)
WEBSOCKET_TICKETS = Counter(
    "atlas_websocket_tickets_issued_total",
    "Short-lived realtime tickets issued",
)
REALTIME_TICKETS = RealtimeTicketStore()
REALTIME_CAPACITY = ConnectionCapacity()
QUERY_PLANS = Counter(
    "atlas_database_query_plans_total",
    "Allowlisted database query plans generated",
    ["engine", "query_name"],
)
CONCURRENCY_PROFILES = Counter(
    "atlas_database_concurrency_profiles_total",
    "Read-only database concurrency profiles generated",
    ["engine"],
)
LOCK_ACTIVITY_SNAPSHOTS = Counter(
    "atlas_database_lock_activity_snapshots_total",
    "Privacy-bounded database lock snapshots generated",
    ["engine", "available"],
)
PROVIDER_COMPARISONS = Counter(
    "atlas_database_provider_comparisons_total",
    "Normalized database provider observations",
    ["engine", "status"],
)
DOCUMENT_PROJECTIONS = Counter(
    "atlas_database_document_projection_operations_total",
    "MongoDB document projection operations",
    ["operation", "status"],
)
CACHE_PROFILES = Counter(
    "atlas_database_cache_profile_operations_total",
    "Redis cache-aside portfolio reads",
    ["status", "cache_state"],
)
WORKBENCH_QUERIES = Counter(
    "atlas_database_workbench_queries_total",
    "Allowlisted database workbench queries",
    ["engine", "query_name", "status"],
)

app = FastAPI(
    title="ATLAS Control Plane",
    version=__version__,
    summary="Multi-tenant project and engineering operations API",
)
app.include_router(applied_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "Last-Event-ID", "X-Request-ID"],
)


@app.middleware("http")
async def operational_boundary(request: Request, call_next):  # type: ignore[no-untyped-def]
    """Attach correlation/security headers and record every completed request."""

    started = time.perf_counter()
    if request.url.path.startswith("/v1/streaming/usage") and request.method == "POST":
        # Bound bytes before JSON parsing, including chunked requests. The request
        # cache lets FastAPI validate the same body after this admission check.
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 16_000:
                return JSONResponse({"detail": "stream batch too large"}, status_code=413,
                                    headers={"Cache-Control": "no-store"})
        request._body = bytes(body)
    request_id = request.headers.get("x-request-id", str(uuid4()))[:128]
    response = await call_next(request)
    if request.url.path.startswith(("/v1/streaming/usage", "/v1/pipelines/usage",
                                    "/v1/infrastructure/")):
        response.headers["Cache-Control"] = "no-store"
    route = request.scope.get("route")
    route_path = getattr(route, "path", "unmatched")
    elapsed = time.perf_counter() - started
    REQUESTS.labels(request.method, route_path, response.status_code).inc()
    LATENCY.labels(request.method, route_path).observe(elapsed)
    response.headers.update(
        {
            "X-Request-ID": request_id,
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "no-referrer",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        }
    )
    logger.info(
        "http_request",
        request_id=request_id,
        method=request.method,
        route=route_path,
        status=response.status_code,
        duration_ms=round(elapsed * 1000, 2),
    )
    return response


@app.get("/health", tags=["operations"])
def health(session: Annotated[Session, Depends(get_session)]) -> dict[str, str]:
    session.execute(text("SELECT 1"))
    return {"status": "ok", "database": "reachable", "version": __version__}


@app.get("/version", tags=["operations"])
def version() -> dict[str, str]:
    return {"service": "atlas-api", "version": __version__}


@app.get("/v1/me", response_model=CurrentIdentity, tags=["identity"])
def current_identity(
    session: Annotated[Session, Depends(get_session)],
    principal: Annotated[Principal, Depends(require_principal)],
) -> CurrentIdentity:
    organization = session.scalar(
        select(Organization).where(Organization.slug == principal.organization_slug)
    )
    if organization is None:
        # A valid identity without a tenant binding is unusable and should alert;
        # never silently attach it to the first organization in the database.
        raise HTTPException(status_code=403, detail="identity has no organization binding")
    return CurrentIdentity(
        subject=principal.subject,
        organization_id=organization.id,
        organization_slug=organization.slug,
        roles=list(principal.roles),
    )


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/realtime/tickets", response_model=RealtimeTicketRead, tags=["events"])
def issue_realtime_ticket(
    response: Response,
    principal: Annotated[Principal, Depends(require_principal)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> RealtimeTicketRead:
    """Exchange HTTP authentication for a short-lived, one-use socket grant.

    Browser WebSocket APIs cannot attach an Authorization header. An opaque grant
    avoids placing the long-lived service credential in a URL, log, or browser state.
    """

    ticket = REALTIME_TICKETS.issue(
        principal,
        ttl_seconds=settings.realtime_ticket_ttl_seconds,
    )
    WEBSOCKET_TICKETS.inc()
    response.headers["Cache-Control"] = "no-store"
    return RealtimeTicketRead(
        ticket=ticket,
        expires_in_seconds=settings.realtime_ticket_ttl_seconds,
    )


@app.get("/v1/projects", response_model=Page, tags=["projects"])
def list_projects(
    session: Annotated[Session, Depends(get_session)],
    principal: Annotated[Principal, Depends(require_principal)],
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page:
    items, total = ProjectRepository(session).list_projects(
        organization_slug=principal.organization_slug, limit=limit, offset=offset
    )
    return Page(
        items=[ProjectRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@app.get("/v1/search", response_model=list[ProjectRead], tags=["search"])
def search(
    session: Annotated[Session, Depends(get_session)],
    principal: Annotated[Principal, Depends(require_principal)],
    query: Annotated[str, Query(alias="q", min_length=2, max_length=120)],
    limit: Annotated[int, Query(ge=1, le=25)] = 10,
) -> list[ProjectRead]:
    """Return authoritative project matches from the L1 search provider."""

    matches = ProjectRepository(session).search(
        query.strip(), organization_slug=principal.organization_slug, limit=limit
    )
    return [ProjectRead.model_validate(project) for project in matches]


@app.get("/v1/database/query-plan", response_model=QueryPlanRead, tags=["database"])
def database_query_plan(
    session: Annotated[Session, Depends(get_session)],
    principal: Annotated[Principal, Depends(require_principal)],
    query_name: Annotated[QueryName, Query()] = "tenant_projects_by_status",
    project_status: Annotated[ProjectStatus, Query(alias="status")] = "active",
) -> QueryPlanRead:
    """Return a normalized plan for one reviewed, tenant-scoped read query.

    The caller supplies a query *name*, never SQL. Keeping the statement allowlist
    in source prevents this observability endpoint from becoming a database console
    or a side-effect primitive.
    """

    # This explicit branch remains useful as the allowlist grows: every public name
    # must map to one reviewed repository method and its own typed parameter set.
    if query_name == "tenant_projects_by_status":
        plan = QueryPlanRepository(session).explain_tenant_projects_by_status(
            organization_slug=principal.organization_slug,
            status=project_status,
        )
    QUERY_PLANS.labels(plan.engine, plan.query_name).inc()
    logger.info(
        "database_query_plan_generated",
        tenant=principal.organization_slug,
        query_name=plan.query_name,
        engine=plan.engine,
        status=project_status,
    )
    return plan


@app.post(
    "/v1/database/workbench",
    response_model=DatabaseWorkbenchRead,
    tags=["database"],
)
def database_workbench(
    request: DatabaseWorkbenchRequest,
    session: Annotated[Session, Depends(get_session)],
    principal: Annotated[Principal, Depends(require_principal)],
) -> DatabaseWorkbenchRead:
    """Run one bounded, parameterized, source-reviewed tenant query template."""

    result = DatabaseWorkbenchRepository(session).execute(
        request,
        organization_slug=principal.organization_slug,
    )
    WORKBENCH_QUERIES.labels(
        result.engine, result.query_name, request.status
    ).inc()
    logger.info(
        "database_workbench_query_completed",
        tenant=principal.organization_slug,
        engine=result.engine,
        query_name=result.query_name,
        project_status=request.status,
        returned_count=result.returned_count,
    )
    return result


@app.get(
    "/v1/database/cache-profile",
    response_model=DatabaseCacheProfileRead,
    tags=["database"],
)
def database_cache_profile(
    session: Annotated[Session, Depends(get_session)],
    principal: Annotated[Principal, Depends(require_principal)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DatabaseCacheProfileRead:
    """Read a tenant portfolio through optional Redis with SQL fallback."""

    redis_url = (
        settings.redis_cache_url.get_secret_value()
        if settings.redis_cache_url is not None
        else None
    )
    result = RedisProjectCacheRepository(session, redis_url).read(
        organization_slug=principal.organization_slug
    )
    CACHE_PROFILES.labels(result.status, result.cache_state).inc()
    logger.info(
        "database_cache_profile_completed",
        tenant=principal.organization_slug,
        engine=result.engine,
        status=result.status,
        cache_state=result.cache_state,
        project_total=result.project_total,
    )
    return result


@app.get(
    "/v1/database/concurrency-profile",
    response_model=DatabaseConcurrencyProfileRead,
    tags=["database"],
)
def database_concurrency_profile(
    session: Annotated[Session, Depends(get_session)],
    principal: Annotated[Principal, Depends(require_principal)],
) -> DatabaseConcurrencyProfileRead:
    """Inspect engine isolation behavior without accepting or executing caller SQL."""

    profile = ConcurrencyProfileRepository(session).read()
    CONCURRENCY_PROFILES.labels(profile.engine).inc()
    logger.info(
        "database_concurrency_profile_generated",
        tenant=principal.organization_slug,
        engine=profile.engine,
        current_isolation=profile.current_isolation,
        default_isolation=profile.default_isolation,
    )
    return profile


@app.get(
    "/v1/database/lock-activity",
    response_model=DatabaseLockActivityRead,
    tags=["database"],
)
def database_lock_activity(
    session: Annotated[Session, Depends(get_session)],
    principal: Annotated[Principal, Depends(require_principal)],
) -> DatabaseLockActivityRead:
    """Return aggregate lock modes without disclosing queries, relations, or PIDs."""

    snapshot = LockActivityRepository(session).read()
    LOCK_ACTIVITY_SNAPSHOTS.labels(snapshot.engine, str(snapshot.available).lower()).inc()
    logger.info(
        "database_lock_activity_generated",
        tenant=principal.organization_slug,
        engine=snapshot.engine,
        available=snapshot.available,
        total_locks=snapshot.total_locks,
        waiting_locks=snapshot.waiting_locks,
    )
    return snapshot


@app.get(
    "/v1/database/providers",
    response_model=DatabaseProviderComparisonRead,
    tags=["database"],
)
def database_providers(
    session: Annotated[Session, Depends(get_session)],
    principal: Annotated[Principal, Depends(require_principal)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DatabaseProviderComparisonRead:
    """Compare the active provider with optional least-privileged MariaDB evidence."""

    observer_url = (
        settings.mariadb_observer_url.get_secret_value()
        if settings.mariadb_observer_url is not None
        else None
    )
    comparison = ProviderComparisonRepository(session, observer_url).read()
    statuses: list[str] = []
    for provider in comparison.providers:
        PROVIDER_COMPARISONS.labels(provider.engine, provider.status).inc()
        statuses.append(f"{provider.engine}:{provider.status}")
    # Keep labels bounded and omit connection/error data from both logs and metrics.
    logger.info(
        "database_providers_compared",
        tenant=principal.organization_slug,
        providers=statuses,
    )
    return comparison


@app.get(
    "/v1/database/document-projection",
    response_model=DocumentProjectionSnapshotRead,
    tags=["database"],
)
def database_document_projection(
    session: Annotated[Session, Depends(get_session)],
    principal: Annotated[Principal, Depends(require_principal)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DocumentProjectionSnapshotRead:
    """Read the current tenant's bounded MongoDB project projection."""

    mongodb_url = (
        settings.mongodb_projection_url.get_secret_value()
        if settings.mongodb_projection_url is not None
        else None
    )
    snapshot = MongoProjectProjectionRepository(session, mongodb_url).read(
        organization_slug=principal.organization_slug
    )
    DOCUMENT_PROJECTIONS.labels("read", snapshot.status).inc()
    logger.info(
        "database_document_projection_read",
        tenant=principal.organization_slug,
        engine=snapshot.engine,
        status=snapshot.status,
        document_count=snapshot.document_count,
    )
    return snapshot


@app.post(
    "/v1/database/document-projection/publish",
    response_model=DocumentProjectionPublishRead,
    tags=["database"],
)
def publish_database_document_projection(
    session: Annotated[Session, Depends(get_session)],
    principal: Annotated[Principal, Depends(require_principal)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DocumentProjectionPublishRead:
    """Explicitly refresh the caller's MongoDB read model from PostgreSQL."""

    if "owner" not in principal.roles:
        DOCUMENT_PROJECTIONS.labels("publish", "forbidden").inc()
        raise HTTPException(status_code=403, detail="owner role required")
    mongodb_url = (
        settings.mongodb_projection_url.get_secret_value()
        if settings.mongodb_projection_url is not None
        else None
    )
    try:
        result = MongoProjectProjectionRepository(session, mongodb_url).publish(
            organization_slug=principal.organization_slug
        )
    except DocumentProjectionUnavailable as error:
        DOCUMENT_PROJECTIONS.labels("publish", "unavailable").inc()
        logger.warning(
            "database_document_projection_unavailable",
            tenant=principal.organization_slug,
            engine="mongodb",
        )
        raise HTTPException(status_code=503, detail="document projection unavailable") from error
    DOCUMENT_PROJECTIONS.labels("publish", "success").inc()
    logger.info(
        "database_document_projection_published",
        tenant=principal.organization_slug,
        engine=result.engine,
        published_count=result.published_count,
        removed_count=result.removed_count,
    )
    return result


@app.post(
    "/v1/projects",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    tags=["projects"],
)
def create_project(
    data: ProjectCreate,
    session: Annotated[Session, Depends(get_session)],
    principal: Annotated[Principal, Depends(require_principal)],
) -> ProjectRead:
    try:
        return ProjectRead.model_validate(
            ProjectRepository(session).create(
                data, organization_slug=principal.organization_slug, actor=principal.subject
            )
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post(
    "/v1/projects/{project_id}/notes",
    response_model=NoteRead,
    status_code=status.HTTP_201_CREATED,
    tags=["projects"],
)
def add_note(
    project_id: UUID,
    data: NoteCreate,
    session: Annotated[Session, Depends(get_session)],
    principal: Annotated[Principal, Depends(require_principal)],
) -> NoteRead:
    repository = ProjectRepository(session)
    project = repository.get(project_id, organization_slug=principal.organization_slug)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    return NoteRead.model_validate(repository.add_note(project, data, actor=principal.subject))


@app.get("/v1/projects/{project_id}/notes", response_model=list[NoteRead], tags=["projects"])
def list_notes(
    project_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    principal: Annotated[Principal, Depends(require_principal)],
) -> list[NoteRead]:
    repository = ProjectRepository(session)
    project = repository.get(project_id, organization_slug=principal.organization_slug)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    return [NoteRead.model_validate(note) for note in repository.list_notes(project)]


@app.get("/v1/audit", response_model=list[AuditEventRead], tags=["security"])
def list_audit(
    session: Annotated[Session, Depends(get_session)],
    principal: Annotated[Principal, Depends(require_principal)],
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
) -> list[AuditEventRead]:
    events = ProjectRepository(session).list_audit(
        organization_slug=principal.organization_slug, limit=limit
    )
    return [AuditEventRead.model_validate(event) for event in events]


async def audit_event_stream(
    *, organization_slug: str, limit: int, once: bool, initial: list[AuditEventRead]
) -> AsyncIterator[str]:
    """Poll the portable repository and encode new audit records as SSE frames.

    A later event-broker adapter can replace polling without changing the browser
    contract. Each poll owns a fresh session because request-scoped sessions close
    before a long-lived streaming response completes.
    """

    from atlas_api.database import SessionLocal

    emitted: set[str] = set()
    # Browsers use this field to wait before reconnecting after a network break.
    yield "retry: 2000\n\n"
    for event in initial:
        event_id = str(event.id)
        emitted.add(event_id)
        yield f"id: {event_id}\nevent: audit\ndata: {event.model_dump_json()}\n\n"
    if once:
        return
    while True:
        with SessionLocal() as stream_session:
            events = ProjectRepository(stream_session).list_audit(
                organization_slug=organization_slug, limit=limit
            )
            payloads = [AuditEventRead.model_validate(event) for event in reversed(events)]
        for event in payloads:
            event_id = str(event.id)
            if event_id in emitted:
                continue
            emitted.add(event_id)
            yield f"id: {event_id}\nevent: audit\ndata: {event.model_dump_json()}\n\n"
        # SSE comments keep intermediaries from treating an idle connection as dead.
        yield ": heartbeat\n\n"
        await asyncio.sleep(2)


@app.get("/v1/events/stream", tags=["events"])
def stream_events(
    session: Annotated[Session, Depends(get_session)],
    principal: Annotated[Principal, Depends(require_principal)],
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
    once: bool = False,
    last_event_id: Annotated[UUID | None, Header(alias="Last-Event-ID")] = None,
) -> StreamingResponse:
    """Stream tenant audit events, resuming strictly after Last-Event-ID."""

    # Materialize through the injected provider so SQLite tests and PostgreSQL
    # production share the same initial-snapshot behavior.
    repository = ProjectRepository(session)
    if last_event_id is None:
        events = repository.list_audit(
            organization_slug=principal.organization_slug, limit=limit
        )
        events.reverse()
    else:
        resumed = repository.list_audit_after(
            organization_slug=principal.organization_slug,
            cursor_id=last_event_id,
            limit=limit,
        )
        if resumed is None:
            # Do not silently replay a snapshot: clients must decide how to recover
            # from expired state, and another tenant's cursor remains undisclosed.
            raise HTTPException(status_code=409, detail="event cursor unavailable")
        events = resumed
    initial = [AuditEventRead.model_validate(event) for event in events]
    return StreamingResponse(
        audit_event_stream(
            organization_slug=principal.organization_slug,
            limit=limit,
            once=once,
            initial=initial,
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no"},
    )


async def reject_websocket(websocket: WebSocket, *, code: int, reason: str) -> None:
    """Close a handshake with a stable private code and bounded metric label."""

    WEBSOCKET_REJECTIONS.labels(reason).inc()
    logger.warning("websocket_rejected", reason=reason)
    await websocket.close(code=code, reason=reason)


@app.websocket("/v1/realtime/ws")
async def realtime_websocket(
    websocket: WebSocket,
    ticket: Annotated[str, Query(min_length=32, max_length=128)],
) -> None:
    """Serve the first authenticated, tenant-bound bidirectional protocol.

    The current presence request is intentionally small, but the boundary already
    demonstrates the controls every later collaborative protocol must retain:
    origin validation, one-use auth, capacity, message size/rate limits, typed
    envelopes, structured lifecycle logs, and low-cardinality metrics.
    """

    settings = get_settings()
    origin = websocket.headers.get("origin")
    if origin not in settings.origin_list:
        # Validate origin before redemption so a cross-site handshake cannot burn a
        # legitimate ticket that it somehow observed.
        await reject_websocket(websocket, code=4403, reason="origin_not_allowed")
        return
    principal = REALTIME_TICKETS.redeem(ticket)
    if principal is None:
        await reject_websocket(websocket, code=4401, reason="ticket_unavailable")
        return
    if not REALTIME_CAPACITY.acquire(maximum=settings.realtime_max_connections):
        await reject_websocket(websocket, code=4429, reason="connection_capacity")
        return

    limiter = SlidingWindowRateLimiter(
        maximum=settings.realtime_messages_per_window,
        window_seconds=float(settings.realtime_rate_window_seconds),
    )
    connected_at = time.perf_counter()
    tenant = principal.organization_slug
    WEBSOCKET_CONNECTIONS.labels(tenant).inc()
    await websocket.accept()
    logger.info(
        "websocket_connected",
        tenant=tenant,
        subject=principal.subject,
    )
    try:
        while True:
            message = await websocket.receive()
            if message["type"] == "websocket.disconnect":
                break
            payload = message.get("text")
            if not isinstance(payload, str):
                await reject_websocket(websocket, code=4400, reason="text_required")
                return
            if len(payload.encode("utf-8")) > settings.realtime_max_message_bytes:
                await reject_websocket(websocket, code=4409, reason="message_too_large")
                return
            if not limiter.allow():
                await reject_websocket(websocket, code=4429, reason="message_rate")
                return

            started = time.perf_counter()
            try:
                request = PresencePing.model_validate_json(payload)
            except ValidationError:
                WEBSOCKET_MESSAGES.labels("inbound", "protocol.invalid").inc()
                error = RealtimeError(
                    code="invalid_message",
                    detail="expected a presence.ping envelope with a UUID request_id",
                )
                await websocket.send_json(error.model_dump(mode="json"))
                WEBSOCKET_MESSAGES.labels("outbound", error.type).inc()
                continue

            WEBSOCKET_MESSAGES.labels("inbound", request.type).inc()
            response = PresencePong(
                request_id=request.request_id,
                organization_slug=tenant,
                subject=principal.subject,
                server_time=datetime.now(UTC),
            )
            await websocket.send_json(response.model_dump(mode="json"))
            WEBSOCKET_MESSAGES.labels("outbound", response.type).inc()
            WEBSOCKET_MESSAGE_DURATION.labels(request.type).observe(
                time.perf_counter() - started
            )
    except WebSocketDisconnect:
        # Disconnects are a normal transport event; lifecycle telemetry below still
        # records the session without manufacturing an application error.
        pass
    finally:
        WEBSOCKET_CONNECTIONS.labels(tenant).dec()
        REALTIME_CAPACITY.release()
        logger.info(
            "websocket_disconnected",
            tenant=tenant,
            subject=principal.subject,
            duration_ms=round((time.perf_counter() - connected_at) * 1000, 2),
        )
