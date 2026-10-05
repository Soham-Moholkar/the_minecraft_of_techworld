"""Deterministic Phase 9 workflow and approval-boundary tests."""

import hashlib
from pathlib import Path
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from atlas_api.agent_test_worker import _record_workflow_evidence
from atlas_api.agent_workflows import (
    PatchWorkflowCreate,
    PatchWorkflowMachine,
    WorkflowTransitionError,
)
from atlas_api.config import Settings, get_settings
from atlas_api.database import get_session
from atlas_api.main import app
from atlas_api.models import AIRepositoryTestRun


def _settings(root: Path) -> Settings:
    return Settings(
        database_url="sqlite+pysqlite:///:memory:",
        dev_token="atlas-test-token-is-long-enough",  # noqa: S106
        repository_root=str(root),
        ai_patch_tools_enabled=True,
        ai_test_tools_enabled=True,
    )


def _payload(source: Path, *, replacement: str = "value = 2\n") -> dict[str, object]:
    current = source.read_bytes().decode("utf-8")
    return {
        "objective": "Change the reviewed example value without granting execution authority.",
        "plan": {
            "path": "apps/api-python/example.py",
            "expected_sha256": hashlib.sha256(current.encode()).hexdigest(),
            "start_line": 1,
            "end_line": 1,
            "replacement": replacement,
            "summary": "Update the reviewed example value",
            "rationale": "Exercise deterministic plan validation before human approval.",
        },
    }


def test_workflow_records_validation_then_waits_for_separate_approval(
    client: TestClient, auth_headers: dict[str, str], tmp_path: Path
) -> None:
    (tmp_path / "apps" / "api-python").mkdir(parents=True)
    source = tmp_path / "apps" / "api-python" / "example.py"
    source.write_text("value = 1\n", encoding="utf-8")
    app.dependency_overrides[get_settings] = lambda: _settings(tmp_path)

    created = client.post(
        "/v1/ai/repository/workflows",
        headers=auth_headers,
        json=_payload(source),
    )
    assert created.status_code == 201, created.text
    workflow = created.json()
    assert workflow["status"] == "awaiting_approval"
    assert [event["state"] for event in workflow["events"]] == [
        "submitted",
        "validating",
        "awaiting_approval",
    ]
    assert source.read_text(encoding="utf-8") == "value = 1\n"
    proposal = workflow["proposal"]
    assert proposal["status"] == "pending"

    requested = client.post(
        f"/v1/ai/repository/patches/{proposal['id']}/test-runs",
        headers=auth_headers,
        json={"profile_id": "api-agent-boundary"},
    )
    assert requested.status_code == 201, requested.text
    run = requested.json()
    queued = client.post(
        f"/v1/ai/repository/test-runs/{run['id']}/approve",
        headers=auth_headers,
        json={
            "run_digest": run["run_digest"],
            "confirmation": "RUN ISOLATED TEST PROFILE",
        },
    )
    assert queued.status_code == 200, queued.text
    listed = client.get("/v1/ai/repository/workflows", headers=auth_headers)
    assert listed.status_code == 200
    assert [event["step"] for event in listed.json()[0]["events"]][-2:] == [
        "test_requested",
        "test_queued",
    ]
    assert listed.json()[0]["status"] == "awaiting_approval"
    session = next(app.dependency_overrides[get_session]())
    run_record = session.get(AIRepositoryTestRun, UUID(run["id"]))
    assert run_record is not None
    _record_workflow_evidence(
        session,
        run_record,
        step="test_passed",
        detail="Isolated test attempt 1 finished with passed.",
    )
    session.commit()
    session.close()
    terminal_evidence = client.get("/v1/ai/repository/workflows", headers=auth_headers)
    assert terminal_evidence.json()[0]["events"][-1]["step"] == "test_passed"
    assert terminal_evidence.json()[0]["status"] == "awaiting_approval"
    cancelled = client.post(
        f"/v1/ai/repository/test-runs/{run['id']}/cancel",
        headers=auth_headers,
    )
    assert cancelled.status_code == 200

    applied = client.post(
        f"/v1/ai/repository/patches/{proposal['id']}/approve",
        headers=auth_headers,
        json={
            "proposal_digest": proposal["proposal_digest"],
            "confirmation": "APPLY EXACT PATCH",
        },
    )
    assert applied.status_code == 200, applied.text
    listed = client.get("/v1/ai/repository/workflows", headers=auth_headers)
    assert listed.status_code == 200
    assert listed.json()[0]["status"] == "applied"
    assert listed.json()[0]["events"][-1]["step"] == "patch_applied"
    replay = client.get(
        f"/v1/ai/repository/workflows/{workflow['id']}/replay", headers=auth_headers
    )
    assert replay.status_code == 200, replay.text
    frames = replay.json()["frames"]
    assert replay.json()["graph"]["version"] == 1
    assert [frame["sequence"] for frame in frames] == list(range(len(frames)))
    assert (
        next(frame for frame in frames if frame["event"]["step"] == "test_passed")["authority"]
        == "none"
    )
    assert frames[-1]["condition"] == "patch_approved"
    assert frames[-1]["authority"] == "patch_approval"
    assert source.read_text(encoding="utf-8") == "value = 2"


def test_invalid_plan_is_persisted_as_failed_without_a_proposal(
    client: TestClient, auth_headers: dict[str, str], tmp_path: Path
) -> None:
    (tmp_path / "apps" / "api-python").mkdir(parents=True)
    source = tmp_path / "apps" / "api-python" / "example.py"
    source.write_text("value = 1\n", encoding="utf-8")
    app.dependency_overrides[get_settings] = lambda: _settings(tmp_path)
    response = client.post(
        "/v1/ai/repository/workflows",
        headers=auth_headers,
        json=_payload(source, replacement="if:\n"),
    )
    assert response.status_code == 201
    workflow = response.json()
    assert workflow["status"] == "failed"
    assert workflow["failure_reason"] == "patch_policy_rejected"
    assert workflow["proposal"] is None
    replay = client.get(
        f"/v1/ai/repository/workflows/{workflow['id']}/replay", headers=auth_headers
    )
    assert replay.status_code == 200
    assert replay.json()["frames"][-1]["condition"] == "policy_rejected"
    assert replay.json()["frames"][-1]["authority"] == "none"
    assert source.read_text(encoding="utf-8") == "value = 1\n"


def test_state_machine_rejects_skipped_human_review() -> None:
    data = PatchWorkflowCreate.model_validate(
        {
            "objective": "Keep explicit human review between planning and application.",
            "plan": {
                "path": "apps/example.py",
                "expected_sha256": "a" * 64,
                "start_line": 1,
                "end_line": 1,
                "replacement": "value = 2\n",
                "summary": "Update the reviewed example value",
                "rationale": "Verify that the state graph cannot skip approval.",
            },
        }
    )
    workflow = PatchWorkflowMachine.create(data, organization_id=uuid4(), actor="tester")
    PatchWorkflowMachine.record_evidence(
        workflow,
        step="test_requested",
        detail="Optional test evidence was requested without changing workflow authority.",
    )
    assert workflow.status == "submitted"
    assert workflow.current_step == "plan_received"
    assert workflow.events[-1]["step"] == "test_requested"
    try:
        PatchWorkflowMachine.transition(
            workflow,
            "applied",
            step="unsafe_skip",
            detail="This transition must never be accepted.",
        )
    except WorkflowTransitionError:
        pass
    else:
        raise AssertionError("workflow skipped deterministic validation and human review")

    # A status-shaped event with an unregistered step is also forbidden. The
    # branch condition is determined by policy, never by the event producer.
    try:
        PatchWorkflowMachine.transition(
            workflow,
            "validating",
            step="unreviewed_route",
            detail="This branch is absent from the source-owned graph.",
        )
    except WorkflowTransitionError:
        pass
    else:
        raise AssertionError("workflow accepted a caller-defined branch")


def test_replay_rejects_changed_history_and_unknown_workflow(
    client: TestClient, auth_headers: dict[str, str], tmp_path: Path
) -> None:
    (tmp_path / "apps" / "api-python").mkdir(parents=True)
    source = tmp_path / "apps" / "api-python" / "example.py"
    source.write_text("value = 1\n", encoding="utf-8")
    app.dependency_overrides[get_settings] = lambda: _settings(tmp_path)
    created = client.post(
        "/v1/ai/repository/workflows", headers=auth_headers, json=_payload(source)
    )
    assert created.status_code == 201
    workflow_id = created.json()["id"]
    assert (
        client.get(
            f"/v1/ai/repository/workflows/{uuid4()}/replay", headers=auth_headers
        ).status_code
        == 404
    )
    session = next(app.dependency_overrides[get_session]())
    from atlas_api.models import AIRepositoryPatchWorkflow

    record = session.get(AIRepositoryPatchWorkflow, UUID(workflow_id))
    assert record is not None
    changed = [*record.events]
    changed[1] = {**changed[1], "step": "unreviewed_route"}
    record.events = changed
    session.commit()
    rejected = client.get(f"/v1/ai/repository/workflows/{workflow_id}/replay", headers=auth_headers)
    assert rejected.status_code == 409
    assert rejected.json()["detail"] == "workflow history failed policy validation"

    # A policy revision is never guessed from current code. Operators must
    # retain that version's graph before its old history can be replayed.
    record = session.get(AIRepositoryPatchWorkflow, UUID(workflow_id))
    assert record is not None
    record.events = created.json()["events"]
    record.graph_version = 999
    session.commit()
    session.close()
    incompatible = client.get(
        f"/v1/ai/repository/workflows/{workflow_id}/replay", headers=auth_headers
    )
    assert incompatible.status_code == 409
