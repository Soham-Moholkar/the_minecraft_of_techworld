"""Durable worker for approved repository tests inside a locked-down container.

The worker never executes a caller command. It stages only a reviewed candidate,
then runs one source-owned profile through Docker with networking disabled. There
is deliberately no host-process fallback when the isolation backend is absent.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess  # noqa: S404 -- exact Docker argv is constructed from source policy
import tempfile
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path, PurePosixPath

from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas_api.agent_tests import (
    TestProfile,
    TestRunTransitionError,
    get_test_profile,
    verify_test_run_policy,
)
from atlas_api.agent_workflows import PatchWorkflowMachine
from atlas_api.config import Settings, get_settings
from atlas_api.database import SessionLocal
from atlas_api.models import (
    AIRepositoryPatchProposal,
    AIRepositoryPatchWorkflow,
    AIRepositoryTestRun,
    AuditEvent,
)

_DENIED_NAMES = {".env", ".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", "__pycache__"}
_DENIED_SUFFIXES = {".key", ".pem", ".p12", ".pfx"}
_MAX_STAGED_FILES = 5_000
_MAX_STAGED_BYTES = 64 * 1024 * 1024
_DOCKER_EXECUTABLE = shutil.which("docker") or "docker"


class TestWorkerPolicyError(RuntimeError):
    """Raised when the candidate or local runtime violates worker policy."""


def _record_workflow_evidence(
    session: Session,
    run: AIRepositoryTestRun,
    *,
    step: str,
    detail: str,
) -> None:
    # Worker sessions are ordinary SQLAlchemy Sessions. Keeping the helper free of
    # HTTP concerns makes terminal evidence available during startup recovery too.
    workflow = session.scalar(
        select(AIRepositoryPatchWorkflow).where(
            AIRepositoryPatchWorkflow.proposal_id == run.proposal_id
        )
    )
    if workflow is not None:
        PatchWorkflowMachine.record_evidence(workflow, step=step, detail=detail)


@dataclass(frozen=True)
class TestExecutionResult:
    status: str
    output_excerpt: str
    output_sha256: str
    output_truncated: bool
    exit_code: int | None
    duration_ms: int
    failure_reason: str | None = None


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _classify_exit(exit_code: int) -> tuple[str, str | None]:
    if exit_code == 0:
        return "passed", None
    if exit_code in {125, 126, 127}:
        # Docker reserves these codes for daemon/CLI/image or command startup
        # failures. Missing isolation must never be reported as a test result.
        return "worker_failed", "docker_execution_failed"
    return "failed", "tests_failed"


def _stage_candidate(
    root: Path,
    stage: Path,
    proposal: AIRepositoryPatchProposal,
    profile: TestProfile,
) -> None:
    """Copy one fixed project subtree without links, caches, credentials, or VCS data."""

    source_root = (root / PurePosixPath(profile.path_prefix.rstrip("/"))).resolve()
    repository_root = root.resolve()
    if repository_root not in source_root.parents or not source_root.is_dir():
        raise TestWorkerPolicyError("profile source root is unavailable")

    count = 0
    total = 0
    for source in source_root.rglob("*"):
        relative = source.relative_to(repository_root)
        if any(part in _DENIED_NAMES for part in relative.parts):
            continue
        if source.name == ".env" or source.name.startswith(".env."):
            continue
        if source.is_symlink():
            raise TestWorkerPolicyError("candidate tree contains a symbolic link")
        if source.is_dir():
            continue
        if not source.is_file() or source.suffix.lower() in _DENIED_SUFFIXES:
            raise TestWorkerPolicyError("candidate tree contains a denied file type")
        data = source.read_bytes()
        count += 1
        total += len(data)
        if count > _MAX_STAGED_FILES or total > _MAX_STAGED_BYTES:
            raise TestWorkerPolicyError("candidate tree exceeds staging limits")
        destination = stage / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)

    live_target = (repository_root / PurePosixPath(proposal.path)).resolve()
    if repository_root not in live_target.parents or live_target.is_symlink():
        raise TestWorkerPolicyError("proposal target escaped the repository")
    if _sha256(live_target.read_bytes()) != proposal.original_sha256:
        raise TestWorkerPolicyError("proposal source changed before isolated testing")
    staged_target = stage / PurePosixPath(proposal.path)
    if not staged_target.is_file():
        raise TestWorkerPolicyError("proposal target was not staged")
    patched = proposal.patched_content.encode("utf-8")
    if _sha256(patched) != proposal.patched_sha256:
        raise TestWorkerPolicyError("stored candidate hash is invalid")
    staged_target.write_bytes(patched)
    # The container user is deliberately unrelated to the host operator. World
    # read bits allow that non-root UID to traverse the staging tree; the Docker
    # bind mount, not host mode bits, enforces immutability inside the container.
    if os.name == "posix":
        for staged in stage.rglob("*"):
            staged.chmod(0o755 if staged.is_dir() else 0o644)
        stage.chmod(0o755)


def docker_command(profile: TestProfile, stage: Path, container_name: str) -> list[str]:
    """Return the complete shell-free Docker argv for security review and tests."""

    mount = f"type=bind,src={stage.resolve()},dst=/workspace,readonly"
    return [
        _DOCKER_EXECUTABLE,
        "run",
        "--rm",
        "--pull=never",
        "--name",
        container_name,
        "--network=none",
        "--read-only",
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges",
        "--pids-limit",
        str(profile.pids_limit),
        "--memory",
        f"{profile.memory_mb}m",
        "--memory-swap",
        f"{profile.memory_mb}m",
        "--cpus",
        profile.cpus,
        "--user",
        "65532:65532",
        "--ulimit",
        "nofile=256:256",
        "--tmpfs",
        "/tmp:rw,noexec,nosuid,nodev,size=128m",  # noqa: S108 - container tmpfs
        "--mount",
        mount,
        "--workdir",
        profile.cwd,
        "--env",
        "HOME=/tmp",
        "--env",
        "NO_PROXY=*",
        "--env",
        "PYTHONDONTWRITEBYTECODE=1",
        "--env",
        "PYTHONHASHSEED=0",
        "--env",
        "PYTHONPATH=/workspace/apps/api-python/src",
        profile.image,
        *profile.command,
    ]


class DockerTestRunner:
    """Execute a staged candidate only through the mandatory Docker boundary."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @staticmethod
    def force_remove(container_name: str) -> None:
        if not container_name.startswith("atlas-test-"):
            return
        try:
            subprocess.run(  # noqa: S603 -- exact executable and validated internal name
                [_DOCKER_EXECUTABLE, "rm", "--force", container_name],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired):
            # Recovery still records the durable interruption. The deterministic
            # name remains available for a later operator/worker orphan scan.
            return

    def run(
        self,
        run: AIRepositoryTestRun,
        proposal: AIRepositoryPatchProposal,
        profile: TestProfile,
        *,
        cancelled: Callable[[], bool],
    ) -> TestExecutionResult:
        if self.settings.environment != "development" or not self.settings.ai_test_tools_enabled:
            raise TestWorkerPolicyError("isolated test tools are disabled")
        root = Path(self.settings.repository_root).resolve()
        if not root.is_dir():
            raise TestWorkerPolicyError("repository root is unavailable")

        started = time.monotonic()
        container_name = f"atlas-test-{run.id.hex}"
        run.container_name = container_name
        with tempfile.TemporaryDirectory(prefix="atlas-test-stage-") as directory:
            stage = Path(directory)
            _stage_candidate(root, stage, proposal, profile)
            command = docker_command(profile, stage, container_name)
            try:
                process = subprocess.Popen(  # noqa: S603 -- exact shell-free Docker argv
                    command,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    env={"PATH": os.environ.get("PATH", "")},
                    shell=False,
                )
            except (FileNotFoundError, OSError) as error:
                raise TestWorkerPolicyError("Docker isolation backend is unavailable") from error

            digest = hashlib.sha256()
            excerpt = bytearray()
            output_limit_hit = threading.Event()

            def drain() -> None:
                assert process.stdout is not None
                while chunk := process.stdout.read(8_192):
                    digest.update(chunk)
                    remaining = max(0, profile.output_limit_bytes - len(excerpt))
                    excerpt.extend(chunk[:remaining])
                    if len(chunk) > remaining:
                        output_limit_hit.set()

            reader = threading.Thread(target=drain, name=f"{container_name}-output", daemon=True)
            reader.start()
            outcome = "failed"
            reason: str | None = None
            while process.poll() is None:
                elapsed = time.monotonic() - started
                if cancelled():
                    outcome, reason = "cancelled", "operator_cancelled"
                    self.force_remove(container_name)
                    break
                if output_limit_hit.is_set():
                    outcome, reason = "output_limit", "output_limit_exceeded"
                    self.force_remove(container_name)
                    break
                if elapsed > profile.timeout_seconds:
                    outcome, reason = "timed_out", "timeout_exceeded"
                    self.force_remove(container_name)
                    break
                time.sleep(0.2)

            try:
                exit_code = process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                exit_code = process.wait(timeout=5)
            reader.join(timeout=5)
            if outcome == "failed":
                outcome, reason = _classify_exit(exit_code)
            duration_ms = int((time.monotonic() - started) * 1_000)
            return TestExecutionResult(
                status=outcome,
                output_excerpt=bytes(excerpt).decode("utf-8", errors="replace"),
                output_sha256=digest.hexdigest(),
                output_truncated=output_limit_hit.is_set(),
                exit_code=exit_code,
                duration_ms=duration_ms,
                failure_reason=reason,
            )


def _recover_interrupted(settings: Settings) -> None:
    cutoff = datetime.now(UTC) - timedelta(minutes=10)
    with SessionLocal() as session:
        stale = session.scalars(
            select(AIRepositoryTestRun).where(
                AIRepositoryTestRun.status.in_(["running", "cancel_requested"]),
                AIRepositoryTestRun.heartbeat_at < cutoff,
            )
        ).all()
        for run in stale:
            if run.container_name:
                DockerTestRunner.force_remove(run.container_name)
            run.status = "interrupted"
            run.failure_reason = "worker_heartbeat_expired"
            run.finished_at = datetime.now(UTC)
            _record_workflow_evidence(
                session,
                run,
                step="test_interrupted",
                detail=f"Test attempt {run.attempt} was interrupted after its heartbeat expired.",
            )
        session.commit()


def process_one(settings: Settings) -> bool:
    """Claim and execute one approved run; return whether work was found."""

    with SessionLocal() as session:
        run = session.scalar(
            select(AIRepositoryTestRun)
            .where(AIRepositoryTestRun.status == "queued")
            .order_by(AIRepositoryTestRun.created_at)
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        if run is None:
            return False
        proposal = session.get(AIRepositoryPatchProposal, run.proposal_id)
        if proposal is None or proposal.status != "pending":
            run.status = "worker_failed"
            run.failure_reason = "proposal_not_pending"
            run.finished_at = datetime.now(UTC)
            _record_workflow_evidence(
                session,
                run,
                step="test_worker_failed",
                detail=f"Test attempt {run.attempt} stopped because its proposal was not pending.",
            )
            session.commit()
            return True
        try:
            profile = get_test_profile(run.profile_id)
            verify_test_run_policy(run, proposal, profile)
        except TestRunTransitionError:
            run.status = "worker_failed"
            run.failure_reason = "run_policy_digest_changed"
            run.finished_at = datetime.now(UTC)
            _record_workflow_evidence(
                session,
                run,
                step="test_worker_failed",
                detail=f"Test attempt {run.attempt} stopped because its profile policy changed.",
            )
            session.commit()
            return True
        run.status = "running"
        run.started_at = datetime.now(UTC)
        run.heartbeat_at = run.started_at
        run.container_name = f"atlas-test-{run.id.hex}"
        _record_workflow_evidence(
            session,
            run,
            step="test_running",
            detail=f"Isolated worker started test attempt {run.attempt}.",
        )
        session.commit()
        run_id = run.id
        proposal_id = proposal.id

    last_heartbeat = 0.0

    def cancelled() -> bool:
        nonlocal last_heartbeat
        now = time.monotonic()
        with SessionLocal() as check_session:
            current = check_session.get(AIRepositoryTestRun, run_id)
            if current is None:
                return True
            if now - last_heartbeat >= 1:
                current.heartbeat_at = datetime.now(UTC)
                check_session.commit()
                last_heartbeat = now
            return current.cancel_requested

    with SessionLocal() as session:
        active = session.get(AIRepositoryTestRun, run_id)
        proposal = session.get(AIRepositoryPatchProposal, proposal_id)
        assert active is not None and proposal is not None
        try:
            result = DockerTestRunner(settings).run(
                active,
                proposal,
                profile,
                cancelled=cancelled,
            )
            container_name = active.container_name
        except TestWorkerPolicyError as error:
            result = TestExecutionResult(
                status="worker_failed",
                output_excerpt="",
                output_sha256=hashlib.sha256(b"").hexdigest(),
                output_truncated=False,
                exit_code=None,
                duration_ms=0,
                failure_reason=str(error)[:120],
            )
            container_name = active.container_name

    with SessionLocal() as session:
        completed = session.get(AIRepositoryTestRun, run_id)
        assert completed is not None
        completed.status = result.status
        completed.container_name = container_name
        completed.output_excerpt = result.output_excerpt
        completed.output_sha256 = result.output_sha256
        completed.output_truncated = result.output_truncated
        completed.exit_code = result.exit_code
        completed.duration_ms = result.duration_ms
        completed.failure_reason = result.failure_reason
        completed.finished_at = datetime.now(UTC)
        _record_workflow_evidence(
            session,
            completed,
            step=f"test_{result.status}",
            detail=f"Isolated test attempt {completed.attempt} finished with {result.status}.",
        )
        session.add(
            AuditEvent(
                organization_id=completed.organization_id,
                actor="atlas-test-worker",
                action=f"ai.test_run.{result.status}",
                target_type="ai_repository_test_run",
                target_id=str(completed.id),
                details={
                    "profile_id": completed.profile_id,
                    "proposal_id": str(completed.proposal_id),
                    "output_sha256": completed.output_sha256,
                    "duration_ms": completed.duration_ms,
                },
            )
        )
        session.commit()
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="ATLAS isolated repository test worker")
    parser.add_argument("--once", action="store_true", help="process at most one queued run")
    args = parser.parse_args()
    settings = get_settings()
    if settings.environment != "development" or not settings.ai_test_tools_enabled:
        raise SystemExit("isolated test tools are disabled")
    _recover_interrupted(settings)
    while True:
        found = process_one(settings)
        if args.once:
            return
        if not found:
            time.sleep(1)


if __name__ == "__main__":
    main()
