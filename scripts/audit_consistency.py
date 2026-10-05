"""Fail on drift between registry, progress, displayed levels and source locations.

YAML is loaded as data only. This gate does not certify runtime availability or
infer completion from file existence; it checks claims already made by metadata.
"""

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def audit() -> None:
    manifests = [ROOT / "compose.yaml", *sorted((ROOT / "infra").glob("*/compose.yaml"))]
    for manifest in manifests:
        services = yaml.safe_load(manifest.read_text(encoding="utf-8"))["services"]
        for service in services.values():
            for port in service.get("ports", []):
                assert isinstance(port, str) and port.startswith("127.0.0.1:"), (
                    f"development service published outside loopback: {manifest.name}"
                )
    technologies = yaml.safe_load(
        (ROOT / "registry/technologies.yaml").read_text(encoding="utf-8")
    )["technologies"]
    products = yaml.safe_load(
        (ROOT / "registry/products.yaml").read_text(encoding="utf-8")
    )["products"]
    for entries in (technologies, products):
        ids = [entry["id"] for entry in entries]
        assert len(ids) == len(set(ids)), "duplicate registry identifier"
        for entry in entries:
            paths = entry.get(
                "locations", entry.get("integration", {}).get("locations", [])
            )
            paths += entry.get("progression", {}).get("source", [])
            for path in paths:
                assert (ROOT / path).exists(), f"{entry['id']}: missing {path}"
    levels = {
        entry["id"]: entry["progression"]["max_implemented_level"]
        for entry in technologies
        if "progression" in entry
    }
    progress = json.loads((ROOT / ".atlas/progress.json").read_text(encoding="utf-8"))[
        "implemented_progression_max"
    ]
    for key, value in progress.items():
        assert key in levels, f"unknown progress identifier: {key}"
        assert levels[key] == value, f"progression drift: {key}"
    source = (ROOT / "apps/web/src/data/platform.ts").read_text(encoding="utf-8")
    displayed = re.findall(
        r'"?id"?:\s*"([a-z0-9-]+)"[^\n]*?"?implemented"?:\s*(\d+)', source
    )
    assert displayed, "no displayed progression rows found"
    for key, level in displayed:
        assert key in levels, f"displayed technology lacks registry progression: {key}"
        assert levels[key] == int(level), f"displayed level drift: {key}"
    for parent in (ROOT / "apps/web/src/app").rglob("*"):
        if parent.is_dir():
            dynamic = [
                child.name
                for child in parent.iterdir()
                if child.is_dir()
                and child.name.startswith("[")
                and not child.name.startswith(("[...", "[[..."))
            ]
            assert len(dynamic) <= 1, f"conflicting route parameter names: {parent}"
    references = re.findall(r'"?(?:paths|tests)"?:\s*(\[[^\]]*\])', source)
    for values in references:
        for value in json.loads(values):
            first = value.split(" ", 1)[0]
            if first.startswith(("apps/", "labs/", "docs/", "output/", "scripts/")):
                assert (ROOT / first).exists(), (
                    f"missing displayed source/test: {first}"
                )
    print(
        f"consistency: {len(technologies)} technologies, "
        f"{len(products)} products, {len(displayed)} displayed levels"
    )


if __name__ == "__main__":
    audit()
