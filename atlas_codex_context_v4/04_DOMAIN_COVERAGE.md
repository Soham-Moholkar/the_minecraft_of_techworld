# Domain Coverage Catalog

> **Product identity override:** Interpret this file through `00_PRODUCT_IDENTITY.md`. ATLAS is the real application; the IDE is the primary place for source modification. Any older “lesson/playground” wording means engineering documentation, operational tooling, reference modules, or controlled test environments—not the central product model.


This is the long-term coverage target. It is intentionally broad.

## 1. Python

Cover:
- syntax and execution model,
- values/types,
- variables and name binding,
- operators,
- strings,
- collections,
- comprehensions,
- conditionals,
- loops,
- functions,
- arguments,
- closures,
- decorators,
- iterators,
- generators,
- context managers,
- exceptions,
- modules/packages,
- imports,
- OOP,
- dataclasses,
- typing,
- protocols/generics,
- file I/O,
- serialization,
- pathlib,
- datetime,
- regex,
- logging,
- subprocess,
- environment/process interaction,
- networking,
- HTTP clients,
- async/await,
- asyncio,
- threading,
- multiprocessing,
- concurrent futures,
- synchronization,
- memory/profiling,
- testing,
- packaging/build systems,
- virtual environments,
- linting/formatting/type checking,
- Python internals at an educational level,
- C-extension/interface concepts where useful.

For the standard library and major libraries, create searchable reference catalogs. Rich labs should focus on meaningful APIs rather than superficial pages for every name.

## 2. Additional programming languages

Teach enough real projects and internals to compare ecosystems.

### JavaScript
- language fundamentals,
- prototypes,
- closures,
- event loop,
- promises,
- async,
- modules,
- DOM/browser APIs,
- workers,
- performance.

### TypeScript
- structural typing,
- unions/intersections,
- generics,
- utility types,
- narrowing,
- inference,
- conditional/mapped/template types,
- declaration files,
- project references,
- strictness,
- type-level patterns.

### Java
- JVM mental model,
- collections,
- generics,
- streams,
- concurrency,
- IO/networking,
- Spring ecosystem.

### Go
- packages,
- interfaces,
- goroutines,
- channels,
- context,
- servers,
- profiling.

### Rust
- ownership,
- borrowing,
- lifetimes,
- enums/traits,
- error handling,
- async,
- systems/server examples.

### C/C++
Use for:
- memory,
- compilation/linking,
- pointers,
- resource ownership,
- low-level networking/performance,
- interoperability examples.

## 3. Frontend

- HTML semantics,
- CSS fundamentals,
- layout,
- responsive design,
- accessibility,
- forms,
- browser rendering,
- network behavior,
- web performance,
- JavaScript/TypeScript,
- React,
- Next.js,
- Vue,
- Angular,
- Svelte/SvelteKit,
- state management patterns,
- server state,
- forms,
- design systems,
- WebSockets/SSE,
- workers,
- PWA concepts,
- testing,
- frontend security.

## 4. Backend

### Python
- FastAPI
- Flask
- Django
- Django REST Framework

### Node
- native Node APIs
- Express
- Fastify
- NestJS

### Java
- Spring Boot
- JPA/Hibernate concepts

### Go/Rust
Representative services for comparison.

### API paradigms
- REST
- GraphQL
- gRPC
- WebSockets
- SSE
- SOAP concepts and legacy interoperability

### Backend engineering
- validation,
- authentication,
- authorization,
- sessions,
- API versioning,
- idempotency,
- pagination,
- caching,
- rate limiting,
- background jobs,
- queues,
- scheduling,
- file handling,
- email integration examples,
- storage,
- transactions,
- resilience,
- observability,
- configuration,
- deployment.

## 5. Databases and DBMS

### Relational
- PostgreSQL
- MySQL/MariaDB
- SQLite

### Document
- MongoDB

### Key-value/cache
- Redis

### Wide-column
- Cassandra

### Graph
- Neo4j and graph database concepts

### Search
- Elasticsearch/OpenSearch concepts
- Lucene concepts

### Analytical/columnar
- ClickHouse
- DuckDB
- warehouse/lakehouse concepts

### Time-series
- PostgreSQL time-series extensions/concepts
- representative time-series systems

### Vector
Teach vector database concepts and multiple representative implementations.

### DBMS theory
- relational model,
- schema,
- constraints,
- normalization,
- denormalization,
- algebra concepts,
- SQL parsing/execution,
- query planning,
- joins,
- indexes,
- B-tree/B+tree concepts,
- LSM concepts,
- hashing,
- transactions,
- ACID,
- locks,
- deadlocks,
- MVCC,
- isolation levels,
- WAL,
- crash recovery,
- buffer cache,
- connection pools,
- replication,
- failover,
- partitioning,
- sharding,
- consistency,
- backups,
- restore,
- security,
- query optimization.

## 6. Networking

- OSI/TCP-IP mental models,
- Ethernet concepts,
- IP,
- subnetting,
- routing,
- TCP,
- UDP,
- sockets,
- DNS,
- HTTP versions,
- TLS,
- certificates,
- proxies,
- reverse proxies,
- load balancers,
- NAT,
- firewalls,
- VPN,
- CDN,
- WebSockets,
- packet capture/analysis in local labs,
- latency/bandwidth/loss experiments.

## 7. Operating-system concepts

No standalone interview-prep section. Teach systems concepts through real engineering:
- process/thread,
- scheduling,
- memory/virtual memory,
- filesystems,
- permissions,
- signals,
- IPC,
- sockets,
- containers/namespaces/cgroups concepts,
- system calls,
- Linux tooling.

## 8. Software architecture

- layered architecture,
- hexagonal,
- clean architecture,
- modular monolith,
- microservices,
- event-driven,
- serverless,
- CQRS,
- event sourcing,
- saga/workflow patterns,
- outbox/inbox,
- API gateway,
- BFF,
- service discovery,
- resilience patterns.

## 9. Distributed systems

- CAP and its limitations,
- consistency models,
- clocks/time,
- ordering,
- idempotency,
- retries,
- deduplication,
- consensus concepts,
- leader election,
- replication,
- quorum,
- partitioning,
- distributed locks,
- transactions,
- failure detectors,
- backpressure,
- messaging semantics,
- eventual consistency.

## 10. DevOps

- Linux
- Bash/shell
- Git
- GitHub
- CI/CD
- Docker
- Compose
- Kubernetes
- Helm
- Terraform
- Ansible
- artifact registries
- build systems
- configuration management
- secrets management
- deployment strategies
- rollback
- infrastructure testing
- policy as code concepts

## 11. Cloud

Teach equivalent building blocks across:
- AWS
- Azure
- GCP

Categories:
- identity,
- networking,
- compute,
- containers,
- serverless,
- object storage,
- block/file storage,
- managed SQL,
- NoSQL,
- cache,
- queues/events,
- API gateways,
- observability,
- secrets,
- key management,
- CDN,
- DNS,
- ML/AI services,
- data analytics,
- IaC,
- cost and architecture tradeoffs.

Avoid building cloud labs that silently incur cost. Every cloud lab needs a cost/safety note and teardown procedure.

## 12. Observability and SRE

- structured logging,
- metrics,
- traces,
- OpenTelemetry,
- Prometheus,
- Grafana,
- service dashboards,
- SLIs/SLOs,
- error budgets,
- alerting,
- on-call concepts,
- capacity,
- reliability,
- runbooks,
- incident response,
- postmortems,
- chaos/resilience testing.

## 13. Data engineering

- ETL/ELT,
- CDC,
- batch,
- streaming,
- event-driven pipelines,
- orchestration,
- data quality,
- lineage,
- catalogs,
- file formats,
- lake/lakehouse/warehouse,
- partitioning,
- schemas,
- schema evolution,
- distributed compute.

## 14. Apache / free open-source ecosystem

Give Apache technologies a dedicated discovery area and deep labs for the most useful ones.

Priority projects:
- Apache Spark
- Apache Kafka
- Apache Flink
- Apache Airflow
- Apache Beam
- Apache Hadoop (HDFS/YARN/MapReduce concepts)
- Apache Hive
- Apache HBase
- Apache Cassandra
- Apache Iceberg
- Apache Arrow
- Apache Parquet
- Apache Avro
- Apache ORC
- Apache Superset
- Apache NiFi
- Apache Pulsar
- Apache Pinot
- Apache Druid
- Apache ZooKeeper concepts/legacy coordination
- Apache Calcite
- Apache Lucene
- Apache Solr
- Apache JMeter
- Apache Maven
- Apache Tomcat

Before adding a project, verify current Apache project status and official guidance.

## 15. Software engineering craft

- SOLID,
- cohesion/coupling,
- refactoring,
- design patterns,
- error handling,
- configuration,
- versioning,
- API contracts,
- migrations,
- code review,
- documentation,
- ADRs,
- dependency management,
- release engineering,
- feature flags,
- backward compatibility.