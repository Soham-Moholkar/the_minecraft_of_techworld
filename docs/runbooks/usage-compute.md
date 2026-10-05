# Usage compute

ATLAS owns a bounded Spark 4.2.0 Parquet rollup. It reads the authenticated
accepted-sink export, checks digest/schema/tenant/identity/aggregate lineage,
then uses Spark's actual Parquet reader and SQL aggregate. It publishes one
numeric, content-bound receipt. `/pipelines` reads the receipt through an
owner-only development API and reports whether current accepted data still has
that digest. A current receipt's aggregates must also match the source lineage.

This is an operator-run job, not a web SQL runner or job submission service.
No browser request chooses commands, paths, master URLs, sources or credentials.
The local shared directory is trusted operator state, not remote attestation.
It contains a fixed Parquet source and one receipt per tenant/provider. Protect
that directory; API containers mount it read-only. Never use the development
identity/profile as shared production access control.

## Local acceptance

Install the optional `compute` extra and use Java 17+ from an official source.
The currently verified release is Spark/PySpark 4.2.0 (Apache-2.0). The portable
test JRE is Temurin 21.0.12.1+1 (GPL-2.0 with Classpath Exception), downloaded from
the official Adoptium API/GitHub release into ignored `.tools`. Its archive SHA-256
is `d35f31e712f0fcf6ac5a093edc90204fbff22f720ba3950bd09d331d5e621636`.
The archive keeps upstream license/notice files. No system Java/PATH is changed.

```powershell
.venv/Scripts/python.exe -m pip install -e './apps/api-python[compute]'
$env:JAVA_HOME=(Resolve-Path '.tools/jdk-21.0.12.1+1-jre').Path
.venv/Scripts/python.exe scripts/verify_usage_spark.py
```

The gate creates a unique disposable API/store, publishes two synthetic events,
consumes them, runs actual Spark in `local[2]`, verifies 2 rows / 7 units through
the receipt/status API, then verifies staleness after another accepted event.
It has a 240-second job deadline, stops its own API, removes its unique fixture
and preserves `output/phase10-spark-runtime.log`. This does not verify standalone
cluster deployment. Windows/Hadoop native-I/O compatibility may require a
supported Linux environment; do not download unofficial `winutils` executables
or disable validation to force a pass.

## Standalone development cluster

Merge the source-owned override from the repository root:

```powershell
docker compose -f compose.yaml -f infra/spark/compose.yaml --profile compute config --quiet
docker compose -f compose.yaml -f infra/spark/compose.yaml --profile compute up -d spark-master spark-worker
docker compose -f compose.yaml -f infra/spark/compose.yaml --profile compute run --rm --no-deps --use-aliases spark-usage
```

Start/configure the existing API with streaming and Arrow extras first. Set
`ATLAS_PIPELINE_ENABLED=true` for the job and `ATLAS_USAGE_COMPUTE_ENABLED=true`
for API reads; both default false. The API and job use the configured development
credential through environment only. A dedicated internal network carries Spark
worker traffic; no Spark RPC/UI ports are published. This unauthenticated local
cluster is a trusted single-operator profile. Resource caps bound CPU, memory,
PIDs, two executor cores and two shuffle partitions. The job deadline is 240s.

The shared named `atlas_compute` volume lets driver/executors read the same
source path. Compose one-off driver networking must retain its service alias:
use `run --use-aliases` when executing `spark-usage`. Do not run concurrent jobs.
An exclusive `spark.lock` protects source replacement; an abrupt termination
leaves it for operator investigation. Stop only the compute services when done;
preserve the named volume. Do not run `down -v` as routine teardown.

Spark's source input is a consistent accepted-sink read, not an atomic broker
offset cutoff. It neither consumes offsets nor writes back usage effects. A
later event legitimately makes its receipt stale; rerun the job for fresh data.
Backpressure/checkpoints belong to streaming providers, not this batch receipt.

## Evidence and limitations

Native contracts are tested separately from actual JVM execution and standalone
container acceptance. Read `CHECKPOINT.md` for their current results. A configured
image/profile or recorded receipt is not evidence of a healthy distributed cluster.

Official references: [Spark release/downloads](https://spark.apache.org/downloads.html),
[PySpark installation](https://spark.apache.org/docs/4.2.0/api/python/getting_started/install.html),
[standalone deployment](https://spark.apache.org/docs/4.2.0/spark-standalone.html),
[official image source](https://github.com/apache/spark-docker/tree/master/4.2.0),
[Temurin installation](https://adoptium.net/installation/).

## Flink foundation and Linux acceptance

`infra/flink/usage_job.py` owns a bounded Flink 2.3.0 Table API batch alternative.
It validates the authenticated Parquet export, executes a real count/sum through
Flink's planner, and reports the actual job ID and numeric evidence. It does not
claim streaming checkpoint recovery. The API projects the configured job's state,
checkpoint counts and up to three pressure samples. Deprecated samples remain
unavailable. Plans/configuration/SQL/logs/paths and submit/cancel/savepoint controls
are excluded. Blank job ID means unconfigured, not a startup error.

Official PyFlink 2.3.0 requires Beam <=2.61 and Arrow <21. Beam 2.61 additionally
requires Arrow <17. The isolated image pins Beam 2.61.0 and Arrow 16.1.0; API/Spark
retain Arrow 25.0.1. Keep upstream Apache-2.0 notices. This older constrained graph
needs Linux dependency/runtime acceptance before broader deployment. Native
status contracts do not verify the image, Table job or streaming recovery.

```powershell
docker compose -f compose.yaml -f infra/flink/compose.yaml --profile flink config --quiet
docker compose -f compose.yaml -f infra/flink/compose.yaml --profile flink up -d flink-jobmanager flink-taskmanager
docker compose -f compose.yaml -f infra/flink/compose.yaml --profile flink exec flink-jobmanager timeout 240s /opt/flink/bin/flink run -py /opt/atlas/usage_flink_job.py -pyexec /opt/pyflink/bin/python -pyclientexec /opt/pyflink/bin/python
```

First configure the API with `ATLAS_STREAMING=true` at build and
`ATLAS_STREAMING_ENABLED=true` at runtime, with actual accepted events. Set
`ATLAS_PIPELINE_ENABLED=true` for the job. Set `ATLAS_FLINK_ENABLED=true` and the
returned 32-hex `ATLAS_FLINK_JOB_ID` for observations, then recreate only the API
to load immutable settings. REST stays loopback 58081; RPC/taskmanager ports are
unpublished. Only the jobmanager/client receives the usage API credential.
Resource caps and two slots bound the profile. Stop only the two Flink services
after verification. Sustained streaming needs checkpoint storage, controlled
recovery/backpressure acceptance and teardown before later progression levels.
Linux tests are pending while Docker's supported engine is unavailable.

Official references: [Flink Docker/PyFlink](https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/deployment/resource-providers/standalone/docker/),
[REST contracts](https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/ops/rest_api/),
[PyFlink dependency metadata](https://pypi.org/project/apache-flink/2.3.0/),
[Beam dependency metadata](https://pypi.org/project/apache-beam/2.61.0/).
