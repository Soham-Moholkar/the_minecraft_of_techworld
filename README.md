# ATLAS

ATLAS is a production-style, polyglot enterprise technology platform. The
application is real; the repository is the mastery environment.

The complete integrated code is on `main`. See [phase branches](docs/phase-branches.md)
for isolated current source views, branch names and the status of unfinished phases.

## Run the core profile

Prerequisites: Node 22+, pnpm 10+, Python 3.12+, and optionally Docker.

```powershell
Copy-Item .env.example .env
pnpm install
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".\apps\api-python[data,dev]"
docker compose up -d postgres
.\.venv\Scripts\python -m alembic -c apps/api-python/alembic.ini upgrade head
.\.venv\Scripts\python -m atlas_api.seed
```

Run the API and web app in separate terminals:

```powershell
.\.venv\Scripts\python -m uvicorn atlas_api.main:app --app-dir apps/api-python/src --reload
pnpm dev
```

Open http://localhost:3000. The OpenAPI document is at
http://localhost:8000/docs and Prometheus metrics are at
http://localhost:8000/metrics.

For a zero-service API run, omit `ATLAS_DATABASE_URL`; SQLite is used locally.
See [the usage guide](docs/runbooks/using-atlas.md),
[the architecture](docs/architecture/platform.md), [the current checkpoint](CHECKPOINT.md),
and [the technology registry](registry/technologies.yaml).

## Optional deep-learning comparison

The Models workspace compares CPU PyTorch and TensorFlow/Keras with the existing
classical baselines. Enable the optional image and rebuild:

```powershell
$env:ATLAS_NEURAL = "true"
docker compose up -d --build api web
```

For local Python dependencies and the resettable lab, see
[labs/deep-learning/framework-comparison](labs/deep-learning/framework-comparison/README.md).
Phase 7's completed applied workflows are recorded in
[ATLAS-DL-P07](work/ai/ATLAS-DL-P07.md).

## Repository code intelligence

`/ai/repository` lists the curated source snapshot and renders exact code lines
beside structured explanations. Set `ATLAS_OPENAI_API_KEY` in `.env`, then restart
the API. Auto mode uses `gpt-5.6-luna` for economical explanations and
`gpt-5.6-terra` for reviews/change plans. The models are configurable through the
two `ATLAS_AI_*_MODEL` variables; callers cannot submit arbitrary model IDs.

The explanation and retrieval path remains read-only: models cannot run code or access
filesystem tools. Phase 9 adds a separate local-operator patch review workflow. Enable
it only for a trusted local checkout with `ATLAS_AI_PATCH_TOOLS_ENABLED=true` while
running the API natively. The Compose image intentionally does not forward this flag:
its `/workspace` is an image snapshot, not the host checkout. ATLAS
generates the diff from current repository bytes, binds approval to its exact digest and
source hash, applies a bounded allowlisted replacement atomically, audits the lifecycle,
and permits hash-safe rollback. It cannot use Git, create or delete files, commit, push,
install dependencies, or deploy. Never enable this mode
on a public/shared deployment. See [ADR 0008](docs/adr/0008-cost-aware-repository-intelligence.md)
and [ADR 0009](docs/adr/0009-local-human-approved-patch-workflow.md).

The Phase 9 workflow option persists each typed change plan and its deterministic
`submitted → validating → awaiting approval` timeline. Policy failures and source
conflicts remain visible evidence. The workflow cannot apply its own proposal: the exact
diff still requires the separate human approval action.
Its source-owned conditional graph now identifies each validation outcome and the
approval needed for a privileged edge. The operator can replay a version-pinned,
policy-verified event history in the workflow panel; replay is read-only and never
starts a tool. Existing runs are pinned to graph version 1 by migration 0014.

The same page now includes a local MCP contract explorer: filter nine source-owned
tool contracts and inspect input JSON Schema, scope, owner role, approval requirements,
source/REST locations and flag eligibility. It works with patch/test flags disabled and
never invokes a tool. This is a catalog-only inspection adapter, not an MCP server or
remote connection. See [ADR 0010](docs/adr/0010-local-mcp-contract-discovery.md).

Operator memory on this page stores up to 50 bounded tenant notes with provenance
and 1/7/30-day expiry (default 7). Review the no-secrets/no-approvals attestation before
saving. Notes never enter model context automatically or grant tool authority. Expiry
hides notes immediately; the next save or **Remove expired memory** physically removes
expired rows. Explicit deletion requires a second confirmation. Audit retains lifecycle
metadata only; backups/database pages may retain earlier copies. Secret detection is
best-effort, not DLP. Apply migration 0015 before use; see
[ADR 0011](docs/adr/0011-operator-managed-agent-memory.md).

Candidate tests are a second opt-in boundary. Build the fixed worker image with
`docker build -f apps/api-python/Dockerfile.test-worker -t atlas-api-test-worker:local .`,
set `ATLAS_AI_TEST_TOOLS_ENABLED=true`, and run
`python -m atlas_api.agent_test_worker` beside the native API. The operator first
requests a source-defined profile and then approves its immutable run digest. The worker
stages the candidate without changing the checkout and uses a read-only, non-root Docker
container with no network, capabilities, privilege escalation, or secret-bearing host
environment; CPU, memory, PIDs, time and output are bounded. There is no host fallback.
Passing tests only persist evidence and never approve or apply the patch.

When a proposal belongs to a deterministic workflow, test lifecycle events are appended
to that workflow timeline without changing its authority state. If a worker heartbeat
expires, the run becomes `interrupted`. The recovery action creates a new attempt with
fresh lineage and a new digest; it does not reuse or replay the earlier approval.

To use an operator-managed OpenAI-compatible local runtime instead, set
`ATLAS_LOCAL_AI_ENABLED=true`, `ATLAS_LOCAL_AI_BASE_URL`, and
`ATLAS_LOCAL_AI_MODEL`. The UI compares redacted provider readiness and streams
either provider through the same validated contract. Base URLs and keys never
come from browser input.

Owners can save the current instruction as an immutable tenant prompt version and
reuse it in later streamed runs. Each revision is audited; inline drafts are not
persisted.

The same workspace can search the allowlisted repository through bounded
overlapping chunks and deterministic hybrid ranking. Results include exact file,
line and SHA-256 citations plus untrusted-instruction warnings. Owners can run a
fixed grounding, citation-integrity and prompt-injection regression suite; ATLAS
stores the immutable tenant-scoped evaluation report, not repository snippets or
queries.

Hosted calls are admitted through a durable monthly tenant budget reservation and
settled to actual token cost. Configure the limit and conservative per-run floor
with `ATLAS_AI_MONTHLY_BUDGET_USD` and `ATLAS_AI_RUN_RESERVATION_USD`. Auto mode
can fall back to the explicitly enabled local adapter only before output starts;
explicit provider choices never fall back. The workspace reports remaining
budget, retrieval cache evidence, and the rolling availability/p95 SLO window.
# Phase 10 usage streaming

`/streaming` operates bounded tenant-owned counters with durable consumer lag,
quarantine and replay-safe effects. Optional Kafka, Arrow/Parquet export and local
Iceberg snapshots use separate opt-ins. See [usage streaming runbook](docs/runbooks/usage-streaming.md).
Phase 10 remains in progress; live Kafka, distributed processing, orchestration
and Superset are not certified complete.

The `/pipelines` workspace now reads a fixed tenant-bound Airflow DAG's actual run
and task status. Its manual usage DAG invokes bounded API tasks for consume,
Parquet validation and local Iceberg refresh. Native task-chain tests pass; live
scheduler and container acceptance remain pending. See the
[orchestration runbook](docs/runbooks/usage-orchestration.md) and
[past-phase audit](docs/phase-audit-2026-10-03.md).

The same workspace observes actual Spark receipts, fixed-job Flink status and
tenant-bound Superset publication metadata through independently enabled adapters.
Local JVM Spark acceptance passes, including Parquet aggregation and stale-source
detection. Linux standalone/Flink/Superset acceptance remains pending. Read the
[compute runbook](docs/runbooks/usage-compute.md) and
[BI runbook](docs/runbooks/usage-bi.md) for operator commands and exact boundaries.

The pipeline canvas connects source-defined stages to independently observed
streaming/compute evidence. Selecting stages and refreshing it only reads state.
Test Center retains each gate's original check time; for frontend-only edits,
`node scripts/quality-snapshot.mjs data-engineering --refresh-web` reruns registry
and web gates while preserving other checks and their dates. A full profile is
required when backend, worker or lab behavior changes.

# Phase 11 Infrastructure deployment review

`/infrastructure` now observes the owned Helm-rendered development deployment,
checks its complete security/scope/resource contract, calculates pod budgets and
shows a data-preserving manual teardown plan. Enable the independent local opt-in
`ATLAS_DEPLOYMENT_REVIEW_ENABLED=true` on the API. The web BFF keeps owner credentials
server-side. Existing runtime source inventory remains available below the review.

`python scripts/verify_deployment.py` runs real Helm 4.3.0 lint/template and rejects
artifact drift and unsupported overrides; `bash scripts/deployment-preflight.sh`
provides the same read-only operator/CI entry point. The fresh
`node scripts/quality-snapshot.mjs platform` profile includes native Helm, existing
data-engineering checks and the complete local API/frontend gates. Live provider
gates remain unrun until the corresponding runtimes are available. For web-only
changes use that same profile with `--refresh-web` to preserve backend check dates.

See the [deployment runbook](docs/runbooks/deployment-review.md) and
[ADR 0016](docs/adr/0016-owned-development-deployment-review.md). Phase 11 is in
progress; live Kubernetes scheduling/CNI/PVC acceptance, Terraform/Ansible and
cloud comparison remain unfinished. Starting it does not certify Phase 9 or 10.

The Infrastructure workspace also observes actual OpenTofu 1.13.0 local budget
plans. `python scripts/verify_infrastructure_plan.py --publish` verifies a
builtin-only create/no-op/budget-rejection/owned-teardown lifecycle and publishes
a small source-bound receipt. Enable `ATLAS_INFRASTRUCTURE_PLAN_ENABLED=true`
independently for the owner-only read API. This state baseline is a disposable
local fixture; cloud resources, raw plans and credentials are not served. See the
[local-plan runbook](docs/runbooks/local-infrastructure-plan.md) and
[ADR 0017](docs/adr/0017-local-infrastructure-plan-receipts.md).
