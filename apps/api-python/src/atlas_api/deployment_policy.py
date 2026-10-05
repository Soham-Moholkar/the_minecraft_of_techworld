"""Offline review of the owned ATLAS development deployment.

This deliberately narrow policy recognizes one topology, rather than pretending
to be a general Kubernetes admission controller. Every resource and field must
match the source-owned contract. Unknown objects/fields fail closed, so an added
sidecar, RBAC grant, credential, host mount or public service cannot slip through
checks limited to a few familiar fields. No cluster client or subprocess lives
in this service. Editing the chart requires reviewing this independent contract.
"""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

NAMESPACE: Literal["atlas-dev"] = "atlas-dev"
LABELS = {"app.kubernetes.io/managed-by": "atlas", "atlas.dev/tenant": "northstar"}
MAX_BYTES = 256_000
KEEP = {"helm.sh/resource-policy": "keep"}


def expected_resources() -> list[dict[str, Any]]:
    """Independent deployment contract, also used by executable policy regressions."""

    def resource(kind: str, name: str, spec: dict[str, Any]) -> dict[str, Any]:
        version = {"Deployment": "apps/v1", "NetworkPolicy": "networking.k8s.io/v1"}
        metadata: dict[str, Any] = {"name": name, "labels": LABELS.copy()}
        if kind != "Namespace":
            metadata["namespace"] = NAMESPACE
        if kind in {"Namespace", "PersistentVolumeClaim"}:
            metadata["annotations"] = KEEP.copy()
        return {"apiVersion": version.get(kind, "v1"), "kind": kind, "metadata": metadata, **spec}

    objects = [
        resource("Namespace", NAMESPACE, {}),
        resource("ServiceAccount", "atlas-runtime", {"automountServiceAccountToken": False}),
        resource(
            "PersistentVolumeClaim",
            "atlas-data",
            {
                "spec": {
                    "accessModes": ["ReadWriteOnce"],
                    "resources": {"requests": {"storage": "1Gi"}},
                }
            },
        ),
        resource(
            "ResourceQuota",
            "atlas-budget",
            {
                "spec": {
                    "hard": {
                        "requests.cpu": "1",
                        "limits.cpu": "2",
                        "requests.memory": "1Gi",
                        "limits.memory": "2Gi",
                        "requests.storage": "1Gi",
                        "persistentvolumeclaims": "1",
                        "pods": "2",
                        "services": "2",
                    }
                }
            },
        ),
    ]
    # Namespace admission is defense in depth. Enforcement and CNI behavior still
    # need acceptance against an actual, independently versioned local cluster.
    objects[0]["metadata"]["labels"]["pod-security.kubernetes.io/enforce"] = "restricted"
    for component, port, memory, cpu, path in [
        ("api", 8000, "512Mi", "250m", "/health"),
        ("web", 3000, "256Mi", "100m", "/"),
    ]:
        selector = {"app.kubernetes.io/name": "atlas-" + component}
        secret = {"name": "atlas-operator", "key": "dev-token"}
        env: list[dict[str, Any]] = [
            {"name": "ATLAS_DEV_TOKEN", "valueFrom": {"secretKeyRef": secret}}
        ]
        if component == "api":
            values = {
                "ATLAS_DATABASE_URL": "sqlite:////var/lib/atlas/atlas.db",
                "ATLAS_REPOSITORY_ROOT": "/workspace",
                "ATLAS_DEPLOYMENT_REVIEW_ENABLED": "true",
                "ATLAS_STREAMING_STORE": "/var/lib/atlas/streaming.db",
            }
        else:
            values = {
                "ATLAS_API_URL": "http://atlas-api:8000",
                "HOSTNAME": "0.0.0.0",  # noqa: S104 - private ClusterIP, no host port
                "PORT": "3000",
                "ATLAS_ALLOWED_ORIGINS": "http://localhost:3000",
            }
        env.extend({"name": key, "value": value} for key, value in values.items())
        mounts = [{"name": "tmp", "mountPath": "/tmp"}]  # noqa: S108 - bounded private emptyDir
        volumes: list[dict[str, Any]] = [{"name": "tmp", "emptyDir": {"sizeLimit": "64Mi"}}]
        if component == "api":
            mounts.append({"name": "data", "mountPath": "/var/lib/atlas"})
            volumes.append({"name": "data", "persistentVolumeClaim": {"claimName": "atlas-data"}})
        else:
            mounts.append({"name": "cache", "mountPath": "/app/apps/web/.next/cache"})
            volumes.append({"name": "cache", "emptyDir": {"sizeLimit": "64Mi"}})
        probe = {
            "httpGet": {"path": path, "port": port},
            "timeoutSeconds": 2,
            "periodSeconds": 10,
            "failureThreshold": 3,
        }
        objects.append(
            resource(
                "Deployment",
                "atlas-" + component,
                {
                    "spec": {
                        "replicas": 1,
                        "strategy": {"type": "Recreate"},
                        "selector": {"matchLabels": selector},
                        "template": {
                            "metadata": {"labels": {**LABELS, **selector}},
                            "spec": {
                                "serviceAccountName": "atlas-runtime",
                                "automountServiceAccountToken": False,
                                "securityContext": {
                                    "runAsNonRoot": True,
                                    "runAsUser": 10001,
                                    "runAsGroup": 10001,
                                    "fsGroup": 10001,
                                    "seccompProfile": {"type": "RuntimeDefault"},
                                },
                                "containers": [
                                    {
                                        "name": component,
                                        "image": "atlas-" + component + ":local",
                                        "imagePullPolicy": "Never",
                                        "ports": [{"containerPort": port}],
                                        "env": env,
                                        "volumeMounts": mounts,
                                        "securityContext": {
                                            "allowPrivilegeEscalation": False,
                                            "readOnlyRootFilesystem": True,
                                            "capabilities": {"drop": ["ALL"]},
                                        },
                                        "resources": {
                                            "requests": {"cpu": cpu, "memory": memory},
                                            "limits": {
                                                "cpu": "1000m",
                                                "memory": "1Gi" if component == "api" else "512Mi",
                                            },
                                        },
                                        "readinessProbe": probe.copy(),
                                        "livenessProbe": probe.copy(),
                                        "startupProbe": {**probe, "failureThreshold": 60},
                                    }
                                ],
                                "volumes": volumes,
                            },
                        },
                    }
                },
            )
        )
        objects.append(
            resource(
                "Service",
                "atlas-" + component,
                {
                    "spec": {
                        "type": "ClusterIP",
                        "selector": selector,
                        "ports": [{"name": "http", "port": port, "targetPort": port}],
                    }
                },
            )
        )
    objects.append(
        resource(
            "NetworkPolicy",
            "atlas-deny",
            {
                "spec": {
                    "podSelector": {},
                    "policyTypes": ["Ingress", "Egress"],
                    "ingress": [],
                    "egress": [],
                }
            },
        )
    )
    web_selector = {"matchLabels": {"app.kubernetes.io/name": "atlas-web"}}
    api_selector = {"matchLabels": {"app.kubernetes.io/name": "atlas-api"}}
    dns = {
        "to": [
            {
                "namespaceSelector": {
                    "matchLabels": {"kubernetes.io/metadata.name": "kube-system"}
                },
                "podSelector": {"matchLabels": {"k8s-app": "kube-dns"}},
            }
        ],
        "ports": [{"protocol": "UDP", "port": 53}, {"protocol": "TCP", "port": 53}],
    }
    objects.extend(
        [
            resource(
                "NetworkPolicy",
                "atlas-web-egress",
                {
                    "spec": {
                        "podSelector": web_selector,
                        "policyTypes": ["Egress"],
                        "egress": [
                            dns,
                            {
                                "to": [{"podSelector": api_selector}],
                                "ports": [{"protocol": "TCP", "port": 8000}],
                            },
                        ],
                    }
                },
            ),
            resource(
                "NetworkPolicy",
                "atlas-api-ingress",
                {
                    "spec": {
                        "podSelector": api_selector,
                        "policyTypes": ["Ingress"],
                        "ingress": [
                            {
                                "from": [{"podSelector": web_selector}],
                                "ports": [{"protocol": "TCP", "port": 8000}],
                            }
                        ],
                    }
                },
            ),
        ]
    )
    return objects


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class ResourceRead(ContractModel):
    kind: str
    name: str
    retained: bool
    matches_contract: bool


class Finding(ContractModel):
    code: Literal["resource-contract", "inventory-contract"]
    message: str


class BudgetRead(ContractModel):
    cpu_request_millicores: int
    cpu_limit_millicores: int
    memory_request_mib: int
    memory_limit_mib: int
    storage_mib: int
    replicas: int


class DeploymentReview(ContractModel):
    namespace: Literal["atlas-dev"] = NAMESPACE
    release: Literal["atlas"] = "atlas"
    checked_at: datetime
    manifest_digest: str
    status: Literal["passed", "blocked"]
    cluster_status: Literal["not_checked"] = "not_checked"
    resources: list[ResourceRead]
    findings: list[Finding]
    budget: BudgetRead | None
    teardown: list[str]
    retained: list[str]


def unique_json(raw: bytes) -> Any:
    """Avoid different interpreters resolving duplicate JSON fields differently."""

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("duplicate manifest field")
            value[key] = item
        return value

    return json.loads(raw, object_pairs_hook=unique_object)


def review(raw: bytes) -> DeploymentReview:
    """Bound and project fixed resources; never echo unknown manifest content."""
    if len(raw) > MAX_BYTES:
        raise ValueError("manifest bound")
    objects = unique_json(raw)
    if not isinstance(objects, list) or len(objects) > 32:
        raise ValueError("manifest inventory bound")
    expected = expected_resources()
    known = {(item["kind"], item["metadata"]["name"]): item for item in expected}
    observed: dict[tuple[str, str], Any] = {}
    invalid = False
    for item in objects:
        if not isinstance(item, dict) or not isinstance(item.get("metadata"), dict):
            invalid = True
            continue
        kind, name = item.get("kind"), item["metadata"].get("name")
        if not isinstance(kind, str) or not isinstance(name, str):
            invalid = True
            continue
        key = (kind, name)
        if key not in known or key in observed:
            invalid = True
        observed[key] = item
    findings = []
    if invalid or set(observed) != set(known):
        findings.append(
            Finding(code="inventory-contract", message="Unknown, duplicate or missing resources.")
        )
    resources = []
    for key, item in known.items():
        # Canonical JSON distinguishes true from 1, unlike Python dict equality.
        matches = json.dumps(observed.get(key), sort_keys=True) == json.dumps(item, sort_keys=True)
        retained = key[0] in {"Namespace", "PersistentVolumeClaim"}
        resources.append(
            ResourceRead(kind=key[0], name=key[1], retained=retained, matches_contract=matches)
        )
        if not matches:
            findings.append(
                Finding(
                    code="resource-contract",
                    message=f"Review {key[0]} {key[1]} against the owned policy.",
                )
            )
    passed = not findings
    # Totals are only reported for the exact validated topology. Recreate avoids
    # unbudgeted surge pods, and SQLite must never have multiple API writers.
    budget = None
    if passed:
        workloads = [item["spec"] for item in objects if item["kind"] == "Deployment"]

        def total(bucket: str, dimension: str) -> int:
            result = 0
            for workload in workloads:
                for container in workload["template"]["spec"]["containers"]:
                    quantity = container["resources"][bucket][dimension]
                    multiplier = 1024 if quantity.endswith("Gi") else 1
                    number = quantity.removesuffix("Gi").removesuffix("Mi").removesuffix("m")
                    result += int(number) * multiplier * workload["replicas"]
            return result

        pvc = next(item for item in objects if item["kind"] == "PersistentVolumeClaim")
        storage = int(pvc["spec"]["resources"]["requests"]["storage"].removesuffix("Gi")) * 1024
        budget = BudgetRead(
            cpu_request_millicores=total("requests", "cpu"),
            cpu_limit_millicores=total("limits", "cpu"),
            memory_request_mib=total("requests", "memory"),
            memory_limit_mib=total("limits", "memory"),
            storage_mib=storage,
            replicas=sum(item["replicas"] for item in workloads),
        )
    teardown = (
        [
            f"kubectl --context kind-atlas --namespace atlas-dev delete {key[0].lower()} {key[1]}"
            for key in sorted(
                known,
                key=lambda key: {
                    "Deployment": 0,
                    "Service": 1,
                    "NetworkPolicy": 2,
                    "ResourceQuota": 3,
                    "ServiceAccount": 4,
                }.get(key[0], 5),
            )
            if key[0] not in {"Namespace", "PersistentVolumeClaim"}
        ]
        if passed
        else []
    )
    return DeploymentReview(
        checked_at=datetime.now(UTC),
        manifest_digest=hashlib.sha256(raw).hexdigest(),
        status="passed" if passed else "blocked",
        resources=resources,
        findings=findings,
        budget=budget,
        teardown=teardown,
        retained=[
            "Namespace atlas-dev",
            "PersistentVolumeClaim atlas-data",
            "External Secret atlas-operator",
            "Helm release metadata",
        ],
    )


def read_manifest(root: Path) -> bytes:
    """Reject redirected files; the operator selects only the repository root."""
    root = root.resolve(strict=True)
    path = root / "infra/kubernetes/atlas-dev.json"
    if path.resolve(strict=True) != path or not path.is_file():
        raise ValueError("manifest path")
    # Incremental cap also handles concurrent growth after stat. A shared root
    # is an operator boundary, not protection against a hostile OS administrator.
    with path.open("rb") as source:
        raw = source.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("manifest bound")
    return raw
