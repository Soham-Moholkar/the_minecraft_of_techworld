# ATLAS-DATA-P10 — Data engineering and Apache

Status: in progress. Owner: Data Platform. Roadmap: Phase 10.

First slice: resettable local usage-event pipeline with tenant-scoped durable
source IDs, bounded batches, consumer checkpoints/lag, negative-unit quarantine,
atomic effects/checkpoint commit, injected crash recovery and safe replay.
Catalog, progression, registry and local quality profile include the runnable lab.

Completed next slice: stable broker contract, persistent SQLite source and sink,
optional real Kafka SDK adapter, authenticated owner-only development API and
server-only BFF, `/streaming` ingestion/processing/lag/checkpoint/quarantine view.
Manual Kafka partition assignment/group offset acknowledgement; no distributed
balancing claim. Sink commits precede broker acknowledgements and stable event
identities handle replay. Retention gaps fail closed. Storage/request bounds,
structured logs/counters, privacy and negative tests are implemented.

Arrow/Parquet exports accepted counters with explicit schema, content digest and
lineage. Optional local Iceberg projection publishes bounded full-refresh snapshots,
skips unchanged source content, preserves old-snapshot reads and isolates tenants.
All versions pinned after official release/license/security review (ADR 0012).

Verification: 14 focused API/SDK/Parquet/Iceberg/FileIO tests passed. Full web/API and local
profile verification recorded in CHECKPOINT.md after final checks. Live Kafka and
the API streaming/lakehouse container builds have not run: Docker engine absent.

Remaining: live Kafka acceptance, partition/group coordination, Arrow/Parquet
ingestion, distributed Spark/Flink acceptance and streaming recovery, live Airflow
scheduling, remote Iceberg catalog/schema/retention management, live Superset
dataset/chart/role acceptance, richer operational canvas and distributed traces.
A workspace-local verified JRE runs Spark; Docker's Linux pipe remains absent.
Airflow/Flink/Superset require supported Linux/WSL/container execution. These are
pending work, not simulated or certified complete. Each needs actual product
behavior, teardown, security/telemetry, tests and registry evidence.

Phase 9 remains unfinished: the resettable agent-security lab is implemented and
verified; broader multi-agent scope and MCP transport remain incomplete. Starting Phase 10 does not certify
those requirements or grant agent execution authority.

Completed additional implementation: source-owned Airflow manual DAG with bounded
actual usage API tasks, Parquet validation, retry policy, tenant-bound read-only
status API/BFF and `/pipelines` run/task dependency view. Nine API and four web
regressions passed; Linux CI parse/live Kafka jobs added. Airflow Linux image and
standalone profile are source/config only until real runtime acceptance passes.
Explicit Kafka and usage/catalog named volumes replace disposable container state.
Past-phase audit fixes and evidence are recorded in `docs/phase-audit-2026-10-03.md`.

Spark additional slice: actual Parquet reader and SQL rollup, bounded source and
atomically published numeric receipt, owner/development read-only API/BFF, stale
source/aggregate checks and `/pipelines` observation. Actual local JVM acceptance
passed (2 rows / 7 units / later-source detection); source/receipt/security/UI
regressions pass. Optional standalone profile remains runtime-unverified.

Flink additional foundation: source-owned bounded Table API job, fixed-job
tenant-bound status adapter, checkpoint counts and deprecated-safe backpressure
projection. Native provider/privacy/configuration tests pass. Linux image/package
resolution, actual job execution and streaming checkpoint recovery are pending.
The PyFlink Beam/Arrow dependency graph is isolated from API/Spark.
Development Compose ports now bind loopback, enforced by the consistency gate.

Superset additional foundation: an operator-owned accepted-Parquet projection
stores only tenant/provider aggregate counts and lineage in a separate SQLite
database. Actual SQLAlchemy read-only URI enforcement and projection reruns pass.
An owner/development read-only API/BFF observes the configured tenant dashboard's
publication metadata; `/pipelines` distinguishes disabled, unpublished and published.
Publication is not a claim of data freshness. Superset 6.1.0 profile, authenticated
setup, dedicated observer role and read-only dataset commands are documented in
`docs/runbooks/usage-bi.md`. Actual Linux startup, chart, role and refresh acceptance
remain unverified. See ADR 0015; no application database is exposed to BI.

Operational canvas: fixed topic → accepted sink → Parquet → provider branches,
interactive stage inspection, real lag/retention/accepted counters and current or
older Spark lineage. Independent read-only refresh, contract failures and unmount
cancellation have four regressions. Source-defined branches never imply healthy
runtimes. The separate Airflow dependency/run view remains the orchestration view;
freeform workflow editing and production job authority are outside this slice.
