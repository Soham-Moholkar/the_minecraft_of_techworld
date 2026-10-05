"""Contract drift, local authorization and no-dispatch regression tests."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from atlas_api.agent_mcp import build_mcp_catalog
from atlas_api.agent_patches import PatchApproval, PatchProposalCreate, PatchRollback
from atlas_api.agent_tests import TestRunApproval as RunApproval
from atlas_api.agent_tests import TestRunRequest as RunRequest
from atlas_api.agent_workflows import PatchWorkflowCreate
from atlas_api.ai_routes import MCP_CATALOG_READS
from atlas_api.auth import Principal, require_principal
from atlas_api.config import Settings, get_settings
from atlas_api.database import get_session
from atlas_api.main import app
from atlas_api.models import (
    AIRepositoryPatchProposal,
    AIRepositoryPatchWorkflow,
    AIRepositoryTestRun,
    AuditEvent,
)

URL = "/v1/ai/repository/mcp/catalog"


def test_catalog_schema_tracks_real_requests() -> None:
    catalog = build_mcp_catalog(Settings())
    tools = {tool.name: tool for tool in catalog.tools}
    assert len(tools) == 9
    assert list(tools) == sorted(tools)
    assert catalog.invocation_enabled is False
    models = {
        "repository.patch.propose": PatchProposalCreate,
        "repository.patch.apply": PatchApproval,
        "repository.patch.rollback": PatchRollback,
        "repository.test.request": RunRequest,
        "repository.test.approve": RunApproval,
        "repository.workflow.create": PatchWorkflowCreate,
    }
    for name, model in models.items():
        actual = tools[name].inputSchema
        expected = model.model_json_schema()
        assert actual["additionalProperties"] is False
        assert actual["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        for field, schema in expected["properties"].items():
            assert actual["properties"][field] == schema  # type: ignore[index]
            assert field in actual["required"]  # type: ignore[operator]
        if "$defs" in expected:
            assert actual["$defs"] == expected["$defs"]
    apply_properties = tools["repository.patch.apply"].inputSchema["properties"]
    assert apply_properties["proposal_id"]["format"] == "uuid"  # type: ignore[index]
    assert apply_properties["confirmation"]["const"] == "APPLY EXACT PATCH"  # type: ignore[index]


@pytest.mark.parametrize(
    "patch,test,expected", [(False, True, False), (True, False, False), (True, True, True)]
)
def test_flags_report_eligibility_not_invocation(patch: bool, test: bool, expected: bool) -> None:
    catalog = build_mcp_catalog(Settings(ai_patch_tools_enabled=patch, ai_test_tools_enabled=test))
    tool = next(item for item in catalog.tools if item.name == "repository.test.approve")
    assert tool.policy.local_flags_enabled is expected
    assert len(tool.policy.required_flags) == 2
    assert catalog.invocation_enabled is False


def test_discovery_is_read_only_without_secret_or_host_path_values(
    client: TestClient,
    auth_headers: dict[str, str],
    tmp_path: Path,
) -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(
        repository_root=str(tmp_path),
        ai_patch_tools_enabled=True,
        ai_test_tools_enabled=True,
    )
    source = tmp_path / "untouched.txt"
    source.write_text("unchanged", encoding="utf-8")
    session = next(app.dependency_overrides[get_session]())
    tables = [AIRepositoryPatchProposal, AIRepositoryPatchWorkflow, AIRepositoryTestRun, AuditEvent]
    before = [session.scalar(select(func.count()).select_from(table)) for table in tables]
    first = client.get(URL, headers=auth_headers)
    assert first.status_code == 200
    assert first.headers["Cache-Control"] == "no-store"
    assert first.json() == client.get(URL, headers=auth_headers).json()
    assert first.json()["invocation_enabled"] is False
    assert str(tmp_path) not in first.text
    assert "atlas-test-token" not in first.text
    assert (
        client.post(URL, headers=auth_headers, json={"name": "repository.patch.apply"}).status_code
        == 405
    )
    assert (
        client.post(
            "/v1/ai/repository/mcp/call",
            headers=auth_headers,
            json={"name": "repository.patch.apply"},
        ).status_code
        == 404
    )
    assert source.read_text(encoding="utf-8") == "unchanged"
    assert [session.scalar(select(func.count()).select_from(table)) for table in tables] == before
    session.close()


@pytest.mark.parametrize(
    "slug,roles,status", [("northstar", ("reader",), 403), ("unknown", ("owner",), 404)]
)
def test_discovery_requires_owned_organization(
    client: TestClient,
    slug: str,
    roles: tuple[str, ...],
    status: int,
) -> None:
    app.dependency_overrides[require_principal] = lambda: Principal("inspector", slug, roles)
    assert client.get(URL).status_code == status


def test_catalog_requires_authentication_and_local_environment(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    assert client.get(URL).status_code == 401
    app.dependency_overrides[get_settings] = lambda: Settings(environment="production")
    assert client.get(URL, headers=auth_headers).status_code == 503


def test_catalog_has_no_instance_evidence() -> None:
    payload = json.loads(build_mcp_catalog(Settings()).model_dump_json())
    assert payload["mode"] == "catalog-only"
    assert all(tool["policy"]["required_role"] == "owner" for tool in payload["tools"])
    assert all(
        not tool["policy"]["local_flags_enabled"]
        for tool in payload["tools"]
        if tool["policy"]["rest_method"] == "POST"
    )


def test_catalog_references_existing_rest_routes() -> None:
    # Discovery is useful only when every source-owned descriptor names a real API.
    routes = app.openapi()["paths"]
    for tool in build_mcp_catalog(Settings()).tools:
        assert tool.policy.rest_method.lower() in routes[tool.policy.rest_path]


def test_catalog_read_telemetry_counts_only_authorized_reads(
    client: TestClient, auth_headers: dict[str, str],
) -> None:
    before = MCP_CATALOG_READS._value.get()
    assert client.get(URL).status_code == 401
    assert MCP_CATALOG_READS._value.get() == before
    assert client.get(URL, headers=auth_headers).status_code == 200
    assert MCP_CATALOG_READS._value.get() == before + 1
