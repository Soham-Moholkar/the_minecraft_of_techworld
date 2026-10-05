"""Source-owned MCP-shaped discovery only; deliberately no dispatcher or transport.

JSON Schema describes input shape, not authorization. Existing REST handlers remain
the enforcement boundary for tenant ownership, digests, state and filesystem policy.
"""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, JsonValue

from atlas_api.agent_patches import PatchApproval, PatchProposalCreate, PatchRollback
from atlas_api.agent_tests import TestRunApproval, TestRunRequest
from atlas_api.agent_workflows import PatchWorkflowCreate
from atlas_api.config import Settings


class ApplyInput(PatchApproval):
    proposal_id: UUID


class RollbackInput(PatchRollback):
    proposal_id: UUID


class RequestTestInput(TestRunRequest):
    proposal_id: UUID


class RunID(BaseModel):
    model_config = ConfigDict(extra="forbid")
    run_id: UUID


class ApproveTestInput(TestRunApproval):
    run_id: UUID


class ReplayInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    workflow_id: UUID


class ToolPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    scope: Literal["organization-owned repository"] = "organization-owned repository"
    required_role: Literal["owner"] = "owner"
    approval: str
    boundary: str
    rest_method: Literal["GET", "POST"]
    rest_path: str
    source: str
    required_flags: list[str]
    local_flags_enabled: bool


class ToolContract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    name: str
    title: str
    description: str
    inputSchema: dict[str, JsonValue]
    # ATLAS policy is intentionally outside MCP annotations: hints never grant power.
    policy: ToolPolicy


class MCPDiscoveryCatalog(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    catalog_version: Literal[1] = 1
    specification_revision: Literal["2026-07-28"] = "2026-07-28"
    mode: Literal["catalog-only"] = "catalog-only"
    invocation_enabled: Literal[False] = False
    tools: list[ToolContract]


def build_mcp_catalog(settings: Settings) -> MCPDiscoveryCatalog:
    """Project existing validation models without reading files or executing tools.

    Path parameters are added to inherited body models so the discovery schema shows
    the whole REST operation. Cross-field/state checks still live in the actual gateway.
    Flag eligibility is not worker health, approval, or permission to invoke from here.
    """
    patch_enabled = settings.environment == "development" and settings.ai_patch_tools_enabled
    test_enabled = patch_enabled and settings.ai_test_tools_enabled
    patch_flags = ["ATLAS_AI_PATCH_TOOLS_ENABLED"]
    test_flags = [*patch_flags, "ATLAS_AI_TEST_TOOLS_ENABLED"]
    prefix = "/v1/ai/repository"

    def contract(
        name: str,
        title: str,
        description: str,
        model: type[BaseModel],
        path: str,
        approval: str,
        boundary: str,
        source: str,
        *,
        test: bool = False,
        readonly: bool = False,
    ) -> ToolContract:
        schema = model.model_json_schema()
        schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        return ToolContract(
            name=name,
            title=title,
            description=description,
            inputSchema=schema,
            policy=ToolPolicy(
                approval=approval,
                boundary=boundary,
                rest_method="GET" if readonly else "POST",
                rest_path=prefix + path,
                source=f"apps/api-python/src/atlas_api/{source}.py",
                required_flags=[] if readonly else test_flags if test else patch_flags,
                local_flags_enabled=True if readonly else test_enabled if test else patch_enabled,
            ),
        )

    contracts = [
        contract(
            "repository.patch.propose",
            "Propose exact patch",
            "Validate a bounded existing-file edit and persist review evidence.",
            PatchProposalCreate,
            "/patches",
            "No write approval; application requires separate exact-digest approval.",
            "Allowlisted relative paths, bounded line ranges and source hash; no file write.",
            "agent_patches",
        ),
        contract(
            "repository.patch.apply",
            "Apply reviewed patch",
            "Apply only the pending, digest-bound proposal through the guarded gateway.",
            ApplyInput,
            "/patches/{proposal_id}/approve",
            "Exact proposal digest and APPLY EXACT PATCH.",
            "Local atomic allowlisted write; current source hash "
            "and tenant ownership checked again.",
            "agent_patches",
        ),
        contract(
            "repository.patch.rollback",
            "Roll back reviewed patch",
            "Restore captured bytes only while the current hash matches the applied patch.",
            RollbackInput,
            "/patches/{proposal_id}/rollback",
            "Separate exact digest and ROLL BACK EXACT PATCH.",
            "Hash-safe restoration; never overwrite later edits.",
            "agent_patches",
        ),
        contract(
            "repository.test.request",
            "Request candidate test",
            "Create a pending request for a fixed source-owned test profile.",
            RequestTestInput,
            "/patches/{proposal_id}/test-runs",
            "Separate test approval required before queueing.",
            "No commands accepted; only registered profiles and pending candidate patches.",
            "agent_tests",
            test=True,
        ),
        contract(
            "repository.test.approve",
            "Approve isolated test",
            "Queue the exact approved candidate/profile digest for the isolated worker.",
            ApproveTestInput,
            "/test-runs/{run_id}/approve",
            "Exact run digest and RUN ISOLATED TEST PROFILE.",
            "Non-root, networkless, read-only, resource-bounded Docker; absence fails closed. "
            "Never applies patches.",
            "agent_tests",
            test=True,
        ),
        contract(
            "repository.test.cancel",
            "Cancel candidate test",
            "Record cancellation for an owned run without granting any new execution.",
            RunID,
            "/test-runs/{run_id}/cancel",
            "Owner cancellation; no execution approval granted.",
            "State-checked cancellation; a running worker observes the cancellation request.",
            "agent_tests",
            test=True,
        ),
        contract(
            "repository.test.retry",
            "Retry interrupted test",
            "Create a fresh pending attempt with immutable lineage; never reuse approval.",
            RunID,
            "/test-runs/{run_id}/retry",
            "Fresh run digest and separate approval required.",
            "Only interrupted runs; new ID and digest. No automatic queueing.",
            "agent_tests",
            test=True,
        ),
        contract(
            "repository.workflow.create",
            "Create guarded workflow",
            "Validate the typed plan, persist conditional evidence and stop for human review.",
            PatchWorkflowCreate,
            "/workflows",
            "Separate patch and test approvals; plan is not authority.",
            "Source-owned versioned graph; no arbitrary tool, shell, remote "
            "or multi-agent execution.",
            "agent_workflows",
        ),
        contract(
            "repository.workflow.replay",
            "Inspect workflow replay",
            "Verify stored transitions and project a read-only event snapshot.",
            ReplayInput,
            "/workflows/{workflow_id}/replay",
            "No mutation approval; authenticated owner read only.",
            "Tenant-scoped, version-pinned replay; incompatible history fails closed.",
            "agent_workflows",
            readonly=True,
        ),
    ]
    # Stable discovery makes reviews/diffs reproducible; there is no callable registry.
    return MCPDiscoveryCatalog(tools=sorted(contracts, key=lambda item: item.name))
