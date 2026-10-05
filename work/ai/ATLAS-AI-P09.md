# ATLAS-AI-P09 — Agentic systems

Status: in progress. Owner: AI Platform. Roadmap: Phase 9.

Completed first vertical slice: an opt-in local operator patch workflow with a separate
guarded filesystem adapter, immutable tenant proposal evidence, server-generated unified
diffs, exact-digest approval, current-source hash binding, bounded allowlisted writes,
Python/JSON syntax validation, atomic replacement, post-write verification, hash-safe
rollback, lifecycle audit events, Prometheus counters, same-origin BFF routes, and an
accessible review UI.

Completed deterministic workflow slice: tenant-scoped workflow runs persist the typed
objective and plan, append state-transition evidence, validate through the same guarded
gateway, and stop at `awaiting_approval`. Failed policy checks and source conflicts are
durable outcomes. Patch application and rollback synchronize the workflow, while the
state graph rejects any transition that skips validation or human review. The UI exposes
the state timeline beside the exact diff.

Security boundary: the model still receives no tool. Proposal output is untrusted data;
only the operator can authorize the exact server-derived digest. Shell, tests, Git,
network, package installation, new files, deletion, commit, push, and deployment remain
out of scope. Remote and multi-user use is explicitly unsupported.

Completed isolated-test slice: a second opt-in creates digest-bound test requests for
versioned, source-owned profiles. Separate approval queues durable work for a local
worker that stages the candidate and requires a non-root, networkless, read-only Docker
container with fixed argv/environment/cwd and bounded time, CPU, memory, swap, PIDs and
output. Cancellation, heartbeats, interrupted-run recovery, audit events, metrics,
bounded output evidence, BFF contracts and operator UI are included. Docker absence
fails closed; passing tests never apply, commit, push or deploy.

Completed workflow-evidence and recovery slice: linked workflows append test request,
queue, start, cancellation and terminal evidence without changing workflow authority.
Interrupted runs expose an explicit retry action that creates immutable parent/attempt
lineage, a new run ID and a new digest, then stops at `pending_approval`. The old record
and approval are never reused. Migration 0013, API/BFF contracts, UI lineage, audit,
security tests and migration round-trip evidence are included.

Completed conditional graph/replay slice: versioned source-owned policy defines typed
nodes, a single guarded proposal tool, observed branch conditions and separate
authorities on patch and rollback edges. Live routing and read-only replay use the same
graph. Replay verifies each persisted event before the operator can step through it;
tampered or incompatible histories fail closed. Migration 0014 pins existing workflow
runs to graph version 1. API/BFF/UI, branch/security tests and a migration round-trip
are included.

Completed MCP discovery slice: a local owner-only GET catalog derives nine tool input
schemas from the real request models and exposes scope, exact approval requirements,
REST/source locations and local flag eligibility. The API/BFF/UI enforce catalog-only
mode and literal disabled invocation, render inert schema text, redact failures and
emit read telemetry. No dispatcher, transport, arbitrary server URL, new dependency,
file read or persistent side effect was added. See ADR 0010 and the discovery tests.

Completed operator-memory slice: migration 0015 persists local owner/tenant notes with
provenance, bounded input, database-enforced 50-slot quota and 1/7/30-day expiry.
Expired notes are hidden on reads/open-page timers; saves or explicit cleanup physically
remove expired tenant rows. Deliberate deletion and content-free transactional audit,
best-effort secret/approval rejection, fixed-label telemetry, no-store BFF contracts,
UI lifecycle/security tests and a SQLite migration round-trip are included. Notes remain
untrusted operator data: no automatic model context, prompt selection or tool authority.
See ADR 0011 for backup/idle-retention limitations.

Completed resettable agent-security exercise: real memory persistence, tenant
isolation, expiry and content-free audit; seven rejected credential/approval/workflow
attempts; separate test-digest queue approval without tool execution. `run.py test`
re-executes the actual policy instead of trusting saved evidence. Local and CI gates
include the manifest/lifecycle. Broader multi-agent behavior and MCP transport remain
incomplete; this exercise does not certify live isolated worker execution.
