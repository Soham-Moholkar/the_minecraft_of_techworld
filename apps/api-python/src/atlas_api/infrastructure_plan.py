"""Fixed local IaC plan projection and source-bound receipt observation.

OpenTofu runs only in the separate operator script. HTTP cannot invoke a tool,
select providers, upload a plan, apply state or access cloud credentials. Plan
JSON can contain cleartext secrets: only a small numeric projection is persisted.
"""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import Field

from atlas_api.deployment_policy import (
    BudgetRead,
    ContractModel,
    read_manifest,
    review,
    unique_json,
)

VERSION = "1.13.0"
ADDRESS = "terraform_data.atlas_budget"
PROVIDER = "terraform.io/builtin/terraform"


def owned_configuration() -> dict[str, Any]:
    """Whole-configuration allowlist prevents modules/data/provisioners/backends."""
    return {
        "terraform": {"required_version": "= 1.13.0"},
        "variable": {"deployment": {"type": "any"}},
        "resource": {
            "terraform_data": {
                "atlas_budget": {
                    "input": "${var.deployment}",
                    "lifecycle": {
                        "precondition": [
                            {
                                "condition": '${var.deployment.namespace == "atlas-dev" && '
                                "var.deployment.budget.replicas == 2 && "
                                "var.deployment.budget.cpu_limit_millicores <= 2000 && "
                                "var.deployment.budget.memory_limit_mib <= 1536 && "
                                "var.deployment.budget.storage_mib <= 1024}",
                                "error_message": "Owned development deployment budget exceeded.",
                            }
                        ]
                    },
                }
            }
        },
        "output": {"planned_budget": {"value": "${terraform_data.atlas_budget.output}"}},
    }


def read_fixed(root: Path, relative: str, limit: int = 64_000) -> bytes:
    """Internal callers supply source-owned paths; reject directory redirection."""
    root = root.resolve(strict=True)
    path = root / relative
    if path.resolve(strict=True) != path or not path.is_file():
        raise ValueError("plan path")
    with path.open("rb") as source:
        raw = source.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("plan bound")
    return raw


def configuration_bytes(root: Path) -> bytes:
    raw = read_fixed(root, "infra/terraform/local-budget/main.tf.json")
    if json.dumps(unique_json(raw), sort_keys=True) != json.dumps(
        owned_configuration(), sort_keys=True
    ):
        raise ValueError("unsupported IaC configuration")
    # The operator script copies only this one checked file into its fixture.
    # Additional checkout files are not executable inputs to that isolated run.
    return raw


class PlanInput(ContractModel):
    namespace: Literal["atlas-dev"]
    manifest_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    budget: BudgetRead


class PlanReceipt(ContractModel):
    schema_version: Literal[1] = 1
    engine: Literal["opentofu"] = "opentofu"
    engine_version: Literal["1.13.0"] = "1.13.0"
    scope: Literal["local-metadata"] = "local-metadata"
    state_baseline: Literal["empty-disposable-fixture"] = "empty-disposable-fixture"
    created: Literal[1] = 1
    changed: Literal[0] = 0
    destroyed: Literal[0] = 0
    configuration_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    plan_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    input: PlanInput
    finished_at: datetime


class PlanObservation(ContractModel):
    checked_at: datetime
    source_current: bool | None
    receipt: PlanReceipt | None


def deployment_input(root: Path) -> PlanInput:
    manifest = review(read_manifest(root))
    if manifest.status != "passed" or manifest.budget is None:
        raise ValueError("deployment policy blocked")
    return PlanInput(
        namespace="atlas-dev", manifest_digest=manifest.manifest_digest, budget=manifest.budget
    )


def project_plan(raw: bytes, expected: PlanInput) -> Literal["create", "no-op"]:
    """Accept one known builtin resource and fully known, non-sensitive input."""
    if len(raw) > 256_000:
        raise ValueError("plan response bound")
    value = unique_json(raw)
    if (
        not str(value.get("format_version", "")).startswith("1.")
        or value.get("terraform_version") != VERSION
        or value.get("errored", False)
    ):
        raise ValueError("plan format/version/error")
    changes = value.get("resource_changes", [])
    if len(changes) != 1:
        raise ValueError("plan resource count")
    resource = changes[0]
    if (
        resource.get("address") != ADDRESS
        or resource.get("type") != "terraform_data"
        or resource.get("mode") != "managed"
        or resource.get("provider_name") != PROVIDER
        or "module_address" in resource
        or "index" in resource
        or "deposed" in resource
    ):
        raise ValueError("plan provider/scope")
    change = resource["change"]
    actions = change["actions"]
    if actions not in [["create"], ["no-op"]]:
        raise ValueError("plan action denied")
    if json.dumps(change["after"]["input"], sort_keys=True) != json.dumps(
        expected.model_dump(mode="json"), sort_keys=True
    ):
        raise ValueError("plan input mismatch")

    # The native format represents nested object masks as maps of false leaves,
    # not only a scalar false. Do not treat a numeric zero as a boolean marker.
    def all_known(value: Any) -> bool:
        if value is None or value is False:
            return True
        if isinstance(value, dict):
            return all(all_known(item) for item in value.values())
        if isinstance(value, list):
            return all(all_known(item) for item in value)
        return False

    if not all_known(change.get("after_unknown", {}).get("input")):
        raise ValueError("unknown plan input")
    if not all_known(change.get("after_sensitive", {}).get("input")):
        raise ValueError("sensitive plan input")
    configuration = value.get("configuration", {})
    root_module = configuration.get("root_module", {})
    configured = root_module.get("resources", [])
    if (
        root_module.get("module_calls")
        or len(configured) != 1
        or configured[0].get("address") != ADDRESS
        or configured[0].get("provisioners")
    ):
        raise ValueError("plan configuration scope")
    return "create" if actions == ["create"] else "no-op"


def observe_plan(root: Path) -> PlanObservation:
    root = root.resolve(strict=True)
    source = configuration_bytes(root)
    current = deployment_input(root)
    path = root / "artifacts/infrastructure/local-plan.json"
    receipt = None
    source_current = None
    if path.exists():
        raw = read_fixed(root, "artifacts/infrastructure/local-plan.json", 16_000)
        unique_json(raw)
        receipt = PlanReceipt.model_validate_json(raw, strict=True)
        source_current = (
            receipt.configuration_digest == hashlib.sha256(source).hexdigest()
            and receipt.input == current
        )
    return PlanObservation(
        checked_at=datetime.now(UTC), source_current=source_current, receipt=receipt
    )
