"""Native OpenTofu lifecycle in an owned fixture; publish a redacted plan receipt.

Only the independently allowlisted builtin configuration is copied. No providers,
modules, provisioners, remote backends, user tfvars, CLI credentials or cloud
environment are passed to the tool. apply/destroy below affect only disposable
terraform_data metadata; they never deploy a cluster or cloud resource.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from atlas_api.infrastructure_plan import (
    PlanReceipt,
    configuration_bytes,
    deployment_input,
    project_plan,
)

ROOT = Path(__file__).resolve().parents[1]


class PlanEngine(Protocol):
    def plan(self) -> tuple[bytes, bytes]:
        """Return a saved local plan and machine-readable observation."""
        ...


class NativeOpenTofu:
    """Source-owned operator adapter, never imported by the HTTP composition root."""

    def __init__(self, fixture: Path) -> None:
        portable = ROOT / ".tools/opentofu-1.13.0/tofu.exe"
        executable = str(portable) if os.name == "nt" else shutil.which("tofu")
        if not executable or not Path(executable).is_file():
            raise RuntimeError("Official checksum-verified OpenTofu 1.13.0 is required")
        self.executable = executable
        self.fixture = fixture
        # No TF_VAR/TF_CLI_ARGS, proxy credentials, cloud keys or user CLI config.
        # Do not mutate system/user environment or PATH; only this child is scoped.
        allowed = {"SYSTEMROOT", "WINDIR", "PATH", "TEMP", "TMP", "LANG", "LC_ALL"}
        self.env = {key: value for key, value in os.environ.items() if key.upper() in allowed}
        cli = fixture / "owned.tfrc"
        cli.write_text("disable_checkpoint = true\n", encoding="utf-8")
        self.env.update(TF_CLI_CONFIG_FILE=str(cli), TF_IN_AUTOMATION="true", TF_INPUT="false")
        version = json.loads(self.run(["version", "-json"]))
        if version.get("terraform_version") != "1.13.0":
            raise RuntimeError("Unexpected native toolchain version")

    def run(self, arguments: list[str], allowed_codes: tuple[int, ...] = (0,)) -> bytes:
        result = subprocess.run([self.executable, *arguments], cwd=self.fixture, env=self.env,
                                capture_output=True, timeout=30)
        if len(result.stdout) + len(result.stderr) > 256_000:
            raise RuntimeError("Native tool output bound")
        if result.returncode not in allowed_codes:
            # Plans can contain cleartext values: do not print raw tool failures.
            raise RuntimeError("Native local plan command failed: " + arguments[0])
        return result.stdout

    def plan(self) -> tuple[bytes, bytes]:
        self.run(["plan", "-input=false", "-no-color", "-detailed-exitcode", "-out=plan.bin",
                  "-lock-timeout=2s", "-parallelism=1"], (0, 2))
        raw = self.run(["show", "-json", "plan.bin"])
        path = self.fixture / "plan.bin"
        if path.stat().st_size > 256_000:
            raise RuntimeError("Native binary plan bound")
        return path.read_bytes(), raw


def verify(publish: bool = False) -> None:
    source = configuration_bytes(ROOT)
    input_value = deployment_input(ROOT)
    fixture_root = ROOT / "artifacts/plan-fixtures"
    fixture_root.mkdir(parents=True, exist_ok=True)
    if fixture_root.resolve() != fixture_root:
        raise ValueError("fixture root redirection")
    receipt = None
    # TemporaryDirectory owns a unique resolved child beneath artifacts. Cleanup
    # removes only this fixture, never the operator's other state or credentials.
    with tempfile.TemporaryDirectory(prefix="atlas-plan-", dir=fixture_root) as directory:
        fixture = Path(directory)
        (fixture / "main.tf.json").write_bytes(source)
        variables = fixture / "deployment.auto.tfvars.json"
        variables.write_text(json.dumps({"deployment": input_value.model_dump(mode="json")}),
                             encoding="utf-8")
        native = NativeOpenTofu(fixture)
        native.run(["init", "-input=false", "-no-color"])
        native.run(["validate", "-no-color"])
        engine: PlanEngine = native
        binary, raw = engine.plan()
        if project_plan(raw, input_value) != "create":
            raise ValueError("fresh local fixture did not plan one metadata creation")
        receipt = PlanReceipt(configuration_digest=hashlib.sha256(source).hexdigest(),
                              plan_digest=hashlib.sha256(binary).hexdigest(), input=input_value,
                              finished_at=datetime.now(UTC))
        # Verify real state/idempotence only after whole source and plan validation.
        native.run(["apply", "-input=false", "-no-color", "plan.bin"])
        _, unchanged = engine.plan()
        if project_plan(unchanged, input_value) != "no-op":
            raise ValueError("local metadata lifecycle is not idempotent")
        forbidden = input_value.model_dump(mode="json")
        forbidden["budget"]["cpu_limit_millicores"] = 2001
        variables.write_text(json.dumps({"deployment": forbidden}), encoding="utf-8")
        attempt = subprocess.run([native.executable, "plan", "-input=false", "-no-color"],
                                 cwd=fixture, env=native.env, capture_output=True, timeout=30)
        if attempt.returncode == 0:
            raise ValueError("native precondition failed to block the resource budget")
        variables.write_text(json.dumps({"deployment": input_value.model_dump(mode="json")}),
                             encoding="utf-8")
        native.run(["destroy", "-auto-approve", "-input=false", "-no-color", "-parallelism=1"])
        state = json.loads(native.run(["show", "-json"]))
        if state.get("values", {}).get("root_module", {}).get("resources"):
            raise ValueError("owned metadata teardown left resources")
    if configuration_bytes(ROOT) != source or deployment_input(ROOT) != input_value:
        raise ValueError("source changed during native verification")
    if publish:
        destination = ROOT / "artifacts/infrastructure/local-plan.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.parent.resolve() != destination.parent or destination.is_symlink():
            raise ValueError("receipt destination redirection")
        with tempfile.NamedTemporaryFile(dir=destination.parent, suffix=".json", delete=False) as tmp:
            temporary = Path(tmp.name)
            tmp.write(receipt.model_dump_json(indent=2).encode())
        try:
            temporary.replace(destination)
        finally:
            temporary.unlink(missing_ok=True)
    print("local IaC: OpenTofu 1.13.0; create=1, noop after apply; over-budget blocked; "
          "owned metadata teardown/fixture cleanup passed; no cloud resources")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true")
    verify(parser.parse_args().publish)
