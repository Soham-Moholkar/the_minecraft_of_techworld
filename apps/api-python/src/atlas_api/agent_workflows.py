"""Deterministic Phase 9 workflow state machine.

The workflow does not grant a model tools. It accepts a typed change plan, records
each deterministic validation transition, and delegates proposal construction to
the guarded PatchGateway. Human approval remains a separate HTTP mutation.
"""

from datetime import UTC, datetime
from typing import Literal, get_args
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from atlas_api.agent_patches import PatchProposalCreate, PatchProposalRead
from atlas_api.models import AIRepositoryPatchWorkflow

WorkflowStatus = Literal[
    "submitted",
    "validating",
    "awaiting_approval",
    "applied",
    "rolled_back",
    "conflicted",
    "failed",
]

WorkflowCondition = Literal[
    "plan_accepted",
    "proposal_ready",
    "source_conflict",
    "policy_rejected",
    "duplicate_proposal",
    "patch_approved",
    "patch_source_conflict",
    "patch_failed",
    "rollback_approved",
    "rollback_conflict",
    "rollback_failed",
]
WorkflowAuthority = Literal["none", "patch_approval", "rollback_approval"]


class WorkflowNode(BaseModel):
    """A fixed policy node; only the validation node invokes the guarded gateway."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    state: WorkflowStatus
    title: str
    kind: Literal["automatic", "tool", "human_gate", "terminal"]
    tool: Literal["guarded_patch_proposal"] | None = None


class WorkflowEdge(BaseModel):
    """An observed branch with its independent authority requirement."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source: WorkflowStatus
    target: WorkflowStatus
    step: str
    condition: WorkflowCondition
    authority: WorkflowAuthority = "none"


class WorkflowGraph(BaseModel):
    """Schema-checked source policy that replay and live routing both use."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    version: Literal[1] = 1
    nodes: tuple[WorkflowNode, ...]
    edges: tuple[WorkflowEdge, ...]

    @model_validator(mode="after")
    def validate_policy(self) -> "WorkflowGraph":
        states = {node.state for node in self.nodes}
        if len(states) != len(self.nodes) or states != set(get_args(WorkflowStatus)):
            raise ValueError("workflow graph must define every state exactly once")
        if any((node.kind == "tool") != (node.tool is not None) for node in self.nodes):
            raise ValueError("workflow tool nodes require a fixed tool id")
        # Each observed condition must select exactly one edge from a state.
        # This is checked at import time, before any request can use the policy.
        branches = [(edge.source, edge.condition) for edge in self.edges]
        if len(branches) != len(set(branches)):
            raise ValueError("workflow graph contains ambiguous conditional branches")
        for edge in self.edges:
            if edge.source not in states or edge.target not in states:
                raise ValueError("workflow edge refers to an unknown state")
            if edge.authority == "patch_approval" and edge.source != "awaiting_approval":
                raise ValueError("patch authority must originate at human review")
            if edge.authority == "rollback_approval" and edge.source != "applied":
                raise ValueError("rollback authority must originate at applied")
            if edge.source == "awaiting_approval" and edge.authority != "patch_approval":
                raise ValueError("leaving human review requires patch approval")
            if edge.source == "applied" and edge.authority != "rollback_approval":
                raise ValueError("leaving applied requires rollback approval")
        return self


# This policy is source-owned and versioned. A stored event names one exact edge;
# neither model output nor an HTTP caller may supply a graph, condition, or tool.
WORKFLOW_GRAPH = WorkflowGraph(
    nodes=(
        WorkflowNode(state="submitted", title="Plan received", kind="automatic"),
        WorkflowNode(
            state="validating",
            title="Guarded validation",
            kind="tool",
            tool="guarded_patch_proposal",
        ),
        WorkflowNode(state="awaiting_approval", title="Human review", kind="human_gate"),
        WorkflowNode(state="applied", title="Patch applied", kind="automatic"),
        WorkflowNode(state="rolled_back", title="Patch rolled back", kind="terminal"),
        WorkflowNode(state="conflicted", title="Source conflict", kind="terminal"),
        WorkflowNode(state="failed", title="Workflow failed", kind="terminal"),
    ),
    edges=(
        WorkflowEdge(
            source="submitted",
            target="validating",
            step="policy_validation",
            condition="plan_accepted",
        ),
        WorkflowEdge(
            source="validating",
            target="awaiting_approval",
            step="human_review",
            condition="proposal_ready",
        ),
        WorkflowEdge(
            source="validating",
            target="conflicted",
            step="source_conflict",
            condition="source_conflict",
        ),
        WorkflowEdge(
            source="validating",
            target="failed",
            step="policy_rejected",
            condition="policy_rejected",
        ),
        WorkflowEdge(
            source="validating",
            target="failed",
            step="duplicate_proposal",
            condition="duplicate_proposal",
        ),
        WorkflowEdge(
            source="awaiting_approval",
            target="applied",
            step="patch_applied",
            condition="patch_approved",
            authority="patch_approval",
        ),
        WorkflowEdge(
            source="awaiting_approval",
            target="conflicted",
            step="source_conflict",
            condition="patch_source_conflict",
            authority="patch_approval",
        ),
        WorkflowEdge(
            source="awaiting_approval",
            target="failed",
            step="application_failed",
            condition="patch_failed",
            authority="patch_approval",
        ),
        WorkflowEdge(
            source="applied",
            target="rolled_back",
            step="patch_rolled_back",
            condition="rollback_approved",
            authority="rollback_approval",
        ),
        WorkflowEdge(
            source="applied",
            target="conflicted",
            step="rollback_conflict",
            condition="rollback_conflict",
            authority="rollback_approval",
        ),
        WorkflowEdge(
            source="applied",
            target="failed",
            step="rollback_failed",
            condition="rollback_failed",
            authority="rollback_approval",
        ),
    ),
)

_EVIDENCE_STEPS = frozenset(
    {
        "test_requested",
        "test_queued",
        "test_cancel_requested",
        "test_cancelled",
        "test_retry_requested",
        "test_running",
        "test_passed",
        "test_failed",
        "test_timed_out",
        "test_output_limit",
        "test_worker_failed",
        "test_interrupted",
    }
)


class WorkflowTransitionError(RuntimeError):
    """Raised when code attempts a transition outside the reviewed graph."""


class PatchWorkflowCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    objective: str = Field(min_length=10, max_length=500)
    plan: PatchProposalCreate


class PatchWorkflowEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: WorkflowStatus
    step: str = Field(min_length=1, max_length=40)
    at: datetime
    detail: str = Field(min_length=1, max_length=120)


class PatchWorkflowRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    objective: str
    graph_version: int
    status: WorkflowStatus
    current_step: str
    events: list[PatchWorkflowEvent]
    failure_reason: str | None
    created_by: str
    created_at: datetime
    updated_at: datetime
    proposal: PatchProposalRead | None = None


class WorkflowReplayFrame(BaseModel):
    """One verified point in the persisted event stream."""

    model_config = ConfigDict(extra="forbid")

    sequence: int = Field(ge=0)
    kind: Literal["transition", "evidence"]
    event: PatchWorkflowEvent
    condition: WorkflowCondition | None
    authority: WorkflowAuthority


class WorkflowReplayRead(BaseModel):
    """Read-only projection; constructing it has no execution side effects."""

    model_config = ConfigDict(extra="forbid")

    workflow_id: UUID
    graph: WorkflowGraph
    final_state: WorkflowStatus
    frames: list[WorkflowReplayFrame]


def _edge_for(source: str, target: str, step: str) -> WorkflowEdge:
    """Require the persisted transition to match one unambiguous policy edge."""

    matching = [
        edge
        for edge in WORKFLOW_GRAPH.edges
        if edge.source == source and edge.target == target and edge.step == step
    ]
    if len(matching) != 1:
        raise WorkflowTransitionError(f"unrecognized workflow edge {source} -> {target} ({step})")
    return matching[0]


class PatchWorkflowMachine:
    """Apply only explicit transitions and retain an append-only event history."""

    @staticmethod
    def create(
        data: PatchWorkflowCreate, *, organization_id: UUID, actor: str
    ) -> AIRepositoryPatchWorkflow:
        now = datetime.now(UTC)
        return AIRepositoryPatchWorkflow(
            organization_id=organization_id,
            objective=data.objective,
            plan=data.plan.model_dump(mode="json"),
            graph_version=WORKFLOW_GRAPH.version,
            status="submitted",
            current_step="plan_received",
            events=[
                PatchWorkflowEvent(
                    state="submitted",
                    step="plan_received",
                    at=now,
                    detail="Typed change plan accepted for deterministic validation.",
                ).model_dump(mode="json")
            ],
            created_by=actor,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def transition(
        workflow: AIRepositoryPatchWorkflow,
        status: WorkflowStatus,
        *,
        step: str,
        detail: str,
    ) -> None:
        # The step identifies a specific conditional edge. A generic status
        # change is insufficient: it could hide a skipped approval or a new
        # branch that was never reviewed as part of the source-owned policy.
        if workflow.graph_version != WORKFLOW_GRAPH.version:
            raise WorkflowTransitionError("workflow graph version is unavailable")
        _edge_for(workflow.status, status, step)
        now = datetime.now(UTC)
        event = PatchWorkflowEvent(state=status, step=step, at=now, detail=detail)
        # Assign a fresh list so SQLAlchemy observes the JSON mutation without a
        # mutable extension and the prior history remains append-only by contract.
        workflow.events = [*workflow.events, event.model_dump(mode="json")]
        workflow.status = status
        workflow.current_step = step
        workflow.updated_at = now

    @staticmethod
    def advance(
        workflow: AIRepositoryPatchWorkflow,
        condition: WorkflowCondition,
        *,
        detail: str,
    ) -> None:
        """Route one observed outcome through the fixed graph.

        Only trusted service code supplies the condition after checking the
        filesystem or an exact approval. No request field can choose an edge.
        """

        matching = [
            edge
            for edge in WORKFLOW_GRAPH.edges
            if edge.source == workflow.status and edge.condition == condition
        ]
        if len(matching) != 1:
            raise WorkflowTransitionError(
                f"no unique workflow branch for {workflow.status}: {condition}"
            )
        edge = matching[0]
        PatchWorkflowMachine.transition(workflow, edge.target, step=edge.step, detail=detail)

    @staticmethod
    def record_evidence(
        workflow: AIRepositoryPatchWorkflow,
        *,
        step: str,
        detail: str,
    ) -> None:
        """Append evidence without granting a state transition or new authority."""

        # Tool evidence has its own fixed vocabulary. The worker may report a
        # result, but a result never becomes a patch or rollback approval.
        if workflow.graph_version != WORKFLOW_GRAPH.version:
            raise WorkflowTransitionError("workflow graph version is unavailable")
        if step not in _EVIDENCE_STEPS:
            raise WorkflowTransitionError(f"unrecognized workflow evidence {step}")
        now = datetime.now(UTC)
        event = PatchWorkflowEvent(
            state=workflow.status,  # type: ignore[arg-type]
            step=step,
            at=now,
            detail=detail,
        )
        workflow.events = [*workflow.events, event.model_dump(mode="json")]
        workflow.updated_at = now

    @staticmethod
    def replay(workflow: AIRepositoryPatchWorkflow) -> WorkflowReplayRead:
        """Verify every stored edge and return an immutable point-in-time projection.

        The JSON event list is only ever appended by the application. Replay
        never invokes a tool or changes the row; malformed or reordered history
        fails closed rather than presenting a plausible but false timeline.
        """

        # Version pinning keeps old histories interpretable after a future
        # policy revision. A revision must retain its own graph definition.
        if workflow.graph_version != WORKFLOW_GRAPH.version:
            raise WorkflowTransitionError("workflow graph version is unavailable")
        events = [PatchWorkflowEvent.model_validate(item) for item in workflow.events]
        if not events or events[0].state != "submitted" or events[0].step != "plan_received":
            raise WorkflowTransitionError("workflow history has no valid initial event")
        frames = [
            WorkflowReplayFrame(
                sequence=0,
                kind="transition",
                event=events[0],
                condition=None,
                authority="none",
            )
        ]
        current: WorkflowStatus = "submitted"
        last_transition_step = "plan_received"
        previous_at = events[0].at
        for sequence, event in enumerate(events[1:], start=1):
            # Event order is part of the evidence. Clock ties are allowed for
            # rapid local transitions, but time must never move backwards.
            if event.at < previous_at:
                raise WorkflowTransitionError("workflow history is out of order")
            previous_at = event.at
            if event.state == current:
                if event.step not in _EVIDENCE_STEPS:
                    raise WorkflowTransitionError("workflow history contains unknown evidence")
                frames.append(
                    WorkflowReplayFrame(
                        sequence=sequence,
                        kind="evidence",
                        event=event,
                        condition=None,
                        authority="none",
                    )
                )
                continue
            edge = _edge_for(current, event.state, event.step)
            frames.append(
                WorkflowReplayFrame(
                    sequence=sequence,
                    kind="transition",
                    event=event,
                    condition=edge.condition,
                    authority=edge.authority,
                )
            )
            current = event.state
            last_transition_step = event.step
        if current != workflow.status or last_transition_step != workflow.current_step:
            raise WorkflowTransitionError("workflow history disagrees with its stored state")
        return WorkflowReplayRead(
            workflow_id=workflow.id,
            graph=WORKFLOW_GRAPH,
            final_state=current,
            frames=frames,
        )


def workflow_read(
    workflow: AIRepositoryPatchWorkflow, proposal: PatchProposalRead | None = None
) -> PatchWorkflowRead:
    return PatchWorkflowRead(
        id=workflow.id,
        objective=workflow.objective,
        graph_version=workflow.graph_version,
        status=workflow.status,  # type: ignore[arg-type]
        current_step=workflow.current_step,
        events=[PatchWorkflowEvent.model_validate(event) for event in workflow.events],
        failure_reason=workflow.failure_reason,
        created_by=workflow.created_by,
        created_at=workflow.created_at,
        updated_at=workflow.updated_at,
        proposal=proposal,
    )
