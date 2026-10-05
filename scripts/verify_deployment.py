"""Execute real Helm lint/template and compare the owned deployment contract.

No cluster access is required or attempted. --write deliberately regenerates the
checked-in JSON observation; normal verification rejects drift without changing
source. Only the fixed atlas release and atlas-dev namespace are rendered.
"""

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

import yaml

from atlas_api.deployment_policy import review

ROOT = Path(__file__).resolve().parents[1]


def verify(write: bool = False) -> None:
    portable = ROOT / ".tools/helm-4.3.0/windows-amd64/helm.exe"
    helm = str(portable) if os.name == "nt" and portable.is_file() else shutil.which("helm")
    if not helm:
        raise RuntimeError("Helm 4.3.0 is required; see deployment-review runbook")
    chart = str(ROOT / "infra/helm/atlas")
    version = subprocess.run([helm, "version", "--short"], check=True,
                             capture_output=True, text=True, timeout=10).stdout.strip()
    if not version.startswith("v4.3.0+"):
        raise RuntimeError("Use the verified Helm 4.3.0 toolchain")
    subprocess.run([helm, "lint", chart, "--strict", "--namespace", "atlas-dev"],
                   check=True, timeout=30)
    rendered = subprocess.run([helm, "template", "atlas", chart, "--namespace", "atlas-dev"],
                              check=True, capture_output=True, text=True, timeout=30).stdout
    namespace = yaml.safe_load((ROOT / "infra/kubernetes/namespace.yaml").read_text())
    resources = [namespace, *[item for item in yaml.safe_load_all(rendered) if item is not None]]
    raw = (json.dumps(resources, indent=2, sort_keys=True) + "\n").encode()
    result = review(raw)
    if result.status != "passed":
        raise RuntimeError(result.model_dump_json())
    destination = ROOT / "infra/kubernetes/atlas-dev.json"
    if write:
        destination.write_bytes(raw)
    elif destination.read_bytes() != raw:
        raise RuntimeError("Rendered manifest drift; review and regenerate with --write")
    # The chart's fixed scope must reject overrides before any cluster access.
    for arguments in [["--namespace", "default"], ["--set", "apiImage=malicious:latest"]]:
        attempt = subprocess.run([helm, "template", "atlas", chart, "--namespace", "atlas-dev",
                                  *arguments], capture_output=True, text=True, timeout=30)
        if attempt.returncode == 0:
            raise RuntimeError("Chart accepted an unsupported scope/image override")
    print(f"deployment: Helm {version}; {len(resources)} resources; policy passed; "
          f"digest {result.manifest_digest}; cluster not checked")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    verify(parser.parse_args().write)
