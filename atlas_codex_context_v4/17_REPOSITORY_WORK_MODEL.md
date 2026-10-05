# 17 — Repository Work Model: Tickets, Refactors and Inherited-Code Experience

## Goal

ATLAS should feel like a mature repository inherited from a real engineering organization.

The learner should receive work, not only explanations.

## Backlog

```text
work/
├── backlog/
├── bugs/
├── performance/
├── security/
├── migrations/
├── refactors/
├── features/
├── reliability/
├── data/
├── ai/
├── infrastructure/
└── completed/
```

Each work item can include:

- id
- title
- context
- affected services
- symptoms
- acceptance criteria
- non-goals
- tests expected
- security implications
- observability signals
- difficulty
- dependencies
- optional hints
- ADR required?
- rollout plan?
- rollback plan?

## Example work items

- `ATLAS-DB-014`: analytics p95 exceeds 1.5s at 8M events; optimize below 400ms without API change.
- `ATLAS-BE-031`: migrate TypeScript audit service from TypeORM to Drizzle while preserving schema/contracts.
- `ATLAS-PY-022`: migrate a legacy Flask endpoint into FastAPI while preserving auth/rate-limit behavior.
- `ATLAS-JAVA-010`: convert reporting path to a reactive Spring implementation and document tradeoffs.
- `ATLAS-GO-006`: reimplement ingestion gateway in Go and compare CPU/memory/throughput with Python.
- `ATLAS-RS-004`: move CPU-heavy parser to Rust through FFI or service boundary.
- `ATLAS-EVT-019`: implement Pulsar behind the event-bus interface currently using Kafka.
- `ATLAS-DATA-042`: profiling pipeline exhausts memory at 20M rows; redesign with Polars/DuckDB/Spark.
- `ATLAS-ML-028`: improve anomaly-model recall without exceeding false-positive threshold.
- `ATLAS-AI-050`: agent DB tool is over-privileged; add scoped credentials and approvals.
- `ATLAS-SEC-033`: fix broken object authorization and add regression tests.
- `ATLAS-K8S-017`: configure autoscaling/disruption behavior for inference traffic.
- `ATLAS-OBS-011`: trace context is lost across Kafka; fix propagation.
- `ATLAS-IOS-008`: add offline incident notes/conflict resolution.
- `ATLAS-WEB-077`: reduce excessive analytics-grid rerenders.

## Repository realism

Include intentionally:
- legacy modules
- migrations
- deprecations
- TODO/FIXME
- ADRs
- runbooks
- schema migrations
- feature flags
- compatibility layers
- flaky-test history
- postmortems
- old API versions
- deprecated event schemas.

Do not make the repo artificially broken. Complexity should be deliberate and documented.

## Change-and-observe loop

A work item should allow:

1. reproduce behavior,
2. find source,
3. inspect architecture,
4. change code in IDE,
5. run tests,
6. run the real product,
7. observe a measurable/visible change,
8. inspect telemetry,
9. commit/document the decision.

The UI may display work/backlog state, but source editing remains IDE-first.
