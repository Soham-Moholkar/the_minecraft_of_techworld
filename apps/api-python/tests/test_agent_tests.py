"""Security and lifecycle coverage for separately approved isolated test profiles."""

import hashlib
from pathlib import Path
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from atlas_api.agent_patches import PatchGateway, PatchProposalCreate
from atlas_api.agent_test_worker import (
    TestWorkerPolicyError as WorkerPolicyError,
)
from atlas_api.agent_test_worker import (
    _classify_exit,
    _stage_candidate,
    docker_command,
)
from atlas_api.agent_tests import TEST_PROFILES
from atlas_api.config import Settings, get_settings
from atlas_api.database import get_session
from atlas_api.main import app
from atlas_api.models import AIRepositoryTestRun


def _settings(root: Path, *, tests_enabled: bool = True) -> Settings:
    return Settings(
        database_url="sqlite+pysqlite:///:memory:",
        dev_token="atlas-test-token-is-long-enough",  # noqa: S106
        repository_root=str(root),
        ai_patch_tools_enabled=True,
        ai_test_tools_enabled=tests_enabled,
    )


def _proposal(
    client: TestClient, headers: dict[str, str], root: Path
) -> dict[str, object]:
    source = root / "apps" / "api-python" / "src" / "atlas_api" / "example.py"
    source.parent.mkdir(parents=True)
    source.write_text("value = 1\n", encoding="utf-8")
    current = source.read_bytes()
    response = client.post(
        "/v1/ai/repository/patches",
        headers=headers,
        json={
            "path": "apps/api-python/src/atlas_api/example.py",
            "expected_sha256": hashlib.sha256(current).hexdigest(),
            "start_line": 1,
            "end_line": 1,
            "replacement": "value = 2\n",
            "summary": "Update the isolated test candidate",
            "rationale": "Verify separate approval without modifying the live checkout.",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_test_run_requires_its_own_digest_approval_and_can_be_cancelled(
    client: TestClient, auth_headers: dict[str, str], tmp_path: Path
) -> None:
    app.dependency_overrides[get_settings] = lambda: _settings(tmp_path)
    proposal = _proposal(client, auth_headers, tmp_path)
    requested = client.post(
        f"/v1/ai/repository/patches/{proposal['id']}/test-runs",
        headers=auth_headers,
        json={"profile_id": "api-agent-boundary"},
    )
    assert requested.status_code == 201, requested.text
    run = requested.json()
    assert run["status"] == "pending_approval"

    rejected = client.post(
        f"/v1/ai/repository/test-runs/{run['id']}/approve",
        headers=auth_headers,
        json={
            "run_digest": "0" * 64,
            "confirmation": "RUN ISOLATED TEST PROFILE",
        },
    )
    assert rejected.status_code == 409

    queued = client.post(
        f"/v1/ai/repository/test-runs/{run['id']}/approve",
        headers=auth_headers,
        json={
            "run_digest": run["run_digest"],
            "confirmation": "RUN ISOLATED TEST PROFILE",
        },
    )
    assert queued.status_code == 200
    assert queued.json()["status"] == "queued"

    blocked_apply = client.post(
        f"/v1/ai/repository/patches/{proposal['id']}/approve",
        headers=auth_headers,
        json={
            "proposal_digest": proposal["proposal_digest"],
            "confirmation": "APPLY EXACT PATCH",
        },
    )
    assert blocked_apply.status_code == 409

    cancelled = client.post(
        f"/v1/ai/repository/test-runs/{run['id']}/cancel",
        headers=auth_headers,
    )
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"
    source = tmp_path / "apps" / "api-python" / "src" / "atlas_api" / "example.py"
    assert source.read_text(encoding="utf-8") == "value = 1\n"


def test_profiles_are_fixed_and_docker_policy_denies_network(tmp_path: Path) -> None:
    profile = TEST_PROFILES["api-agent-boundary"]
    command = docker_command(profile, tmp_path, "atlas-test-" + "a" * 32)
    assert Path(command[0]).name.lower() in {"docker", "docker.exe"}
    assert command[1:3] == ["run", "--rm"]
    assert "--network=none" in command
    assert "--read-only" in command
    assert "--cap-drop=ALL" in command
    assert "--security-opt=no-new-privileges" in command
    assert "--pull=never" in command
    assert command[-len(profile.command) :] == list(profile.command)
    assert all("secret" not in value.lower() for value in command)
    assert _classify_exit(0) == ("passed", None)
    assert _classify_exit(1) == ("failed", "tests_failed")
    assert _classify_exit(125) == ("worker_failed", "docker_execution_failed")


def test_test_execution_fails_closed_until_second_opt_in(
    client: TestClient, auth_headers: dict[str, str], tmp_path: Path
) -> None:
    app.dependency_overrides[get_settings] = lambda: _settings(tmp_path, tests_enabled=False)
    proposal = _proposal(client, auth_headers, tmp_path)
    response = client.post(
        f"/v1/ai/repository/patches/{proposal['id']}/test-runs",
        headers=auth_headers,
        json={"profile_id": "api-agent-boundary"},
    )
    assert response.status_code == 503


def test_interrupted_retry_creates_new_digest_and_requires_new_approval(
    client: TestClient, auth_headers: dict[str, str], tmp_path: Path
) -> None:
    app.dependency_overrides[get_settings] = lambda: _settings(tmp_path)
    proposal = _proposal(client, auth_headers, tmp_path)
    requested = client.post(
        f"/v1/ai/repository/patches/{proposal['id']}/test-runs",
        headers=auth_headers,
        json={"profile_id": "api-agent-boundary"},
    )
    assert requested.status_code == 201, requested.text
    original = requested.json()

    session = next(app.dependency_overrides[get_session]())
    record = session.get(AIRepositoryTestRun, UUID(original["id"]))
    assert record is not None
    record.status = "interrupted"
    record.failure_reason = "worker_heartbeat_expired"
    session.commit()
    session.close()

    response = client.post(
        f"/v1/ai/repository/test-runs/{original['id']}/retry",
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    retry = response.json()
    assert retry["id"] != original["id"]
    assert retry["run_digest"] != original["run_digest"]
    assert retry["retry_of_id"] == original["id"]
    assert retry["attempt"] == 2
    assert retry["status"] == "pending_approval"
    assert retry["approved_by"] is None

    stale_approval = client.post(
        f"/v1/ai/repository/test-runs/{retry['id']}/approve",
        headers=auth_headers,
        json={
            "run_digest": original["run_digest"],
            "confirmation": "RUN ISOLATED TEST PROFILE",
        },
    )
    assert stale_approval.status_code == 409

    approved = client.post(
        f"/v1/ai/repository/test-runs/{retry['id']}/approve",
        headers=auth_headers,
        json={
            "run_digest": retry["run_digest"],
            "confirmation": "RUN ISOLATED TEST PROFILE",
        },
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["status"] == "queued"


def test_worker_stages_candidate_without_mutating_checkout_and_rejects_stale_source(
    tmp_path: Path,
) -> None:
    source = tmp_path / "apps" / "api-python" / "src" / "atlas_api" / "example.py"
    source.parent.mkdir(parents=True)
    source.write_text("value = 1\n", encoding="utf-8")
    proposal = PatchGateway(_settings(tmp_path)).build(
        PatchProposalCreate(
            path="apps/api-python/src/atlas_api/example.py",
            expected_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            start_line=1,
            end_line=1,
            replacement="value = 2\n",
            summary="Update the isolated candidate",
            rationale="Prove staging does not mutate the live checkout.",
        ),
        organization_id=uuid4(),
        actor="tester",
    )
    stage = tmp_path / "stage"
    stage.mkdir()
    _stage_candidate(tmp_path, stage, proposal, TEST_PROFILES["api-agent-boundary"])
    assert source.read_text(encoding="utf-8") == "value = 1\n"
    assert (stage / proposal.path).read_text(encoding="utf-8") == proposal.patched_content

    source.write_text("value = 3\n", encoding="utf-8")
    try:
        _stage_candidate(
            tmp_path,
            tmp_path / "stale",
            proposal,
            TEST_PROFILES["api-agent-boundary"],
        )
    except WorkerPolicyError as error:
        assert "changed" in str(error)
    else:
        raise AssertionError("stale proposal source was staged")
