"""Plan scope/privacy/lineage contracts; native lifecycle is a separate CLI gate."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from atlas_api.auth import Principal, require_principal
from atlas_api.config import Settings, get_settings
from atlas_api.infrastructure_plan import (
    PlanReceipt,
    configuration_bytes,
    deployment_input,
    observe_plan,
    project_plan,
)
from atlas_api.main import app

ROOT = Path(__file__).resolve().parents[3]


def fixture_root(tmp_path: Path) -> Path:
    for relative in [
        "infra/terraform/local-budget/main.tf.json",
        "infra/kubernetes/atlas-dev.json",
    ]:
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / relative).read_bytes())
    return tmp_path


def plan_document() -> dict[str, Any]:
    return {
        "format_version": "1.2",
        "terraform_version": "1.13.0",
        "errored": False,
        "resource_changes": [
            {
                "address": "terraform_data.atlas_budget",
                "type": "terraform_data",
                "mode": "managed",
                "provider_name": "terraform.io/builtin/terraform",
                "change": {
                    "actions": ["create"],
                    "after": {"input": deployment_input(ROOT).model_dump(mode="json")},
                    "after_unknown": {"input": {"budget": {"replicas": False}}},
                    "after_sensitive": {"input": {"budget": {}}},
                },
            }
        ],
        "configuration": {
            "root_module": {"resources": [{"address": "terraform_data.atlas_budget"}]}
        },
    }


def test_plan_accepts_known_nested_native_masks_and_noop() -> None:
    document = plan_document()
    assert project_plan(json.dumps(document).encode(), deployment_input(ROOT)) == "create"
    document["resource_changes"][0]["change"]["actions"] = ["no-op"]
    assert project_plan(json.dumps(document).encode(), deployment_input(ROOT)) == "no-op"


@pytest.mark.parametrize(
    "drift",
    [
        "version",
        "format",
        "error",
        "provider",
        "address",
        "extra-resource",
        "module",
        "data",
        "delete",
        "replace",
        "update",
        "input",
        "unknown",
        "sensitive",
        "numeric-mask",
        "provisioner",
        "child-module",
    ],
)
def test_plan_blocks_nonlocal_actions_and_unknown_or_sensitive_input(drift: str) -> None:
    document = plan_document()
    resource = document["resource_changes"][0]
    change = resource["change"]
    if drift == "version":
        document["terraform_version"] = "1.12.6"
    elif drift == "format":
        document["format_version"] = "2.0"
    elif drift == "error":
        document["errored"] = True
    elif drift == "provider":
        resource["provider_name"] = "registry.opentofu.org/hashicorp/aws"
    elif drift == "address":
        resource["address"] = "aws_instance.private"
    elif drift == "extra-resource":
        document["resource_changes"].append(resource.copy())
    elif drift == "module":
        resource["module_address"] = "module.private"
    elif drift == "data":
        resource["mode"] = "data"
    elif drift in {"delete", "replace", "update"}:
        change["actions"] = ["delete", "create"] if drift == "replace" else [drift]
    elif drift == "input":
        change["after"]["input"]["namespace"] = "private"
    elif drift == "unknown":
        change["after_unknown"]["input"]["budget"]["replicas"] = True
    elif drift == "sensitive":
        change["after_sensitive"]["input"]["budget"]["replicas"] = True
    elif drift == "numeric-mask":
        change["after_unknown"]["input"]["budget"]["replicas"] = 0
    elif drift == "provisioner":
        document["configuration"]["root_module"]["resources"][0]["provisioners"] = [
            {"type": "local-exec"}
        ]
    else:
        document["configuration"]["root_module"]["module_calls"] = {"child": {}}
    with pytest.raises(ValueError) as failure:
        project_plan(json.dumps(document).encode(), deployment_input(ROOT))
    assert "private" not in str(failure.value)


def test_plan_size_bound() -> None:
    with pytest.raises(ValueError, match="bound"):
        project_plan(b"x" * 256001, deployment_input(ROOT))


def test_duplicate_configuration_fields_are_rejected_before_native_execution(
    tmp_path: Path,
) -> None:
    root = fixture_root(tmp_path)
    path = root / "infra/terraform/local-budget/main.tf.json"
    source = path.read_bytes()
    path.write_bytes(b'{"terraform":{"backend":{"s3":{}}},' + source[1:])
    with pytest.raises(ValueError, match="duplicate manifest field"):
        configuration_bytes(root)


def test_receipt_missing_current_and_whitespace_source_change(tmp_path: Path) -> None:
    root = fixture_root(tmp_path)
    assert observe_plan(root).receipt is None
    receipt = PlanReceipt(
        configuration_digest=hashlib.sha256(configuration_bytes(root)).hexdigest(),
        plan_digest="a" * 64,
        input=deployment_input(root),
        finished_at=datetime.now(UTC),
    )
    path = root / "artifacts/infrastructure/local-plan.json"
    path.parent.mkdir(parents=True)
    path.write_text(receipt.model_dump_json(), encoding="utf-8")
    assert observe_plan(root).source_current is True
    source = root / "infra/terraform/local-budget/main.tf.json"
    source.write_bytes(source.read_bytes() + b"\n")
    assert observe_plan(root).source_current is False
    path.write_text('{"credential":"private"}', encoding="utf-8")
    with pytest.raises(ValueError):
        observe_plan(root)


@pytest.mark.parametrize("key", ["provider", "module", "data", "backend", "provisioner"])
def test_source_blocks_additional_executable_config_before_tool_use(
    tmp_path: Path, key: str
) -> None:
    root = fixture_root(tmp_path)
    path = root / "infra/terraform/local-budget/main.tf.json"
    source = json.loads(path.read_bytes())
    source[key] = {"private": {}}
    path.write_text(json.dumps(source), encoding="utf-8")
    with pytest.raises(ValueError, match="unsupported IaC configuration"):
        configuration_bytes(root)


@pytest.mark.parametrize(
    "enabled,environment,roles,tenant,status",
    [
        (False, "development", ("owner",), "northstar", 403),
        (True, "production", ("owner",), "northstar", 403),
        (True, "development", ("viewer",), "northstar", 403),
        (True, "development", ("owner",), "other", 403),
        (True, "development", ("owner",), "northstar", 200),
    ],
)
def test_api_opt_in_and_read_only_missing_receipt(
    tmp_path: Path,
    enabled: bool,
    environment: str,
    roles: tuple[str, ...],
    tenant: str,
    status: int,
) -> None:
    root = fixture_root(tmp_path)
    app.dependency_overrides[get_settings] = lambda: Settings(
        infrastructure_plan_enabled=enabled, environment=environment, repository_root=str(root)
    )
    app.dependency_overrides[require_principal] = lambda: Principal("operator", tenant, roles)
    try:
        with TestClient(app) as client:
            response = client.get("/v1/infrastructure/plan")
            assert (
                response.status_code == status and response.headers["cache-control"] == "no-store"
            )
            if status == 200:
                assert response.json()["receipt"] is None
                assert response.json()["source_current"] is None
            assert client.post("/v1/infrastructure/plan").status_code == 405
            assert client.delete("/v1/infrastructure/plan").status_code == 405
    finally:
        app.dependency_overrides.clear()


def test_api_redacts_missing_source_and_requires_auth(tmp_path: Path) -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(
        infrastructure_plan_enabled=True, repository_root=str(tmp_path)
    )
    try:
        with TestClient(app) as client:
            assert client.get("/v1/infrastructure/plan").status_code == 401
            app.dependency_overrides[require_principal] = lambda: Principal(
                "operator", "northstar", ("owner",)
            )
            response = client.get("/v1/infrastructure/plan")
            assert response.status_code == 503
            assert str(tmp_path) not in response.text and "private" not in response.text
            assert response.headers["cache-control"] == "no-store"
    finally:
        app.dependency_overrides.clear()
