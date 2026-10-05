# ATLAS checkpoint — 2026-10-05

## GitHub publication — user authorized 2026-10-05

Published to https://github.com/Soham-Moholkar/the_minecraft_of_techworld.git.
Integrated source commit: 8c76cca9692437b232adcf57893348e68f165ac1. The existing
remote initial commit 1cf471c is preserved; no force push or history replacement.
Main and 16 named phase branches were pushed atomically and all remote object
hashes matched their local refs. Branch names/status are in docs/phase-branches.md.
Phases 0–11 are current source extractions with transitive local imports, colocated
tests, shared bootstrap and scoped optional API router wiring. Each branch has a
PHASE_SCOPE.json and branch README. Phases 12–15 are explicitly unimplemented
roadmap reference trees. There were no historical local phase commits to recover.
Source views are not historical releases; integrate changes file by file on main.

Validation: six extraction regressions, import closure/Python syntax for all
views, actual API import and OpenAPI registration for 12 code trees. Independent
full frontend builds/runtime acceptance of the extracted views are unverified;
their copied quality snapshots are reset to unrun. Main retains its real quality
snapshot. Temporary validation directories were cleaned; current checkout is main.
Generated logs, home link, databases, credentials, dependency/build folders and
portable binaries are excluded from Git. No secrets were found in staged source;
the private-key marker match is an intentional rejection fixture. Native runtime
limitations and incomplete phase status below remain unchanged by publication.
## Current continuation — Phase 11 authoritative state

User moved to Phase 11 and requested resuming from the last limit. Phase 11 is
in progress. Phases 9 and 10 remain unfinished; Phases 0–8 retain their historical
local baselines. Starting a later phase does not certify earlier runtime gates.

Last completed: native OpenTofu local infrastructure plan slice, including fresh
full platform verification, final production rebuild and real browser acceptance.
The first Helm deployment review slice remains verified. Fixed the stale checkpoint,
progress counts and work item that still described completed plan work as next work.

Implemented source: apps/api-python/src/atlas_api/infrastructure_plan.py and
infrastructure_plan_routes.py; scripts/verify_infrastructure_plan.py;
infra/terraform/local-budget/main.tf.json; independent opt-in in config/main/env;
apps/web/src/lib/infrastructure-plan.ts, components/infrastructure-plan-workspace.tsx,
app/api/infrastructure/plan/route.ts and app/infrastructure/page.tsx. Deployment
policy now shares duplicate-key-safe JSON and web budget schema. Quality runner,
CI native job, registry/progression metadata and curated API Docker image inputs
include this slice. ADR 0017, local-infrastructure-plan runbook, threat model,
provenance/platform-toolchain.md and ATLAS-PLAT-P11 record its boundary.
No application migration or deployment was performed in the Phase 11 slice. Subsequent user-authorized Git publication is recorded above.

Native OpenTofu 1.13.0 is official checksum-verified portable Windows tooling under
ignored .tools/opentofu-1.13.0, notices retained, no global PATH change. Whole-source
allowlist permits one builtin terraform_data metadata resource and no provider,
module, data read, provisioner or backend. Isolated child environment and unique
fixture exclude cloud/ATLAS credentials, user CLI config, extra source/tfvars.
Actual init/validate/create plan/apply/no-op plan/over-budget rejection/destroy/empty
state/fixture cleanup pass. Raw plans and state are not published. Only a redacted
atomic receipt persists at artifacts/infrastructure/local-plan.json. API is owner,
development and northstar only, independently opt-in, fixed paths, read-only,
no-store; HTTP cannot run OpenTofu or apply a plan. Fixed-label logs/metrics omit
provider values. Receipt lineage is an unsigned local observation, not live health.

The prior Helm slice owns infra/helm/atlas and a separately retained namespace
under infra/kubernetes. Native Helm 4.3.0 lint/template/schema/unsupported override
and canonical artifact consistency pass, as does actual Git Bash preflight. The
full-object independent policy rejects unknown/duplicate/missing resources,
extra fields, public services, privilege/sidecar/credential/scope/budget/retention
drift and numeric boolean substitution. Eleven resources pass; validated totals
are 350/2000 mCPU, 768/1536 MiB, 1024 MiB retained storage and two replicas.
Teardown is review only and retains namespace/PVC/operator secret/release metadata.
No Kubernetes scheduling, CNI enforcement or storage recovery is certified.

Quality: output/phase11-plan-quality.log completed with 25 passed / 0 failed /
6 not_run across 31 gates. Snapshot schema 2, profile platform, generated
2026-10-04T14:33:41.231Z; preserved check timestamps. Full API: 253 passed,
3 warnings, 324.12s, coverage >=80 gate passed. Frontend: 128 passed / 50 files;
lint, strict types, production build passed. Strict mypy: 51 source files.
Registry consistency: 54 technologies / 27 products / 37 displayed levels.
Focused new slice: 32 API and four web tests; prior Helm slice: 33 API and five web.
Final production rebuild with the completed snapshot passed 2026-10-05:
output/phase11-plan-final-web-build.log. Final script Ruff and native OpenTofu
lifecycle also passed after removing one unused import. Consistency rerun passed.
Six unrun gates: live Kafka, Linux Airflow DagBag and four live databases. Actual
standalone Spark/Flink/Superset and Kubernetes runtime acceptance also remain pending.
Remote Linux CI job execution is unverified.

Real browser acceptance 2026-10-05: saved plan shows one local metadata creation,
zero changes/destroys, original capture time and fresh observation timestamps.
Refresh updates observation. A temporary whitespace source change displays older
lineage; exact byte restoration returns current. Invalid source and actual owned
API stop each cause refresh to clear counts, hashes and timestamps. Independent
Helm review keeps its recorded observation; it is explicitly not live health.
Mobile viewport 390x844 has no document overflow (document width 380, viewport 390),
hashes wrap; viewport reset. Positive console warnings/errors were empty before
intentional 503 cases. Test Center shows 25/31 with original dates and platform
refresh command. Source SHA-256 restored exactly:
68eed8d7da02a37e87d19dd99db7e03f93de3e2e798d862ea4b265d3998af993.

Evidence: output/phase11-plan-browser-proof.png, phase11-plan-older-proof.png,
phase11-plan-mobile-proof.png, phase11-plan-unavailable-proof.png and
phase11-plan-disconnected-proof.png; native/build/quality/API/web logs retained.
All owned loopback API/web processes stopped with PID creation-time checks, unique
phase11-plan-browser test DB and sidecars removed after absolute ownership checks,
temporary browser tab closed. No fixture listeners remain on 58001/58003. No
fixtures remain under artifacts/plan-fixtures. Published plan receipt is retained.
No existing user database, Docker volume or system setting was modified. Approval
service briefly failed due to capacity; recovery succeeded and cleanup completed.

Current runtime check 2026-10-05: docker info still fails on missing
//./pipe/dockerDesktopLinuxEngine. Approved wsl.exe --list --quiet lists only
docker-desktop, not a supported general-purpose Ansible controller. Do not modify
Docker's managed distribution, reset volumes or claim Linux acceptance. No public
or paid infrastructure has been created. The previously untracked source is now committed and published on main, with its
original remote parent preserved; see the publication record above.

Exact next acceptance: restore a supported Docker Linux engine, build owned API/web
images and exercise an isolated kind cluster (admission, namespace/CNI isolation,
quota, PVC recovery and retained-data teardown/reconcile). Next commands:
  docker info --format '{{.ServerVersion}}'
  .venv/Scripts/python.exe scripts/verify_deployment.py
  .venv/Scripts/python.exe scripts/verify_infrastructure_plan.py
Remaining native/product scope: persistent state governance, immutable releases,
Ansible, cloud provider comparison and cost/teardown guards. Preserve existing
interfaces and independent development opt-ins, never route apply through HTTP.
Phase 11 completion and unfinished Phase 9/10 scope are not certified by this slice.

---
## Previous continuation history (superseded; retained evidence)

# ATLAS checkpoint — 2026-10-04

## Current continuation — authoritative state

User requests: complete the current phase, audit/fix inconsistencies in past phases,
and resume where the usage limit interrupted execution. Phase 10 remains in progress;
Phase 9 remains unfinished. Phases 0–8 retain their historical local baseline status.
User subsequently authorized Phase 11 on 2026-10-04. Phase 11 is now in progress; preserve unfinished Phase 9/10 acceptance. Native Infrastructure deployment preflight is the active slice.

### Last completed work and owned files

- Existing usage streaming API/UI, optional Kafka SDK adapter, typed Parquet lineage
  export and local Iceberg snapshots remain verified locally.
- Airflow: owned manual DAG/tasks under infra/airflow, bounded real usage task chain,
  fixed tenant/DAG read-only status API and /pipelines run/dependency/task view.
- Spark: infra/spark/usage_job.py, actual Spark 4.2.0 Parquet/SQL rollup, bounded
  schema/digest/lineage validation, exclusive input lock and atomic numeric receipt;
  usage_compute.py and typed BFF/UI distinguish current, older and missing receipts.
- Flink: infra/flink source-owned Table API batch job, isolated Beam/Arrow graph,
  fixed-job tenant-bound read-only checkpoint/backpressure API/BFF/UI. Deprecated
  samples are unavailable; Linux execution/recovery is unverified.
- Superset: scripts/publish_usage_bi.py aggregate-only SQLite projection, actual
  SQLAlchemy read-only URI tests, configured tenant/dashboard publication metadata
  API/BFF/UI and optional authenticated profile. Publication is not data freshness.
- Operational canvas: usage-pipeline-canvas.tsx and four regressions, source-defined
  topology, interactive stage boundaries, actual lag/retention/accepted counters and
  current/older Spark lineage; independent read-only refresh and cancelled mounts.
- Past-phase audit fixes: real dashboard data and honest development shell/inventory;
  typed/origin-checked bounded BFFs; tenant-safe idempotent seed; normalized Next
  dynamic route names; actual resettable agent-security lab; registry/progression
  corrections; CI extras/runtime gates; loopback Compose ports; named usage volumes;
  curated owned infrastructure source reading with .tools excluded; Docker build
  context excludes .tools/output. See docs/phase-audit-2026-10-03.md.
- Streaming JSON and binary-download BFFs now share incremental byte bounds,
  cancel oversized/error bodies and reject redirects. Four regressions verify
  cancellation, refusal before forwarding and binary/header preservation.
- Test Center displays each gate's original check time, separately from snapshot
  generation. The quality runner supports --retry-failed and --refresh-web without
  promoting unexecuted gates or resetting retained observation times.

Architecture decisions: docs/adr/0012-usage-stream-and-local-lakehouse.md,
0013-source-owned-usage-orchestration.md, 0014-bounded-usage-compute.md and
0015-isolated-usage-bi.md. New ADRs follow the existing docs/adr convention.
No Phase 10 application migration; existing head 0015 remains unchanged.
All source is uncommitted working-tree work. No commit, push or deployment.

### Verification and exact evidence

- Fresh data-engineering profile: output/phase10-final-quality.log. Initial Spark
  teardown and source-reader line-length failures were corrected; explicit recovery
  passed in output/phase10-quality-recovery.log. Teardown terminates only its still-live
  owned Windows process tree; bounded retries cover only transient sharing violations.
- Final registry/web refresh: output/phase10-completion-quality.log — lint, strict
  types, **119 web tests / 46 files**, build and consistency pass. Final production
  rebuild embeds the resulting snapshot: output/phase10-completion-web-build.log.
- Full API suite: **188 passed / 3 warnings** in 178.85s with coverage gate passed;
  detailed prior run output/phase10-api-complete.log records 82.40% coverage and
  321.69s. Aggregate API timeout is 600s; individual framework worker limits unchanged.
- Strict mypy: 47 source files passed. Node REST/GraphQL/gRPC and all selected local
  labs pass. Registry: **51 technologies / 25 products / 34 displayed levels**.
- Snapshot: **23 passed / 0 failed / 6 not_run**, generated 2026-10-04T07:54:57.189Z.
  API gate retains its original 07:27:59.805Z observation; frontend unit gate is
  07:54:07.248Z. Commands/scopes/profile are checked before retained gates are reused.
- Actual local Spark JVM acceptance: 2 rows / 7 units / later-source detection and
  owned process/fixture cleanup pass. Portable checksum-verified Temurin JRE lives
  in ignored .tools with upstream notices; no system Java/PATH change.
- Actual browser: topic lag 1; Spark receipt current at 1 row / 4 units; process the
  queued event via BFF → accepted 2 / units 7 / lag 0; canvas and compute correctly
  show the original receipt as older source. Read-only refresh and disabled providers
  behave correctly. No browser console errors/warnings. Explicit allowed web origin
  is ATLAS_ALLOWED_ORIGINS; a wrongly configured fixture was rejected then corrected.
- Screenshots: output/phase10-canvas-browser-proof.png (viewport),
  output/phase10-canvas-lineage-browser-proof.png (complete lineage view),
  output/phase10-completion-quality-browser-proof.png (original per-gate dates).
  Earlier pipeline/streaming browser proofs and logs remain in output.
- Combined streaming/Airflow/Spark/Flink/Superset Compose config passes. Latest
  unsandboxed docker info still reports missing dockerDesktopLinuxEngine pipe.

### Services, security and remaining work

Owned API 58001 and web 58003 processes/listeners are verified stopped; temporary
browser tabs and named audit-browser/audit-canvas/Spark fixtures are removed.
Screenshots/logs remain. Unrelated processes/stores and Docker volumes were untouched.
Other user service status is unknown. Optional provider flags default false with
blank credentials. Owner/development/tenant guards, fixed provider paths, server-held
credentials, no redirects/proxies, bounded observations, read-only compute/BI mounts
and existing agent approval authority remain intact.

Docker Desktop's Linux backend is unavailable despite earlier approved hidden startup
attempts; no OS reset, volume reset or security bypass was attempted. JRE absence is
no longer a blocker. Native/source foundations are implemented, but actual Linux
Kafka, Airflow, standalone Spark, Flink and Superset acceptance is not certified.

Exact next task: restore a supported Linux Docker engine, then run unique-owned
Kafka acceptance and repair actual integration failures before advancing. First
commands: `docker info --format '{{.ServerVersion}}'`,
`docker compose --profile streaming up -d kafka`,
`.venv/Scripts/python.exe scripts/verify_kafka.py`.
Then follow docs/runbooks/usage-orchestration.md for Linux DagBag/live scheduling,
usage-compute.md for standalone Spark/Flink job/recovery/backpressure and usage-bi.md
for authenticated Superset role/chart/read-only mount/refresh acceptance. Six unrun
snapshot gates are live Kafka, Linux Airflow parse and four database runtime labs;
Superset/Flink/standalone runtime acceptance is additional, explicitly pending work.

Remaining advanced implementation: partition/group coordination, bounded Arrow
input ingestion, remote Iceberg schema/retention/orphan management, richer workflow
editing and distributed traces. Phase 9 still needs broader multi-agent behavior
and MCP transport. Do not label these completed or convert contract mocks to runtime
acceptance. Backend/worker changes require a fresh full profile; frontend-only
changes can run `node scripts/quality-snapshot.mjs data-engineering --refresh-web`.

---
## Previous checkpoint history (superseded; retained historical evidence)

# ATLAS checkpoint — 2026-10-03

## Current continuation: Phase 10 remains in progress

User request: complete the current phase. This run implemented and verified the
usage streaming / Parquet / local Iceberg product slices. Phase 10 is NOT complete;
Phase 9 also remains unfinished. Do not certify the remaining Apache integrations.

### Completed behavior and files

- `/streaming`: real publish/process/refresh, topic lag/checkpoints, quarantine,
  accepted counters, Parquet download and local Iceberg snapshot history.
- `streaming.py`: stable Broker contract, SQLite source/sink, strict schemas,
  transactional identity deduplication, conflict/negative/malformed quarantine,
  tenant/provider namespaces and storage quota. Replay remains possible at quota.
- `kafka_broker.py`: optional actual SDK transport, manual single-partition/group
  offsets, disabled autocommit/autostore/autocreate, retention-gap failure and
  bounded I/O. Sink commits before acknowledgements. Delivery is at-least-once;
  distributed balancing/multiple partitions/exactly-once are NOT implemented.
- `streaming_routes.py`, main/config: owner/development/independent opt-in gates,
  server-selected tenant/topic/path, pre-JSON byte cap, no-store, redacted failures,
  structured logs and fixed-label counters. New standalone tables, no migration
  or modification of the existing developer application database.
- `streaming_export.py`: real typed Arrow/Parquet accepted-sink export with digest
  and embedded lineage; no raw rejected data or arbitrary paths/SQL/uploads.
- `usage_lakehouse.py`, `local_iceberg_io.py`: real local Iceberg SQL catalog,
  bounded full-refresh snapshots, unchanged-content retries, historical reads,
  tenant isolation, canonical URI/Windows long-path handling and remote-I/O denial.
- Web typed contracts/proxy/routes/workspace and UI/BFF tests. Existing shell links
  to streaming. Registry/products/apache/progression/evolution/threat model updated.
- Optional pinned Kafka 4.3.1 Compose profile (loopback, resource bounds), client
  2.15.1, Arrow 25.0.1, PyIceberg 0.12.0; dependency compatibility check passed.
  API optional build extras/config, ADR 0012 and usage-streaming runbook added.
- `scripts/verify_streaming.py`: real runtime smoke + safe unique-fixture cleanup.
  `scripts/verify_kafka.py`: unique-owned topic/group live gate, NOT run against a
  working broker. New data-engineering quality profile requires actual local extras.

### Verification

- `scripts/quality.ps1 -Profile local`: PASS; evidence in
  `output/phase10-local-quality.log`. Web lint/types, 91 tests / 32 files,
  production build (including all streaming routes), API/Node and local labs passed.
- Final API suite: 154 passed / 2 benign Iceberg empty-delete warnings in 45.90s;
  `output/phase10-api-final.log`.
- Latest focused Phase 10 suite: 14 passed; Ruff and strict mypy across 43 files pass.
- Actual local replay→Parquet→Iceberg smoke and cleanup passed;
  `output/phase10-streaming-smoke.log` records 4 units, 1 quarantine, 0 lag,
  1 Parquet row, 1 Iceberg snapshot, unchanged replay.
- Registry: 43 unique technologies, 19 unique products; integration paths exist.
- `docker compose --profile streaming config --quiet`: PASS. Client extras installed
  in repository venv; pip check passed. Live Kafka and container builds NOT verified.
- Initial failures fixed: validation exception redaction, nullable SDK offsets,
  UI effect/fixture cleanup, download-link lint, Windows URI/MAX_PATH and quota replay.
- Restricted final full API run had 18 existing temp-fixture permission errors;
  rerun with approved temp/process access passed all 154 tests. No product workaround.
- No live browser verification or refreshed aggregate snapshot; old Docker-backed
  snapshot gates are not promoted. No commit, push or deploy.

### Runtime and blockers

Docker Desktop was installed but stopped. Starting it hidden was approved and
attempted. Backend processes appeared briefly, then exited; repeated unsandboxed
`docker info` reported absent `dockerDesktopLinuxEngine`. No Compose volumes were
reset by this run. Do not assume services running. Java is not installed on PATH.
Airflow/Superset need supported Linux/WSL/container environments. Native streaming
API/web were not left running. Container stream/catalog stores currently use /tmp
and are disposable; native files are durable until explicitly removed.

### Remaining Phase 10 scope and exact continuation

Live Kafka acceptance; multi-partition/group coordination; Arrow/Parquet ingestion;
Airflow orchestration with real DAG status; Spark/Flink distributed processing and
backpressure/checkpoint views; remote Iceberg/schema/retention/orphan management;
Superset integration; operational DAG/pipeline canvas and distributed traces.
These are actual pending implementation/verification, not completed local substitutes.

Exact next task: restore a usable Docker Linux engine, then run the isolated Kafka
acceptance gate and fix actual SDK/broker issues. In parallel with provider availability,
implement a source-owned Airflow usage-rollup DAG invoking the bounded API and add
DAG/run status contracts/UI with offline tests and Linux integration verification.

Exact next commands (with a healthy engine):
`docker compose --profile streaming up -d kafka`
`.venv/Scripts/python.exe scripts/verify_kafka.py`
Then read `work/data/ATLAS-DATA-P10.md`, `docs/runbooks/usage-streaming.md`, ADR 0012,
and current official Airflow/Spark/Flink/Superset docs before adding dependencies.

---
## Previous checkpoint history (superseded continuation; retained evidence)
# ATLAS checkpoint — 2026-10-03

## Current continuation: Phase 10 started by user request

The user requested the next phase. Phase 10 (data engineering and Apache) is now
in progress. Phase 9 remains unfinished; its security lab described below and
broader multi-agent requirements are not certified complete. Phases 0–8 retain
their prior complete baseline status. ATLAS is not complete.

Implemented the first Phase 10 slice in `labs/data-engineering/event-pipeline`:
real SQLite-backed synthetic usage ingestion, idempotent/conflict-checked event
IDs, tenant/consumer-scoped aggregates, bounded batches, checkpoint/lag summaries,
negative-counter quarantine and transactional pre-commit crash/replay recovery.
The lifecycle produces numeric evidence and removes fixed generated files on
reset. It never touches the application's database or executes model tools.

Added runnable source/tests/manifest/README, catalog and engineering progression
metadata, technology/product registry entries, local and snapshot quality gates,
`docs/evolution/data-engineering.md` and `work/data/ATLAS-DATA-P10.md`. No new
dependency, copied external source, architecture overhaul or application migration.
SQLite local processing does not establish distributed exactly-once semantics.
Kafka, Spark, Airflow, Flink, Iceberg, Arrow/Parquet and Superset remain pending.

Verification so far: 5 pipeline tests, lifecycle/reset, manifest validation,
Ruff and strict pipeline mypy passed; web lint/types and 86 tests passed.
Registry validation: 39 unique technologies, 17 unique products; paths exist.
Web production build passed, including `/labs/durable-event-pipeline`. Full API/local profile and live
browser were not rerun for this isolated lab/catalog change. A first fixture run
failed because sandbox temporary-directory access was denied; workspace-local
test fixtures fixed it and all 5 tests passed. No services were started, no
volumes reset, and no commit/push/deploy. No Docker pipes were found on 2026-10-03.

Exact next task: stable broker provider contract and an optional actual Kafka
provider with bounded tenant-scoped ingestion and API/UI consumer lag, preserving
offline tests. Inspect official maintenance/version/license/security information
before adding dependencies. Do not represent the local provider as Kafka.
Exact next command: read `work/data/ATLAS-DATA-P10.md`,
`docs/evolution/data-engineering.md`, `compose.yaml`, existing API auth/repository
contracts and the local pipeline, then implement the broker seam and API slice.

## Prior Phase 9 checkpoint (retained history)

Phases 0–8 are complete baselines. Phase 9 remains in progress. The exact-diff patch,
persisted workflow, isolated candidate tests, evidence/retry, conditional graph/replay,
local MCP discovery and operator-managed memory slices are complete. ATLAS is not complete.

## Last completed task

Added bounded, tenant-scoped operator memory at /ai/repository:

- Owner-only local-development API supports create/list, explicit confirmed deletion
  and tenant-only expired-note cleanup. No patch/test enablement is required or granted.
- Migration 0015 persists provenance, creator and timestamps. Input limits are 120/2000/240
  characters for title/note/provenance; retention is 1, 7 or 30 days, default 7.
- Unique tenant slots and a 1–50 check enforce quota at the database boundary.
  PostgreSQL parent locks serialize save/cleanup; SQLite conflicts fail closed.
- Expired notes disappear from fresh reads and open-page timers. Physical cleanup runs
  on save or explicit removal, not an unattended daemon. GET does not mutate storage.
- Save/delete/expiry evidence and row mutations commit together; immutable audit retains
  only lifecycle identities/action/actor, never title, text, provenance or content hashes.
- Conservative credential/approval detection plus operator attestation protects the
  persistence boundary. Detection is best-effort, not comprehensive DLP.
- Server-only, no-store BFF routes validate origin, UUID, size and typed contracts and
  redact rejected-input bodies. The UI renders inert text and keeps drafts in memory only.
- Structured logs/fixed-label counters omit note text. Adjacent comments explain quota,
  transactions, privacy, expiry, lifecycle and server/browser separation.

Memory never enters inference, retrieval, workflow authority or the MCP catalog.
automatic_context is literally false across API/BFF/UI. No model receives a tool.
Row deletion is not secure erasure of database pages, logs or backups; the UI/runbook
state this limitation. Public/shared/remote/multi-agent execution remains unsupported.

## Files and architecture decisions

Added agent_memory.py, agent_memory_routes.py, AgentMemory ORM model, migration
20261001_0015_agent_memory.py, API/migration tests, shared server-only BFF contracts/proxy,
memory routes/tests and AgentMemoryWorkspace with UI tests. Integrated API composition
and repository page. Vitest alone aliases the Next server-only marker for route tests;
production compiler enforcement is unchanged. No dependency was added.

Updated ADR 0011, work item ATLAS-AI-P09, registry/products, website progression,
README, runbook, evolution, threat model and progress.

## Database migration

Migration 20261001_0015 adds agent_memories and quota constraints.
A disposable SQLite database passed full upgrade, real memory persistence, downgrade
to 0014 and re-upgrade. No existing developer database or live PostgreSQL was migrated.
Run python -m alembic -c apps/api-python/alembic.ini upgrade head before using the panel.

## Verification

- scripts/quality.ps1 -Profile local: passed (web, API, Node and all local labs).
- Web: lint, strict types, 30 files / 86 tests and production build passed.
- API: Ruff and strict mypy across 37 files passed.
- Focused memory API suite: 20 passed, including migration/privacy/quota/tenant checks.
- Focused memory UI/BFF suite: 15 passed, including open-page expiry.
- Full API final resumed rerun: 140 passed; initial full local quality profile also passed.
- Node: protocol types and 2 tests passed; all local labs passed.
- Registry: 38 unique technologies / 16 unique products; integration paths exist.
- git diff --check: clean for tracked paths; the repository remains untracked/uncommitted.

Initial test fixture issues (DELETE body helper, expired ORM identity refresh, reused
Response body, server-only test resolution) were fixed and reverified. A redundant
final API rerun spanned a runtime suspension and hit the existing training timeout:
139 passed / 1 training timeout after more than a day elapsed. A fresh resumed full
rerun passed all 140 tests in 163 seconds; no unrelated training code was changed.

No live browser was started; DOM tests/build passed, not visual browser verification.
Docker's Linux engine pipe remains absent (checked 2026-10-02). Four
Docker provider gates, live worker execution and PostgreSQL locking remain deferred.
No volumes/data were reset. Services are not assumed running. No commit/push/deploy.

## Exact next task

Continue Phase 9 with a resettable local agent-security lab for memory poisoning,
secret rejection and independent patch/test approval boundaries, with deterministic
evidence surfaced through the existing lab catalog. Do not invoke real tools, expose
services, store credentials, or broaden model/worker/remote/multi-agent authority.

Exact next command: read work/ai/ATLAS-AI-P09.md, inspect the existing lab runner/catalog
and agent security tests, then implement the smallest resettable lab vertical slice.


