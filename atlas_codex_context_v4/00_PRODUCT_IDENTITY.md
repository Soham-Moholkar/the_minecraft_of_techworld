# 00 — Product Identity: ATLAS Is the Project, Not a Playground

This file is authoritative. If any older context file describes ATLAS primarily as a tutorial site, coding playground, lesson portal, or collection of disconnected labs, interpret that wording through this document.

## Core idea

ATLAS is a very large, production-style, polyglot enterprise technology platform.

The learner does not primarily learn inside an embedded playground.

The learner:

1. clones/opens the repository in VS Code or another IDE,
2. runs the real ATLAS system locally,
3. uses the actual product,
4. reads unfamiliar production-style code,
5. traces requests and data through the system,
6. changes implementation details,
7. runs tests,
8. observes the effect in the real product,
9. introduces controlled failures,
10. diagnoses and fixes them,
11. refactors or replaces technologies,
12. deploys/scales the real system.

> **The IDE is the playground. The ATLAS repository is the curriculum. The ATLAS application is the thing being changed.**

## What ATLAS should resemble

ATLAS is an original enterprise platform with product surfaces inspired by categories of systems such as:

- enterprise analytics,
- cloud/infrastructure operations,
- observability,
- security operations,
- data platforms,
- AI assistants,
- agent/workflow systems,
- developer platforms,
- project/knowledge management,
- internal developer portals,
- ML platforms,
- business intelligence.

Do not clone proprietary products. Build an original coherent platform.

## Real product surfaces

ATLAS should contain real user-facing product areas such as:

- Organizations
- Users
- Teams
- Projects
- Workspaces
- Analytics
- Reports
- Dashboards
- Data Explorer
- Datasets
- Data Catalog
- Data Quality
- Data Lineage
- ETL/ELT Pipelines
- Streaming
- Warehouses/Lakehouse
- ML Experiments
- Models
- Model Registry
- Predictions
- Forecasting
- Anomaly Detection
- AI Assistant
- Knowledge/RAG
- Agents
- Agent Tools
- MCP Integrations
- Agent Workflows
- AI Evaluations
- Infrastructure
- Cloud Resources
- Containers
- Kubernetes
- Deployments
- CI/CD
- Logs
- Metrics
- Traces
- Alerts
- Incidents
- SLOs
- Security Findings
- Audit Logs
- Access Control
- Policies
- Threat Models
- Automation
- Jobs
- Queues
- Schedules
- Notifications
- APIs
- Webhooks
- Integrations
- Developer Portal
- API Keys
- SDKs
- Usage/Metering
- Cost Analytics
- Billing Simulation
- Feature Flags
- Experiments
- Admin
- Settings

These surfaces create legitimate reasons for the repository to contain many technologies.

## Technology legitimacy rule

Do not add a technology merely to display its logo.

A technology belongs when at least one of these is true:

1. it powers a real ATLAS feature,
2. it is an interchangeable implementation of an ATLAS subsystem,
3. it is a production-quality alternate implementation used for comparison,
4. it supports infrastructure/testing/security/observability of ATLAS,
5. it is historically or architecturally important enough to have a maintained reference implementation inside an isolated adapter/example module.

## Multi-implementation architecture

Important subsystems should expose stable interfaces with multiple implementations.

Examples:

```text
MessagingProvider
├── Kafka
├── Pulsar
├── RabbitMQ
├── NATS
└── Redis Streams

ORM/DataAccess
├── SQLAlchemy
├── Django ORM
├── Prisma
├── Drizzle
├── TypeORM
├── Hibernate/JPA
├── Entity Framework Core
├── GORM/sqlc
└── SQLx/Diesel

SearchProvider
├── PostgreSQL FTS
├── OpenSearch/Elasticsearch
├── Lucene/Solr concepts
├── Vector Search
└── Hybrid Search

ObjectStorageProvider
├── local filesystem
├── S3
├── Azure Blob
├── GCS
├── MinIO
└── Ceph concepts

InferenceProvider
├── local model runtime
├── vLLM-style serving
├── OpenAI-compatible endpoint
├── hosted provider adapters
└── batch inference

AnalyticsEngine
├── PostgreSQL
├── DuckDB
├── ClickHouse
├── Spark
├── Flink
└── lakehouse query engine
```

This lets the learner replace infrastructure without changing higher-level product contracts.

## Ticket-driven learning

ATLAS should maintain realistic engineering tasks, for example:

- optimize a query that became slow at 5M rows,
- migrate a service from one ORM to another,
- replace Kafka with Pulsar behind an existing interface,
- move a large pandas workload to Polars/DuckDB/Spark,
- rewrite a throughput-critical Python service in Rust/Go,
- add missing authorization to an endpoint,
- implement OpenTelemetry tracing across a workflow,
- add idempotency to an event consumer,
- fix a race condition,
- make an upload resumable,
- add offline sync to mobile,
- improve RAG retrieval quality,
- add agent permission boundaries,
- make a Kubernetes workload autoscale,
- recover from a simulated region failure.

The repository should contain TODOs/issues/backlog metadata for such work.

## Completeness philosophy

“Everything under the sky” is implemented as a **living technology registry and ecosystem-parity model**, not by blindly importing every package ever published.

For every major language/ecosystem:

- map all major engineering categories,
- integrate first-class technologies deeply,
- integrate major alternatives behind comparable interfaces,
- retain historically important/legacy technologies as reference modules where worthwhile,
- track experimental/emerging technologies separately,
- record unsupported/unintegrated technologies in the registry,
- let Codex expand coverage continuously.

The objective is maximum breadth without turning ATLAS into an unmaintainable dependency graveyard.

## Non-goal

No dedicated DSA/LeetCode/interview-algorithm product area.
Low-level data structures may appear only when required by real systems such as databases, runtimes, compilers, indexes, caches, schedulers, networking, storage or distributed systems.
