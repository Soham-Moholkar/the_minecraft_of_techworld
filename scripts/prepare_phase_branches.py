"""Create isolated current-source phase views without checking out or editing main.

These are extractions, not recovered historical releases. A separate temporary Git
index builds each tree. Local imports and colocated tests are included transitively;
the API composition root mounts only foundation and selected phase routers.
No network, credentials, force pushes or user file deletion occur in this script.
"""

import argparse
import ast
import json
import os
import posixpath
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "soham-moholkar/phase-"
PHASES = [
    ("00-repository-foundation", "Repository foundation", "historical local baseline"),
    ("01-core-ui", "ATLAS Core UI", "historical local baseline"),
    ("02-python-mastery", "Python mastery", "historical local baseline"),
    ("03-full-stack-engineering", "Full-stack engineering", "historical local baseline"),
    ("04-dbms-laboratory", "DBMS laboratory", "historical local baseline"),
    ("05-data-science", "Data science", "historical local baseline"),
    ("06-machine-learning", "Machine learning", "historical local baseline"),
    ("07-deep-learning-applied-ai", "Deep learning and applied AI", "historical local baseline"),
    ("08-llm-ai-engineering", "LLM and AI engineering", "historical local baseline"),
    ("09-agentic-systems", "Agentic systems", "in progress"),
    ("10-data-engineering-apache", "Data engineering and Apache", "in progress"),
    ("11-devops-cloud", "DevOps and cloud", "in progress"),
    ("12-security-devsecops", "Security and DevSecOps", "not started; roadmap reference only"),
    ("13-observability-sre", "Observability and SRE", "not started; roadmap reference only"),
    ("14-distributed-systems-design", "Distributed systems and system design", "not started; roadmap reference only"),
    ("15-capstone-integrations", "Capstone integrations", "not started; roadmap reference only"),
]

# Ownership identifies current feature files, not their original creation dates.
# Shared imports may pull lower or adjacent phase code into a view legitimately.
RULES = [
    (11, r"deployment|infrastructure.plan|infra/(helm|kubernetes|terraform)/|platform.toolchain|PLAT-P11|platform-deployment"),
    (10, r"streaming|lakehouse|iceberg|kafka|airflow|flink|superset|usage.(bi|compute|orchestration|pipeline)|infra/(spark|airflow|flink|superset)/|data.engineering|DATA-P10"),
    (9, r"agent.(memory|mcp|patch|test|workflow)|repository.(patch|mcp)|agent.boundar|AI-P09|0009-|0010-|0011-|infra/agent"),
    (8, r"repository.(ai|retrieval)|ai.operations|ai.engineering|AI-P08|0008-|apps/web/src/app/(api/)?ai/|000[789]_"),
    (7, r"neural|tensorflow|applied.(ai|training|routes)|deep.learning|DL-P07|0007-|0006_applied"),
    (6, r"machine.learning|ml.routes|ML-P06|model.experiment|0006-immutable|000[45]_.*(model|experiment)"),
    (5, r"data.science|dataset|science.quality|DATA-P05|0005-|0003_datasets"),
    (4, r"database|query.plan|concurrency|lock.activity|document.projection|cache.profile|provider.comparison|phase.four|DB-P04|infra/(mariadb|mongodb|redis)/"),
    (3, r"realtime|live.events|full.stack|control.plane.evolution|control.plane.api|FS-P03|WEB-P03|apps/api-node/|packages/contracts/"),
    (2, r"python.mastery|PY-P02|labs/python/python-mastery/"),
    (1, r"apps/web/src/(components|app|data|lib)/|apps/web/public/"),
]
ROUTERS = {"dataset_router": 5, "ml_router": 6, "applied_router": 7,
           "ai_router": 8, "memory_router": 9, "streaming_router": 10,
           "airflow_router": 10, "compute_router": 10, "flink_router": 10,
           "superset_router": 10, "deployment_router": 11, "infrastructure_plan_router": 11}
API = "apps/api-python/src/"
WEB = "apps/web/src/"
MAIN = API + "atlas_api/main.py"


def git(*args: str, env: dict[str, str] | None = None, data: bytes | None = None) -> bytes:
    result = subprocess.run(["git", *args], cwd=ROOT, env=env, input=data,
                            capture_output=True, check=True)
    return result.stdout


def owner(path: str) -> int:
    for number, pattern in RULES:
        if re.search(pattern, path, re.IGNORECASE):
            return number
    return 0


def scoped_main(raw: bytes, phase: int) -> bytes:
    """Retain owned core code/comments; remove unrelated optional router wiring."""
    text = raw.decode()
    for alias, number in ROUTERS.items():
        if number == phase or (phase == 9 and number == 8):
            continue
        text = re.sub(rf"^from atlas_api\.[\w]+ import router as {alias}\r?\n", "", text,
                      flags=re.MULTILINE)
        text = re.sub(rf"^app\.include_router\({alias}\)\r?\n", "", text,
                      flags=re.MULTILINE)
    ast.parse(text)
    return text.encode()


def dependencies(path: str, raw: bytes, files: dict[str, tuple[str, str]]) -> set[str]:
    found: set[str] = set()
    text = raw.decode("utf-8", errors="replace")
    if path.endswith(".py"):
        tree = ast.parse(text)
        for node in ast.walk(tree):
            modules = []
            if isinstance(node, ast.Import):
                modules = [item.name for item in node.names]
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if node.level and path.startswith(API):
                    base = path[len(API):].split("/")[:-node.level]
                    module = ".".join([*base, module]).strip(".")
                modules = [module, *[module + "." + item.name for item in node.names]]
            for module in modules:
                if module.startswith("atlas_api"):
                    base = API + module.replace(".", "/")
                    candidates = [base + ".py", base + "/__init__.py"]
                else:
                    candidates = [posixpath.join(posixpath.dirname(path), module + ".py")]
                found.update(candidate for candidate in candidates if candidate in files)
    if path.endswith((".ts", ".tsx", ".js", ".mjs")):
        for specifier in re.findall(r"(?:from\s*|import\s*\(\s*|import\s*)[\"']([^\"']+)[\"']", text):
            # Next generates this declaration when building; .next is never source.
            if path == "apps/web/next-env.d.ts" and specifier in {
                "./.next/types/routes.d.ts", "./.next/types/root-params.d.ts"
            }:
                continue
            if specifier.startswith("@/"):
                base = WEB + specifier[2:]
            elif specifier.startswith("."):
                base = posixpath.normpath(posixpath.join(posixpath.dirname(path), specifier))
            else:
                continue
            candidates = [base, *[base + suffix for suffix in (".ts", ".tsx", ".json", ".js")],
                          base + "/index.ts", base + "/index.tsx"]
            resolved = [item for item in candidates if item in files]
            if not resolved:
                raise ValueError(f"Unresolved local import: {path}: {specifier}")
            found.update(resolved)
    return found


def prepare(source: str, create: bool) -> list[dict[str, object]]:
    source_sha = git("rev-parse", source).decode().strip()
    entries = git("ls-tree", "-r", "-z", source_sha).split(b"\0")
    files = {}
    for entry in entries:
        if not entry:
            continue
        metadata, name = entry.decode().split("\t", 1)
        mode, kind, sha = metadata.split()
        if kind != "blob" or mode == "120000" or name.startswith(("~/", "output/")):
            raise ValueError("Unexpected non-source Git entry")
        files[name] = (mode, sha)
    # One binary-safe batch avoids hundreds of process launches on Windows.
    batch = git("cat-file", "--batch", data="".join(v[1] + "\n" for v in files.values()).encode())
    cache = {}
    offset = 0
    for path, (_, sha) in files.items():
        end = batch.index(b"\n", offset)
        header_sha, kind, size_text = batch[offset:end].decode().split()
        size = int(size_text)
        if header_sha != sha or kind != "blob" or size > 5_000_000:
            raise ValueError("Unexpected source blob")
        offset = end + 1
        cache[path] = batch[offset:offset + size]
        offset += size + 1
    common = {path for path in files if path in {
        ".gitignore", ".editorconfig", "AGENTS.md", "package.json", "pnpm-workspace.yaml",
        "pnpm-lock.yaml", "docs/phase-branches.md"} or path.startswith("atlas_codex_context_v4/")}
    # Bootstrap files remain current shared dependencies; full CI/runtime inventory
    # belongs to main and must not certify an extracted tree accidentally.
    bootstrap = {path for path in files if (
        path.startswith("apps/api-python/") and "/src/" not in path and "/tests/" not in path
        and "/alembic/versions/" not in path and not path.endswith("Dockerfile")
    ) or (path.startswith("apps/web/") and "/src/" not in path and "/public/" not in path
          and not path.endswith("Dockerfile"))}
    bootstrap |= {MAIN, API + "atlas_api/__init__.py", API + "atlas_api/py.typed",
                  "apps/api-python/tests/conftest.py", "apps/web/src/test/setup.ts",
                  "apps/web/src/test/server-only.ts", ".env.example",
                  WEB + "app/layout.tsx", WEB + "app/page.tsx", WEB + "app/globals.css",
                  WEB + "app/api/health/route.ts", WEB + "app/api/projects/route.ts",
                  WEB + "app/api/audit/route.ts", WEB + "app/api/session/route.ts"}
    output = []
    for number, (slug, title, status) in enumerate(PHASES):
        feature = {path for path in files if owner(path) == number}
        feature -= common | bootstrap
        # Integration indexes, composite CI, checkpoints and global audit commands
        # describe main. Each view gets its own explicit manifest instead.
        excluded = {"README.md", "CHECKPOINT.md", "ATLAS_FULL_CONTEXT_V4.md",
                    "compose.yaml", "scripts/prepare_phase_branches.py"}
        excluded |= {p for p in files if p.startswith((".atlas/", ".github/", "registry/"))}
        if number == 0:
            feature -= {p for p in files if p.startswith(("docs/", "scripts/", "provenance/",
                                                         "security/", "work/", "packages/"))}
        selected = (common | feature | bootstrap) - excluded if number < 12 else common
        selected &= files.keys()
        overrides = {MAIN: scoped_main(cache[MAIN], number)} if number < 12 else {}
        pending = list(selected)
        while pending:
            path = pending.pop()
            needs = dependencies(path, overrides.get(path, cache[path]), files)
            if path.endswith(".py") and path.startswith(API):
                needs.add(API + "atlas_api/__init__.py")
            if path.endswith((".tsx", ".ts")) and not path.endswith((".test.tsx", ".test.ts")):
                stem = path.rsplit(".", 1)[0]
                needs |= {p for p in (stem + ".test.ts", stem + ".test.tsx") if p in files}
            for dep in needs - selected:
                selected.add(dep)
                pending.append(dep)
        if number >= 12:
            feature = set()
        branch = PREFIX + slug
        manifest = {"schema_version": 1, "phase": number, "title": title,
                    "status": status, "branch": branch, "source_commit": source_sha,
                    "kind": "current-source-extraction" if number < 12 else "roadmap-reference",
                    "historical_release": False,
                    "feature_files": sorted(feature & selected),
                    "shared_dependencies": sorted(selected - feature),
                    "adapted_files": list(overrides),
                    "validation": "local import closure and Python syntax; main quality evidence does not certify this view"}
        readme = (f"# ATLAS — Phase {number:02}: {title}\n\n"
                  f"Branch: `{branch}`. Status: **{status}**.\n\n"
                  f"This is a {'current source extraction' if number < 12 else 'roadmap reference'} "
                  f"from integration commit `{source_sha}`. It is not a historical release. "
                  "The complete integrated application and its checkpoint are on `main`.\n\n"
                  "`PHASE_SCOPE.json` lists this phase's source and transitive shared dependencies. "
                  "Shared current models/contracts may contain fields used by adjacent phases. "
                  "Optional API router wiring is limited to the selected phase and core. "
                  "These source views are for studying and developing phase code; integrate changes "
                  "on main file by file rather than merging a subset tree.\n\n"
                  "Import closure and Python syntax are checked for each extraction. Full runtime, "
                  "frontend build and phase acceptance are not implied by a branch existing. "
                  "Read the authoritative roadmap for remaining acceptance.\n\n"
                  + ("No implementation is published for this future phase. Its branch contains "
                     "the authoritative roadmap and instructions only.\n\n" if number >= 12 else
                     "API environment: `python -m pip install -e './apps/api-python[data,dev]'`. "
                     "Some phase tests require optional frameworks/streaming/lakehouse extras and "
                     "native runtimes described in their runbooks. Frontend: "
                     "`pnpm install --frozen-lockfile`, then run the selected component tests.\n\n")
                  + "See [all phase branches](docs/phase-branches.md).\n")
        for path in selected:
            if path.endswith(".py"):
                ast.parse(overrides.get(path, cache[path]).decode(), filename=path)
        # No UI snapshot from the integration tree is reused as branch certification.
        quality = WEB + "data/quality-snapshot.json"
        if quality in selected:
            snapshot = json.loads(cache[quality])
            snapshot["revision"] = source_sha
            for gate in snapshot["gates"]:
                gate.update(status="not_run", duration_ms=0, exit_code=None, checked_at=None)
            snapshot["summary"] = {"total": len(snapshot["gates"]), "passed": 0,
                                   "failed": 0, "not_run": len(snapshot["gates"])}
            overrides[quality] = json.dumps(snapshot, indent=2).encode()
        if create:
            if subprocess.run(["git", "show-ref", "--verify", "--quiet", "refs/heads/" + branch],
                              cwd=ROOT).returncode == 0:
                raise ValueError(f"Branch already exists: {branch}")
            with tempfile.TemporaryDirectory(prefix="atlas-phase-index-") as directory:
                env = os.environ.copy()
                env["GIT_INDEX_FILE"] = str(Path(directory) / "index")
                git("read-tree", "--empty", env=env)
                records = []
                for path in sorted(selected):
                    mode, sha = files[path]
                    if path in overrides:
                        sha = git("hash-object", "-w", "--stdin", data=overrides[path]).decode().strip()
                    records.append(f"{mode} {sha}\t{path}\0")
                for path, data in {"README.md": readme.encode(),
                                   "PHASE_SCOPE.json": json.dumps(manifest, indent=2).encode()}.items():
                    sha = git("hash-object", "-w", "--stdin", data=data).decode().strip()
                    records.append(f"100644 {sha}\t{path}\0")
                git("update-index", "-z", "--index-info", env=env, data="".join(records).encode())
                tree = git("write-tree", env=env).decode().strip()
                commit = git("commit-tree", tree, "-p", source_sha,
                             "-m", f"Extract phase {number:02}: {title}").decode().strip()
                git("update-ref", "refs/heads/" + branch, commit, "0" * 40)
        output.append({"branch": branch, "phase": number, "files": len(selected) + 2,
                       "feature_files": len(feature & selected), "status": status})
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="main")
    parser.add_argument("--create", action="store_true", help="Create local branches after validation")
    args = parser.parse_args()
    print(json.dumps(prepare(args.source, args.create), indent=2))
