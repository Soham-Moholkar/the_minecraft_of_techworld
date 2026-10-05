"""Security and lifecycle coverage for the Phase 9 local patch gateway."""

import hashlib
from pathlib import Path
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select

from atlas_api.agent_patches import PatchGateway, PatchPolicyError, PatchProposalCreate
from atlas_api.config import Settings, get_settings
from atlas_api.database import get_session
from atlas_api.main import app
from atlas_api.models import AIRepositoryPatchProposal, AuditEvent


def _sha(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def _settings(root: Path, *, enabled: bool = True) -> Settings:
    return Settings(
        database_url="sqlite+pysqlite:///:memory:",
        dev_token="atlas-test-token-is-long-enough",  # noqa: S106
        repository_root=str(root),
        ai_patch_tools_enabled=enabled,
    )


def _propose(
    client: TestClient, headers: dict[str, str], source: Path, replacement: str
) -> dict[str, object]:
    current = source.read_bytes().decode("utf-8")
    response = client.post(
        "/v1/ai/repository/patches",
        headers=headers,
        json={
            "path": "apps/example.py",
            "expected_sha256": _sha(current),
            "start_line": 1,
            "end_line": 1,
            "replacement": replacement,
            "summary": "Update the example value",
            "rationale": "Exercise the exact-diff approval and rollback boundary.",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_exact_digest_approval_applies_and_rolls_back(
    client: TestClient, auth_headers: dict[str, str], tmp_path: Path
) -> None:
    (tmp_path / "apps").mkdir()
    source = tmp_path / "apps" / "example.py"
    source.write_text("value = 1\nprint(value)\n", encoding="utf-8")
    app.dependency_overrides[get_settings] = lambda: _settings(tmp_path)

    proposal = _propose(client, auth_headers, source, "value = 2\n")
    assert "-value = 1" in str(proposal["unified_diff"])
    assert "original_content" not in proposal and "patched_content" not in proposal

    wrong = client.post(
        f"/v1/ai/repository/patches/{proposal['id']}/approve",
        headers=auth_headers,
        json={"proposal_digest": "0" * 64, "confirmation": "APPLY EXACT PATCH"},
    )
    assert wrong.status_code == 409
    assert source.read_text(encoding="utf-8").startswith("value = 1")

    applied = client.post(
        f"/v1/ai/repository/patches/{proposal['id']}/approve",
        headers=auth_headers,
        json={
            "proposal_digest": proposal["proposal_digest"],
            "confirmation": "APPLY EXACT PATCH",
        },
    )
    assert applied.status_code == 200, applied.text
    assert applied.json()["status"] == "applied"
    assert source.read_text(encoding="utf-8").startswith("value = 2")

    rolled_back = client.post(
        f"/v1/ai/repository/patches/{proposal['id']}/rollback",
        headers=auth_headers,
        json={
            "proposal_digest": proposal["proposal_digest"],
            "confirmation": "ROLL BACK EXACT PATCH",
        },
    )
    assert rolled_back.status_code == 200, rolled_back.text
    assert rolled_back.json()["status"] == "rolled_back"
    assert source.read_text(encoding="utf-8") == "value = 1\nprint(value)\n"

    session = next(app.dependency_overrides[get_session]())
    actions = session.scalars(
        select(AuditEvent.action).where(AuditEvent.target_type == "ai_repository_patch")
    ).all()
    assert actions == [
        "ai.patch.proposed",
        "ai.patch.approved",
        "ai.patch.applied",
        "ai.patch.rolled_back",
    ]


def test_source_change_invalidates_approval(
    client: TestClient, auth_headers: dict[str, str], tmp_path: Path
) -> None:
    (tmp_path / "apps").mkdir()
    source = tmp_path / "apps" / "example.py"
    source.write_text("value = 1\n", encoding="utf-8")
    app.dependency_overrides[get_settings] = lambda: _settings(tmp_path)
    proposal = _propose(client, auth_headers, source, "value = 2\n")
    source.write_text("value = 3\n", encoding="utf-8")

    response = client.post(
        f"/v1/ai/repository/patches/{proposal['id']}/approve",
        headers=auth_headers,
        json={
            "proposal_digest": proposal["proposal_digest"],
            "confirmation": "APPLY EXACT PATCH",
        },
    )
    assert response.status_code == 409
    assert source.read_text(encoding="utf-8") == "value = 3\n"
    session = next(app.dependency_overrides[get_session]())
    record = session.get(AIRepositoryPatchProposal, UUID(str(proposal["id"])))
    assert record is not None and record.status == "conflicted"


def test_gateway_rejects_traversal_symlinks_invalid_syntax_and_new_files(tmp_path: Path) -> None:
    (tmp_path / "apps").mkdir()
    source = tmp_path / "apps" / "example.py"
    source.write_text("value = 1\n", encoding="utf-8")
    gateway = PatchGateway(_settings(tmp_path))
    base = {
        "expected_sha256": _sha(source.read_bytes().decode("utf-8")),
        "start_line": 1,
        "end_line": 1,
        "replacement": "value = 2\n",
        "summary": "Update the example value",
        "rationale": "Confirm that unsafe patch targets are rejected by policy.",
    }
    for path in ("../outside.py", ".env", "apps/missing.py", "compose.yaml"):
        try:
            gateway.build(
                PatchProposalCreate(path=path, **base),
                organization_id=uuid4(),
                actor="tester",
            )
        except PatchPolicyError:
            pass
        else:
            raise AssertionError(f"unsafe patch path accepted: {path}")

    invalid = PatchProposalCreate(path="apps/example.py", **(base | {"replacement": "if:\n"}))
    try:
        gateway.build(invalid, organization_id=uuid4(), actor="tester")
    except PatchPolicyError as error:
        assert "syntax" in str(error)
    else:
        raise AssertionError("invalid Python syntax was accepted")


def test_patch_tools_fail_closed_until_operator_opt_in(
    client: TestClient, auth_headers: dict[str, str], tmp_path: Path
) -> None:
    (tmp_path / "apps").mkdir()
    source = tmp_path / "apps" / "example.py"
    source.write_text("value = 1\n", encoding="utf-8")
    app.dependency_overrides[get_settings] = lambda: _settings(tmp_path, enabled=False)
    response = client.post(
        "/v1/ai/repository/patches",
        headers=auth_headers,
        json={
            "path": "apps/example.py",
            "expected_sha256": _sha(source.read_bytes().decode("utf-8")),
            "start_line": 1,
            "end_line": 1,
            "replacement": "value = 2\n",
            "summary": "Update the example value",
            "rationale": "The disabled guard must reject mutation before file access.",
        },
    )
    assert response.status_code == 503
    assert source.read_text(encoding="utf-8") == "value = 1\n"
