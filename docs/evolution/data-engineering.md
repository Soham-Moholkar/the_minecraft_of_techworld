# Data engineering progression

Phase 10 starts with a real local durable usage pipeline, not a distributed stack.
Its SQLite provider is deliberately limited to one machine and a synthetic usage
stream. Subsequent product adapters are listed separately below.

- L0: bounded typed usage events in a durable local source.
- L1: tenant/consumer-scoped usage aggregation with source ID deduplication.
- L2: atomic sink/checkpoint/rejection transactions, bounded batches, consumer lag,
  pre-commit crash recovery and restart/replay regression evidence.
- L3 implemented locally: stable broker contract, authenticated API and `/streaming`
  UI, durable sink identity deduplication, bounded quarantine/processing, real lag
  and checkpoint inspection. Optional real Kafka SDK adapter and Compose profile
  use one manual partition and group offsets; live broker verification is blocked.
  Distributed balancing, multiple partitions and broker health integration remain pending.
- L4 pending: source schemas, retries, bounded dead-letter handling and lineage.
- L5 pending: distributed Flink/Spark execution and backpressure/checkpoints.
- L6 pending: retention, recovery, access control, quotas, SLOs and operations.
- L7 pending: measured alternative engines and table formats.

Source: `labs/data-engineering/event-pipeline/pipeline.py`. Tests and resettable
evidence: `labs/data-engineering/event-pipeline/run.py verify`. Product discovery:
`/labs/durable-event-pipeline` and `/developer/technologies`.

Local transaction atomicity cannot extend across an external broker and sink.
The Kafka transition must use durable event identity and sink deduplication and
must document delivery semantics. It must not call local offset replay proof an
exactly-once distributed guarantee.

## Arrow/Parquet and Iceberg

Arrow/Parquet L0–L2: explicit empty/nonempty schema, accepted-sink product download,
embedded lineage, content digest, bounded rows and real round-trip/isolation tests.
Source: `apps/api-python/src/atlas_api/streaming_export.py`.

Iceberg L0–L2: real local SQL catalog, tenant/provider-owned tables, full accepted
sink refresh, idempotent content-digest retries, bounded immutable snapshot history,
old-snapshot data readback and API/UI integration. Source:
`apps/api-python/src/atlas_api/usage_lakehouse.py`. This introduces table snapshots
because analytical consumers need repeatable historical reads of accepted counters.
It does not claim distributed compute or an atomic broker/sink/catalog checkpoint.

Arrow ingestion from untrusted files, schema evolution, remote Iceberg catalogs,
snapshot expiry/orphan cleanup, distributed Spark/Flink and live Superset acceptance remain pending.
Airflow source/task/status integration is described below; live acceptance is pending. See ADR 0012 and `docs/runbooks/usage-streaming.md`.

## Airflow

L0-L1: real source-owned manual DAG; bounded consume, actual Parquet lineage
validation and local Iceberg refresh; tenant-bound status API and `/pipelines`
run/task dependency view; offline provider contracts and real native task-chain
tests. Linux DAG parsing, image startup and live scheduling remain acceptance
gates. Do not infer scheduler health from source inventory. Durable run-scoped
claims, scheduled asset triggers, distributed workers and orchestration traces
remain future levels. See ADR 0013 and `docs/runbooks/usage-orchestration.md`.

## Spark and Flink

Spark L0–L2 reads the real accepted-event Parquet export and executes a typed
native Spark SQL aggregate. The actual local JVM acceptance passed with 2 rows /
7 units, including API receipt verification and detection of a later source change.
The read-only `/pipelines` observation checks digest and current source totals.
The standalone driver/worker profile remains unverified until Linux Docker is
available. Local JVM acceptance is not distributed recovery acceptance.

Flink L0–L1 has a source-owned bounded Table API batch job and a tenant-bound
read-only REST adapter projecting checkpoint counts and up to three vertex
pressure observations. Deprecated samples remain unavailable, not healthy.
Native provider/security contracts pass; its Linux image, actual job execution,
checkpoint recovery and sustained backpressure behavior remain acceptance gates.
PyFlink's Beam/Arrow dependency graph is isolated from API/Spark. See ADR 0014
and `docs/runbooks/usage-compute.md` for versions, limits and continuation.

Superset L0–L1 has an actual accepted-counter aggregate publisher, separate BI-only
SQLite dataset, tested read-only SQLAlchemy URI, fixed-dashboard observer API/BFF
and publication UI. The local profile has no default login, requires an operator
secret and preserves vendor CSRF/template boundaries. Linux startup, role isolation,
actual dashboard data and refresh acceptance remain pending. See the usage-BI
runbook; metadata publication does not certify dataset freshness.
