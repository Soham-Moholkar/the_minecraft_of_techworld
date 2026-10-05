# ADR 0013: Bounded manual usage orchestration

Status: accepted for local implementation; live runtime acceptance pending.

The usage pipeline needs observable orchestration beyond manual individual API
operations. Adopt an optional Apache Airflow 3.3.2 source-owned DAG with a manual
schedule, one active run and three bounded API task helpers. Keep Apache-2.0
Airflow in its supported Linux image, with pinned Arrow 25.0.1 for export validation.
The API gains a read-only server-configured status adapter; `/pipelines` projects
real runs onto fixed dependencies. No new model or browser execution authority.

Automatic consume retries are disabled: a lost HTTP response can hide a committed
batch, so another request can consume the next batch. Stable identities make sink
effects replay-safe, but cannot make a run claim an exact broker cutoff. Validation
and unchanged-content Iceberg retries remain bounded and explicitly separate.
No raw datasets/credentials enter XCom. Airflow conf is never interpreted by tasks.
Status drops upstream configuration, logs, notes and rendered payloads and caps I/O.

Docker stores Kafka source state and usage sink/catalog state in explicit named
volumes. The API image initializes its usage directory for the non-root runtime.
This corrects earlier disposable /tmp paths without resetting existing host stores.
Build and persistence acceptance remain separate runtime gates.

Native task-chain and adapter integration tests are required. Linux CI parses the
actual DAG under the pinned official constraints. Live scheduler, image startup and
end-to-end status acceptance remain required; passing local tests does not promote
Airflow beyond the implemented foundation. Spark, Flink and Superset remain pending.

Sources consulted: Airflow 3.3.2 DAG, REST API, installation and security docs;
official Airflow release/constraints endpoints and upstream public API models;
Apache Kafka official image Dockerfile for its pre-owned data directory. PyYAML
6.0.3 (MIT, maintained stable release) is an explicit dev dependency for safe YAML
registry consistency validation, never an object/unsafe loader.

- https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html
- https://airflow.apache.org/docs/apache-airflow/stable/security/api.html
- https://raw.githubusercontent.com/apache/airflow/constraints-3.3.2/constraints-3.12.txt
- https://pypi.org/project/apache-airflow/3.3.2/
- https://pypi.org/project/PyYAML/6.0.3/
