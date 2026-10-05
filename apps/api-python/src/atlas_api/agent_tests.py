"""Approval contracts and source-owned profiles for isolated candidate tests.

Callers select only a profile identifier. Commands, image, environment, working
directory and resource limits are immutable source policy and are covered by the
run digest shown to the operator before the separate execution approval.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from atlas_api.models import AIRepositoryPatchProposal, AIRepositoryTestRun

TestRunStatus = Literal[
    "pending_approval",
    "queued",
    "running",
    "cancel_requested",
    "passed",
    "failed",
    "cancelled",
    "timed_out",
    "output_limit",
    "worker_failed",
    "interrupted",
]

TERMINAL_TEST_STATUSES = {
    "passed",
    "failed",
    "cancelled",
    "timed_out",
    "output_limit",
    "worker_failed",
    "interrupted",
}


@dataclass(frozen=True)
class TestProfile:
    """One auditable command and its complete container resource policy."""

    id: str
    version: int
    title: str
    description: str
    path_prefix: str
    command: tuple[str, ...]
    cwd: str = "/workspace/apps/api-python"
    image: str = "atlas-api-test-worker:local"
    timeout_seconds: int = 180
    memory_mb: int = 768
    cpus: str = "1.0"
    pids_limit: int = 128
    output_limit_bytes: int = 131_072


TEST_PROFILES: dict[str, TestProfile] = {
    "api-agent-boundary": TestProfile(
        id="api-agent-boundary",
        version=1,
        title="Agent boundary tests",
        description="Patch, deterministic workflow, and isolated-run security tests.",
        path_prefix="apps/api-python/",
        command=(
            "python",
            "-m",
            "pytest",
            "tests/test_agent_patches.py",
            "tests/test_agent_workflows.py",
            "tests/test_agent_tests.py",
            "-q",
        ),
    ),
    "api-full": TestProfile(
        id="api-full",
        version=1,
        title="Full API suite",
        description="The complete Python API test suite with strict pytest markers.",
        path_prefix="apps/api-python/",
        command=("python", "-m", "pytest", "-q", "--strict-markers"),
        timeout_seconds=300,
        memory_mb=1_024,
    ),
}


class TestProfileRead(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    version: int
    title: str
    description: str
    command: list[str]
    cwd: str
    timeout_seconds: int
    memory_mb: int
    cpus: str
    pids_limit: int
    output_limit_bytes: int
    network: Literal["none"] = "none"
    checkout: Literal["staged-read-only"] = "staged-read-only"


class TestRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    profile_id: str = Field(pattern=r"^[a-z][a-z0-9-]{2,63}$")


class TestRunApproval(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    run_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    confirmation: Literal["RUN ISOLATED TEST PROFILE"]


class TestRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    proposal_id: UUID
    retry_of_id: UUID | None
    attempt: int = Field(ge=1, le=100)
    profile_id: str
    profile_version: int
    run_digest: str
    status: TestRunStatus
    requested_by: str
    approved_by: str | None
    output_excerpt: str
    output_sha256: str | None
    output_truncated: bool
    exit_code: int | None
    duration_ms: int | None
    failure_reason: str | None
    cancel_requested: bool
    created_at: datetime
    approved_at: datetime | None
    started_at: datetime | None
    finished_at: datetime | None


class TestRunTransitionError(RuntimeError):
    """Raised when a test run attempts to bypass approval or terminal state."""


def profile_read(profile: TestProfile) -> TestProfileRead:
    return TestProfileRead(
        id=profile.id,
        version=profile.version,
        title=profile.title,
        description=profile.description,
        command=list(profile.command),
        cwd=profile.cwd,
        timeout_seconds=profile.timeout_seconds,
        memory_mb=profile.memory_mb,
        cpus=profile.cpus,
        pids_limit=profile.pids_limit,
        output_limit_bytes=profile.output_limit_bytes,
    )


def get_test_profile(profile_id: str) -> TestProfile:
    try:
        return TEST_PROFILES[profile_id]
    except KeyError as error:
        raise TestRunTransitionError("unknown test profile") from error


def test_run_digest(
    proposal: AIRepositoryPatchProposal,
    profile: TestProfile,
    *,
    run_id: UUID,
    attempt: int,
    retry_of_id: UUID | None,
) -> str:
    payload = {
        "run_id": str(run_id),
        "attempt": attempt,
        "retry_of_id": str(retry_of_id) if retry_of_id is not None else None,
        "proposal_digest": proposal.proposal_digest,
        "patched_sha256": proposal.patched_sha256,
        "profile": asdict(profile),
        "network": "none",
        "checkout": "staged-read-only",
        "environment": {
            "HOME": "/tmp",  # noqa: S108 - isolated container tmpfs
            "NO_PROXY": "*",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
            "PYTHONPATH": "/workspace/apps/api-python/src",
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def create_test_run(
    proposal: AIRepositoryPatchProposal,
    profile: TestProfile,
    *,
    organization_id: UUID,
    actor: str,
    retry_of: AIRepositoryTestRun | None = None,
) -> AIRepositoryTestRun:
    if proposal.status != "pending":
        raise TestRunTransitionError("tests require a pending patch proposal")
    if not proposal.path.startswith(profile.path_prefix):
        raise TestRunTransitionError("profile does not cover the proposed path")
    if retry_of is not None and retry_of.status != "interrupted":
        raise TestRunTransitionError("only an interrupted test run can be retried")
    if retry_of is not None and retry_of.proposal_id != proposal.id:
        raise TestRunTransitionError("retry lineage does not match the patch proposal")
    run_id = uuid4()
    attempt = 1 if retry_of is None else retry_of.attempt + 1
    retry_of_id = None if retry_of is None else retry_of.id
    return AIRepositoryTestRun(
        id=run_id,
        organization_id=organization_id,
        proposal_id=proposal.id,
        retry_of_id=retry_of_id,
        attempt=attempt,
        profile_id=profile.id,
        profile_version=profile.version,
        run_digest=test_run_digest(
            proposal,
            profile,
            run_id=run_id,
            attempt=attempt,
            retry_of_id=retry_of_id,
        ),
        status="pending_approval",
        requested_by=actor,
        output_excerpt="",
        output_truncated=False,
        cancel_requested=False,
        created_at=datetime.now(UTC),
    )


def approve_test_run(run: AIRepositoryTestRun, approval: TestRunApproval, *, actor: str) -> None:
    if run.status != "pending_approval":
        raise TestRunTransitionError("test run is not waiting for approval")
    if run.run_digest != approval.run_digest:
        raise TestRunTransitionError("approval digest does not match the reviewed test run")
    run.status = "queued"
    run.approved_by = actor
    run.approved_at = datetime.now(UTC)


def verify_test_run_policy(
    run: AIRepositoryTestRun,
    proposal: AIRepositoryPatchProposal,
    profile: TestProfile,
) -> None:
    if profile.version != run.profile_version:
        raise TestRunTransitionError("reviewed test profile version changed")
    expected = test_run_digest(
        proposal,
        profile,
        run_id=run.id,
        attempt=run.attempt,
        retry_of_id=run.retry_of_id,
    )
    if expected != run.run_digest:
        raise TestRunTransitionError("reviewed test profile policy changed")


def cancel_test_run(run: AIRepositoryTestRun) -> None:
    if run.status in TERMINAL_TEST_STATUSES:
        raise TestRunTransitionError("test run is already terminal")
    run.cancel_requested = True
    if run.status in {"pending_approval", "queued"}:
        run.status = "cancelled"
        run.finished_at = datetime.now(UTC)
    elif run.status == "running":
        run.status = "cancel_requested"


def test_run_read(run: AIRepositoryTestRun) -> TestRunRead:
    return TestRunRead.model_validate(run)
