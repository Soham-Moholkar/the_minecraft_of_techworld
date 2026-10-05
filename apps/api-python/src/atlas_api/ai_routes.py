"""Authenticated repository-intelligence HTTP boundary."""

import hashlib
import json
import time
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from prometheus_client import Counter, Histogram
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from atlas_api.agent_mcp import MCPDiscoveryCatalog, build_mcp_catalog
from atlas_api.agent_patches import (
    PatchApproval,
    PatchConflictError,
    PatchGateway,
    PatchPolicyError,
    PatchProposalCreate,
    PatchProposalRead,
    PatchRollback,
)
from atlas_api.agent_tests import (
    TEST_PROFILES,
    TestProfileRead,
    TestRunApproval,
    TestRunRead,
    TestRunRequest,
    TestRunTransitionError,
    approve_test_run,
    cancel_test_run,
    create_test_run,
    get_test_profile,
    profile_read,
    test_run_read,
    verify_test_run_policy,
)
from atlas_api.agent_workflows import (
    PatchWorkflowCreate,
    PatchWorkflowMachine,
    PatchWorkflowRead,
    WorkflowCondition,
    WorkflowReplayRead,
    WorkflowTransitionError,
    workflow_read,
)
from atlas_api.ai_operations import (
    AIBudgetExceeded,
    AIOperationsSnapshot,
    ai_slo_tracker,
    budget_snapshot,
    fail_budget,
    reserve_budget,
    settle_budget,
)
from atlas_api.auth import Principal, require_principal
from atlas_api.config import Settings, get_settings
from atlas_api.database import get_session
from atlas_api.models import (
    AIPromptVersion,
    AIRepositoryPatchProposal,
    AIRepositoryPatchWorkflow,
    AIRepositoryTestRun,
    AIRetrievalEvaluation,
    AuditEvent,
    Organization,
)
from atlas_api.repository_ai import (
    AIProviderContractError,
    AIProviderUnavailable,
    AnnotatedSourceLine,
    CodeIntelligenceProvider,
    ModelUsage,
    PromptVersionCreate,
    PromptVersionRead,
    ProviderHealth,
    RepositoryExplainRequest,
    RepositoryExplanation,
    RepositoryFile,
    RepositoryPathError,
    get_code_provider,
    get_source_reader,
    provider_health,
)
from atlas_api.repository_retrieval import (
    RepositoryRetriever,
    RetrievalEvaluation,
    RetrievalEvaluationRead,
    RetrievalRequest,
    RetrievalResponse,
)

router = APIRouter(prefix="/v1/ai/repository", tags=["repository-ai"])
logger = structlog.get_logger()
RUNS = Counter("atlas_repository_ai_runs_total", "Repository AI runs", ["outcome", "intent"])
RUN_SECONDS = Histogram("atlas_repository_ai_run_seconds", "Repository AI provider latency")
TOKENS = Counter("atlas_repository_ai_tokens_total", "Repository AI tokens", ["direction", "model"])
RETRIEVAL_RUNS = Counter(
    "atlas_repository_retrieval_runs_total",
    "Repository retrieval runs",
    ["outcome", "mode"],
)
RETRIEVAL_SECONDS = Histogram(
    "atlas_repository_retrieval_run_seconds",
    "Repository retrieval latency",
)
RETRIEVAL_EVALUATIONS = Counter(
    "atlas_repository_retrieval_evaluations_total",
    "Persisted repository retrieval evaluations",
    ["outcome"],
)
RETRIEVAL_CACHE = Counter(
    "atlas_repository_retrieval_cache_total",
    "Content-addressed repository retrieval cache outcomes",
    ["outcome"],
)
FALLBACKS = Counter(
    "atlas_repository_ai_fallbacks_total",
    "Repository AI automatic provider fallbacks",
    ["from_provider", "to_provider"],
)
PATCH_ACTIONS = Counter(
    "atlas_repository_patch_actions_total",
    "Human-approved repository patch lifecycle actions",
    ["action", "outcome"],
)
WORKFLOW_ACTIONS = Counter(
    "atlas_repository_patch_workflows_total",
    "Deterministic repository patch workflow transitions",
    ["state"],
)
TEST_RUN_ACTIONS = Counter(
    "atlas_repository_test_runs_total",
    "Separately approved isolated repository test lifecycle actions",
    ["action", "outcome"],
)
MCP_CATALOG_READS = Counter(
    "atlas_repository_mcp_catalog_reads_total", "Authorized MCP contract reads"
)

Db = Annotated[Session, Depends(get_session)]
Identity = Annotated[Principal, Depends(require_principal)]
Configuration = Annotated[Settings, Depends(get_settings)]


def provider_dependency(settings: Configuration) -> CodeIntelligenceProvider:
    return get_code_provider(settings)


Provider = Annotated[CodeIntelligenceProvider, Depends(provider_dependency)]


@router.get("/files")
def list_repository_files(settings: Configuration, _: Identity) -> list[RepositoryFile]:
    """Return metadata only; file bodies remain behind the bounded explain call."""
    return get_source_reader(settings).catalog()


@router.get("/providers")
def list_repository_ai_providers(settings: Configuration, _: Identity) -> list[ProviderHealth]:
    """Compare redacted hosted/local readiness without exposing endpoint URLs."""

    return provider_health(settings)


@router.get("/operations")
def repository_ai_operations(
    session: Db, principal: Identity, settings: Configuration
) -> AIOperationsSnapshot:
    organization = session.scalar(
        select(Organization).where(Organization.slug == principal.organization_slug)
    )
    if organization is None:
        raise HTTPException(404, "organization not found")
    return AIOperationsSnapshot(
        budget=budget_snapshot(session, organization.id, settings),
        slo=ai_slo_tracker.snapshot(settings),
    )


@router.get("/prompts")
def list_prompt_versions(session: Db, principal: Identity) -> list[PromptVersionRead]:
    organization = session.scalar(
        select(Organization).where(Organization.slug == principal.organization_slug)
    )
    if organization is None:
        raise HTTPException(404, "organization not found")
    prompts = session.scalars(
        select(AIPromptVersion)
        .where(AIPromptVersion.organization_id == organization.id)
        .order_by(AIPromptVersion.prompt_key, AIPromptVersion.version.desc())
        .limit(100)
    ).all()
    return [PromptVersionRead.model_validate(prompt) for prompt in prompts]


@router.post("/prompts", status_code=201)
def create_prompt_version(
    data: PromptVersionCreate, session: Db, principal: Identity
) -> PromptVersionRead:
    if "owner" not in principal.roles:
        raise HTTPException(403, "owner role required")
    organization = session.scalar(
        select(Organization)
        .where(Organization.slug == principal.organization_slug)
        .with_for_update()
    )
    if organization is None:
        raise HTTPException(404, "organization not found")
    count = session.scalar(
        select(func.count(AIPromptVersion.id)).where(
            AIPromptVersion.organization_id == organization.id
        )
    )
    if (count or 0) >= 100:
        raise HTTPException(409, "prompt version quota reached")
    latest = session.scalar(
        select(func.max(AIPromptVersion.version)).where(
            AIPromptVersion.organization_id == organization.id,
            AIPromptVersion.prompt_key == data.prompt_key,
        )
    )
    prompt = AIPromptVersion(
        organization_id=organization.id,
        prompt_key=data.prompt_key,
        version=(latest or 0) + 1,
        name=data.name,
        instruction=data.instruction,
        created_by=principal.subject,
    )
    session.add(prompt)
    session.flush()
    session.add(
        AuditEvent(
            organization_id=organization.id,
            actor=principal.subject,
            action="ai.prompt.version_created",
            target_type="ai_prompt_version",
            target_id=str(prompt.id),
            details={"prompt_key": prompt.prompt_key, "version": str(prompt.version)},
        )
    )
    session.commit()
    return PromptVersionRead.model_validate(prompt)


@router.post("/retrieval/search")
def search_repository(
    request: RetrievalRequest, session: Db, principal: Identity, settings: Configuration
) -> RetrievalResponse:
    if "owner" not in principal.roles:
        raise HTTPException(403, "owner role required")
    organization = session.scalar(
        select(Organization).where(Organization.slug == principal.organization_slug)
    )
    if organization is None:
        raise HTTPException(404, "organization not found")
    started = time.perf_counter()
    result = RepositoryRetriever(get_source_reader(settings)).search(request)
    RETRIEVAL_SECONDS.observe(time.perf_counter() - started)
    RETRIEVAL_RUNS.labels("success", request.mode).inc()
    RETRIEVAL_CACHE.labels("hit").inc(result.cache_hits)
    RETRIEVAL_CACHE.labels("miss").inc(result.cache_misses)
    logger.info(
        "repository_retrieval_completed",
        query_hash=hashlib.sha256(request.query.encode()).hexdigest()[:16],
        mode=request.mode,
        hits=len(result.hits),
        truncated=result.truncated,
    )
    return result


@router.get("/retrieval/evaluations")
def list_retrieval_evaluations(session: Db, principal: Identity) -> list[RetrievalEvaluationRead]:
    organization = session.scalar(
        select(Organization).where(Organization.slug == principal.organization_slug)
    )
    if organization is None:
        raise HTTPException(404, "organization not found")
    records = session.scalars(
        select(AIRetrievalEvaluation)
        .where(AIRetrievalEvaluation.organization_id == organization.id)
        .order_by(AIRetrievalEvaluation.created_at.desc())
        .limit(50)
    ).all()
    return [
        RetrievalEvaluationRead(
            id=record.id,
            name=record.name,
            report=RetrievalEvaluation.model_validate(record.report),
            created_by=record.created_by,
            created_at=record.created_at,
        )
        for record in records
    ]


@router.post("/retrieval/evaluations", status_code=201)
def run_retrieval_evaluation(
    session: Db, principal: Identity, settings: Configuration
) -> RetrievalEvaluationRead:
    if "owner" not in principal.roles:
        raise HTTPException(403, "owner role required")
    organization = session.scalar(
        select(Organization)
        .where(Organization.slug == principal.organization_slug)
        .with_for_update()
    )
    if organization is None:
        raise HTTPException(404, "organization not found")
    count = session.scalar(
        select(func.count(AIRetrievalEvaluation.id)).where(
            AIRetrievalEvaluation.organization_id == organization.id
        )
    )
    if (count or 0) >= 100:
        raise HTTPException(409, "retrieval evaluation quota reached")
    report = RepositoryRetriever(get_source_reader(settings)).evaluate()
    RETRIEVAL_EVALUATIONS.labels(
        "passed"
        if report.grounding_passed
        and report.citation_accuracy == 1.0
        and report.injection_detection_passed
        else "failed"
    ).inc()
    record = AIRetrievalEvaluation(
        organization_id=organization.id,
        name="Repository retrieval regression",
        report=report.model_dump(mode="json"),
        created_by=principal.subject,
    )
    session.add(record)
    session.flush()
    session.add(
        AuditEvent(
            organization_id=organization.id,
            actor=principal.subject,
            action="ai.retrieval.evaluated",
            target_type="ai_retrieval_evaluation",
            target_id=str(record.id),
            details={
                "grounding_passed": str(report.grounding_passed),
                "citation_accuracy": str(report.citation_accuracy),
                "injection_detection_passed": str(report.injection_detection_passed),
            },
        )
    )
    session.commit()
    return RetrievalEvaluationRead(
        id=record.id,
        name=record.name,
        report=report,
        created_by=record.created_by,
        created_at=record.created_at,
    )


@router.post("/explain")
def explain_repository_file(
    request: RepositoryExplainRequest,
    session: Db,
    principal: Identity,
    settings: Configuration,
    provider: Provider,
) -> RepositoryExplanation:
    if "owner" not in principal.roles:
        raise HTTPException(403, "owner role required")
    organization = session.scalar(
        select(Organization).where(Organization.slug == principal.organization_slug)
    )
    if organization is None:
        raise HTTPException(404, "organization not found")
    if request.prompt_version_id is not None:
        prompt = session.scalar(
            select(AIPromptVersion).where(
                AIPromptVersion.id == request.prompt_version_id,
                AIPromptVersion.organization_id == organization.id,
            )
        )
        if prompt is None:
            raise HTTPException(404, "prompt version not found")
        request = request.model_copy(update={"instruction": prompt.instruction})
    try:
        source = get_source_reader(settings).read(request)
    except (RepositoryPathError, UnicodeDecodeError) as error:
        RUNS.labels("invalid", request.intent).inc()
        raise HTTPException(404, str(error)) from error

    try:
        reservation = reserve_budget(
            session, organization, request, source, settings, principal.subject
        )
    except AIBudgetExceeded as error:
        RUNS.labels("budget_exhausted", request.intent).inc()
        raise HTTPException(429, str(error)) from error

    started = time.perf_counter()
    try:
        result = provider.explain(
            source,
            request,
            tenant=principal.organization_slug,
            subject=principal.subject,
        )
    except AIProviderContractError as error:
        fail_budget(reservation)
        session.commit()
        ai_slo_tracker.record("failure", time.perf_counter() - started)
        RUNS.labels("invalid_response", request.intent).inc()
        logger.warning("repository_ai_contract_failed", path=source.file.path)
        raise HTTPException(502, "repository AI returned invalid structured output") from error
    except AIProviderUnavailable as error:
        fail_budget(reservation)
        session.commit()
        ai_slo_tracker.record("failure", time.perf_counter() - started)
        RUNS.labels("unavailable", request.intent).inc()
        logger.warning("repository_ai_unavailable", path=source.file.path)
        raise HTTPException(503, str(error)) from error
    duration = time.perf_counter() - started
    RUN_SECONDS.observe(duration)
    ai_slo_tracker.record("success", duration)
    RUNS.labels("success", request.intent).inc()
    TOKENS.labels("input", result.model).inc(result.input_tokens)
    TOKENS.labels("output", result.model).inc(result.output_tokens)
    if result.fallback_from is not None:
        FALLBACKS.labels(result.fallback_from, result.provider).inc()

    # Reattach trusted bytes after provider validation. This prevents a model from
    # silently altering source while the UI presents its explanation as faithful.
    by_line = {line.line_number: line for line in result.draft.lines}
    annotated = [
        AnnotatedSourceLine(
            **by_line[number].model_dump(),
            code=code,
        )
        for number, code in source.code_by_line.items()
    ]
    session.add(
        AuditEvent(
            organization_id=organization.id,
            actor=principal.subject,
            action="ai.repository.explained",
            target_type="repository_file",
            target_id=source.file.sha256[:32],
            details={
                "path": source.file.path,
                "intent": request.intent,
                "model": result.model,
                "fallback_from": str(result.fallback_from or "none"),
                "lines": str(len(annotated)),
                "prompt_version_id": str(request.prompt_version_id or "inline"),
            },
        )
    )
    settle_budget(reservation, result)
    session.commit()
    logger.info(
        "repository_ai_completed",
        path=source.file.path,
        intent=request.intent,
        model=result.model,
        lines=len(annotated),
    )
    return RepositoryExplanation(
        file=source.file,
        start_line=source.start_line,
        end_line=source.end_line,
        intent=request.intent,
        prompt_version_id=request.prompt_version_id,
        provider=result.provider,
        fallback_from=result.fallback_from,
        model=result.model,
        overview=result.draft.overview,
        architecture_relations=result.draft.architecture_relations,
        suggested_change=result.draft.suggested_change,
        lines=annotated,
        usage=ModelUsage(
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            estimated_cost_usd=result.estimated_cost_usd,
        ),
    )


@router.post("/explain/stream")
def stream_repository_file(
    request: RepositoryExplainRequest,
    session: Db,
    principal: Identity,
    settings: Configuration,
    provider: Provider,
) -> StreamingResponse:
    """Normalize hosted/local token streams and validate the completed document."""

    if "owner" not in principal.roles:
        raise HTTPException(403, "owner role required")
    organization = session.scalar(
        select(Organization).where(Organization.slug == principal.organization_slug)
    )
    if organization is None:
        raise HTTPException(404, "organization not found")
    if request.prompt_version_id is not None:
        prompt = session.scalar(
            select(AIPromptVersion).where(
                AIPromptVersion.id == request.prompt_version_id,
                AIPromptVersion.organization_id == organization.id,
            )
        )
        if prompt is None:
            raise HTTPException(404, "prompt version not found")
        request = request.model_copy(update={"instruction": prompt.instruction})
    try:
        source = get_source_reader(settings).read(request)
    except (RepositoryPathError, UnicodeDecodeError) as error:
        RUNS.labels("invalid", request.intent).inc()
        raise HTTPException(404, str(error)) from error

    try:
        reservation = reserve_budget(
            session, organization, request, source, settings, principal.subject
        )
    except AIBudgetExceeded as error:
        RUNS.labels("budget_exhausted", request.intent).inc()
        raise HTTPException(429, str(error)) from error

    def frame(event: str, payload: object) -> str:
        return f"event: {event}\ndata: {json.dumps(payload, separators=(',', ':'))}\n\n"

    def events() -> Iterator[str]:
        started = time.perf_counter()
        finished = False
        try:
            for item in provider.stream_explain(
                source,
                request,
                tenant=principal.organization_slug,
                subject=principal.subject,
            ):
                if item.delta is not None:
                    yield frame("delta", {"delta": item.delta})
                    continue
                if item.result is None:  # Defensive guard for non-ATLAS adapters.
                    raise AIProviderContractError("provider stream omitted its final result")
                result = item.result
                by_line = {line.line_number: line for line in result.draft.lines}
                annotated = [
                    AnnotatedSourceLine(**by_line[number].model_dump(), code=code)
                    for number, code in source.code_by_line.items()
                ]
                explanation = RepositoryExplanation(
                    file=source.file,
                    start_line=source.start_line,
                    end_line=source.end_line,
                    intent=request.intent,
                    prompt_version_id=request.prompt_version_id,
                    provider=result.provider,
                    fallback_from=result.fallback_from,
                    model=result.model,
                    overview=result.draft.overview,
                    architecture_relations=result.draft.architecture_relations,
                    suggested_change=result.draft.suggested_change,
                    lines=annotated,
                    usage=ModelUsage(
                        input_tokens=result.input_tokens,
                        output_tokens=result.output_tokens,
                        estimated_cost_usd=result.estimated_cost_usd,
                    ),
                )
                session.add(
                    AuditEvent(
                        organization_id=organization.id,
                        actor=principal.subject,
                        action="ai.repository.streamed",
                        target_type="repository_file",
                        target_id=source.file.sha256[:32],
                        details={
                            "path": source.file.path,
                            "intent": request.intent,
                            "provider": result.provider,
                            "model": result.model,
                            "fallback_from": str(result.fallback_from or "none"),
                            "lines": str(len(annotated)),
                            "prompt_version_id": str(request.prompt_version_id or "inline"),
                        },
                    )
                )
                settle_budget(reservation, result)
                session.commit()
                duration = time.perf_counter() - started
                RUN_SECONDS.observe(duration)
                ai_slo_tracker.record("success", duration)
                RUNS.labels("success", request.intent).inc()
                TOKENS.labels("input", result.model).inc(result.input_tokens)
                TOKENS.labels("output", result.model).inc(result.output_tokens)
                if result.fallback_from is not None:
                    FALLBACKS.labels(result.fallback_from, result.provider).inc()
                logger.info(
                    "repository_ai_stream_completed",
                    path=source.file.path,
                    provider=result.provider,
                    model=result.model,
                    lines=len(annotated),
                )
                finished = True
                yield frame("result", explanation.model_dump(mode="json"))
        except AIProviderContractError:
            fail_budget(reservation)
            session.commit()
            finished = True
            ai_slo_tracker.record("failure", time.perf_counter() - started)
            RUNS.labels("invalid_response", request.intent).inc()
            logger.warning("repository_ai_stream_contract_failed", path=source.file.path)
            yield frame("error", {"detail": "Repository AI returned invalid structured output."})
        except AIProviderUnavailable:
            fail_budget(reservation)
            session.commit()
            finished = True
            ai_slo_tracker.record("failure", time.perf_counter() - started)
            RUNS.labels("unavailable", request.intent).inc()
            logger.warning("repository_ai_stream_unavailable", path=source.file.path)
            yield frame("error", {"detail": "Repository AI provider is unavailable."})
        finally:
            # Client cancellation or an unexpected generator close must release
            # the conservative reservation rather than consuming monthly budget.
            if not finished:
                fail_budget(reservation)
                session.commit()

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
    )


def _patch_organization(session: Session, principal: Principal) -> Organization:
    if "owner" not in principal.roles:
        raise HTTPException(403, "owner role required")
    organization = session.scalar(
        select(Organization).where(Organization.slug == principal.organization_slug)
    )
    if organization is None:
        raise HTTPException(404, "organization not found")
    return organization


def _require_local_patch_mode(settings: Settings) -> None:
    # A future remote worker must not silently inherit this local-filesystem power.
    if not settings.ai_patch_tools_enabled or settings.environment != "development":
        raise HTTPException(503, "local repository patch tools are disabled")


def _require_local_test_mode(settings: Settings) -> None:
    _require_local_patch_mode(settings)
    if not settings.ai_test_tools_enabled:
        raise HTTPException(503, "isolated repository test tools are disabled")


@router.get("/mcp/catalog")
def repository_mcp_catalog(
    session: Db,
    principal: Identity,
    settings: Configuration,
    response: Response,
) -> MCPDiscoveryCatalog:
    # Discovery may run with mutation flags off, but is still local and owner-only.
    organization = _patch_organization(session, principal)
    if settings.environment != "development":
        raise HTTPException(503, "local MCP discovery is disabled")
    catalog = build_mcp_catalog(settings)
    response.headers["Cache-Control"] = "no-store"
    MCP_CATALOG_READS.inc()
    logger.info(
        "repository_mcp_catalog_read",
        organization_id=str(organization.id),
        tool_count=len(catalog.tools),
        catalog_version=catalog.catalog_version,
    )
    return catalog


@router.get("/patches")
def list_patch_proposals(session: Db, principal: Identity) -> list[PatchProposalRead]:
    organization = _patch_organization(session, principal)
    records = session.scalars(
        select(AIRepositoryPatchProposal)
        .where(AIRepositoryPatchProposal.organization_id == organization.id)
        .order_by(AIRepositoryPatchProposal.created_at.desc())
        .limit(50)
    ).all()
    return [PatchProposalRead.model_validate(record) for record in records]


@router.post("/patches", status_code=201)
def create_patch_proposal(
    data: PatchProposalCreate,
    session: Db,
    principal: Identity,
    settings: Configuration,
) -> PatchProposalRead:
    _require_local_patch_mode(settings)
    organization = _patch_organization(session, principal)
    count = session.scalar(
        select(func.count(AIRepositoryPatchProposal.id)).where(
            AIRepositoryPatchProposal.organization_id == organization.id
        )
    )
    if (count or 0) >= 100:
        raise HTTPException(409, "patch proposal quota reached")
    try:
        proposal = PatchGateway(settings).build(
            data, organization_id=organization.id, actor=principal.subject
        )
    except PatchConflictError as error:
        PATCH_ACTIONS.labels("propose", "conflict").inc()
        raise HTTPException(409, str(error)) from error
    except PatchPolicyError as error:
        PATCH_ACTIONS.labels("propose", "rejected").inc()
        raise HTTPException(422, str(error)) from error
    duplicate = session.scalar(
        select(AIRepositoryPatchProposal.id).where(
            AIRepositoryPatchProposal.organization_id == organization.id,
            AIRepositoryPatchProposal.proposal_digest == proposal.proposal_digest,
        )
    )
    if duplicate is not None:
        PATCH_ACTIONS.labels("propose", "duplicate").inc()
        raise HTTPException(409, "an identical patch proposal already exists")
    session.add(proposal)
    session.flush()
    session.add(
        AuditEvent(
            organization_id=organization.id,
            actor=principal.subject,
            action="ai.patch.proposed",
            target_type="ai_repository_patch",
            target_id=str(proposal.id),
            details={
                "path": proposal.path,
                "digest": proposal.proposal_digest,
                "original_sha256": proposal.original_sha256,
                "patched_sha256": proposal.patched_sha256,
            },
        )
    )
    session.commit()
    PATCH_ACTIONS.labels("propose", "success").inc()
    logger.info(
        "repository_patch_proposed",
        path=proposal.path,
        proposal_id=str(proposal.id),
        digest=proposal.proposal_digest[:16],
    )
    return PatchProposalRead.model_validate(proposal)


def _tenant_patch(
    session: Session, organization_id: UUID, proposal_id: UUID
) -> AIRepositoryPatchProposal:
    proposal = session.scalar(
        select(AIRepositoryPatchProposal)
        .where(
            AIRepositoryPatchProposal.id == proposal_id,
            AIRepositoryPatchProposal.organization_id == organization_id,
        )
        .with_for_update()
    )
    if proposal is None:
        raise HTTPException(404, "patch proposal not found")
    return proposal


def _transition_workflow_for_proposal(
    session: Session,
    proposal_id: UUID,
    condition: WorkflowCondition,
    *,
    detail: str,
) -> None:
    workflow = session.scalar(
        select(AIRepositoryPatchWorkflow)
        .where(AIRepositoryPatchWorkflow.proposal_id == proposal_id)
        .with_for_update()
    )
    if workflow is None:
        return
    PatchWorkflowMachine.advance(workflow, condition, detail=detail)
    WORKFLOW_ACTIONS.labels(workflow.status).inc()


def _record_workflow_test_evidence(
    session: Session,
    proposal_id: UUID,
    *,
    step: str,
    detail: str,
) -> None:
    workflow = session.scalar(
        select(AIRepositoryPatchWorkflow)
        .where(AIRepositoryPatchWorkflow.proposal_id == proposal_id)
        .with_for_update()
    )
    if workflow is None:
        return
    PatchWorkflowMachine.record_evidence(workflow, step=step, detail=detail)
    WORKFLOW_ACTIONS.labels("evidence").inc()


@router.post("/patches/{proposal_id}/approve")
def approve_and_apply_patch(
    proposal_id: UUID,
    data: PatchApproval,
    session: Db,
    principal: Identity,
    settings: Configuration,
) -> PatchProposalRead:
    _require_local_patch_mode(settings)
    organization = _patch_organization(session, principal)
    proposal = _tenant_patch(session, organization.id, proposal_id)
    if proposal.status != "pending":
        raise HTTPException(409, "patch proposal is not pending")
    if proposal.proposal_digest != data.proposal_digest:
        PATCH_ACTIONS.labels("apply", "digest_mismatch").inc()
        raise HTTPException(409, "approval digest does not match the reviewed proposal")
    active_test = session.scalar(
        select(AIRepositoryTestRun.id).where(
            AIRepositoryTestRun.proposal_id == proposal.id,
            AIRepositoryTestRun.status.in_(["queued", "running", "cancel_requested"]),
        )
    )
    if active_test is not None:
        raise HTTPException(409, "an approved test run is still active for this proposal")

    # Commit approval evidence before crossing the non-transactional filesystem
    # boundary. A crash leaves an observable `applying` journal state rather than
    # falsely claiming either that nothing happened or that application completed.
    proposal.status = "applying"
    proposal.approved_by = principal.subject
    proposal.approved_at = datetime.now(UTC)
    session.add(
        AuditEvent(
            organization_id=organization.id,
            actor=principal.subject,
            action="ai.patch.approved",
            target_type="ai_repository_patch",
            target_id=str(proposal.id),
            details={"path": proposal.path, "digest": proposal.proposal_digest},
        )
    )
    session.commit()
    try:
        PatchGateway(settings).apply(proposal)
    except PatchConflictError as error:
        proposal.status = "conflicted"
        proposal.failure_reason = "source_hash_changed"
        _transition_workflow_for_proposal(
            session,
            proposal.id,
            "patch_source_conflict",
            detail="Source hash changed after proposal creation.",
        )
        session.commit()
        PATCH_ACTIONS.labels("apply", "conflict").inc()
        raise HTTPException(409, str(error)) from error
    except (PatchPolicyError, OSError) as error:
        proposal.status = "failed"
        proposal.failure_reason = "guarded_write_failed"
        _transition_workflow_for_proposal(
            session, proposal.id, "patch_failed", detail="Guarded filesystem application failed."
        )
        session.commit()
        PATCH_ACTIONS.labels("apply", "failed").inc()
        logger.exception("repository_patch_apply_failed", proposal_id=str(proposal.id))
        raise HTTPException(500, "guarded patch application failed") from error

    proposal.status = "applied"
    proposal.applied_at = datetime.now(UTC)
    _transition_workflow_for_proposal(
        session,
        proposal.id,
        "patch_approved",
        detail="Human-approved exact patch was applied and verified.",
    )
    session.add(
        AuditEvent(
            organization_id=organization.id,
            actor=principal.subject,
            action="ai.patch.applied",
            target_type="ai_repository_patch",
            target_id=str(proposal.id),
            details={"path": proposal.path, "patched_sha256": proposal.patched_sha256},
        )
    )
    session.commit()
    PATCH_ACTIONS.labels("apply", "success").inc()
    return PatchProposalRead.model_validate(proposal)


@router.post("/patches/{proposal_id}/rollback")
def rollback_patch(
    proposal_id: UUID,
    data: PatchRollback,
    session: Db,
    principal: Identity,
    settings: Configuration,
) -> PatchProposalRead:
    _require_local_patch_mode(settings)
    organization = _patch_organization(session, principal)
    proposal = _tenant_patch(session, organization.id, proposal_id)
    if proposal.status != "applied":
        raise HTTPException(409, "only an applied patch can be rolled back")
    if proposal.proposal_digest != data.proposal_digest:
        PATCH_ACTIONS.labels("rollback", "digest_mismatch").inc()
        raise HTTPException(409, "rollback digest does not match the applied proposal")
    proposal.status = "rolling_back"
    session.commit()
    try:
        PatchGateway(settings).rollback(proposal)
    except PatchConflictError as error:
        proposal.status = "rollback_conflict"
        proposal.failure_reason = "patched_hash_changed"
        _transition_workflow_for_proposal(
            session,
            proposal.id,
            "rollback_conflict",
            detail="Applied file changed before rollback.",
        )
        session.commit()
        PATCH_ACTIONS.labels("rollback", "conflict").inc()
        raise HTTPException(409, str(error)) from error
    except (PatchPolicyError, OSError) as error:
        proposal.status = "rollback_failed"
        proposal.failure_reason = "guarded_rollback_failed"
        _transition_workflow_for_proposal(
            session, proposal.id, "rollback_failed", detail="Guarded filesystem rollback failed."
        )
        session.commit()
        PATCH_ACTIONS.labels("rollback", "failed").inc()
        logger.exception("repository_patch_rollback_failed", proposal_id=str(proposal.id))
        raise HTTPException(500, "guarded patch rollback failed") from error
    proposal.status = "rolled_back"
    proposal.rolled_back_at = datetime.now(UTC)
    _transition_workflow_for_proposal(
        session,
        proposal.id,
        "rollback_approved",
        detail="Original bytes were restored and verified.",
    )
    session.add(
        AuditEvent(
            organization_id=organization.id,
            actor=principal.subject,
            action="ai.patch.rolled_back",
            target_type="ai_repository_patch",
            target_id=str(proposal.id),
            details={"path": proposal.path, "restored_sha256": proposal.original_sha256},
        )
    )
    session.commit()
    PATCH_ACTIONS.labels("rollback", "success").inc()
    return PatchProposalRead.model_validate(proposal)


@router.get("/workflows")
def list_patch_workflows(session: Db, principal: Identity) -> list[PatchWorkflowRead]:
    organization = _patch_organization(session, principal)
    workflows = session.scalars(
        select(AIRepositoryPatchWorkflow)
        .where(AIRepositoryPatchWorkflow.organization_id == organization.id)
        .order_by(AIRepositoryPatchWorkflow.created_at.desc())
        .limit(50)
    ).all()
    result: list[PatchWorkflowRead] = []
    for workflow in workflows:
        proposal = (
            session.get(AIRepositoryPatchProposal, workflow.proposal_id)
            if workflow.proposal_id is not None
            else None
        )
        result.append(
            workflow_read(
                workflow,
                PatchProposalRead.model_validate(proposal) if proposal is not None else None,
            )
        )
    return result


@router.get("/workflows/{workflow_id}/replay")
def replay_patch_workflow(
    workflow_id: UUID, session: Db, principal: Identity
) -> WorkflowReplayRead:
    """Verify and project one tenant's persisted history without executing tools."""

    organization = _patch_organization(session, principal)
    workflow = session.scalar(
        select(AIRepositoryPatchWorkflow).where(
            AIRepositoryPatchWorkflow.id == workflow_id,
            AIRepositoryPatchWorkflow.organization_id == organization.id,
        )
    )
    if workflow is None:
        raise HTTPException(404, "patch workflow not found")
    try:
        replay = PatchWorkflowMachine.replay(workflow)
    except (WorkflowTransitionError, ValidationError) as error:
        WORKFLOW_ACTIONS.labels("replay_invalid").inc()
        logger.warning("repository_workflow_replay_invalid", workflow_id=str(workflow_id))
        raise HTTPException(409, "workflow history failed policy validation") from error
    WORKFLOW_ACTIONS.labels("replayed").inc()
    return replay


@router.post("/workflows", status_code=201)
def create_patch_workflow(
    data: PatchWorkflowCreate,
    session: Db,
    principal: Identity,
    settings: Configuration,
) -> PatchWorkflowRead:
    _require_local_patch_mode(settings)
    organization = _patch_organization(session, principal)
    count = session.scalar(
        select(func.count(AIRepositoryPatchWorkflow.id)).where(
            AIRepositoryPatchWorkflow.organization_id == organization.id
        )
    )
    if (count or 0) >= 100:
        raise HTTPException(409, "patch workflow quota reached")

    workflow = PatchWorkflowMachine.create(
        data, organization_id=organization.id, actor=principal.subject
    )
    session.add(workflow)
    session.flush()
    session.add(
        AuditEvent(
            organization_id=organization.id,
            actor=principal.subject,
            action="ai.patch_workflow.submitted",
            target_type="ai_repository_patch_workflow",
            target_id=str(workflow.id),
            details={"path": data.plan.path},
        )
    )
    session.commit()
    PatchWorkflowMachine.advance(
        workflow,
        "plan_accepted",
        detail="Validating path, source hash, bounds, result syntax, and diff limits.",
    )
    session.commit()
    WORKFLOW_ACTIONS.labels("validating").inc()

    try:
        proposal = PatchGateway(settings).build(
            data.plan,
            organization_id=organization.id,
            actor=principal.subject,
        )
    except PatchConflictError:
        PatchWorkflowMachine.advance(
            workflow,
            "source_conflict",
            detail="Source hash did not match the submitted plan.",
        )
        workflow.failure_reason = "source_hash_changed"
        session.commit()
        WORKFLOW_ACTIONS.labels("conflicted").inc()
        return workflow_read(workflow)
    except PatchPolicyError:
        PatchWorkflowMachine.advance(
            workflow,
            "policy_rejected",
            detail="The submitted plan violated the guarded patch policy.",
        )
        workflow.failure_reason = "patch_policy_rejected"
        session.commit()
        WORKFLOW_ACTIONS.labels("failed").inc()
        return workflow_read(workflow)

    duplicate = session.scalar(
        select(AIRepositoryPatchProposal.id).where(
            AIRepositoryPatchProposal.organization_id == organization.id,
            AIRepositoryPatchProposal.proposal_digest == proposal.proposal_digest,
        )
    )
    if duplicate is not None:
        PatchWorkflowMachine.advance(
            workflow,
            "duplicate_proposal",
            detail="An identical immutable patch proposal already exists.",
        )
        workflow.failure_reason = "duplicate_proposal"
        session.commit()
        WORKFLOW_ACTIONS.labels("failed").inc()
        return workflow_read(workflow)

    session.add(proposal)
    session.flush()
    workflow.proposal_id = proposal.id
    PatchWorkflowMachine.advance(
        workflow,
        "proposal_ready",
        detail="Server-derived exact diff is waiting for explicit human approval.",
    )
    session.add(
        AuditEvent(
            organization_id=organization.id,
            actor=principal.subject,
            action="ai.patch_workflow.awaiting_approval",
            target_type="ai_repository_patch_workflow",
            target_id=str(workflow.id),
            details={
                "proposal_id": str(proposal.id),
                "digest": proposal.proposal_digest,
                "path": proposal.path,
            },
        )
    )
    session.commit()
    WORKFLOW_ACTIONS.labels("awaiting_approval").inc()
    return workflow_read(workflow, PatchProposalRead.model_validate(proposal))


@router.get("/test-profiles")
def list_test_profiles(_: Identity) -> list[TestProfileRead]:
    """Expose reviewed policy metadata, never a caller-defined command surface."""

    return [profile_read(profile) for profile in TEST_PROFILES.values()]


@router.get("/test-runs")
def list_test_runs(session: Db, principal: Identity) -> list[TestRunRead]:
    organization = _patch_organization(session, principal)
    runs = session.scalars(
        select(AIRepositoryTestRun)
        .where(AIRepositoryTestRun.organization_id == organization.id)
        .order_by(AIRepositoryTestRun.created_at.desc())
        .limit(50)
    ).all()
    return [test_run_read(run) for run in runs]


def _tenant_test_run(session: Session, organization_id: UUID, run_id: UUID) -> AIRepositoryTestRun:
    run = session.scalar(
        select(AIRepositoryTestRun)
        .where(
            AIRepositoryTestRun.id == run_id,
            AIRepositoryTestRun.organization_id == organization_id,
        )
        .with_for_update()
    )
    if run is None:
        raise HTTPException(404, "test run not found")
    return run


@router.post("/patches/{proposal_id}/test-runs", status_code=201)
def request_test_run(
    proposal_id: UUID,
    data: TestRunRequest,
    session: Db,
    principal: Identity,
    settings: Configuration,
) -> TestRunRead:
    _require_local_test_mode(settings)
    organization = _patch_organization(session, principal)
    proposal = _tenant_patch(session, organization.id, proposal_id)
    count = session.scalar(
        select(func.count(AIRepositoryTestRun.id)).where(
            AIRepositoryTestRun.organization_id == organization.id
        )
    )
    if (count or 0) >= 100:
        raise HTTPException(409, "test run quota reached")
    try:
        profile = get_test_profile(data.profile_id)
        run = create_test_run(
            proposal,
            profile,
            organization_id=organization.id,
            actor=principal.subject,
        )
    except TestRunTransitionError as error:
        TEST_RUN_ACTIONS.labels("request", "rejected").inc()
        raise HTTPException(409, str(error)) from error
    session.add(run)
    session.flush()
    _record_workflow_test_evidence(
        session,
        proposal.id,
        step="test_requested",
        detail=f"Test profile {profile.id} attempt {run.attempt} awaits separate approval.",
    )
    session.add(
        AuditEvent(
            organization_id=organization.id,
            actor=principal.subject,
            action="ai.test_run.requested",
            target_type="ai_repository_test_run",
            target_id=str(run.id),
            details={
                "proposal_id": str(proposal.id),
                "profile_id": profile.id,
                "profile_version": profile.version,
                "run_digest": run.run_digest,
            },
        )
    )
    session.commit()
    TEST_RUN_ACTIONS.labels("request", "success").inc()
    return test_run_read(run)


@router.post("/test-runs/{run_id}/approve")
def approve_repository_test_run(
    run_id: UUID,
    data: TestRunApproval,
    session: Db,
    principal: Identity,
    settings: Configuration,
) -> TestRunRead:
    _require_local_test_mode(settings)
    organization = _patch_organization(session, principal)
    run = _tenant_test_run(session, organization.id, run_id)
    proposal = _tenant_patch(session, organization.id, run.proposal_id)
    try:
        profile = get_test_profile(run.profile_id)
        verify_test_run_policy(run, proposal, profile)
        if proposal.status != "pending":
            raise TestRunTransitionError("patch proposal is no longer pending")
        approve_test_run(run, data, actor=principal.subject)
    except TestRunTransitionError as error:
        TEST_RUN_ACTIONS.labels("approve", "rejected").inc()
        raise HTTPException(409, str(error)) from error
    _record_workflow_test_evidence(
        session,
        proposal.id,
        step="test_queued",
        detail=f"Approved test attempt {run.attempt} entered the isolated worker queue.",
    )
    session.add(
        AuditEvent(
            organization_id=organization.id,
            actor=principal.subject,
            action="ai.test_run.approved",
            target_type="ai_repository_test_run",
            target_id=str(run.id),
            details={
                "proposal_id": str(run.proposal_id),
                "profile_id": run.profile_id,
                "run_digest": run.run_digest,
            },
        )
    )
    session.commit()
    TEST_RUN_ACTIONS.labels("approve", "queued").inc()
    return test_run_read(run)


@router.post("/test-runs/{run_id}/cancel")
def cancel_repository_test_run(
    run_id: UUID,
    session: Db,
    principal: Identity,
    settings: Configuration,
) -> TestRunRead:
    _require_local_test_mode(settings)
    organization = _patch_organization(session, principal)
    run = _tenant_test_run(session, organization.id, run_id)
    try:
        cancel_test_run(run)
    except TestRunTransitionError as error:
        TEST_RUN_ACTIONS.labels("cancel", "rejected").inc()
        raise HTTPException(409, str(error)) from error
    _record_workflow_test_evidence(
        session,
        run.proposal_id,
        step="test_cancelled" if run.status == "cancelled" else "test_cancel_requested",
        detail=f"Operator cancellation recorded for test attempt {run.attempt}.",
    )
    session.add(
        AuditEvent(
            organization_id=organization.id,
            actor=principal.subject,
            action="ai.test_run.cancel_requested",
            target_type="ai_repository_test_run",
            target_id=str(run.id),
            details={"status": run.status, "profile_id": run.profile_id},
        )
    )
    session.commit()
    outcome = "cancelled" if run.status == "cancelled" else "requested"
    TEST_RUN_ACTIONS.labels("cancel", outcome).inc()
    return test_run_read(run)


@router.post("/test-runs/{run_id}/retry", status_code=201)
def retry_repository_test_run(
    run_id: UUID,
    session: Db,
    principal: Identity,
    settings: Configuration,
) -> TestRunRead:
    """Create fresh pending evidence; never requeue an interrupted approval."""

    _require_local_test_mode(settings)
    organization = _patch_organization(session, principal)
    interrupted = _tenant_test_run(session, organization.id, run_id)
    proposal = _tenant_patch(session, organization.id, interrupted.proposal_id)
    count = session.scalar(
        select(func.count(AIRepositoryTestRun.id)).where(
            AIRepositoryTestRun.organization_id == organization.id
        )
    )
    if (count or 0) >= 100:
        raise HTTPException(409, "test run quota reached")
    try:
        profile = get_test_profile(interrupted.profile_id)
        retry = create_test_run(
            proposal,
            profile,
            organization_id=organization.id,
            actor=principal.subject,
            retry_of=interrupted,
        )
    except TestRunTransitionError as error:
        TEST_RUN_ACTIONS.labels("retry", "rejected").inc()
        raise HTTPException(409, str(error)) from error
    session.add(retry)
    session.flush()
    _record_workflow_test_evidence(
        session,
        proposal.id,
        step="test_retry_requested",
        detail=f"Fresh test attempt {retry.attempt} awaits a new execution approval.",
    )
    session.add(
        AuditEvent(
            organization_id=organization.id,
            actor=principal.subject,
            action="ai.test_run.retry_requested",
            target_type="ai_repository_test_run",
            target_id=str(retry.id),
            details={
                "retry_of_id": str(interrupted.id),
                "proposal_id": str(proposal.id),
                "profile_id": retry.profile_id,
                "attempt": retry.attempt,
                "run_digest": retry.run_digest,
            },
        )
    )
    session.commit()
    TEST_RUN_ACTIONS.labels("retry", "pending_approval").inc()
    return test_run_read(retry)
