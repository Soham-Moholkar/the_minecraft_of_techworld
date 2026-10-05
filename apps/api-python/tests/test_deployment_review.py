"""Native manifest and hostile-drift regressions; no mock cluster health claims."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from atlas_api.auth import Principal, require_principal
from atlas_api.config import Settings, get_settings
from atlas_api.deployment_policy import expected_resources, read_manifest, review
from atlas_api.main import app

ROOT = Path(__file__).resolve().parents[3]


def test_actual_rendered_source_budget_and_retained_data() -> None:
    result = review(read_manifest(ROOT))
    assert result.status == "passed" and result.cluster_status == "not_checked"
    assert result.budget is not None
    assert result.budget.cpu_request_millicores == 350
    assert result.budget.cpu_limit_millicores == 2000
    assert result.budget.memory_request_mib == 768
    assert result.budget.memory_limit_mib == 1536
    assert result.budget.storage_mib == 1024 and result.budget.replicas == 2
    assert len(result.resources) == 11
    assert len(result.teardown) == 9
    for command in result.teardown:
        assert "--context kind-atlas --namespace atlas-dev delete" in command
        assert "persistentvolumeclaim" not in command and "delete namespace" not in command
        assert "secret" not in command and "--all" not in command


@pytest.mark.parametrize(
    "drift",
    [
        "public-service",
        "inline-token",
        "host-network",
        "privileged",
        "automount",
        "root",
        "host-volume",
        "sidecar",
        "network-egress",
        "cpu-budget",
        "replicas",
        "probe",
        "scope",
        "retention",
        "unknown-kind",
        "duplicate",
        "missing",
        "numeric-bool",
    ],
)
def test_policy_blocks_every_unsupported_field_and_withholds_plan(drift: str) -> None:
    objects = expected_resources()
    deployment = next(item for item in objects if item["kind"] == "Deployment")
    pod = deployment["spec"]["template"]["spec"]
    container = pod["containers"][0]
    if drift == "public-service":
        next(item for item in objects if item["kind"] == "Service")["spec"]["type"] = "LoadBalancer"
    elif drift == "inline-token":
        container["env"].append({"name": "SECRET", "value": "must-never-be-returned"})
    elif drift == "host-network":
        pod["hostNetwork"] = True
    elif drift == "privileged":
        container["securityContext"]["privileged"] = True
    elif drift == "automount":
        pod["automountServiceAccountToken"] = True
    elif drift == "root":
        pod["securityContext"]["runAsUser"] = 0
    elif drift == "host-volume":
        pod["volumes"].append({"name": "host", "hostPath": {"path": "/"}})
    elif drift == "sidecar":
        pod["containers"].append({"name": "unexpected", "image": "unknown"})
    elif drift == "network-egress":
        next(item for item in objects if item["kind"] == "NetworkPolicy")["spec"]["egress"] = [{}]
    elif drift == "cpu-budget":
        container["resources"]["limits"]["cpu"] = "999999m"
    elif drift == "replicas":
        deployment["spec"]["replicas"] = 2
    elif drift == "probe":
        del container["readinessProbe"]
    elif drift == "scope":
        deployment["metadata"]["namespace"] = "kube-system"
    elif drift == "retention":
        objects[2]["metadata"]["annotations"] = {}
    elif drift == "unknown-kind":
        objects.append({"kind": "ClusterRole", "metadata": {"name": "must-never-be-returned"}})
    elif drift == "duplicate":
        objects.append(objects[1])
    elif drift == "missing":
        objects.pop()
    else:
        pod["automountServiceAccountToken"] = 0
    result = review(json.dumps(objects).encode())
    assert result.status == "blocked" and result.findings
    assert result.budget is None and result.teardown == []
    assert "must-never-be-returned" not in result.model_dump_json()


@pytest.mark.parametrize(
    "raw",
    [b"x" * 256001, b"{}", b"[null]" * 100, b"[" + b"{}," * 32 + b"{}]"],
    ids=["oversize", "object", "invalid-json", "too-many-resources"],
)
def test_manifest_bounds_and_structure(raw: bytes) -> None:
    with pytest.raises(ValueError):
        review(raw)


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
def test_api_authority_and_read_only_surface(
    enabled: bool, environment: str, roles: tuple[str, ...], tenant: str, status: int
) -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(
        deployment_review_enabled=enabled, environment=environment, repository_root=str(ROOT)
    )
    app.dependency_overrides[require_principal] = lambda: Principal("operator", tenant, roles)
    try:
        with TestClient(app) as client:
            response = client.get("/v1/infrastructure/deployment")
            assert response.status_code == status
            assert response.headers["cache-control"] == "no-store"
            if status == 200:
                assert response.json()["cluster_status"] == "not_checked"
            for method in [client.post, client.delete]:
                assert method("/v1/infrastructure/deployment").status_code == 405
    finally:
        app.dependency_overrides.clear()


def test_api_missing_manifest_redacts_paths(tmp_path: Path) -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(
        deployment_review_enabled=True, repository_root=str(tmp_path)
    )
    app.dependency_overrides[require_principal] = lambda: Principal(
        "operator", "northstar", ("owner",)
    )
    try:
        with TestClient(app) as client:
            response = client.get("/v1/infrastructure/deployment")
            assert response.status_code == 503
            assert str(tmp_path) not in response.text
            assert response.headers["cache-control"] == "no-store"
    finally:
        app.dependency_overrides.clear()


def test_api_requires_authentication() -> None:
    with TestClient(app) as client:
        assert client.get("/v1/infrastructure/deployment").status_code == 401


def test_duplicate_json_fields_fail_closed() -> None:
    with pytest.raises(ValueError, match="duplicate manifest field"):
        review(b'[{"kind":"Secret","kind":"Namespace"}]')


def test_reader_caps_actual_file_growth(tmp_path: Path) -> None:
    path = tmp_path / "infra/kubernetes/atlas-dev.json"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"x" * 256001)
    with pytest.raises(ValueError, match="manifest bound"):
        read_manifest(tmp_path)


def test_teardown_stops_writers_before_removing_policies() -> None:
    commands = review(read_manifest(ROOT)).teardown
    assert all("delete deployment" in command for command in commands[:2])
    assert "delete serviceaccount" in commands[-1]
