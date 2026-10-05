# Local usage orchestration

The source-owned `atlas_usage_rollup` Airflow DAG is manual, has one active run,
three ordered tasks and a five-minute run timeout. It consumes at most 100 events,
validates the current accepted-sink Parquet digest/schema/tenant/aggregates, then
refreshes local Iceberg. Consume has zero automatic retries; inspect offsets after
an uncertain response before manually retrying. Validation and digest-idempotent
lakehouse refresh each have one retry. Reads across tasks reflect successive sink
states, not a transaction spanning broker, export and catalog.

## Supported runtime

Use the optional Linux container on a healthy Docker engine. From repository root:

```powershell
# API build extras and runtime flags are distinct opt-ins.
$env:ATLAS_STREAMING = 'true'
$env:ATLAS_LAKEHOUSE = 'true'
$env:ATLAS_STREAMING_ENABLED = 'true'
$env:ATLAS_LAKEHOUSE_ENABLED = 'true'
$env:ATLAS_PIPELINE_ENABLED = 'true'
docker compose -f compose.yaml -f infra/airflow/compose.yaml --profile orchestration up -d --build postgres api airflow web
```

Airflow standalone is a local development runtime. Its UI is bound to loopback
port 58080. SimpleAuthManager keeps authentication enabled and generates the
`operator` password in its own named volume. Sign in, unpause the usage DAG and
trigger it manually after publishing synthetic events through `/streaming`.
No dag_run.conf field selects commands, URLs, paths, credentials, tenant or limits.
Do not expose this development identity/runtime as a shared service.

The API status adapter needs an Airflow JWT obtained through the configured
Airflow authentication manager. Keep it in `ATLAS_AIRFLOW_API_TOKEN`, enable
`ATLAS_AIRFLOW_ENABLED`, and restart/recreate the API. Native API runs use
`ATLAS_AIRFLOW_API_URL=http://127.0.0.1:58080`; Compose selects `http://airflow:8080`.
The `/pipelines` page reads five runs and at most three fixed task observations.
The adapter rejects a different tenant/DAG, excessive responses and malformed
states; drops conf, notes, XCom and rendered fields; disables redirects/proxies;
and never triggers, cancels or changes a run. JWT expiry appears as unavailable.

`atlas_airflow_status_reads_total` records fixed success/unavailable labels.
Structured logs retain counts only. Task XCom contains numeric aggregates and a
Parquet digest, never exported bytes, credentials or event payloads.

## Verification and cleanup

Native API tests execute all three actual task helpers into real Parquet/Iceberg:
`python -m pytest apps/api-python/tests/test_usage_orchestration.py`.
Adapter tests exercise schemas, privacy, tenant authority and bounds. Linux CI
installs pinned Airflow with its official Python 3.12 constraints and executes
`python scripts/verify_airflow_dag.py`. A DAG parse and direct task-chain test do
not certify live scheduler execution. A real manual run must show all three task
instances succeeding before live acceptance is recorded.

Stop only Airflow with:
`docker compose -f compose.yaml -f infra/airflow/compose.yaml --profile orchestration stop airflow`.
This preserves history. The `atlas_airflow`, `atlas_usage` and `atlas_kafka` named
volumes survive recreation. Do not use `down -v` for routine cleanup. Archive data
and verify exact owned volumes before a deliberate destructive reset. No reset
was performed during implementation.

As of 2026-10-03, native task-chain/status contracts pass. Container build,
Linux DAG parse and a live Airflow scheduler run remain unverified locally.
