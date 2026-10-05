# Usage streaming and lakehouse (trusted local development)

Install optional runtimes from the repository root:

```powershell
.venv/Scripts/python.exe -m pip install -e 'apps/api-python[streaming,lakehouse]'
$env:ATLAS_STREAMING_ENABLED = 'true'
$env:ATLAS_LAKEHOUSE_ENABLED = 'true'
.venv/Scripts/python.exe -m uvicorn atlas_api.main:app --host 127.0.0.1 --port 8000
```

Start the existing web command in another terminal and open `/streaming`. Publish
a counter with a stable event ID; refresh shows lag. Process up to ten events and
inspect accepted units, quarantine and checkpoint. Negative units enter quarantine.
Retry uncertain delivery with the SAME ID and units. A conflicting local batch
rolls back atomically; Kafka may publish some records before reporting a timeout.

Download Parquet to inspect `atlas.lineage` schema metadata. Refresh the local
Iceberg projection to publish a full accepted-sink snapshot. Repeating unchanged
content creates no additional snapshot. The UI shows real committed identities,
operations and row counts. Prior data remains queryable with PyIceberg's
`table.scan(snapshot_id=...).to_arrow()`. This is local table management, not
Spark/Flink processing, Airflow orchestration or a Superset integration.

Streaming and lakehouse are independent opt-ins. API environment must be
`development`, and the principal must have the owner role. Do not expose the dev
token/BFF on an untrusted network. Optional dependency failures return a redacted
503. The web never receives bearer credentials, paths or broker addresses.

## Actual Kafka

With a running Docker Linux engine:

```powershell
docker compose --profile streaming up -d kafka
docker compose exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:9092 --create --if-not-exists --topic atlas.usage.northstar --partitions 1 --replication-factor 1
$env:ATLAS_STREAMING_PROVIDER = 'kafka'
$env:ATLAS_KAFKA_BOOTSTRAP = '127.0.0.1:59092'
```

Restart the native API after changing settings. Provision each authenticated
tenant's topic explicitly; the API cannot create or select topics. One partition
is mandatory in this slice. Committed offsets identify the next record. A
retention gap is visible and blocks processing; inspect data loss before choosing
a new group or rebuilding. No automatic reset is available. Manual assignment
does not provide distributed consumer-group balancing. Delivery is at-least-once.

Run `.venv/Scripts/python.exe scripts/verify_kafka.py` against that local broker
for live acceptance. It creates a unique verification topic/group, exercises a
lost acknowledgement and replay, validates actual lag/units/quarantine, and deletes
only its own topic/group plus generated sink. Failures are not skipped. The script
has not run successfully while the engine is unavailable; source/config and offline
SDK contracts alone cannot certify Kafka behavior.

For container API builds, set `ATLAS_STREAMING=true` (build extras),
`ATLAS_STREAMING_ENABLED=true`, and optionally `ATLAS_LAKEHOUSE=true` /
`ATLAS_LAKEHOUSE_ENABLED=true`, then rebuild the API. Usage/catalog state mounts
`atlas_usage` at `/var/lib/atlas`; Kafka mounts `atlas_kafka` at its owned data
path. These named volumes survive recreation. `docker compose stop kafka` stops
the optional broker without removing data. Volume permissions, recreation and
recovery still require live acceptance; no container persistence pass is claimed.

## Bounds, diagnostics and cleanup

HTTP batches are capped at 16,000 bytes before API JSON parsing; at most 100 events
or processed records, 512 bytes per consumed payload, 48 characters per event ID
and ±1000 units per event. Only synthetic usage data belongs in this profile.
Storage quota is 10,000 records and Iceberg history is capped at 32 snapshots.
Quota failures return 409 and require deliberate archive/rebuild. There is no
automatic destructive cleanup endpoint. Stop the native API before archiving or
removing the operator-configured `atlas-streaming.db` / `artifacts/usage-lakehouse`
store. Verify those exact paths and retain snapshots needed for history.

Structured logs/counters omit event payloads, IDs, credentials and paths.
`atlas_streaming_operations_total` uses bounded provider/operation/status labels;
the existing request correlation and latency metrics cover the routes. This
manual local flow has no distributed tracing yet. Quarantine stores reason and
offset only. Reads use no-store. API/export tests use unique disposable fixtures
and verify cleanup stays inside their fixture directories.

Verification commands:

```powershell
.venv/Scripts/python.exe -m pytest apps/api-python/tests/test_streaming.py apps/api-python/tests/test_kafka_broker.py apps/api-python/tests/test_streaming_export.py apps/api-python/tests/test_usage_lakehouse.py apps/api-python/tests/test_usage_lakehouse_api.py
.venv/Scripts/python.exe scripts/verify_streaming.py
./scripts/quality.ps1 -Profile data-engineering
docker compose --profile streaming config --quiet
pnpm test
```

Optional SDK/Arrow/Iceberg tests skip explicitly when their extras are absent;
install both extras for the Phase 10 acceptance gate. Offline Kafka tests do not
replace live broker verification. As of 2026-10-03, Docker's Linux pipe and Java
are unavailable here. Live Kafka, Spark/Flink, Airflow and Superset acceptance
remain incomplete. Airflow/Superset require supported Linux/WSL/container setups.

Container persistence now uses `atlas_usage` for `/var/lib/atlas` and `atlas_kafka`
for the broker's pre-owned `/var/lib/kafka/data`. Native files are independent.
Volumes survive recreation; startup/permission/persistence acceptance is pending.
For source-owned Airflow tasks and status, see `usage-orchestration.md`.
