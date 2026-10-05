# ATLAS — Complete Codex Context V4

> V4 adds mandatory progressive complexity and extensively commented source-code requirements.

## Included documents
- `STARTING_PROMPT_FOR_CODEX.md`
- `START_HERE.md`
- `AGENTS.md`
- `00_PRODUCT_IDENTITY.md`
- `CODEX_TASK.md`
- `01_MASTER_BUILD_SPEC.md`
- `02_MONOREPO_ARCHITECTURE.md`
- `03_FRONTEND_AND_DESIGN_SYSTEM.md`
- `04_DOMAIN_COVERAGE.md`
- `05_DATA_SCIENCE_AI_ML.md`
- `06_SECURITY_CYBERSECURITY.md`
- `07_TESTING_QUALITY_RELIABILITY.md`
- `08_LABS_DATASETS_BENCHMARKS.md`
- `09_SYSTEM_DESIGN_CASE_STUDIES.md`
- `10_PAGE_AND_COMPONENT_INVENTORY.md`
- `11_IMPLEMENTATION_ROADMAP.md`
- `12_CURRENT_TECH_NOTES.md`
- `13_FRAMEWORK_LIBRARY_MATRIX.md`
- `14_ECOSYSTEM_PARITY_AND_COMPLETENESS.md`
- `15_EXPANDED_PRODUCT_SURFACES.md`
- `16_TECHNOLOGY_REGISTRY.md`
- `17_REPOSITORY_WORK_MODEL.md`
- `18_OPEN_SOURCE_SOURCING_AND_PROVENANCE.md`
- `19_AUTONOMOUS_EXECUTION_AND_COMPLETION.md`
- `20_PROGRESSIVE_COMPLEXITY_AND_COMMENTS.md`

---


<!-- BEGIN STARTING_PROMPT_FOR_CODEX.md -->

# ATLAS — Starting Prompt for Codex

You are responsible for building the ATLAS repository.

Before writing code, read the ATLAS context files in the exact order defined by `START_HERE.md`, beginning with `AGENTS.md` and `00_PRODUCT_IDENTITY.md`.

## Mission

Build the complete ATLAS platform described by these specifications.

ATLAS must be a **real, production-style, modular, cohesive, polyglot enterprise application**, not a tutorial website and not a coding playground.

The learner will work primarily from an IDE:

```text
open repository
→ run real ATLAS
→ use feature
→ trace source
→ modify implementation
→ run tests
→ observe changed product behavior
→ debug/profile/secure/refactor
```

The repository itself is the mastery environment.

## Generate the actual repository

You must create **all required files, directories, source code, configuration, schemas, migrations, tests, infrastructure, CI/CD, security configuration, observability configuration, documentation and tooling** required to implement the specifications.

Do not wait for me to manually create boilerplate.

If the repository is empty, initialize it.

If it already contains work, inspect it first and continue without destroying valid existing implementation.

## Architecture requirements

ATLAS must remain:

### Cohesive
Everything belongs to one ATLAS monorepo, shares contracts/conventions, and forms one functioning product.

### Modular
Major capabilities have explicit boundaries and can be added/replaced later.

Use stable interfaces/adapters/providers for concerns such as:

- database/data access
- message brokers
- cache
- object storage
- search
- vector stores
- analytics engines
- AI inference
- authentication/identity
- feature flags
- notifications
- cloud providers
- telemetry.

### Polyglot
Use multiple languages when they provide real engineering value.

First-class ecosystem coverage must be deep.

Python must not mean only FastAPI. It must cover the relevant Python engineering ecosystem including Django, FastAPI, Flask, SQLAlchemy, Django ORM, migrations, drivers, validation, background jobs, messaging, caching, auth, GraphQL, gRPC, WebSockets, testing, security, observability, profiling, packaging and the data/AI ecosystem.

Node/TypeScript must receive equivalent breadth: Express, Fastify, NestJS, Prisma, Drizzle, TypeORM and equivalent libraries for migrations, auth, jobs, queues, caching, validation, GraphQL, gRPC, realtime, testing, security, observability and build tooling.

Apply ecosystem parity to Java, .NET/C#, Go, Rust, Kotlin, Scala, PHP, Ruby, Elixir, Swift, Dart/Flutter, C/C++ and additional ecosystems according to the registry.

Do not create a dedicated DSA section.

## Product scope

Implement the real ATLAS product surfaces specified in the context, including over time:

- identity, organizations, tenants, teams and access control
- projects/workspaces
- analytics/reporting
- datasets/catalog/quality/lineage
- pipelines/ETL/ELT/CDC
- streaming/event systems
- ML experiments/models/registry/inference
- AI assistant/RAG/agents/MCP/evals
- infrastructure/cloud/Kubernetes/deployments
- observability/logs/metrics/traces/SLO/incidents
- security findings/audit/policies/threat models
- automation/jobs/queues/schedules
- developer portal/APIs/webhooks/SDKs
- search
- file/document/media processing
- mobile/desktop/CLI clients
- billing/metering/FinOps
- feature flags/experimentation
- connectors/integrations
- system-design-relevant infrastructure
- all additional scope in the authoritative files.

## Frontend

Build a large, polished frontend utility/component system.

Use current shadcn/ui extensively and create ATLAS-owned composed components for:

- shell/navigation
- dashboards
- dense tables
- data grids
- analytics
- charts
- AI conversations/tool calls/agents
- model/experiment views
- database inspection
- pipeline/streaming views
- Kubernetes/cloud views
- logs/metrics/traces
- security findings/threat models
- admin/settings
- developer/API views
- file/media workflows
- workflow/graph/canvas views.

Use reputable online/open-source components when useful, but follow `18_OPEN_SOURCE_SOURCING_AND_PROVENANCE.md`. Do not blindly patch unrelated repositories together.

## Existing open-source code

You are encouraged to search official documentation, official repositories, maintained open-source projects and examples.

Use them to accelerate implementation.

However:

- ATLAS owns its architecture/contracts.
- Prefer dependencies and official generators over copied source.
- Integrate large external systems through adapters/services.
- Copy/adapt code only when license/security/provenance are clear.
- Record copied/adapted source in provenance metadata.
- Never create a Frankenstein repository by merging unrelated repos wholesale.

## Tests, security and observability are mandatory

A feature is incomplete without the appropriate combination of:

- unit tests
- integration tests
- contract/API tests
- E2E tests for critical flows
- performance tests where relevant
- security tests where relevant
- input validation
- authn/authz
- secrets hygiene
- logs
- metrics
- traces for distributed/asynchronous flows
- migrations/seed behavior
- error/loading/empty states
- accessibility for UI.

Run the relevant quality gates and fix failures.

## Technology registry

Maintain the machine-readable technology registry.

Whenever a significant framework/tool/database/protocol is added:

- classify it,
- record ecosystem/category,
- record integration location,
- record status,
- record alternatives,
- record version,
- record last verification.

Use the registry to identify missing ecosystem categories.

## Work like an engineering organization

Maintain realistic:
- tickets
- bugs
- migrations
- refactors
- performance work
- security remediation
- ADRs
- runbooks
- postmortems
- deprecations
- compatibility paths.

The repo should feel inherited, but complexity must be deliberate rather than random.

## Execution instruction — do not stop at planning

**Do not merely give me a plan. Begin creating and modifying the actual repository immediately.**

After finishing a coherent task:

1. run its checks,
2. fix failures,
3. update progress,
4. immediately continue to the next highest-priority incomplete task.

**Do not voluntarily stop after scaffolding, one milestone, one service, one domain, or one roadmap phase. Continue advancing through the specification until the complete defined ATLAS scope is implemented and verified.**

Do not ask me for confirmation between normal phases.

Make reasonable architectural decisions yourself using the context and official best practices.

If a cloud credential, paid service or unavailable external resource blocks one integration, create the provider boundary/local implementation/emulator and continue with the rest of ATLAS.

If a session, tool, execution or resource limit makes it impossible to continue in the current run, do not pretend the project is complete. Before stopping:

- create/update `CHECKPOINT.md`,
- create/update `.atlas/progress.json`,
- record exact completed work,
- record test status,
- record blockers,
- record the exact next task and command.

On the next run, read those files first and continue.

## Progressive complexity is mandatory

For every important technology you add, create a progression from simple to increasingly sophisticated real implementations.

Use the progression model in `20_PROGRESSIVE_COMPLEXITY_AND_COMMENTS.md`:

- L0 Foundation
- L1 Simple Product Integration
- L2 Realistic Engineering
- L3 Advanced
- L4 Complex System
- L5 Scale / Distributed
- L6 Production-Hardened
- L7 Expert / Alternate Architecture

Examples:

- APIs should evolve from a small spontaneous endpoint to persistence, validation, auth, caching, queues/events, distributed flows, observability/security and scale.
- PostgreSQL should evolve from simple queries to transactions/indexes, query planning/MVCC, partitioning/replication, high-volume workloads and production recovery.
- Kafka should evolve from producer/consumer to partitions/groups, schemas/retries/DLQs, idempotent event-driven systems, scale and DR.
- React/Next.js should evolve from small components/pages to real data flows, complex state/realtime UIs, performance, accessibility and production hardening.
- AI/ML should evolve from baselines to pipelines, tuning, serving, monitoring, distributed scale and alternate architectures.
- RAG/agents should evolve from a minimal implementation to retrieval/tooling, evaluation, permissions, observability, multi-tenancy and scale.

Do not create complexity without a reason. Preserve the evolution so I can inspect the simple version and understand why the harder version exists.

The ATLAS website must include a developer-facing progression view showing each technology's implemented levels, source paths, tests, architecture evolution and work items.

## Extensively commented source

Write unusually readable code.

Use extensive high-value comments and docstrings to explain:

- why code exists,
- why a framework/library was selected,
- architectural intent,
- invariants,
- data/transaction boundaries,
- concurrency/async behavior,
- distributed-system assumptions,
- security boundaries,
- failure/retry behavior,
- performance tradeoffs,
- non-obvious framework behavior,
- compatibility/migration concerns.

Do not fill the codebase with useless comments that simply restate obvious syntax.

Foundation/simple implementations may be more educational and explicit; advanced production code should use professional comments focused on rationale and invariants.

## Starting action

Now:

1. inspect the repository,
2. read all context,
3. create or update the technology registry,
4. determine the earliest incomplete roadmap phase,
5. create the required project structure and real code,
6. run the project and quality gates,
7. fix failures,
8. continue automatically.

Start implementation now. Do not answer with only an architecture proposal.


<!-- END STARTING_PROMPT_FOR_CODEX.md -->

---


<!-- BEGIN START_HERE.md -->

# ATLAS — Codex Build Context

## Purpose

ATLAS is a massive production-style, multidisciplinary, polyglot enterprise technology platform.

It is designed so a learner can inherit the repository as if joining a serious engineering organization, run the real product, read unfamiliar code, modify it in an IDE, test it, profile it, secure it, deploy it and observe the resulting change.

> **ATLAS is the project. The repository is the curriculum. The IDE is the playground.**

## Explicit non-goal

No dedicated DSA/LeetCode/interview-algorithm product area.

## Core loop

```text
run real product
→ trace implementation
→ read code
→ change code in IDE
→ test
→ observe
→ debug/profile
→ secure
→ deploy
→ scale/refactor/migrate
```

## Read order for Codex

1. `AGENTS.md`
2. `00_PRODUCT_IDENTITY.md`
3. `01_MASTER_BUILD_SPEC.md`
4. `02_MONOREPO_ARCHITECTURE.md`
5. `03_FRONTEND_AND_DESIGN_SYSTEM.md`
6. `04_DOMAIN_COVERAGE.md`
7. `05_DATA_SCIENCE_AI_ML.md`
8. `06_SECURITY_CYBERSECURITY.md`
9. `07_TESTING_QUALITY_RELIABILITY.md`
10. `08_LABS_DATASETS_BENCHMARKS.md`
11. `09_SYSTEM_DESIGN_CASE_STUDIES.md`
12. `10_PAGE_AND_COMPONENT_INVENTORY.md`
13. `11_IMPLEMENTATION_ROADMAP.md`
14. `12_CURRENT_TECH_NOTES.md`
15. `13_FRAMEWORK_LIBRARY_MATRIX.md`
16. `14_ECOSYSTEM_PARITY_AND_COMPLETENESS.md`
17. `15_EXPANDED_PRODUCT_SURFACES.md`
18. `16_TECHNOLOGY_REGISTRY.md`
19. `17_REPOSITORY_WORK_MODEL.md`
20. `18_OPEN_SOURCE_SOURCING_AND_PROVENANCE.md`
21. `19_AUTONOMOUS_EXECUTION_AND_COMPLETION.md`
22. `20_PROGRESSIVE_COMPLEXITY_AND_COMMENTS.md`
23. `STARTING_PROMPT_FOR_CODEX.md`

## Scope pillars

Programming, frontend, backend, mobile, desktop, CLI/TUI, databases/DBMS, search, files/media, data science, ML/deep learning, AI/LLM/agents/MCP, data engineering, Apache, streaming/messaging, workflows, cloud, DevOps/platform engineering, networking, cybersecurity/DevSecOps, observability/SRE, distributed systems, system design, testing/reliability, storage, virtualization/containers, WASM, geospatial, IoT/edge, HPC, compilers/DSLs, policy engines, feature flags/experimentation, billing/FinOps, governance/privacy/compliance, SDKs/plugins, disaster recovery/chaos and production support.

## Completeness model

A first-class ecosystem means the full stack.

Python is not only FastAPI:
- Django
- FastAPI
- Flask
- SQLAlchemy
- Django ORM
- drivers/query tooling
- validation
- migrations
- auth
- jobs
- queues
- caching
- GraphQL
- gRPC
- testing
- observability
- security
- packaging
- profiling
- data/AI
- major alternatives.

Node/TypeScript, Java, .NET, Go, Rust and other first-class ecosystems receive equivalent category coverage.

See `14_ECOSYSTEM_PARITY_AND_COMPLETENESS.md`.

## Definition of success

The learner can receive a realistic engineering ticket, locate the code, understand dependencies, change the actual implementation, run tests and visibly/measurably change the functioning product.

The repository itself is the mastery environment.


<!-- END START_HERE.md -->

---


<!-- BEGIN AGENTS.md -->

# AGENTS.md — Mandatory Instructions for Codex

This file is authoritative for work inside ATLAS.
Read `00_PRODUCT_IDENTITY.md` immediately after this file.

## Mission

Build ATLAS as a production-quality, extremely broad, polyglot enterprise technology platform.

ATLAS is the real application. The repository is the learning environment. The IDE is where the learner reads and changes code.

Do **not** reduce ATLAS to:
- a tutorial website,
- a coding playground,
- a static documentation portal,
- a collection of disconnected toy labs,
- a portfolio mockup.

Implement incrementally, but preserve the architecture required for the full scope.

## Critical rules

### 1. No DSA product area
Do not add a DSA, LeetCode or algorithm-practice section.
Algorithms/data structures may appear only when intrinsic to real systems.

### 2. Product-first, not lesson-first
Every major technology should power:
- a real product capability,
- a real adapter/provider,
- real infrastructure,
- real testing/security/observability,
or a clearly labeled reference/legacy implementation.

### 3. The IDE is the playground
Do not build embedded code-playground experiences as the main learning model.
Developer utilities may exist for real product/operational needs, but source modification is expected in the repository.

### 4. Ecosystem completeness
When a language becomes first-class, cover the complete engineering categories defined in:
- `14_ECOSYSTEM_PARITY_AND_COMPLETENESS.md`
- `16_TECHNOLOGY_REGISTRY.md`

Do not represent Python with only FastAPI, Node with only Express, Java with only Spring, etc.

### 5. Do not fake functionality
Buttons, dashboards, services, tests, integrations and pages must not be decorative placeholders when a reasonable implementation is possible.

### 6. Build vertical slices
Prefer:
UI → API → service → storage/events → tests → telemetry → security → deployment
over disconnected scaffolding.

### 7. Preserve modularity
The repository will become very large.
Enforce:
- module boundaries,
- stable contracts,
- typed interfaces,
- shared primitives,
- adapters/providers,
- dependency direction.

### 8. Tests are part of the feature
A feature is incomplete without appropriate tests.

### 9. Security is part of the feature
A feature is incomplete without validation, authn/authz where applicable, secrets hygiene, threat consideration and relevant security tests.

### 10. Observability is part of the feature
Important flows need structured logs.
Distributed/asynchronous flows should add metrics and traces.

### 11. Current dependency policy
Before installing/upgrading a major framework:
- inspect current official documentation,
- prefer stable releases,
- verify maintenance status,
- review license/security,
- avoid unnecessary dependencies,
- update the technology registry,
- record significant architecture decisions.

### 12. Third-party UI policy
Use shadcn/ui and owned source components heavily.
Community/online registry components require source, license, dependency and accessibility review plus ATLAS styling/tests.

### 13. Provider/adapter architecture
Where multiple technologies solve the same role, prefer stable interfaces and interchangeable implementations.

Examples:
- ORM/data access
- messaging
- cache
- object storage
- search
- analytics
- inference
- auth provider
- cloud provider
- feature flags.

### 14. Technology registry
Every significant technology must be recorded with:
- status
- category
- integration location
- alternatives
- version
- last verification.

### 15. Ticket-driven evolution
Add realistic engineering work for migrations, bugs, performance, security, reliability, data, AI and infrastructure.

## Preferred architecture

Use a monorepo.

Primary frontend:
- Next.js
- React
- TypeScript
- Tailwind
- shadcn/ui
- TanStack ecosystem where appropriate
- rich tables/charts/graphs
- strong accessibility.

Backends:
- Python services
- Node/TypeScript services
- Java/Spring services
- .NET services
- Go/Rust performance/infrastructure services
- additional first-class ecosystems over time.

Data:
- PostgreSQL
- Redis
- ClickHouse
- document/search/vector/graph stores where justified
- lake/lakehouse components.

Events/data:
- Kafka first-class
- alternative brokers behind adapters
- Spark/Flink/Airflow and related systems.

Infrastructure:
- Docker Compose
- Kubernetes
- Helm
- Terraform/OpenTofu concepts
- Ansible
- CI/CD
- observability
- security tooling.

## Monorepo standards

- TypeScript strict mode.
- Strong Python typing.
- Language-appropriate lint/format/static analysis.
- No secrets committed.
- Safe `.env.example`.
- checked-in migrations.
- deterministic seeds where needed.
- idempotent setup.
- explicit ports/service names.
- structured configuration.
- feature flags for optional/heavy subsystems.
- reproducible build/test commands.

## Frontend standards

The UI is a real enterprise product.

Use:
- persistent shell
- global search
- workspaces
- dense tables
- dashboards
- diagrams
- logs/traces
- security findings
- data explorers
- AI/agent views
- infrastructure views
- settings/admin.

Do not make lesson pages the central navigation.

## Secure failure examples

Security/failure scenarios must be local/isolated, authorized and non-public by default.

Prefer:
**detect → explain → patch → regression test → monitor**.

## Working style

Before a large change:
1. read context,
2. inspect implementation,
3. inspect registry,
4. choose coherent vertical slice,
5. implement,
6. lint/typecheck/test,
7. verify security/telemetry,
8. update registry/ADRs/work items,
9. leave repository runnable.

Do not endlessly scaffold.
Every milestone should produce functioning ATLAS behavior.

## Autonomous completion

Follow `19_AUTONOMOUS_EXECUTION_AND_COMPLETION.md`.

Do not voluntarily stop after a plan or milestone when implementation work remains. Continue to the next roadmap item after verification. If session/tool limits prevent continuation, leave `CHECKPOINT.md` and `.atlas/progress.json` with exact continuation state.

## Open-source reuse

Follow `18_OPEN_SOURCE_SOURCING_AND_PROVENANCE.md`.

Use official/open-source code aggressively as reference and dependency input, but never blindly merge unrelated repositories. Preserve ATLAS-owned architecture, provenance, licensing and security.

## Progressive complexity

Follow `20_PROGRESSIVE_COMPLEXITY_AND_COMMENTS.md`.

Every first-class technology must expose a deliberate evolution from a smallest meaningful implementation to realistic, advanced, distributed, production-hardened and expert/alternative forms where applicable.

Complexity must be earned by requirements. Do not begin with unnecessary distributed architecture.

The website must expose progression status and source locations, while the IDE remains the main code-editing environment.

## Commenting requirement

ATLAS code should be unusually readable.

Add extensive **high-value** comments and language-native documentation for non-obvious behavior, architecture, invariants, framework lifecycle, transaction boundaries, concurrency, security, performance and failure behavior.

Do not comment obvious syntax line-by-line.


<!-- END AGENTS.md -->

---


<!-- BEGIN 00_PRODUCT_IDENTITY.md -->

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


<!-- END 00_PRODUCT_IDENTITY.md -->

---


<!-- BEGIN CODEX_TASK.md -->

# Codex Task — Build the Entire ATLAS Platform

Read every context file in the documented order.

Build ATLAS as a real, production-style, polyglot enterprise platform whose codebase intentionally spans an extremely broad range of technologies.

## Non-negotiable interpretation

ATLAS is not primarily:
- a tutorial site,
- a coding playground,
- an interactive course.

The learner works from the IDE.

## Breadth

When a major ecosystem is included, cover its full engineering stack.

Python: Django, FastAPI, Flask, SQLAlchemy, Django ORM, migrations, drivers, jobs, queues, auth, validation, GraphQL, gRPC, caching, testing, observability, security, packaging, profiling, data/AI and major alternatives.

Node/TypeScript: equivalent breadth, including Express, Fastify, NestJS, Prisma, Drizzle, TypeORM and equivalent solutions for all major backend concerns.

Apply the same rule to Java, .NET/C#, Go, Rust, Kotlin, Scala, PHP, Ruby, Elixir, Swift, Dart/Flutter, C/C++ and other ecosystems promoted to first-class status.

Use the parity matrix and technology registry.

## Product rule

Technologies must power real ATLAS features or real interchangeable implementations.

## No DSA

Do not create a DSA product area.

## Priorities

1. product foundation
2. architecture/contracts
3. reusable frontend system
4. real backend services
5. database/event/data infrastructure
6. tests/security/telemetry
7. technology registry
8. engineering backlog
9. ecosystem expansion
10. product-surface expansion

For every feature:
- implement real behavior
- run tests
- typecheck/lint
- secure it
- instrument it
- document significant decisions
- update registry
- update work metadata
- keep local setup reproducible.

Do not respond to implementation requests with only planning.
Do not fill the repo with empty routes/fake cards.
Do not globally install every library merely to claim coverage.

## Completion behavior

Generate all files/code/configuration required by ATLAS.

Do not voluntarily stop after planning or after a roadmap milestone. Verify the current slice, update progress, and continue to the next incomplete slice.

When an execution/session/tool limit forces a stop, write `CHECKPOINT.md` and `.atlas/progress.json` exactly as required by `19_AUTONOMOUS_EXECUTION_AND_COMPLETION.md`, then resume from them on the next run.

Follow the open-source sourcing/provenance policy rather than patching unrelated repositories together.

## Progression and code readability

Every first-class technology must have progressive complexity metadata and implementation paths, from simple/foundation code through realistic/advanced/distributed/production/expert forms where appropriate.

Keep source extensively but intelligently commented. Explain architectural rationale, invariants, failure behavior, security, concurrency and performance—not obvious syntax.

The website should include a progression explorer that links each level back to real repository source paths and engineering work items.


<!-- END CODEX_TASK.md -->

---


<!-- BEGIN 01_MASTER_BUILD_SPEC.md -->

# ATLAS Master Build Specification

> `00_PRODUCT_IDENTITY.md` is authoritative for product identity.

## Product statement

ATLAS is a large production-style enterprise technology platform intentionally designed as a multidisciplinary codebase.

The user learns by opening the repository in an IDE, running the actual product, tracing real implementation, and changing source.

The product exposes real enterprise capabilities across analytics, data, AI, infrastructure, observability, security, automation, developer tooling, integrations, mobile/desktop clients and operations.

ATLAS may contain diagnostic/developer surfaces, but it is not centered around an embedded coding playground.

---

# 1. Core engineering actions

## Use
Operate the actual ATLAS product.

## Read
Trace a feature through frontend, API, service, storage/events and infrastructure.

## Change
Modify the real implementation from the IDE.

## Test
Run unit, integration, API, UI, contract, performance and security suites.

## Benchmark
Measure real implementations and interchangeable providers.

## Break
Introduce controlled failures against ATLAS-owned infrastructure.

## Debug
Inspect logs, metrics, traces, profiles, query plans and tests.

## Secure
Threat-model, scan, patch and verify the actual system.

## Observe
Inspect health, latency, throughput, resource usage, queues and incidents.

## Deploy
Run locally, containers, Kubernetes and selected cloud environments.

## Scale
Change load, data size, workers, replicas, partitions, providers and architecture.

---

# 2. Product dashboard and engineering operations surface

The main dashboard should eventually expose real product and engineering state:

- failed tests,
- benchmark history,
- datasets used,
- active local services,
- lab health,
- recent security findings,
- saved code variants,
- challenges,
- bookmarks,
- notes,
- global resource consumption if lab services are running.

Example domain cards:

- Python
- Web Engineering
- Backend
- Databases / DBMS
- Data Science
- Machine Learning
- Deep Learning
- AI Engineering
- Agents / MCP
- Data Engineering
- Apache Ecosystem
- DevOps
- Cloud
- Networking
- Security
- Testing
- Observability / SRE
- Distributed Systems
- System Design

---

# 3. Topic experience

A topic is not just Markdown.

A rich topic page may contain:

- title/summary,
- prerequisites,
- learning objectives,
- concept explanation,
- interactive architecture diagram,
- executable code snippet,
- editable code,
- output panel,
- logs,
- tests,
- resource usage,
- benchmark comparison,
- “break it” scenario,
- security notes,
- production notes,
- challenge,
- references.

A standard topic record should be data-driven so that hundreds of pages can be indexed consistently.

Suggested conceptual schema:

```ts
type Topic = {
  id: string
  slug: string
  domain: string
  title: string
  summary: string
  level: "foundation" | "intermediate" | "advanced" | "expert"
  prerequisites: string[]
  objectives: string[]
  tags: string[]
  sections: TopicSection[]
  labs: LabRef[]
  tests?: TestSuiteRef[]
  benchmarks?: BenchmarkRef[]
  securityNotes?: SecurityNote[]
  productionNotes?: string[]
  references: Reference[]
}
```

---

# 4. Lab experience

Every executable lab needs:

- lab manifest,
- prerequisites,
- required services,
- startup command,
- reset command,
- expected runtime state,
- tests,
- cleanup,
- safety boundaries,
- resource limits,
- sample inputs,
- expected output,
- explanation of what the learner should change.

Lab status UI:
- stopped,
- starting,
- ready,
- running,
- degraded,
- failed,
- resetting.

Lab controls:
- Start
- Stop
- Reset
- Seed
- Run
- Test
- Benchmark
- Inject Fault
- View Logs
- View Metrics
- View Trace
- Open Code
- Open Data
- Compare
- Export Result

---

# 5. Comparison-first learning

Create reusable comparison infrastructure.

Examples:
- Pandas vs Polars vs DuckDB vs Spark
- FastAPI vs Flask vs Django
- Express vs Fastify vs NestJS
- REST vs GraphQL vs gRPC
- PostgreSQL vs MongoDB for selected workloads
- Redis vs database reads for caching
- threads vs multiprocessing vs asyncio
- CPU vs GPU numerical workloads
- PyTorch vs TensorFlow implementations
- batch vs streaming
- Kafka vs traditional queue semantics
- SQL query with/without index
- monolith vs service split
- local process vs container
- Kubernetes scaling settings
- RAG retrieval strategies
- embedding models
- vector index strategies

Never publish universal winner claims from synthetic benchmarks. Clearly state workload, environment and limitations.

---

# 6. Failure-driven learning

Build a standardized fault injection system where safe.

Examples:
- stop Redis,
- kill a worker,
- kill a database replica,
- delay API responses,
- inject malformed data,
- expire auth token,
- duplicate an event,
- reorder events,
- simulate downstream 500s,
- fill a queue,
- throttle CPU,
- constrain memory,
- change data skew,
- remove an index,
- corrupt a config value,
- deny a permission,
- break DNS in a local lab,
- rotate a secret,
- fail an AI tool,
- return invalid structured LLM output,
- provide untrusted RAG content.

Each scenario requires:
1. hypothesis,
2. trigger,
3. expected symptoms,
4. observability signals,
5. diagnosis,
6. mitigation,
7. regression test.

---

# 7. Integrated capstone applications

ATLAS should contain multiple coherent projects rather than only isolated demos.

Suggested capstones:

## A. AI-powered financial analytics platform
Use as a flagship integration:
- Next.js frontend
- Python APIs
- TypeScript service
- PostgreSQL
- Redis
- event streaming
- analytics database
- data pipelines
- model service
- RAG/agent service
- observability
- containerization
- CI/CD
- security controls

## B. Real-time commerce/order platform
Teach:
- transactions,
- idempotency,
- queues,
- inventory,
- payments simulation,
- caching,
- distributed workflows,
- tracing,
- failure recovery.

## C. Streaming telemetry platform
Teach:
- Kafka,
- Flink/Spark streaming,
- time-series/analytics storage,
- dashboards,
- alerting,
- backpressure.

## D. Secure multi-tenant SaaS
Teach:
- tenancy models,
- RBAC/ABAC,
- billing simulation,
- auditing,
- rate limits,
- secure file uploads,
- row-level security.

## E. AI knowledge workbench
Teach:
- ingestion,
- chunking,
- embeddings,
- hybrid retrieval,
- reranking,
- citations,
- structured outputs,
- agent tools,
- evals,
- prompt-injection defenses.

## F. Distributed media service
Teach:
- object storage,
- CDN concepts,
- metadata,
- transcoding pipeline simulation,
- queues,
- caching,
- system design.

Each capstone must expose architecture, tests, telemetry and security posture in the UI.

---

# 8. Content scale

The architecture must comfortably support:
- hundreds of routes,
- hundreds of labs,
- large code-example catalogs,
- many datasets,
- multiple runtime services,
- thousands of metadata records.

Do not eagerly load everything into the browser.
Use indexing, search, lazy loading, route-level code splitting and server rendering where appropriate.

---

# 9. Search and discovery

Global search should index:
- topics,
- commands,
- language APIs,
- libraries,
- frameworks,
- labs,
- system designs,
- datasets,
- database commands,
- tests,
- errors/common failures,
- glossary terms.

Support filters:
- domain,
- technology,
- level,
- content type,
- runnable/not runnable,
- local/cloud,
- free/open source,
- estimated resource intensity.

---

# 10. Progress system

Track:
- viewed,
- started,
- completed,
- test passed,
- challenge solved,
- benchmark run,
- fault recovered,
- security lab remediated.

Progress must not be based only on opening a page.

---

# 11. Documentation/content architecture

Prefer MDX or structured content for narrative lessons, but keep:
- code examples in real source files when possible,
- manifests in machine-readable files,
- tests in real test suites,
- diagrams as data where possible,
- metadata in typed schemas.

Generate indexes/navigation from content metadata.

---

# 12. Accessibility and usability

Required:
- keyboard support,
- visible focus,
- semantic HTML,
- sufficient contrast,
- reduced motion support,
- screen-reader-friendly labels,
- accessible chart summaries where practical,
- responsive layouts,
- resizable panes,
- user-controlled dense/comfortable table modes.

---

# 13. Performance principles

- Avoid loading heavy editors/charting/canvas packages until needed.
- Virtualize huge tables/logs.
- Paginate server-side for very large datasets.
- Stream long-running lab output.
- Persist only useful client state.
- Cache immutable/reference content.
- Profile before optimizing.


<!-- END 01_MASTER_BUILD_SPEC.md -->

---


<!-- BEGIN 02_MONOREPO_ARCHITECTURE.md -->

# Monorepo Architecture

> **Product identity override:** Interpret this file through `00_PRODUCT_IDENTITY.md`. ATLAS is the real application; the IDE is the primary place for source modification. Any older “lesson/playground” wording means engineering documentation, operational tooling, reference modules, or controlled test environments—not the central product model.


## Goals

The monorepo must:
- support many languages,
- support many independently runnable labs,
- keep the primary product coherent,
- allow optional heavy services,
- make local onboarding possible,
- separate platform infrastructure from educational examples,
- support CI that does not rerun every expensive suite for every change.

## Proposed top-level structure

```text
atlas/
├── apps/
│   ├── web/                         # Next.js ATLAS UI
│   ├── api-python/                  # Primary FastAPI platform API
│   ├── api-node/                    # Node/TS teaching + selected platform services
│   ├── worker/                      # background jobs
│   ├── docs-indexer/                # content/search indexing
│   └── lab-orchestrator/            # starts/stops/resets safe local labs
│
├── packages/
│   ├── ui/                          # shared ATLAS UI system
│   ├── design-tokens/
│   ├── types/
│   ├── schemas/
│   ├── config/
│   ├── auth/
│   ├── telemetry/
│   ├── logger/
│   ├── api-client/
│   ├── content-engine/
│   ├── lab-sdk/
│   ├── benchmark-sdk/
│   ├── test-reporters/
│   ├── security-reporters/
│   └── visualization/
│
├── content/
│   ├── programming/
│   ├── web/
│   ├── databases/
│   ├── data-science/
│   ├── ml/
│   ├── deep-learning/
│   ├── ai-engineering/
│   ├── data-engineering/
│   ├── apache/
│   ├── devops/
│   ├── cloud/
│   ├── networking/
│   ├── security/
│   ├── testing/
│   ├── sre/
│   ├── distributed-systems/
│   └── system-design/
│
├── labs/
│   ├── python/
│   ├── frontend/
│   ├── backend/
│   ├── databases/
│   ├── data-science/
│   ├── ml/
│   ├── ai/
│   ├── data-engineering/
│   ├── apache/
│   ├── devops/
│   ├── cloud/
│   ├── security/
│   ├── networking/
│   └── distributed-systems/
│
├── examples/
│   ├── python/
│   ├── typescript/
│   ├── javascript/
│   ├── java/
│   ├── go/
│   ├── rust/
│   ├── cpp/
│   └── sql/
│
├── datasets/
│   ├── manifests/
│   ├── generators/
│   ├── samples/
│   └── schemas/
│
├── benchmarks/
│   ├── database/
│   ├── dataframes/
│   ├── api/
│   ├── concurrency/
│   ├── messaging/
│   ├── ml/
│   └── infrastructure/
│
├── security/
│   ├── threat-models/
│   ├── policies/
│   ├── scanners/
│   ├── secure-examples/
│   ├── vulnerable-labs/
│   └── incident-scenarios/
│
├── system-design/
│   ├── cases/
│   ├── diagrams/
│   ├── calculators/
│   └── simulations/
│
├── projects/
│   ├── financial-analytics/
│   ├── commerce-platform/
│   ├── telemetry-platform/
│   ├── multi-tenant-saas/
│   ├── ai-knowledge-workbench/
│   └── media-platform/
│
├── infra/
│   ├── docker/
│   ├── compose/
│   ├── kubernetes/
│   ├── helm/
│   ├── terraform/
│   ├── ansible/
│   ├── observability/
│   └── local/
│
├── tests/
│   ├── e2e/
│   ├── contracts/
│   ├── performance/
│   ├── security/
│   └── smoke/
│
├── scripts/
├── tools/
├── docs/
│   ├── adr/
│   ├── architecture/
│   ├── contributing/
│   └── runbooks/
│
├── .github/
│   └── workflows/
├── AGENTS.md
└── README.md
```

## Lab manifest

Every lab should eventually be describable by a manifest.

Example shape:

```yaml
id: postgres-index-basics
title: PostgreSQL Index Lab
domain: databases
runtime: docker
difficulty: intermediate

services:
  - postgres

resources:
  cpu: "1"
  memory: "1Gi"

commands:
  start: "./scripts/start.sh"
  reset: "./scripts/reset.sh"
  test: "./scripts/test.sh"
  benchmark: "./scripts/benchmark.sh"

safety:
  internet_access_required: false
  vulnerable_target: false

artifacts:
  - type: sql
    path: ./queries
  - type: test
    path: ./tests

telemetry:
  logs: true
  metrics: true
  traces: false
```

Build a typed schema and validator for manifests.

## Content metadata

Each content page should expose typed frontmatter:
- id
- slug
- title
- description
- domain
- technology
- level
- prerequisites
- tags
- labs
- related topics
- official references

## Service contracts

Platform services should use explicit OpenAPI/typed contracts.
For educational examples, additionally teach:
- REST
- GraphQL
- gRPC
- WebSockets
- SSE
- event contracts

## Data stores for platform metadata

Start simple:
- PostgreSQL for user/progress/content metadata that needs relational querying.
- Object/filesystem storage for generated artifacts and lab outputs.
- Redis only for valid cache/queue/session use cases.
- Search can begin with a lightweight index and later evolve.

Avoid using a technology merely to “check a box” in the platform core. Extra databases belong in labs unless there is a real platform requirement.

## Optional service profiles

Developer commands should allow profiles such as:
- core
- data
- ai
- observability
- security
- streaming
- full

A contributor should not need to boot Spark, Kafka, multiple vector databases and Kubernetes just to edit a button.

## Heavy labs

Large-data and cluster labs need scaled modes:
- tiny/local
- laptop
- cluster/cloud

Datasets should often be generated deterministically rather than storing giant binaries in Git.

## Architectural decision records

Create ADRs for:
- monorepo tooling,
- content engine,
- auth,
- lab isolation,
- database choices,
- search,
- telemetry,
- AI provider abstraction,
- deployment topology,
- security boundary changes.

<!-- END 02_MONOREPO_ARCHITECTURE.md -->

---


<!-- BEGIN 03_FRONTEND_AND_DESIGN_SYSTEM.md -->

# Frontend, Design System and Utility Component Specification

> **Product identity override:** Interpret this file through `00_PRODUCT_IDENTITY.md`. ATLAS is the real application; the IDE is the primary place for source modification. Any older “lesson/playground” wording means engineering documentation, operational tooling, reference modules, or controlled test environments—not the central product model.


## Goal

The frontend should be one of the most impressive parts of ATLAS: a dense but usable technical workspace capable of rendering lessons, code, datasets, tests, infrastructure, system diagrams, AI conversations, security findings and observability.

It must not become a generic card-grid dashboard.

## Primary stack

Preferred:
- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- shadcn Base UI path for new projects/components where appropriate
- Radix compatibility where an existing component or ecosystem need warrants it
- Lucide icon set or the icon library configured by shadcn
- TanStack Query
- TanStack Table
- React Hook Form
- schema validation
- Monaco Editor for deep code editing
- React Flow / XYFlow-style graph canvas for architectures/workflows
- charting library selected deliberately for each visualization class

Use current official docs when installing.

## shadcn baseline

As of the 2026 shadcn documentation, the official component catalog includes primitives and composites such as:

- Accordion
- Alert
- Alert Dialog
- Aspect Ratio
- Attachment
- Avatar
- Badge
- Breadcrumb
- Bubble
- Button
- Button Group
- Calendar
- Card
- Carousel
- Chart
- Checkbox
- Collapsible
- Combobox
- Command
- Context Menu
- Data Table
- Date Picker
- Dialog
- Direction
- Drawer
- Dropdown Menu
- Empty
- Field
- Hover Card
- Input
- Input Group
- Input OTP
- Item
- Kbd
- Label
- Marker
- Menubar
- Message
- Message Scroller
- Native Select
- Navigation Menu
- Pagination
- Popover
- Progress
- Questionnaire
- Radio Group
- Resizable
- Scroll Area
- Select
- Separator
- Sheet
- Sidebar
- Skeleton
- Slider
- Spinner
- Switch
- Table
- Tabs
- Textarea
- Toast
- Toggle
- Toggle Group
- Tooltip
- Typography

Use these as source-owned components, not as untouchable package abstractions.

## Required ATLAS component layers

### Layer 1 — primitives
Keep `/components/ui` close to shadcn primitives.

### Layer 2 — composed application components
Examples:
- AppShell
- AppSidebar
- DomainSidebar
- MobileNav
- TopNav
- WorkspaceHeader
- BreadcrumbBar
- ContextToolbar
- CommandPalette
- GlobalSearch
- SearchFilters
- QuickSwitcher
- UserMenu
- ThemeToggle
- DensityToggle
- SplitPane
- ResizableWorkspace
- InspectorPanel
- BottomPanel
- StatusBar
- ShortcutHelp
- NotificationCenter

### Layer 3 — learning components
Create:
- TopicHeader
- LearningObjectives
- PrerequisiteGraph
- ConceptCallout
- DefinitionCard
- FormulaBlock
- MathRenderer
- CodeExample
- EditableCodeExample
- ExpectedOutput
- StepRunner
- ExerciseCard
- ChallengePanel
- HintPanel
- SolutionReveal
- CommonMistake
- ProductionNote
- SecurityNote
- PerformanceNote
- FurtherReading
- TopicNavigator
- RelatedTopics
- ProgressCheckpoint
- KnowledgeCheck
- GlossaryPopover
- Citation/ReferenceList
- CompareConcepts
- TimelineExplainer

### Layer 4 — code and runtime utilities
Create:
- MonacoCodeEditor
- ReadOnlyCodeViewer
- DiffViewer
- MultiFileEditor
- FileTree
- TabsForFiles
- TerminalPanel
- CommandRunner
- ProcessList
- EnvironmentVariableViewer
- HTTPRequestBuilder
- HTTPResponseViewer
- WebSocketConsole
- SSEViewer
- GraphQLExplorer
- gRPCRequestPanel
- JSONViewer
- YAMLViewer
- TOMLViewer
- XMLViewer
- CSVViewer
- HexViewer
- StackTraceViewer
- LogViewer
- StructuredLogViewer
- LogFilterBar
- RuntimeStatus
- ResourceMeter
- CPUChart
- MemoryChart
- NetworkChart
- DiskIOChart
- EventLoopLagChart
- FlameGraphContainer
- TraceWaterfall
- SpanDetails
- MetricsExplorer

### Layer 5 — testing utilities
Create:
- TestRunButton
- TestSuiteTree
- TestCaseRow
- TestStatusBadge
- TestSummary
- CoverageGauge
- CoverageFileTree
- CoverageHeatmap
- SnapshotDiff
- AssertionDetails
- PropertyTestResult
- FuzzRunPanel
- MutationScoreCard
- ContractTestMatrix
- E2ETimeline
- LoadTestControls
- LatencyHistogram
- ThroughputChart
- ErrorRateChart
- VirtualUsersChart
- TestArtifactViewer

### Layer 6 — data utilities
Create:
- DatasetBrowser
- DatasetCard
- DatasetMetadata
- SchemaTable
- DataGrid
- VirtualizedDataGrid
- ColumnInspector
- RowInspector
- MissingValuesPanel
- DuplicateAnalyzer
- OutlierExplorer
- DistributionChart
- CorrelationMatrix
- PairPlotContainer
- BoxPlot
- Histogram
- ScatterPlot
- TimeSeriesChart
- CategoricalFrequencyChart
- DataProfiler
- FilterBuilder
- QueryBuilder
- SQLConsole
- DuckDBConsole
- DataTransformationPipeline
- BeforeAfterDataDiff
- DataQualityScore
- DataQualityRuleBuilder
- SamplingControls
- DataSizeSelector
- ExportControls

### Layer 7 — ML utilities
Create:
- ExperimentTracker
- ExperimentRunCard
- HyperparameterTable
- HyperparameterSearchViewer
- TrainingCurve
- LossChart
- MetricChart
- ConfusionMatrix
- ROCChart
- PRCurve
- FeatureImportanceChart
- SHAPViewerAdapter
- PredictionExplorer
- ErrorAnalysisTable
- ModelComparison
- ModelCard
- ModelRegistryTable
- DatasetSplitViewer
- PipelineDiagram
- FeaturePipeline
- InferencePlayground
- BatchInferencePanel
- ModelLatencyChart
- ModelSizeCard
- CheckpointBrowser
- EmbeddingProjectorContainer

### Layer 8 — AI/LLM utilities
Use current shadcn chat primitives and, where valuable, AI-focused open components.

Create:
- AIChatWorkspace
- MessageThread
- StreamingMessage
- ReasoningStatus
- ToolCallCard
- ToolResultCard
- ToolApprovalDialog
- AgentStatus
- AgentTimeline
- AgentGraph
- PromptEditor
- PromptVersionHistory
- SystemPromptPanel
- TokenCounter
- TokenUsageChart
- ContextWindowMeter
- ModelSelector
- ProviderSelector
- TemperatureControls
- StructuredOutputViewer
- JSONSchemaEditor
- RAGPlayground
- RetrievalResults
- ChunkViewer
- ChunkingControls
- EmbeddingSimilarityViewer
- RerankingResults
- CitationViewer
- GroundednessPanel
- EvalSuitePanel
- EvalScoreCard
- HallucinationReview
- PromptInjectionAlert
- AgentPermissionMatrix
- HumanApprovalQueue
- MemoryInspector
- ConversationStateInspector
- MCPServerList
- MCPToolBrowser
- MCPResourceBrowser
- ToolSchemaViewer
- MultiAgentBoard

### Layer 9 — database utilities
Create:
- DatabaseExplorer
- ConnectionStatus
- SchemaExplorer
- TableExplorer
- ERDiagram
- QueryEditor
- QueryResultGrid
- QueryHistory
- ExplainPlanViewer
- ExplainAnalyzeTree
- IndexInspector
- IndexUsageCard
- LockViewer
- TransactionTimeline
- IsolationLevelSimulator
- MVCCVisualizer
- ConnectionPoolViewer
- ReplicationTopology
- ReplicaLagChart
- PartitionViewer
- ShardMap
- SlowQueryTable
- CacheHitChart
- WALViewer
- DatabaseMetricsPanel

### Layer 10 — streaming/data-engineering utilities
Create:
- TopicExplorer
- PartitionMap
- ProducerConsole
- ConsumerConsole
- ConsumerGroupViewer
- ConsumerLagChart
- MessageInspector
- SchemaRegistryViewer
- EventTimeline
- EventReplayPanel
- DeadLetterQueueViewer
- PipelineCanvas
- DAGViewer
- JobRunTimeline
- BackpressureViewer
- CheckpointViewer
- WatermarkVisualizer
- WindowingVisualizer
- BatchVsStreamComparison
- LineageGraph
- DataCatalogExplorer

### Layer 11 — DevOps/cloud utilities
Create:
- ServiceTopology
- ContainerList
- ContainerDetails
- DockerImageExplorer
- DockerLayerViewer
- KubernetesClusterOverview
- NamespaceSelector
- PodTable
- PodDetails
- DeploymentViewer
- ReplicaSetViewer
- ServiceViewer
- IngressViewer
- ConfigMapViewer
- SecretMetadataViewer
- HPAViewer
- ResourceRequestsLimits
- KubeEventTimeline
- HelmReleaseViewer
- TerraformPlanViewer
- TerraformStateExplorer
- IaCResourceGraph
- CICDPipeline
- PipelineRunDetails
- BuildLog
- ArtifactBrowser
- DeploymentTimeline
- RolloutViewer
- RollbackControls
- CloudResourceExplorer
- CostEstimateCard
- RegionMap
- AvailabilityZoneDiagram

### Layer 12 — observability/SRE utilities
Create:
- ServiceHealthGrid
- SLOCard
- SLIChart
- ErrorBudgetGauge
- BurnRateChart
- IncidentTimeline
- AlertList
- AlertDetails
- TraceExplorer
- MetricsDashboard
- LogSearch
- CorrelationView
- REDDashboard
- USEMethodDashboard
- GoldenSignalsPanel
- OnCallRunbookViewer
- PostmortemViewer
- DependencyMap

### Layer 13 — security utilities
Create:
- SecurityOverview
- FindingCard
- FindingTable
- SeverityBadge
- VulnerabilityDetails
- CVEReferencePanel
- DependencyRiskTable
- SecretScanResult
- SASTFindingViewer
- DASTFindingViewer
- ContainerScanViewer
- SBOMExplorer
- LicenseRiskTable
- ThreatModelCanvas
- STRIDEChecklist
- AttackSurfaceMap
- TrustBoundaryDiagram
- PermissionMatrix
- RBACExplorer
- ABACPolicyViewer
- AuthFlowDiagram
- JWTInspector
- OAuthFlowVisualizer
- SessionInspector
- CSPBuilder
- SecurityHeadersViewer
- AuditLogViewer
- DetectionRuleViewer
- SIEMEventTable
- IncidentResponseBoard
- EvidenceTimeline
- RemediationChecklist
- SecurityRegressionStatus

### Layer 14 — system-design utilities
Create:
- ArchitectureCanvas
- ArchitectureNode
- ServiceNode
- DatabaseNode
- QueueNode
- CacheNode
- CDNNode
- LoadBalancerNode
- RegionNode
- ExternalSystemNode
- ArchitectureEdge
- TrustBoundary
- DataFlowOverlay
- RequestFlowAnimator
- FailureOverlay
- CapacityCalculator
- QPSCalculator
- StorageCalculator
- BandwidthCalculator
- CacheCalculator
- PartitionCalculator
- AvailabilityCalculator
- ReplicationCalculator
- BottleneckInspector
- ArchitectureComparison
- TradeoffMatrix
- DecisionRecordPanel

### Layer 15 — generic utilities
Create reusable:
- MetricCard
- StatStrip
- EmptyState
- ErrorState
- LoadingState
- OfflineState
- PermissionDeniedState
- NoResults
- FilterChips
- SortMenu
- ColumnPicker
- SavedViewMenu
- ExportMenu
- ImportDialog
- ConfirmDangerousAction
- CopyButton
- ShareStateButton
- KeyboardShortcut
- RelativeTime
- AbsoluteTime
- Duration
- ByteSize
- Percentage
- CodeBadge
- TechnologyBadge
- StatusPill
- SeverityPill
- VersionBadge
- EnvironmentBadge
- CollapsibleSection
- FullscreenPanel
- StickyToolbar
- FloatingActions
- SideInspector
- DetailDrawer
- MasterDetail
- VirtualList
- InfiniteList
- SearchHighlight
- MarkdownRenderer
- MDXRenderer
- MermaidRenderer
- DiagramExport
- DownloadArtifact
- UploadDropzone
- FilePreview
- ErrorBoundary
- ClientOnly
- CopyableValue
- KeyValueTable
- DefinitionList
- ObjectInspector
- Timeline
- ActivityFeed
- Stepper
- Wizard
- DiffBadge

## Pages and layouts

Use multiple layout archetypes:

1. **Reading layout** — prose + sticky outline + code.
2. **Lab layout** — instructions + workspace + outputs.
3. **IDE layout** — file tree + editor + terminal + tests.
4. **Data layout** — schema + grid + profiling + charts.
5. **Observability layout** — dashboards + logs + traces.
6. **Architecture layout** — full canvas + inspector.
7. **Security layout** — findings + threat model + remediation.
8. **AI layout** — chat/workflow + context/tool/eval sidebars.
9. **Dashboard layout** — metrics and activity.
10. **Comparison layout** — synchronized variants + benchmark results.

## Visual direction

- technical, dense, polished, not childish,
- clear hierarchy,
- restrained motion,
- excellent dark mode,
- readable light mode,
- monospace only where technical,
- spacious reading pages,
- compact operational dashboards,
- consistent semantic colors for success/warning/error/info,
- do not rely on color alone,
- excellent empty/loading/error states.

## Online/community component usage

Codex may use reputable open-source UI components from online registries if they:
- solve a real interaction need,
- can be source-audited,
- have compatible licensing,
- do not balloon dependencies,
- meet accessibility expectations.

Adapt them into the ATLAS component layer. Do not create a visual collage of unrelated component styles.

## Storybook/component lab

Create a component development surface:
- states,
- variants,
- accessibility checks,
- interaction tests,
- responsive previews,
- dark/light,
- dense/comfortable,
- error/empty/loading examples.

## Frontend test baseline

Every important interactive utility needs:
- unit/component tests where useful,
- keyboard behavior tests,
- accessibility assertions,
- E2E coverage for critical flows.

<!-- END 03_FRONTEND_AND_DESIGN_SYSTEM.md -->

---


<!-- BEGIN 04_DOMAIN_COVERAGE.md -->

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

<!-- END 04_DOMAIN_COVERAGE.md -->

---


<!-- BEGIN 05_DATA_SCIENCE_AI_ML.md -->

# Data Science, AI/ML and AI Engineering Specification

> **Product identity override:** Interpret this file through `00_PRODUCT_IDENTITY.md`. ATLAS is the real application; the IDE is the primary place for source modification. Any older “lesson/playground” wording means engineering documentation, operational tooling, reference modules, or controlled test environments—not the central product model.


This is a first-class pillar of ATLAS and should be one of the largest areas.

# 1. Mathematical foundations

Create interactive explanations/labs for:
- vectors,
- matrices,
- matrix multiplication,
- norms,
- dot products,
- eigen concepts,
- probability,
- random variables,
- distributions,
- expectation/variance,
- conditional probability,
- Bayes,
- sampling,
- hypothesis testing,
- confidence intervals,
- correlation/covariance,
- calculus intuition,
- derivatives,
- gradients,
- chain rule,
- optimization,
- gradient descent,
- regularization,
- numerical stability.

Tie math to code and model behavior.

# 2. Numerical/data libraries

## NumPy
Cover:
- ndarrays,
- dtypes,
- shapes,
- indexing,
- slicing,
- broadcasting,
- vectorization,
- ufuncs,
- aggregation,
- random,
- linear algebra,
- memory layout,
- views vs copies,
- performance.

## pandas
Cover:
- Series/DataFrame,
- selection,
- filtering,
- grouping,
- aggregation,
- merges/joins,
- reshaping,
- missing data,
- strings,
- dates,
- categorical data,
- IO,
- windowing,
- time series,
- performance.

## Polars
Teach:
- expressions,
- eager/lazy,
- query optimization,
- streaming concepts,
- comparison with pandas.

## SciPy
Representative practical modules:
- optimization,
- stats,
- signal,
- spatial,
- integration/interpolation,
- sparse.

## DuckDB
Use as an analytical bridge between SQL, files and dataframes.

Also include relevant:
- PyArrow
- Dask concepts/labs
- distributed dataframes where meaningful.

# 3. EDA

EDA should have rich visual and code-driven labs:

- schema inspection,
- data types,
- descriptive statistics,
- missingness,
- duplicates,
- outliers,
- univariate distributions,
- bivariate/multivariate analysis,
- correlation,
- categorical analysis,
- temporal analysis,
- leakage detection,
- data quality,
- class imbalance,
- target analysis,
- sampling,
- transformation,
- feature generation.

Visualizations:
- histogram,
- KDE concept,
- box,
- violin,
- scatter,
- line,
- area,
- bar,
- heatmap,
- correlation matrix,
- pair relationships,
- residual plots,
- QQ concepts,
- geospatial where suitable.

Libraries:
- Matplotlib
- Plotly
- Altair
- additional well-maintained visualization libraries when they add educational value.

# 4. Dataset scaling ladder

Each major data lesson should support one or more scales:

- tiny: 100–1,000 rows
- small: 10k
- medium: 100k
- large: 1M
- very large: 10M+
- distributed mode: generated or external object-store data

Teach memory and execution tradeoffs.

# 5. Classical machine learning

Implement core algorithms in two styles where educationally valuable:

1. from-scratch / NumPy-oriented implementation,
2. production-style library implementation.

Topics:
- linear regression,
- polynomial regression,
- logistic regression,
- k-NN,
- Naive Bayes,
- decision trees,
- random forests,
- gradient boosting,
- XGBoost,
- LightGBM,
- CatBoost,
- SVM,
- clustering,
- k-means,
- hierarchical clustering,
- DBSCAN,
- PCA,
- dimensionality reduction concepts,
- anomaly detection,
- ensembles,
- calibration.

Workflows:
- train/validation/test,
- cross-validation,
- preprocessing,
- pipelines,
- feature selection,
- hyperparameter tuning,
- metrics,
- leakage,
- bias/variance,
- class imbalance,
- model interpretation.

# 6. Deep learning

Primary deep-learning teaching stack should include PyTorch.
Also cover TensorFlow/Keras and JAX concepts/selected examples.

Topics:
- tensors,
- autodiff,
- layers,
- activation functions,
- loss functions,
- optimizers,
- initialization,
- normalization,
- regularization,
- training loop,
- validation,
- checkpointing,
- mixed precision,
- GPU use,
- distributed training concepts,
- CNNs,
- RNNs,
- LSTMs/GRUs,
- attention,
- transformers.

# 7. NLP

- text preprocessing,
- tokenization,
- n-grams,
- classical features,
- embeddings,
- classification,
- NER,
- similarity,
- retrieval,
- transformers,
- sequence-to-sequence concepts,
- evaluation.

# 8. Computer vision

- image representation,
- OpenCV,
- preprocessing,
- augmentation,
- CNNs,
- classification,
- object detection concepts,
- segmentation concepts,
- embeddings,
- transfer learning,
- evaluation,
- inference.

# 9. Time series

- resampling,
- decomposition,
- trends/seasonality,
- lag features,
- rolling windows,
- forecasting metrics,
- classical models,
- ML models,
- deep-learning approaches,
- anomaly detection,
- backtesting.

# 10. Recommendation systems

- popularity baselines,
- collaborative filtering,
- matrix factorization,
- content-based,
- ranking,
- retrieval + ranking,
- implicit feedback,
- cold start,
- offline evaluation,
- serving concepts.

# 11. Reinforcement learning

Cover foundations without pretending RL is needed everywhere:
- state/action/reward,
- policies,
- value functions,
- exploration,
- bandits,
- Q-learning,
- policy-gradient concepts,
- simulation environments.

# 12. MLOps

- experiment tracking,
- MLflow,
- data/version tracking,
- model registry,
- reproducibility,
- feature pipelines,
- model packaging,
- online/batch inference,
- model serving,
- monitoring,
- drift,
- evaluation,
- rollback,
- canary model deployment,
- data quality,
- governance concepts.

# 13. LLM engineering

Teach:
- tokenizer behavior,
- context windows,
- prompting,
- system/user/tool roles,
- structured outputs,
- tool calling,
- embeddings,
- semantic similarity,
- chunking,
- vector indexing,
- hybrid search,
- reranking,
- RAG,
- citations/grounding,
- conversation memory,
- caching,
- streaming,
- latency,
- throughput,
- batching,
- quantization,
- local model serving,
- fine-tuning concepts,
- adapters/LoRA concepts,
- evaluation,
- cost modeling,
- observability.

Support provider abstraction:
- local models,
- open models,
- hosted providers.
Do not hard-code the product to one vendor.

# 14. Agentic AI

Teach progressively:

## Single-agent
- instructions,
- tools,
- state,
- memory,
- retries,
- limits,
- approvals.

## Workflow agents
- deterministic graph,
- conditional routing,
- parallel branches,
- retries,
- checkpoints,
- human-in-the-loop.

## Multi-agent
- planner,
- specialist agents,
- critic/reviewer,
- tool isolation,
- shared vs private state,
- coordination failure modes.

Framework coverage can include current well-maintained tools such as:
- LangChain concepts,
- LangGraph,
- AutoGen-style patterns,
- Crew-style orchestration patterns,
- direct SDK implementations.

Do not teach frameworks without also showing framework-free foundations.

# 15. MCP/tool protocol area

Create:
- MCP architecture explanation,
- server/client mental model,
- tools/resources/prompts where applicable,
- local mock MCP servers,
- schema inspection,
- permissions,
- retries,
- timeouts,
- tool failures,
- audit logs,
- agent-tool contracts,
- integration examples.

The frontend should include an MCP explorer.

# 16. AI evaluation

Create reusable evaluation infrastructure:
- exact-match where applicable,
- semantic similarity,
- LLM-as-judge concepts with caveats,
- groundedness,
- citation correctness,
- retrieval recall/precision,
- tool-use success,
- structured output validity,
- safety checks,
- latency,
- cost/token usage,
- regression suites.

# 17. AI security

Cross-reference the security spec:
- prompt injection,
- indirect prompt injection,
- data exfiltration risks,
- tool privilege,
- insecure output handling,
- RAG poisoning,
- untrusted content,
- multi-tenant isolation,
- secret leakage,
- approval boundaries,
- sandboxing,
- auditability.

# 18. AI lab examples

Examples:
- compare chunk sizes,
- compare embedding models,
- compare retrieval strategies,
- compare rerankers,
- evaluate RAG answer quality,
- break structured output,
- recover from tool timeout,
- revoke a tool permission,
- inspect context usage,
- run local model vs hosted model,
- quantization tradeoff lab,
- prompt regression suite,
- agent workflow replay.

<!-- END 05_DATA_SCIENCE_AI_ML.md -->

---


<!-- BEGIN 06_SECURITY_CYBERSECURITY.md -->

# Security, Cybersecurity and DevSecOps Specification

Security is both:
1. a dedicated learning domain,
2. a cross-cutting requirement for every major feature.

The learning emphasis is defensive and engineering-oriented:
**identify → understand → remediate → test → monitor**.

Security labs must target only local/owned/authorized systems.

# 1. Security foundations

- CIA triad
- threat, vulnerability, risk
- assets
- attack surface
- trust boundaries
- least privilege
- defense in depth
- zero-trust principles
- secure defaults
- fail-safe behavior
- security controls
- threat modeling
- risk assessment
- security requirements

# 2. Cryptography

Teach concepts and safe library use:
- hashes
- password hashing
- salts
- MAC/HMAC
- symmetric encryption
- asymmetric encryption
- key exchange concepts
- digital signatures
- certificates
- PKI
- TLS
- key rotation
- key management
- randomness
- nonce/IV concepts

Clearly distinguish educational primitives from production-safe APIs.
Do not encourage designing custom cryptography.

# 3. Identity and access

- passwords
- MFA
- sessions
- secure cookies
- JWT
- OAuth 2
- OIDC
- SSO
- API keys
- service identities
- RBAC
- ABAC
- policy evaluation
- least privilege
- privilege boundaries
- secret storage
- rotation
- account lifecycle
- audit trails

Build interactive flow visualizers.

# 4. Application security

Teach major OWASP-style classes through local vulnerable/secure pairs:

- injection
- SQL injection
- command injection
- XSS
- CSRF
- SSRF
- path traversal
- insecure file upload
- unsafe deserialization concepts
- broken access control
- authentication failures
- session weaknesses
- misconfiguration
- dependency risk
- sensitive-data exposure
- insecure error handling
- mass assignment concepts
- rate-limit failures
- business-logic abuse
- request smuggling concepts where safe and appropriate
- CORS mistakes
- security headers
- CSP

Every vulnerable example requires:
- explanation,
- secure implementation,
- regression test.

# 5. API security

- authentication
- authorization
- object-level access checks
- input validation
- schemas
- pagination limits
- rate limits
- idempotency
- abuse controls
- replay concerns
- signing where appropriate
- webhook verification
- API gateways
- error sanitization
- audit logs

# 6. Browser/frontend security

- XSS
- DOM sinks
- CSP
- CSRF
- cookies
- SameSite
- storage choices
- clickjacking defense
- iframe policy
- dependency risks
- supply-chain risks
- source maps/secrets
- server/client boundaries
- secure handling of auth state.

# 7. Database security

- parameterized queries
- roles
- grants
- row-level security
- encryption
- credential rotation
- network isolation
- backups
- audit logs
- injection regression tests
- least-privileged service users.

# 8. Network security

- segmentation
- firewall concepts
- WAF
- VPN
- TLS
- DNS security concepts
- proxies
- IDS/IPS concepts
- packet analysis in controlled labs
- secure service-to-service communication
- network policy
- zero-trust network ideas.

# 9. Cloud security

Across AWS/Azure/GCP teach:
- IAM
- roles/service identities
- organization/account/project boundaries
- network segmentation
- security groups/firewalls
- secrets
- key management
- storage permissions
- logging/auditing
- public exposure
- metadata/service identity concepts
- managed database security
- container security
- common misconfigurations
- cost abuse protections.

# 10. Container and Kubernetes security

- image provenance
- minimal images
- non-root users
- capabilities
- filesystem permissions
- secrets
- image scanning
- SBOM
- Kubernetes RBAC
- namespaces
- NetworkPolicy
- admission controls
- security contexts
- resource limits
- runtime monitoring
- audit logs.

# 11. Software supply chain

- dependency inventory
- lockfiles
- integrity
- vulnerability scanning
- malicious/compromised package risks
- SBOM
- provenance
- signing
- artifact integrity
- CI permissions
- dependency pinning/update policy
- license scanning
- secret scanning.

# 12. DevSecOps pipeline

Target pipeline:

```text
commit
  ↓
format/lint/typecheck
  ↓
unit tests
  ↓
SAST
  ↓
secret scan
  ↓
dependency/SCA scan
  ↓
build
  ↓
SBOM
  ↓
container/IaC scan
  ↓
integration/contract tests
  ↓
deploy isolated staging
  ↓
DAST / security regression
  ↓
E2E / performance smoke
  ↓
promotion gate
```

Critical findings may block promotion based on policy.

# 13. Security tooling

Use representative free/open tooling where appropriate:
- Semgrep
- Bandit
- Ruff security-relevant linting where applicable
- dependency scanners
- Trivy
- Grype
- Syft/SBOM concepts
- Gitleaks-style secret scanning
- OWASP ZAP
- JMeter for load/security-adjacent testing where applicable
- container/IaC scanners
- browser security tooling

Verify current project status before adopting.

# 14. Detection and security operations

Teach:
- logs
- audit events
- normalization
- detection logic
- severity
- alert triage
- false positives
- correlation
- SIEM concepts
- anomaly detection concepts
- response playbooks.

Build a Security Operations dashboard with:
- auth failures,
- rate limits,
- blocked requests,
- suspicious events,
- findings,
- service posture,
- incident timeline.

# 15. Incident response

Teach:
- preparation
- identification
- containment
- eradication
- recovery
- lessons learned
- evidence handling concepts
- communication
- postmortems.

Local incident scenarios:
- leaked development secret
- compromised test credential
- vulnerable dependency
- public-storage misconfiguration simulation
- suspicious auth behavior
- malicious input causing application alert
- unauthorized tool request from an AI agent.

# 16. Threat modeling

Every large system-design case should have:
- assets
- actors
- entry points
- data flows
- trust boundaries
- STRIDE-style analysis
- mitigations
- residual risks.

Frontend needs a threat-model canvas.

# 17. AI/agent security

This is mandatory for AI engineering.

Cover:
- prompt injection
- indirect prompt injection
- RAG poisoning
- untrusted tool output
- data leakage
- unsafe tool invocation
- confused-deputy risks
- over-privileged agent
- cross-tenant context leakage
- unsafe code execution
- sensitive logging
- output validation
- human approvals
- sandboxing
- rate limits
- audit trails
- allowlists
- scoped credentials
- tool contracts.

Example policy:

```text
Agent
  └── Tool Gateway
      ├── file.read             allowed in workspace
      ├── file.write            approval or scoped
      ├── db.select             allowed
      ├── db.mutate             restricted
      ├── cloud.read            allowed in lab account
      └── cloud.deploy          explicit approval
```

# 18. Vulnerable-vs-secure pattern

For selected topics:

```text
labs/security/sql-injection/
├── vulnerable/
├── secure/
├── tests/
├── threat-model.md
└── remediation.md
```

The vulnerable version must not expose arbitrary public targets.

# 19. Security acceptance criteria

For each major app:
- secrets absent from source,
- authn/authz boundaries documented,
- validation present,
- relevant security headers,
- dependency scan,
- container scan if containerized,
- security regression tests for known lab vulnerabilities,
- audit events for sensitive actions,
- threat model,
- safe error handling,
- least-privileged service configuration where practical.


<!-- END 06_SECURITY_CYBERSECURITY.md -->

---


<!-- BEGIN 07_TESTING_QUALITY_RELIABILITY.md -->

# Testing, Quality and Reliability Specification

Testing is a product feature, not only a CI concern.

# 1. Test taxonomy

ATLAS should demonstrate:

- unit testing
- component testing
- integration testing
- API testing
- database testing
- contract testing
- end-to-end testing
- smoke testing
- regression testing
- snapshot testing where appropriate
- accessibility testing
- visual regression concepts
- property-based testing
- fuzz testing
- mutation testing
- load testing
- stress testing
- spike testing
- soak/endurance testing
- resilience testing
- chaos/fault-injection testing
- security testing
- data quality tests
- ML evaluation/regression tests
- AI/agent evaluation tests

# 2. Tool coverage

## Python
- pytest
- unittest
- Hypothesis
- coverage tooling
- tox/nox concepts
- mocking/fixtures
- async tests

## JS/TS
- Vitest/Jest concepts
- React Testing Library
- Playwright
- Cypress
- mocking/service worker concepts

## API
- typed client tests
- Postman/Newman-style workflow
- pytest/http client
- Supertest
- REST Assured concepts for Java

## Java
- JUnit
- Spring testing patterns
- Testcontainers concepts

## Performance
- k6
- Locust
- Apache JMeter

## Security
Cross-reference security toolchain.

# 3. Test UI

Build a test center with:
- suite tree,
- live run status,
- pass/fail/skipped,
- duration,
- flaky marker,
- stack trace,
- logs,
- captured artifacts,
- snapshots,
- coverage,
- historical trends.

A learner should be able to intentionally break code and see exactly which tests catch it.

# 4. Coverage

Teach:
- statement,
- branch,
- function,
- line,
- why 100% coverage is not proof of correctness.

Visualize uncovered code.

# 5. Property-based testing

Labs:
- generate input ranges,
- discover edge cases,
- minimize failing case,
- compare example-based vs property-based tests.

# 6. Mutation testing

Show:
- mutation introduced,
- tests killed/survived mutation,
- mutation score,
- weak assertion examples.

# 7. Fuzzing

Only safe local code targets.
Teach:
- input generators,
- corpus,
- crash reproduction,
- shrinking/minimization concepts,
- invariants.

# 8. Performance tests

Standard metrics:
- latency p50/p95/p99
- requests/sec
- throughput
- error rate
- CPU
- memory
- saturation
- queue depth.

Benchmark metadata must include environment.

# 9. Reliability tests

Examples:
- dependency timeout
- dependency unavailable
- worker crash
- retry storm
- partial failure
- stale cache
- duplicate event
- out-of-order event
- database failover simulation
- network latency/loss
- resource exhaustion.

# 10. Testcontainers/local ephemeral services

Where appropriate, use isolated test services for:
- PostgreSQL
- Redis
- Kafka-compatible test flow
- object storage
- other databases.

Avoid shared mutable developer state in automated tests.

# 11. Contract testing

Teach:
- API contracts
- event contracts
- schema compatibility
- consumer/provider expectations
- backward compatibility.

# 12. Data testing

Teach tests for:
- schema
- nullability
- uniqueness
- ranges
- referential expectations
- distribution drift
- row counts
- freshness.

# 13. ML tests

- preprocessing invariants
- train/test leakage checks
- baseline comparison
- metric threshold
- reproducibility
- serialization
- inference schema
- latency
- drift checks.

# 14. AI/agent tests

- structured-output schema validation
- tool-call correctness
- no-tool cases
- tool timeout
- permission denial
- retrieval quality
- citation grounding
- prompt regression
- agent state transitions
- approval flow
- multi-step recovery.

# 15. CI strategy

Use change-aware jobs where practical.

Suggested stages:
1. lint/format
2. typecheck
3. unit/component
4. build
5. integration/contract
6. security
7. E2E
8. performance smoke
9. artifact/report publication

Heavy Spark/Kubernetes/cloud suites may be scheduled or opt-in rather than running on every UI edit.

# 16. Flaky-test discipline

Track:
- retries,
- quarantined tests,
- owner,
- reason,
- date,
- fix task.

Do not hide chronic failures behind unlimited retry logic.

# 17. Quality gates

At minimum:
- no lint errors,
- typecheck passes,
- relevant tests pass,
- build passes,
- critical security policy passes,
- migration checks pass when schemas change.


<!-- END 07_TESTING_QUALITY_RELIABILITY.md -->

---


<!-- BEGIN 08_LABS_DATASETS_BENCHMARKS.md -->

# Labs, Datasets, Benchmarks and Experiment Infrastructure

> **Product identity override:** Interpret this file through `00_PRODUCT_IDENTITY.md`. ATLAS is the real application; the IDE is the primary place for source modification. Any older “lesson/playground” wording means engineering documentation, operational tooling, reference modules, or controlled test environments—not the central product model.


## 1. Lab principles

Labs must be:
- reproducible,
- resettable,
- isolated,
- observable,
- small enough to run locally where possible,
- scalable to larger profiles when useful.

## 2. Lab lifecycle

```text
discover
  ↓
read prerequisites
  ↓
start
  ↓
seed
  ↓
observe baseline
  ↓
modify
  ↓
run
  ↓
test
  ↓
benchmark
  ↓
inject fault
  ↓
diagnose
  ↓
fix
  ↓
reset
```

## 3. Dataset catalog

Do not commit giant datasets blindly.

Each dataset needs a manifest:
- id
- name
- description
- source/license
- schema
- row count
- size
- target/label if relevant
- data quality notes
- PII/sensitivity classification
- checksum
- generation/download instructions.

Prefer:
- small checked-in samples,
- deterministic synthetic generators,
- download scripts for openly licensed public datasets,
- clear attribution/license.

## 4. Dataset classes

Create examples for:
- tabular
- time series
- text
- images
- logs/events
- graph
- geospatial
- transactional
- clickstream
- sensor/IoT
- financial synthetic data
- e-commerce synthetic data
- security event synthetic data.

## 5. Dirty-data laboratory

Create controlled datasets containing:
- missing values
- duplicate records
- bad types
- mixed date formats
- impossible ranges
- outliers
- encoding issues
- inconsistent categories
- skew
- leakage columns
- class imbalance
- schema drift.

## 6. Scale profiles

Dataset generators should support:
- 1k
- 10k
- 100k
- 1M
- 10M
- optionally 100M/distributed profile

Use generated data and document resource expectations.

## 7. Benchmark harness

A benchmark definition should record:
- benchmark id
- implementation
- input size
- warmup
- repetitions
- runtime
- hardware info where available
- dependency versions
- configuration
- result metrics
- notes.

## 8. Benchmark visualization

Frontend needs:
- comparison table,
- distribution plot,
- latency percentiles,
- throughput,
- memory,
- CPU,
- data-size scaling,
- configuration diff,
- run history.

## 9. Benchmark caveats

Always explain:
- synthetic workload limitations,
- cache effects,
- warm/cold behavior,
- hardware differences,
- network effects,
- correctness vs performance tradeoffs.

## 10. Suggested benchmark labs

### Python
- list vs generator memory
- loops vs vectorization
- asyncio vs threads vs processes for appropriate workloads
- serialization options

### Dataframes
- pandas vs Polars vs DuckDB
- groupby
- join
- filter
- CSV/Parquet scans

### Databases
- index vs no index
- join strategies
- read cache
- connection pooling
- bulk insert
- partitioning
- analytical queries

### APIs
- JSON REST throughput
- sync vs async server patterns
- REST vs GraphQL/gRPC for carefully scoped workloads

### Streaming
- partitions
- consumer count
- batching
- backpressure

### ML
- algorithm training time
- CPU/GPU
- batch inference
- quantized vs non-quantized model where available

### Infrastructure
- container resource limits
- HPA behavior
- cache on/off
- queue buffering.

## 11. Artifact capture

Every run may produce:
- stdout/stderr
- logs
- metrics
- traces
- test report
- benchmark JSON
- screenshots where useful
- generated plots
- query plans.

Use a common artifact model.

## 12. Reset discipline

Each stateful lab needs:
- reset data,
- remove generated resources,
- stop containers/processes,
- clean temporary credentials,
- verify clean state.

Cloud labs require an explicit teardown path.

<!-- END 08_LABS_DATASETS_BENCHMARKS.md -->

---


<!-- BEGIN 09_SYSTEM_DESIGN_CASE_STUDIES.md -->

# System Design and Interactive Case Studies

> **Product identity override:** Interpret this file through `00_PRODUCT_IDENTITY.md`. ATLAS is the real application; the IDE is the primary place for source modification. Any older “lesson/playground” wording means engineering documentation, operational tooling, reference modules, or controlled test environments—not the central product model.


System design should be implemented as an interactive frontend laboratory, not as static diagrams.

## 1. Foundation modules

Teach:
- requirements
- functional vs non-functional requirements
- capacity estimation
- QPS
- bandwidth
- storage
- latency
- availability
- consistency
- caching
- CDN
- load balancing
- queues
- databases
- indexes
- partitioning
- replication
- search
- object storage
- rate limiting
- service discovery
- observability
- security.

## 2. Interactive architecture canvas

Users should be able to:
- drag components,
- connect data flow,
- change replicas,
- set region,
- set cache hit rate,
- change partition count,
- alter capacity,
- toggle failures,
- inspect tradeoffs.

Nodes:
- client
- DNS
- CDN
- WAF
- load balancer
- API gateway
- service
- worker
- queue
- stream
- cache
- relational DB
- NoSQL DB
- search
- object storage
- ML service
- agent service
- observability
- external dependency.

## 3. Calculators

Build:
- QPS
- concurrency
- storage
- bandwidth
- cache memory
- replication/storage overhead
- partition sizing
- rough availability composition.

These are educational calculators, not capacity guarantees.

## 4. Case-study ladder

### Foundation
- URL shortener
- Pastebin
- rate limiter
- file upload service
- notification service
- key-value service concepts

### Intermediate
- chat/WhatsApp-like system
- social feed/Instagram-like system
- Twitter/X-like timeline
- ride-hailing/Uber-like dispatch concepts
- Dropbox-like sync
- e-commerce checkout
- payment/ledger simulation
- collaborative editor concepts

### Advanced
- video streaming/Netflix-like architecture
- YouTube-like upload/transcode/delivery
- search engine concepts
- large marketplace/Amazon-like architecture
- Discord/Slack-like real-time system
- analytics platform
- event ingestion platform
- multi-region SaaS
- distributed database concepts
- feature flag platform
- observability platform
- LLM inference platform
- RAG/agent platform.

Use names as familiar analogies, not claims of exact proprietary implementation.

## 5. Every case study includes

1. Problem statement
2. Scope/non-goals
3. Requirements
4. Scale assumptions
5. API sketch
6. Data model
7. Baseline architecture
8. Request/data flow
9. Bottlenecks
10. Scaling evolution
11. Failure scenarios
12. Observability
13. Security/threat model
14. Cost tradeoffs
15. Alternatives
16. Interactive challenge
17. Architecture diff after learner changes.

## 6. Security architecture mode

Toggle from:
- normal architecture
to:
- security architecture

Overlay:
- trust boundaries
- sensitive assets
- auth boundaries
- public/private network boundaries
- encryption
- audit points
- rate-limit points
- secrets
- privileged components
- STRIDE findings.

## 7. Failure mode

Allow safe simulations:
- service down
- cache down
- replica lag
- queue backlog
- network delay
- regional outage model
- overloaded DB
- failed model service
- agent tool timeout.

Show expected user impact and signals.

## 8. Compare architectures

Support side-by-side:
- monolith vs microservices
- sync vs async
- SQL vs NoSQL choice for a specific requirement
- centralized vs partitioned
- single-region vs multi-region
- cache strategies
- queue/stream choices.

No universal “best architecture”.

<!-- END 09_SYSTEM_DESIGN_CASE_STUDIES.md -->

---


<!-- BEGIN 10_PAGE_AND_COMPONENT_INVENTORY.md -->

# Page and Route Inventory

> **Product identity override:** Interpret this file through `00_PRODUCT_IDENTITY.md`. ATLAS is the real application; the IDE is the primary place for source modification. Any older “lesson/playground” wording means engineering documentation, operational tooling, reference modules, or controlled test environments—not the central product model.


This file defines the desired breadth. The exact routes may evolve, but the information architecture must support them.

## Core

```text
/
dashboard
search
activity
bookmarks
notes
progress
settings
services
labs
lab/[id]
benchmarks
benchmark/[id]
projects
project/[id]
datasets
dataset/[id]
glossary
references
```

## Programming

```text
learn/python
learn/python/fundamentals
learn/python/functions
learn/python/oop
learn/python/typing
learn/python/iterators-generators
learn/python/decorators
learn/python/context-managers
learn/python/asyncio
learn/python/threading
learn/python/multiprocessing
learn/python/networking
learn/python/files
learn/python/testing
learn/python/profiling
learn/python/packaging
learn/python/stdlib

learn/javascript
learn/typescript
learn/java
learn/go
learn/rust
learn/c
learn/cpp
```

Each language should fan out into dozens of topic pages driven by metadata.

## Web

```text
web/html
web/css
web/browser
web/javascript
web/typescript
web/react
web/nextjs
web/vue
web/angular
web/svelte
web/accessibility
web/performance
web/forms
web/state
web/server-state
web/websockets
web/security
web/testing
```

## Backend

```text
backend/http
backend/rest
backend/graphql
backend/grpc
backend/websockets
backend/sse
backend/fastapi
backend/flask
backend/django
backend/node
backend/express
backend/fastify
backend/nest
backend/spring
backend/auth
backend/caching
backend/queues
backend/background-jobs
backend/rate-limiting
backend/files
backend/resilience
```

## Databases

```text
databases/dbms
databases/sql
databases/postgresql
databases/mysql
databases/sqlite
databases/mongodb
databases/redis
databases/cassandra
databases/neo4j
databases/search
databases/clickhouse
databases/duckdb
databases/vector
databases/time-series

databases/transactions
databases/mvcc
databases/isolation
databases/indexes
databases/query-plans
databases/joins
databases/locking
databases/wal
databases/replication
databases/partitioning
databases/sharding
databases/backup-recovery
databases/security
databases/performance
```

## Data science

```text
data
data/numpy
data/pandas
data/polars
data/scipy
data/duckdb
data/pyarrow
data/eda
data/statistics
data/visualization
data/cleaning
data/feature-engineering
data/quality
data/large-scale
```

## Machine learning

```text
ml
ml/regression
ml/classification
ml/trees
ml/ensembles
ml/svm
ml/clustering
ml/dimensionality-reduction
ml/anomaly-detection
ml/model-selection
ml/metrics
ml/interpretability
ml/pipelines
```

## Deep learning and applied AI

```text
deep-learning
deep-learning/pytorch
deep-learning/tensorflow
deep-learning/jax
deep-learning/optimization
deep-learning/cnn
deep-learning/rnn
deep-learning/attention
deep-learning/transformers

ai/nlp
ai/computer-vision
ai/time-series
ai/recommendation
ai/reinforcement-learning
```

## LLM and agent engineering

```text
ai-engineering
ai-engineering/llm
ai-engineering/tokenization
ai-engineering/embeddings
ai-engineering/rag
ai-engineering/vector-search
ai-engineering/reranking
ai-engineering/structured-output
ai-engineering/tool-calling
ai-engineering/evals
ai-engineering/observability
ai-engineering/fine-tuning
ai-engineering/quantization
ai-engineering/local-models

agents
agents/fundamentals
agents/workflows
agents/langgraph
agents/multi-agent
agents/memory
agents/tools
agents/human-approval
agents/mcp
agents/security
agents/evaluation
```

## Data engineering and Apache

```text
data-engineering
data-engineering/etl
data-engineering/elt
data-engineering/cdc
data-engineering/batch
data-engineering/streaming
data-engineering/orchestration
data-engineering/lineage
data-engineering/lake
data-engineering/lakehouse
data-engineering/warehouse

apache
apache/spark
apache/kafka
apache/flink
apache/airflow
apache/beam
apache/hadoop
apache/hive
apache/hbase
apache/cassandra
apache/iceberg
apache/arrow
apache/parquet
apache/avro
apache/orc
apache/superset
apache/nifi
apache/pulsar
apache/pinot
apache/druid
apache/calcite
apache/lucene
apache/solr
apache/jmeter
```

## DevOps/cloud

```text
devops
devops/linux
devops/shell
devops/git
devops/github
devops/docker
devops/compose
devops/kubernetes
devops/helm
devops/terraform
devops/ansible
devops/cicd
devops/release
devops/config
devops/secrets

cloud
cloud/aws
cloud/azure
cloud/gcp
cloud/identity
cloud/network
cloud/compute
cloud/containers
cloud/serverless
cloud/storage
cloud/databases
cloud/events
cloud/observability
cloud/security
cloud/cost
```

## Networking

```text
networking
networking/ip
networking/subnetting
networking/tcp
networking/udp
networking/dns
networking/http
networking/tls
networking/sockets
networking/proxy
networking/load-balancing
networking/cdn
networking/firewalls
networking/vpn
networking/packet-analysis
```

## Security

```text
security
security/fundamentals
security/threat-modeling
security/cryptography
security/identity
security/web
security/api
security/database
security/network
security/cloud
security/container
security/kubernetes
security/supply-chain
security/devsecops
security/detection
security/incident-response
security/ai
security/labs
security/findings
```

## Testing

```text
testing
testing/unit
testing/integration
testing/component
testing/api
testing/database
testing/contract
testing/e2e
testing/accessibility
testing/property-based
testing/fuzz
testing/mutation
testing/performance
testing/load
testing/stress
testing/spike
testing/soak
testing/chaos
testing/security
```

## Observability/SRE

```text
observability
observability/logs
observability/metrics
observability/traces
observability/opentelemetry
observability/prometheus
observability/grafana

sre
sre/sli-slo
sre/error-budgets
sre/alerting
sre/incidents
sre/runbooks
sre/postmortems
sre/capacity
sre/chaos
```

## Distributed systems

```text
distributed-systems
distributed-systems/consistency
distributed-systems/cap
distributed-systems/time
distributed-systems/ordering
distributed-systems/replication
distributed-systems/partitioning
distributed-systems/consensus
distributed-systems/leader-election
distributed-systems/idempotency
distributed-systems/retries
distributed-systems/distributed-locks
distributed-systems/backpressure
```

## System design

```text
system-design
system-design/foundations
system-design/calculators
system-design/url-shortener
system-design/pastebin
system-design/rate-limiter
system-design/chat
system-design/social-feed
system-design/ride-hailing
system-design/file-sync
system-design/ecommerce
system-design/payments
system-design/video-streaming
system-design/video-platform
system-design/search
system-design/marketplace
system-design/realtime-collaboration
system-design/analytics
system-design/event-platform
system-design/multi-region-saas
system-design/observability-platform
system-design/llm-serving
system-design/rag-agent-platform
```

## Count philosophy

Do not manually create 700 empty routes.
Build reusable typed page templates and content schemas, then fill them with real content incrementally.

<!-- END 10_PAGE_AND_COMPONENT_INVENTORY.md -->

---


<!-- BEGIN 11_IMPLEMENTATION_ROADMAP.md -->

# Implementation Roadmap and Acceptance Criteria

> **Product identity override:** Interpret this file through `00_PRODUCT_IDENTITY.md`. ATLAS is the real application; the IDE is the primary place for source modification. Any older “lesson/playground” wording means engineering documentation, operational tooling, reference modules, or controlled test environments—not the central product model.


The scope is huge. The way to complete it is disciplined vertical expansion.

# Phase 0 — Repository foundation

Build:
- monorepo
- shared config
- Next.js app shell
- Python API
- PostgreSQL
- authentication skeleton
- content schema
- lab manifest schema
- basic search index
- test setup
- Docker Compose
- CI
- logging
- initial telemetry
- security baseline.

Acceptance:
- one command boots core locally,
- web + API communicate,
- DB migration works,
- CI passes,
- sample topic renders,
- sample lab can be started/reset,
- tests visible in UI.

# Phase 1 — ATLAS Core UI

Build:
- dashboard
- global nav/sidebar
- command palette
- search
- domain catalog
- topic template
- code component
- lab workspace
- test center
- progress tracking
- bookmarks/notes
- dark/light mode
- responsive shell.

Create substantial reusable UI library from `03_FRONTEND_AND_DESIGN_SYSTEM.md`.

Acceptance:
- no placeholder-only navigation,
- keyboard usable,
- E2E smoke tests,
- accessibility baseline.

# Phase 2 — Python mastery vertical

Build enough Python content/labs to prove the content architecture:
- fundamentals
- functions
- OOP
- typing
- generators
- decorators
- async
- threading/multiprocessing
- testing
- profiling.

Acceptance:
- real executable examples,
- tests,
- benchmark examples,
- progress saved.

# Phase 3 — Full-stack engineering

Add:
- web fundamentals
- React
- Next.js
- backend APIs
- FastAPI
- Node
- auth
- REST/GraphQL/gRPC examples
- WebSockets/SSE
- full-stack project slice.

# Phase 4 — DBMS laboratory

Add:
- PostgreSQL deep dive
- MySQL/SQLite
- MongoDB
- Redis
- query editor
- explain viewer
- MVCC/locks/isolation visualizers
- benchmark suite
- database security labs.

# Phase 5 — Data science

Add:
- dataset catalog
- NumPy
- pandas
- Polars
- SciPy
- DuckDB
- EDA
- statistics
- visualization
- dirty-data lab
- scaling benchmarks.

# Phase 6 — Machine learning

Add:
- sklearn workflow
- core algorithms
- from-scratch examples
- experiment tracking UI
- model evaluation
- interpretability
- model comparison.

# Phase 7 — Deep learning and applied AI

Add:
- PyTorch
- TensorFlow/Keras comparison
- CNN
- sequence models
- attention
- transformers
- NLP
- computer vision
- time series
- recommendations.

# Phase 8 — LLM and AI engineering

Add:
- model/provider abstraction
- local model support
- prompt playground
- structured output
- tool calling
- embeddings
- RAG
- reranking
- evals
- telemetry
- cost/token metrics.

# Phase 9 — Agentic systems

Add:
- deterministic workflows
- LangGraph-style examples
- tool gateway
- permissions
- approvals
- memory/state
- multi-agent
- MCP explorer
- agent replay
- AI security labs.

# Phase 10 — Data engineering and Apache

Add high-priority:
- Kafka
- Spark
- Airflow
- Flink
- Iceberg
- Arrow/Parquet
- Superset
then expand the Apache catalog.

Build:
- topic explorer
- consumer lag
- DAG view
- pipeline canvas
- lineage
- backpressure/checkpoint views.

# Phase 11 — DevOps/cloud

Add:
- Linux/shell
- Docker
- Kubernetes
- Helm
- Terraform
- Ansible
- CI/CD
- AWS/Azure/GCP comparison labs
- cost/teardown guardrails.

# Phase 12 — Security and DevSecOps

Although security baselines exist from Phase 0, now add the dedicated domain:
- threat modeling
- crypto
- web/API/database security
- cloud/container security
- supply chain
- scanners
- security operations
- incident response
- cyber range.

# Phase 13 — Observability/SRE

Add:
- OpenTelemetry
- Prometheus
- Grafana
- logs/metrics/traces UI
- SLO/error budget
- incidents/runbooks/postmortems
- chaos/resilience labs.

# Phase 14 — Distributed systems and system design

Add:
- distributed concepts
- architecture canvas
- calculators
- case-study ladder
- failure simulation
- security overlay
- tradeoff comparison.

# Phase 15 — Capstone integrations

Build the six capstones from the master spec.
Each should integrate multiple domains and have:
- architecture
- tests
- telemetry
- threat model
- CI/CD
- runbook
- failure scenarios
- deployment path.

# Continuous phase — expansion

Continuously add:
- additional languages/frameworks,
- reference catalogs,
- more datasets,
- more Apache projects,
- more databases,
- more labs,
- more system designs,
- more UI utilities.

# Feature Definition of Done

A major feature is done only if relevant items pass:

- [ ] user-facing behavior works
- [ ] typed contracts
- [ ] validation
- [ ] unit/component tests
- [ ] integration tests
- [ ] E2E for critical flow
- [ ] error/loading/empty states
- [ ] accessibility
- [ ] structured logging
- [ ] metrics/traces if applicable
- [ ] security considerations
- [ ] no committed secrets
- [ ] documentation
- [ ] reset/cleanup for labs
- [ ] benchmark caveat if benchmarked
- [ ] mobile/responsive behavior if page is user-facing
- [ ] no obvious dead links/placeholders

# Codex execution rule

When asked to “continue building ATLAS”:
1. inspect open issues/TODOs,
2. choose the earliest incomplete roadmap phase unless the user specified another domain,
3. finish a coherent vertical slice,
4. test it,
5. document it,
6. update progress/roadmap metadata.

Do not respond by generating only more plans when implementation is requested.

<!-- END 11_IMPLEMENTATION_ROADMAP.md -->

---


<!-- BEGIN 12_CURRENT_TECH_NOTES.md -->

# Current Technology Notes — 24 August 2026

These notes are context, not permanent version pins. Codex must re-check official documentation before a future dependency installation or major upgrade.

## shadcn/ui

The current official shadcn documentation describes shadcn/ui as open code and a code distribution system rather than a conventional opaque component library.

Current official docs also show:
- Base UI is the default primitive choice for new shadcn projects as of July 2026.
- Radix remains supported.
- shadcn now documents composition structures specifically to make component composition more reliable for humans and coding agents.
- the component catalog includes newer chat-oriented primitives such as Message, Message Scroller, Bubble, Attachment and Marker.
- shadcn provides a registry model and CLI for adding components.
- shadcn explicitly points to community registry components when a needed component is not in the built-in set.

Official references:
- https://ui.shadcn.com/docs
- https://ui.shadcn.com/docs/components
- https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default
- https://ui.shadcn.com/docs/changelog/2026-06-chat-components
- https://ui.shadcn.com/docs/changelog/2026-04-component-composition
- https://ui.shadcn.com/docs/cli

### ATLAS consequence

Use shadcn source-owned components heavily. Create a large ATLAS-specific composition layer rather than adding unrelated UI libraries for every widget.

For community components:
- inspect source,
- confirm license,
- review accessibility,
- review dependencies,
- normalize styling,
- add tests.

## TanStack

Use current official TanStack documentation when adopting Query/Table/Router tooling. The ATLAS recommendation is:
- TanStack Query for server-state concerns,
- TanStack Table for large data-heavy tables.

Official reference:
- https://tanstack.com/

## Apache ecosystem

The Apache ecosystem is central to ATLAS's data engineering track.

Official Apache sources confirm:
- Spark is a unified engine for large-scale analytics and supports batch/streaming, SQL and data-science/ML workflows.
- Kafka is a distributed event-streaming platform.
- Flink is a distributed engine for stateful bounded/unbounded stream computation.

At the date of this file, official pages list modern 2026 releases such as Spark 4.x, Kafka 4.x and Flink 2.x. Do not hard-pin ATLAS to these values without re-checking.

Official references:
- https://spark.apache.org/
- https://kafka.apache.org/
- https://flink.apache.org/
- https://airflow.apache.org/
- https://iceberg.apache.org/
- https://arrow.apache.org/
- https://superset.apache.org/
- https://apache.org/

## Versioning rule

Record runtime versions in:
- lockfiles,
- container tags,
- environment manifests,
- lab metadata.

Content should explain concepts in a version-aware way.
If syntax is version-specific, display the tested version.

## Online resources

Codex may consult official docs and reputable source repositories while implementing.

Order of preference:
1. official framework/project docs,
2. official repositories/examples,
3. standards/specifications,
4. trusted maintainers,
5. community examples.

Do not copy large undocumented snippets from random sites.


<!-- END 12_CURRENT_TECH_NOTES.md -->

---


<!-- BEGIN 13_FRAMEWORK_LIBRARY_MATRIX.md -->

# Framework and Library Coverage Matrix

> **Product identity override:** Interpret this file through `00_PRODUCT_IDENTITY.md`. ATLAS is the real application; the IDE is the primary place for source modification. Any older “lesson/playground” wording means engineering documentation, operational tooling, reference modules, or controlled test environments—not the central product model.


This file prevents “broad coverage” from being interpreted too narrowly.

ATLAS should cover the following ecosystems through a mixture of:
- deep first-class modules,
- comparison labs,
- reference pages,
- smaller examples.

Do not install every item into the platform core. Many belong in isolated labs.
Before adopting a dependency, verify current maintenance status, official docs, license and security posture.

# 1. Python ecosystem

## Core development
- CPython
- uv / pip / virtualenv concepts
- Poetry/pip-tools concepts
- Ruff
- Black concepts
- mypy / Pyright concepts
- pre-commit
- Pydantic
- dataclasses
- attrs concepts

## CLI / terminal / developer tools
- argparse
- Click
- Typer
- Rich
- Textual concepts

## HTTP/networking
- requests
- httpx
- aiohttp
- websockets
- urllib standard library

## Web/backend
- FastAPI
- Starlette
- Flask
- Django
- Django REST Framework
- Litestar concepts if current/relevant
- Uvicorn
- Gunicorn concepts

## Database/data access
- SQLAlchemy
- Alembic
- psycopg
- asyncpg
- Django ORM
- SQLModel concepts
- PyMongo
- redis-py

## Background work
- Celery
- RQ
- Dramatiq concepts
- APScheduler
- asyncio task patterns

## Serialization/config
- json
- csv
- pickle safety concepts
- PyYAML
- TOML
- python-dotenv concepts
- settings management

## Testing
- pytest
- unittest
- Hypothesis
- pytest-asyncio
- coverage.py
- tox/nox concepts
- Testcontainers Python

## Performance
- timeit
- cProfile
- profile
- tracemalloc
- py-spy concepts
- line/memory profiling concepts

# 2. Frontend / React ecosystem

## Foundation
- React
- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- Base UI
- Radix UI compatibility
- React Aria concepts

## State
Teach patterns before libraries.
Representative libraries:
- Zustand
- Redux Toolkit
- Jotai
- XState/state-machine concepts
- React Context/useReducer where appropriate

## Server state/data
- TanStack Query
- SWR comparison
- TanStack Table
- TanStack Virtual

## Forms/validation
- React Hook Form
- Zod
- Valibot concepts where useful

## Routing
- Next.js App Router
- React Router
- TanStack Router comparison where useful

## UI utilities
- Lucide icons
- Floating UI concepts
- cmdk/command-menu concepts
- date-fns
- drag-and-drop library selected from a maintained ecosystem
- resizable/split-pane utilities
- virtualization

## Motion
- Motion/Framer Motion ecosystem
- CSS transitions/animations
- reduced-motion accessibility
- Web Animations API concepts

## Editors/code
- Monaco Editor
- CodeMirror comparison
- Shiki syntax highlighting
- diff rendering
- terminal emulation such as xterm.js where suitable

## Graphs/diagrams
- React Flow / XYFlow
- Mermaid rendering
- D3 for custom visualization concepts
- Cytoscape.js concepts for graph/network views

## Charts
Use more than one when justified:
- shadcn Chart composition
- Recharts
- Plotly
- ECharts concepts
- D3 for lower-level teaching

## Rich content
- MDX
- Markdown
- math rendering
- syntax highlighting
- diagrams

## AI UI
- current shadcn chat primitives
- Vercel AI SDK/UI patterns where appropriate
- AI Elements where useful
- custom ATLAS agent/tool/eval components

# 3. Backend JavaScript / TypeScript

- Node.js
- Express
- Fastify
- NestJS
- Hono concepts where relevant
- tRPC concepts
- GraphQL server ecosystem
- Apollo concepts
- gRPC JS
- Socket.IO vs native WebSocket comparison
- Prisma concepts
- Drizzle ORM concepts
- TypeORM concepts
- Knex concepts
- BullMQ
- node-postgres
- Redis clients
- OpenTelemetry JS
- Pino/Winston logging concepts
- Vitest/Jest
- Supertest
- Playwright

# 4. Java ecosystem

- Java language/JDK
- Maven
- Gradle concepts
- Spring Boot
- Spring Web
- Spring Security
- Spring Data
- JPA
- Hibernate
- JUnit
- Mockito
- Testcontainers
- Micrometer
- OpenTelemetry Java concepts
- Kafka clients/Spring Kafka
- gRPC Java

# 5. Go ecosystem

Use the standard library heavily.
Also teach representative:
- net/http
- chi/gin/fiber comparison where useful
- sql/database drivers
- pgx
- Cobra concepts
- Zap/slog concepts
- testing/benchmarks
- OpenTelemetry Go

# 6. Rust ecosystem

- Cargo
- Tokio
- Axum/Actix comparison concepts
- Serde
- SQLx/Diesel concepts
- tracing
- Criterion benchmarks
- testing
- FFI/interoperability examples

# 7. Data science stack

## Core
- NumPy
- pandas
- Polars
- SciPy
- DuckDB
- PyArrow
- Dask

## Statistics
- statsmodels
- SciPy stats
- probabilistic programming concepts via a maintained library where useful

## Visualization
- Matplotlib
- Seaborn
- Plotly
- Altair
- Bokeh concepts where useful

## EDA/profiling
- custom ATLAS profiler
- ydata-profiling concepts
- missingno concepts
- data quality libraries where maintained

# 8. Classical ML

- scikit-learn
- XGBoost
- LightGBM
- CatBoost
- imbalanced-learn
- Optuna
- SHAP
- model interpretation/evaluation libraries as appropriate

# 9. Deep learning

- PyTorch
- torchvision/torchaudio concepts
- TensorFlow
- Keras
- JAX
- Flax concepts
- Lightning concepts
- ONNX
- ONNX Runtime

# 10. NLP / LLM / GenAI

## Hugging Face ecosystem
- Transformers
- Datasets
- Tokenizers
- Accelerate
- PEFT
- Sentence Transformers
- Safetensors concepts

## Serving/local inference
Teach multiple approaches:
- Ollama
- llama.cpp concepts
- vLLM
- Hugging Face inference patterns
- OpenAI-compatible local endpoints

## Retrieval
- FAISS
- vector database clients
- BM25/search-engine retrieval
- hybrid search
- reranking models

## LLM application frameworks
Cover foundations first, then representative current frameworks:
- LangChain
- LangGraph
- LlamaIndex
- DSPy
- AutoGen-style ecosystem
- CrewAI-style ecosystem
- PydanticAI-style typed agent patterns where current/relevant

Do not let framework abstractions hide tool/state/retry/security fundamentals.

## Evaluation/observability
Representative concepts/tools:
- LangSmith-style tracing/evals
- MLflow GenAI/eval capabilities where appropriate
- OpenTelemetry-based tracing
- custom ATLAS eval runner
- RAG evaluation libraries if current and maintainable

# 11. MLOps / data lifecycle

- MLflow
- DVC
- Optuna
- ONNX
- model registries
- feature-store concepts
- Feast concepts
- BentoML concepts
- KServe concepts
- Seldon concepts if current/relevant
- Ray concepts
- distributed training/serving concepts

# 12. Data engineering ecosystem

## Apache priority
- Spark / PySpark
- Kafka
- Flink
- Airflow
- Beam
- Hadoop
- Hive
- HBase
- Cassandra
- Iceberg
- Arrow
- Parquet
- Avro
- ORC
- Superset
- NiFi
- Pulsar
- Pinot
- Druid
- Calcite
- Lucene
- Solr

## Other important open tools/concepts
- dbt
- Dagster
- Prefect
- Airbyte concepts
- Debezium
- Great Expectations
- OpenLineage
- Marquez concepts
- lakeFS concepts
- Delta Lake concepts
- Trino
- Presto concepts

# 13. Databases

## Relational
- PostgreSQL
- MySQL/MariaDB
- SQLite

## NoSQL/cache
- MongoDB
- Redis
- Cassandra

## Analytical
- DuckDB
- ClickHouse

## Search
- Elasticsearch
- OpenSearch
- Lucene/Solr concepts

## Graph
- Neo4j
- graph query/model concepts

## Vector
Compare representative maintained options, including:
- PostgreSQL vector-extension approach
- FAISS local indexing
- Qdrant-style vector service
- Milvus-style distributed vector database
- Weaviate-style system concepts

Verify current licenses/maintenance before integration.

## Time series
Teach:
- PostgreSQL-based approaches
- Prometheus time-series model
- representative specialized time-series DB concepts.

# 14. Messaging / queues / workflows

- Kafka
- RabbitMQ
- Redis Streams
- NATS concepts
- Apache Pulsar
- cloud queue/pub-sub equivalents
- Celery/BullMQ
- durable workflow concepts
- Temporal-style workflow concepts where appropriate

# 15. DevOps and platform engineering

## Containers/orchestration
- Docker
- Docker Compose
- Kubernetes
- Helm
- Kustomize concepts

## IaC/config
- Terraform
- OpenTofu
- Ansible
- Pulumi concepts

## CI/CD
- GitHub Actions
- Jenkins
- GitLab CI concepts
- Argo CD
- Flux
- Tekton concepts

## Proxies/network edge
- NGINX
- Envoy
- Traefik
- Caddy concepts
- HAProxy concepts

## Service mesh
- Istio
- Linkerd concepts

## Secrets/config/service discovery
- Vault
- Consul
- SOPS concepts
- Sealed Secrets concepts
- External Secrets concepts

# 16. Observability

- OpenTelemetry
- Prometheus
- Grafana
- Loki
- Tempo
- Jaeger
- Alertmanager
- structured logging
- eBPF observability concepts
- OpenSearch/ELK-style logging concepts

# 17. Security tooling

Representative open/free tooling:
- OWASP ZAP
- Semgrep
- Bandit
- Trivy
- Grype
- Syft
- Gitleaks
- dependency audit tools
- npm audit concepts
- pip audit concepts
- container/IaC policy scanners
- Falco concepts
- OPA
- Gatekeeper
- Kyverno
- security headers/CSP tooling
- TLS inspection tools for local labs
- Wireshark/tcpdump concepts for authorized local traffic

# 18. Testing ecosystem

- pytest
- unittest
- Hypothesis
- Vitest
- Jest
- React Testing Library
- Playwright
- Cypress
- JUnit
- Mockito
- Testcontainers
- Pact/contract-testing concepts
- k6
- Locust
- Apache JMeter
- mutation testing tools per language
- fuzzing tools per language

# 19. API / schema / contracts

- OpenAPI
- JSON Schema
- GraphQL
- Protocol Buffers
- gRPC
- AsyncAPI concepts for events
- Avro schemas
- schema evolution
- code generation
- contract testing.

# 20. Rules for “everything”

The target is broad mastery, not dependency hoarding.

For a large ecosystem:
1. create a domain index,
2. teach core concepts without framework dependence,
3. choose first-class libraries for deep labs,
4. add comparison labs for major alternatives,
5. create searchable reference coverage for public APIs/commands,
6. keep niche/legacy frameworks as concise reference modules unless they teach an important idea.

This is how ATLAS can approach “everything under the sky” while remaining maintainable.

<!-- END 13_FRAMEWORK_LIBRARY_MATRIX.md -->

---


<!-- BEGIN 14_ECOSYSTEM_PARITY_AND_COMPLETENESS.md -->

# 14 — Ecosystem Parity and Completeness Matrix

## Objective

When ATLAS says it supports a language or backend ecosystem, it must not mean “we used one framework once.”

Each first-class ecosystem should cover the equivalent engineering surface:

1. language/runtime
2. package/dependency management
3. project/build tooling
4. configuration
5. web framework(s)
6. API framework(s)
7. routing/middleware
8. validation/schema
9. serialization
10. ORM/data mapper
11. lower-level database driver/query builder
12. migrations
13. authentication
14. authorization
15. sessions/cookies/tokens
16. async/concurrency
17. background jobs
18. queues/messaging
19. scheduling
20. caching
21. WebSockets/realtime
22. GraphQL
23. gRPC/Protobuf
24. CLI
25. logging
26. metrics
27. tracing/OpenTelemetry
28. error reporting
29. testing
30. mocking
31. property/fuzz testing where mature
32. performance benchmarking/profiling
33. security scanning/linting
34. formatting/linting
35. type checking/static analysis
36. documentation/API generation
37. deployment/containerization
38. cloud/serverless integrations
39. SDK/client generation
40. file/object storage integrations
41. email/notifications integrations
42. payments/business integrations where relevant
43. feature flags/config distribution
44. resilience/retry/circuit-breaker patterns
45. dependency injection where idiomatic
46. templating/server-rendered UI where idiomatic
47. RPC/event contracts
48. database transaction patterns
49. Testcontainers/ephemeral integration environments
50. production hardening.

The list is extensible. New categories should be added to the technology registry.

# Python ecosystem — extremely deep coverage

Python must be one of the deepest ecosystems in ATLAS.

## Runtime/language
- CPython
- PyPy concepts
- syntax/runtime internals where useful
- asyncio
- threading
- multiprocessing
- concurrent.futures
- subprocess
- pathlib/files
- sockets/networking
- typing/generics/protocols
- dataclasses
- context managers
- decorators
- generators/iterators

## Package/environment/build
- pip
- venv
- uv
- Poetry concepts
- pip-tools concepts
- pyproject.toml
- setuptools concepts
- wheel/sdist
- locking
- private package indexes concepts

## Web frameworks
Deep:
- Django
- FastAPI
- Flask

Also cover/integrate where current and useful:
- Starlette
- Litestar
- Falcon concepts
- Sanic concepts
- Tornado concepts
- Bottle legacy/minimal concepts

## APIs/contracts
- Django REST Framework
- FastAPI
- Flask API patterns
- GraphQL via maintained Python ecosystem
- gRPC Python
- WebSockets
- SSE
- OpenAPI
- JSON Schema
- Protobuf
- AsyncAPI concepts

## Validation/schema
- Pydantic
- dataclasses
- attrs
- marshmallow concepts
- JSON Schema

## ORM/data access
Deep:
- SQLAlchemy ORM/Core
- Django ORM
- SQLModel concepts

Also:
- psycopg
- asyncpg
- query-builder concepts
- PyMongo
- redis-py
- search clients
- vector DB clients

## Migrations
- Alembic
- Django migrations

## Auth/security
- Django auth
- OAuth/OIDC
- JWT
- password hashing
- sessions
- CSRF/CORS
- security headers
- RBAC/ABAC
- secrets
- cryptography library safe usage

## Background jobs/workflows
- Celery
- RQ
- Dramatiq concepts
- APScheduler
- asyncio workers
- durable workflow clients
- Airflow for data jobs

## Messaging
- Kafka clients
- RabbitMQ/AMQP clients
- Redis Streams
- NATS clients
- Pulsar clients
- cloud pub/sub adapters

## Caching
- Redis
- in-process caching
- HTTP caching
- cachetools concepts

## Testing
- pytest
- unittest
- Hypothesis
- pytest-asyncio
- mocking/fixtures
- coverage.py
- tox/nox
- Testcontainers

## Quality
- Ruff
- Black concepts
- mypy
- Pyright concepts
- Bandit
- pip-audit concepts
- pre-commit

## Observability/performance
- logging
- structlog concepts
- OpenTelemetry
- Prometheus client
- error reporting concepts
- cProfile
- tracemalloc
- py-spy concepts

## Data/AI Python stack
- NumPy
- pandas
- Polars
- SciPy
- DuckDB
- PyArrow
- Dask
- statsmodels
- scikit-learn
- XGBoost
- LightGBM
- CatBoost
- imbalanced-learn
- Optuna
- SHAP
- PyTorch
- TensorFlow/Keras
- JAX
- ONNX/ONNX Runtime
- Transformers
- Datasets
- Tokenizers
- Sentence Transformers
- Accelerate
- PEFT
- MLflow
- LangChain
- LangGraph
- LlamaIndex
- DSPy
- agent-framework comparisons
- local-model clients
- vLLM-style serving clients
- Ray concepts
- PySpark
- Airflow
- Beam
- Flink Python APIs where useful

# Node.js / TypeScript ecosystem — parity with Python backend concerns

## Runtime/tooling
- Node.js
- npm
- pnpm
- Yarn concepts
- package.json
- workspaces
- ESM/CommonJS
- TypeScript
- tsconfig
- monorepo tooling

## Web frameworks
Deep:
- Express
- Fastify
- NestJS

Also:
- Hono
- Koa concepts
- AdonisJS concepts
- native Node HTTP
- serverless/edge handlers

## APIs/contracts
- REST
- OpenAPI
- GraphQL
- Apollo concepts
- GraphQL Yoga concepts
- tRPC
- gRPC
- Protobuf
- WebSockets
- Socket.IO
- SSE
- JSON Schema
- AsyncAPI concepts

## Validation
- Zod
- Valibot concepts
- Joi concepts
- class-validator
- Ajv/JSON Schema

## ORM/data access
Deep:
- Prisma
- Drizzle
- TypeORM

Also:
- Sequelize concepts
- MikroORM concepts
- Knex
- Kysely concepts
- node-postgres
- MySQL clients
- MongoDB driver
- Mongoose
- Redis clients
- search/vector clients

## Migrations
- Prisma migrations
- Drizzle migrations
- TypeORM migrations
- Knex migrations
- raw SQL migrations

## Auth/security
- Passport concepts
- Auth.js-style concepts
- sessions
- JWT
- OAuth/OIDC
- RBAC/ABAC
- CSRF/CORS
- Helmet/security headers
- rate limiting
- dependency/security scanning

## Jobs/queues
- BullMQ
- Agenda concepts
- cron
- worker_threads
- child_process
- broker clients
- durable workflow clients

## Testing
- Vitest
- Jest
- Node test runner
- Supertest
- Playwright
- Cypress
- Testcontainers
- mocking
- property/fuzz concepts

## Quality/observability
- ESLint
- Biome concepts
- Prettier
- strict TypeScript
- dependency audits
- Semgrep
- Pino
- Winston concepts
- OpenTelemetry
- Prometheus clients
- profiler/flamegraphs
- event-loop monitoring

# Java ecosystem

- JVM/JDK
- Maven
- Gradle
- Spring Boot
- Spring MVC
- Spring WebFlux
- Spring Security
- Spring Data
- Jakarta EE concepts
- Quarkus
- Micronaut
- Vert.x concepts
- JPA
- Hibernate
- JDBC
- jOOQ concepts
- MyBatis concepts
- Flyway
- Liquibase
- Spring Kafka
- JMS
- RabbitMQ
- scheduled jobs
- batch processing
- REST
- GraphQL
- gRPC
- WebSocket
- OpenAPI
- JUnit
- Mockito
- AssertJ concepts
- Testcontainers
- JMH
- Micrometer
- OpenTelemetry
- SLF4J/Logback
- OAuth/OIDC/JWT

# .NET / C# ecosystem

- .NET runtime
- C#
- NuGet
- dotnet CLI
- MSBuild concepts
- ASP.NET Core
- Minimal APIs
- MVC
- Razor Pages concepts
- Blazor concepts
- Entity Framework Core
- Dapper
- ADO.NET concepts
- EF migrations
- REST/OpenAPI
- GraphQL via maintained ecosystem
- gRPC
- SignalR
- WebSockets
- BackgroundService
- Hangfire concepts
- MassTransit concepts
- xUnit
- NUnit/MSTest concepts
- Moq/NSubstitute concepts
- Testcontainers
- BenchmarkDotNet
- ASP.NET Identity
- OAuth/OIDC/JWT
- policy authorization
- OpenTelemetry
- Serilog concepts

# Go ecosystem

- Go modules/toolchain
- net/http
- Chi
- Gin
- Fiber
- Echo concepts
- database/sql
- pgx
- GORM
- sqlc
- Ent concepts
- migrations
- REST/OpenAPI
- gRPC/Protobuf
- WebSockets
- GraphQL ecosystem
- goroutines/channels
- Kafka/NATS/RabbitMQ/Redis clients
- testing
- testify concepts
- fuzzing
- benchmarks
- race detector
- pprof
- staticcheck
- golangci-lint concepts
- Testcontainers
- OpenTelemetry
- slog/zap concepts
- OAuth/JWT

# Rust ecosystem

- Cargo
- Tokio
- Axum
- Actix Web
- Rocket/Warp concepts
- SQLx
- Diesel
- SeaORM concepts
- REST
- gRPC/Tonic
- WebSockets
- GraphQL ecosystem
- Protobuf
- Kafka/NATS/RabbitMQ/Redis clients
- cargo test
- property testing
- fuzzing
- Criterion
- Clippy
- rustfmt
- cargo audit concepts
- tracing
- OpenTelemetry
- OAuth/JWT integration

# Kotlin ecosystem

Server:
- Kotlin language
- coroutines
- Ktor
- Spring Boot Kotlin
- Exposed ORM concepts
- JPA/Hibernate
- serialization
- Gradle
- testing
- gRPC
- Kafka
- OpenTelemetry

Android:
- Jetpack Compose
- Room
- HTTP clients
- coroutines/Flow
- WorkManager
- secure storage
- notifications
- offline sync

# Scala ecosystem

- Scala
- sbt
- Cats/ZIO concepts
- Akka/Pekko actor concepts
- Play concepts
- Spark
- Kafka
- functional programming
- concurrency
- testing
- observability

# PHP ecosystem

- PHP
- Composer
- Laravel
- Symfony
- Eloquent
- Doctrine ORM
- queues/jobs
- events
- validation
- auth
- caching
- PHPUnit
- Pest concepts
- API development
- observability

# Ruby ecosystem

- Ruby
- Bundler
- Rails
- Active Record
- Rack
- Sidekiq
- background jobs
- Action Cable/WebSockets
- RSpec
- Minitest
- RuboCop
- auth/security
- observability

# Elixir ecosystem

- BEAM/OTP
- Mix
- Phoenix
- LiveView
- Ecto
- supervision trees
- GenServer
- channels
- Oban concepts
- ExUnit
- telemetry
- distributed Elixir

# Swift ecosystem

- Swift
- SwiftUI
- UIKit interoperability
- structured concurrency
- Combine concepts
- URLSession
- Codable
- Core Data/SwiftData concepts
- Keychain
- notifications
- background tasks
- deep links
- testing
- app architecture
- secure storage
- offline sync
- Vapor concepts if useful

# Dart/Flutter ecosystem

- Dart
- Flutter
- state management comparisons
- routing
- HTTP
- serialization
- local persistence
- background work
- secure storage
- notifications
- testing
- desktop/mobile/web deployment

# C/C++ systems ecosystem

- C/C++
- CMake
- Meson concepts
- memory
- threads
- sockets
- OpenSSL concepts
- gRPC C++
- Boost concepts
- database clients
- SIMD
- profiling
- sanitizers
- fuzzing
- GoogleTest/Catch2 concepts
- shared/static libraries
- FFI with Python/Rust/Node

# Cross-ecosystem equivalence

ATLAS documentation/registry should compare the same concern across ecosystems.

Example ORM/data access:

| Concern | Python | Node/TS | Java | .NET | Go | Rust | PHP | Ruby |
|---|---|---|---|---|---|---|---|---|
| High-level ORM | SQLAlchemy/Django ORM | Prisma/Drizzle/TypeORM | Hibernate/JPA | EF Core | GORM/Ent | Diesel/SeaORM | Eloquent/Doctrine | Active Record |
| Lower-level SQL | psycopg/asyncpg | node-postgres/Kysely/Knex | JDBC/jOOQ | ADO.NET/Dapper | database/sql/pgx/sqlc | SQLx | PDO/DBAL | adapters/raw SQL |
| Migration | Alembic/Django | Prisma/Drizzle/TypeORM | Flyway/Liquibase | EF migrations | migration tools | sqlx/diesel migration | Laravel/Doctrine | Rails migrations |

Create equivalent matrices for:
- web frameworks
- validation
- authentication
- authorization
- jobs
- messaging
- caching
- GraphQL
- gRPC
- testing
- observability
- configuration
- CLI
- security
- dependency management
- profiling
- migrations
- realtime
- cloud deployment.

## Rule

When Codex promotes a language to first-class status, it must populate all ecosystem-parity categories instead of adding only a hello-world service.


<!-- END 14_ECOSYSTEM_PARITY_AND_COMPLETENESS.md -->

---


<!-- BEGIN 15_EXPANDED_PRODUCT_SURFACES.md -->

# 15 — Expanded Product Surface and Technology Scope

This file adds broad multidisciplinary scope so technologies are exercised by real ATLAS product features.

## Native mobile
- iOS Swift/SwiftUI
- Android Kotlin/Jetpack Compose
- React Native comparison
- Flutter comparison
- auth
- push notifications
- deep links
- secure storage
- offline sync
- background work

## Desktop
- Tauri-style desktop client
- Electron comparison
- filesystem/process integration
- secure credentials
- auto-update concepts
- packaging

## CLI/TUI
Create a real `atlas` CLI:
- login
- organizations/projects
- services
- deploy
- logs
- datasets
- pipelines
- agents
- models
- migrations
- incidents
- security findings
- configuration

Add a TUI for operations where useful.

## Developer platform
- public REST
- GraphQL
- gRPC
- WebSockets/SSE
- webhooks
- API keys
- OAuth apps
- SDK generation
- Python SDK
- TypeScript SDK
- Java SDK
- Go SDK
- C# SDK
- API explorer
- versioning/deprecation

## Real-time collaboration
- presence
- cursors
- shared documents
- optimistic UI
- CRDT/OT concepts
- conflict resolution
- offline reconciliation

## Enterprise IAM
- organizations/tenants
- teams
- RBAC
- ABAC
- OAuth2/OIDC
- SSO
- MFA
- passkeys/WebAuthn
- service accounts
- API keys
- SCIM concepts
- temporary credentials
- session/device management
- access reviews

## Multi-tenancy
Compare:
- shared tables
- row-level security
- schema-per-tenant
- database-per-tenant
- quotas
- isolation
- encryption boundaries
- noisy-neighbor mitigation

## Billing/metering/FinOps
- plans
- subscriptions
- invoices
- payment simulation
- usage events
- AI token usage
- storage/network/compute usage
- quotas
- credits
- cost attribution
- budgets
- alerts

## Search platform
- PostgreSQL FTS
- OpenSearch/Elasticsearch
- Lucene/Solr concepts
- autocomplete
- fuzzy search
- facets
- filters
- ranking
- semantic/vector search
- hybrid search
- reranking

## File/document platform
- multipart uploads
- resumable uploads
- object storage
- metadata
- versioning
- previews/thumbnails
- malware scanning pipeline
- document parsing
- PDF/Office processing
- OCR
- deduplication
- retention
- signed URLs

## Media engineering
- image processing
- audio/video upload
- transcoding
- thumbnails
- metadata
- adaptive streaming
- codecs
- CDN
- queues
- GPU workers

## Geospatial
- PostGIS
- spatial indexes
- geofencing
- heatmaps
- routing concepts
- geospatial datasets
- maps/vector tiles
- fleet/resource tracking

## Time-series
- Prometheus model
- time-series DB patterns
- high-cardinality
- retention
- rollups
- downsampling
- alerting
- forecasting
- anomaly detection

## Event architecture
Support:
- Kafka
- Pulsar
- RabbitMQ
- NATS
- Redis Streams
- cloud pub/sub adapters
- event schemas
- replay
- DLQ
- ordering
- idempotency
- retries

## Durable workflows
- application workflows
- data workflows
- long-running jobs
- retries
- compensation/sagas
- checkpoints
- schedules
- human approval
- versioning

## Modern data platform
- batch
- streaming
- CDC
- ETL/ELT
- lake
- warehouse
- lakehouse
- federated query
- Iceberg
- Delta/Hudi concepts
- streaming-storage concepts
- catalogs
- lineage
- governance
- quality
- data contracts

## Data governance
- ownership
- catalog
- lineage
- sensitivity classification
- PII detection
- masking
- anonymization
- retention
- schema evolution
- access policies
- provenance
- quality

## Data formats/interchange
- JSON
- CSV
- XML
- YAML
- Avro
- Protobuf
- Parquet
- ORC
- Arrow
- Iceberg
- Delta/Hudi concepts
- compression/encoding
- zero-copy

## Multimodal AI
- text
- images
- audio
- video
- documents
- speech-to-text
- text-to-speech
- vision
- OCR
- multimodal embeddings
- multimodal retrieval
- multimodal agents

## AI infrastructure
- model gateway
- provider routing/failover
- local/hosted models
- GPU scheduling
- inference servers
- batching
- KV-cache concepts
- quantization
- LoRA/adapters
- distributed inference/training concepts
- model registry
- prompt registry
- AI observability
- eval gates

## AI governance/security
- model/prompt versions
- approvals
- evaluation gates
- audit
- data policies
- red-team scenarios
- prompt injection defense
- tool scopes
- tenant isolation
- provenance

## Internal developer platform
- service catalog
- ownership
- golden paths
- environment provisioning
- deployment status
- API catalog
- docs
- dependency health
- scorecards
- runbooks

## GitOps
- desired state
- PR-based changes
- Argo CD concepts
- Flux concepts
- drift/reconciliation
- progressive delivery
- rollback

## Advanced networking/service mesh
- NGINX
- Envoy
- HAProxy concepts
- Traefik/Caddy concepts
- service discovery
- retries
- circuit breaking
- traffic splitting
- mTLS
- Istio
- Linkerd concepts
- ingress/egress
- multi-cluster concepts

## Serverless/edge
- functions
- event triggers
- edge workers
- CDN compute
- cold starts
- edge caching
- geographic execution
- security/observability

## WebAssembly
- browser WASM
- WASI/server WASM concepts
- plugin sandboxing
- Rust/C++ to WASM
- performance comparisons

## Virtualization/container internals
- VMs
- hypervisor concepts
- microVMs
- namespaces
- cgroups
- OCI
- containerd/runc concepts
- filesystem layers
- networking
- sandboxing

## Storage engineering
- block
- file
- object
- distributed filesystem concepts
- S3 semantics
- MinIO
- Ceph concepts
- replication
- erasure coding
- lifecycle
- backup/restore
- caching

## Database internals
- WAL
- buffer pool
- page layout concepts
- B+ trees
- LSM
- compaction
- bloom filters
- query parsing/planning
- execution
- locks
- MVCC
- replication
- checkpoints/recovery

These are systems topics, not DSA practice.

## Distributed coordination
- etcd
- Consul
- ZooKeeper concepts
- leases
- distributed locks
- membership
- leader election
- health/configuration
- consensus
- split brain

## HPC/performance
- CPU profiling
- GPU compute
- CUDA concepts
- SIMD/vectorization
- multiprocessing
- mmap
- zero-copy
- Arrow memory
- distributed compute
- load/network profiling

## IoT/edge
- MQTT
- device registry
- provisioning
- certificates
- telemetry
- digital twins concepts
- OTA concepts
- edge processing
- streaming analytics

## Compiler/language tooling
Build an ATLAS DSL for policies/alerts/automation/workflows:
- lexer
- parser
- AST
- validation
- type checking concepts
- optimizer
- interpreter/executor
- syntax highlighting

## Policy/rules
- OPA/Rego concepts
- policy-as-code
- admission policies
- access rules
- automation rules
- alert expressions

## Feature flags/experimentation
- flags
- cohorts
- rollout percentages
- kill switches
- A/B tests
- assignment
- metrics
- statistics
- progressive delivery

## Recommendation/personalization
- retrieval
- ranking
- collaborative filtering
- content-based
- embeddings
- online signals
- evaluation

## Notifications
- email
- push
- SMS abstraction
- webhooks
- in-app
- templates
- preferences
- retries
- delivery tracking
- digests

## Enterprise connectors
Connector SDK for:
- databases
- object stores
- Git providers
- cloud providers
- project/ticket systems
- messaging
- identity
- warehouses
- SaaS APIs

Support:
- OAuth
- API keys
- webhooks
- polling
- rate limits
- pagination
- sync checkpoints
- backoff/retry

## Release engineering
- semantic versioning
- changelogs
- release candidates
- package/container registries
- signing
- provenance
- migrations
- canary
- blue/green
- rollback

## Build systems/monorepo engineering
- npm/pnpm
- Turborepo/Nx concepts
- Python builds/workspaces
- Maven
- Gradle
- Cargo
- Go modules
- CMake
- build cache
- dependency graphs
- affected builds

## Plugin architecture
Extensions:
- UI modules
- connectors
- agent tools
- MCP integrations
- models
- dashboards
- alert rules
- automation

Include:
- manifests
- permission scopes
- lifecycle
- compatibility
- versioning
- sandboxing

## Browser/web internals
- parsing/rendering
- event loop
- hydration
- Server Components concepts
- caching
- service workers
- Web Workers
- browser storage
- CSP
- profiling
- network waterfalls

## Offline-first
- local persistence
- sync queues
- optimistic writes
- conflict resolution
- retries
- background sync
- eventual consistency

## Disaster recovery
- backups
- PITR
- RPO/RTO
- failover
- restore drills
- region outage simulation
- multi-region data

## Chaos engineering
Controlled ATLAS infrastructure only:
- kill services
- delay networks
- fill disk
- exhaust memory
- expire credentials
- fail broker/cache/database replica/region
- corrupt configuration

## Compliance/privacy/governance
- data deletion/export
- retention
- consent concepts
- auditability
- residency
- access reviews
- control mapping

## GreenOps
- utilization
- idle resources
- cost/resource tradeoffs
- storage lifecycle
- energy/carbon concepts

## Production support
- ownership
- on-call
- escalation
- runbooks
- incidents
- status pages
- postmortems
- maintenance windows

## Product analytics
- events
- funnels
- cohorts
- retention
- attribution concepts
- experimentation metrics
- usage analytics

## Knowledge graph/graph analytics
- entity graph
- service graph
- lineage graph
- graph database
- traversal
- graph analytics
- graph-enhanced retrieval

## Rule

Every product surface must use technologies because the feature requires them. Avoid decorative inclusion.


<!-- END 15_EXPANDED_PRODUCT_SURFACES.md -->

---


<!-- BEGIN 16_TECHNOLOGY_REGISTRY.md -->

# 16 — Technology Registry Specification

## Purpose

ATLAS needs a machine-readable registry so the “everything under the sky” objective is measurable and omissions are visible.

Create:

```text
registry/
├── technologies.yaml
├── ecosystems/
│   ├── python.yaml
│   ├── node-typescript.yaml
│   ├── java.yaml
│   ├── dotnet.yaml
│   ├── go.yaml
│   ├── rust.yaml
│   ├── kotlin.yaml
│   ├── scala.yaml
│   ├── php.yaml
│   ├── ruby.yaml
│   ├── elixir.yaml
│   ├── swift.yaml
│   ├── dart-flutter.yaml
│   └── cpp.yaml
├── categories.yaml
├── products.yaml
├── protocols.yaml
├── databases.yaml
├── apache.yaml
├── cloud-native.yaml
└── generated/
```

## Technology record

```yaml
id: python-sqlalchemy
name: SQLAlchemy
ecosystem: python
domain:
  - backend
  - database
category:
  - orm
  - sql-toolkit

status: first_class
maturity: active

integration:
  kind: real_product
  locations:
    - services/analytics-python
  adapter: null

alternatives:
  - django-orm
  - sqlmodel
  - psycopg

capabilities:
  - orm
  - sql-expression
  - transactions
  - pooling
  - async

tests:
  - unit
  - integration
  - migration

docs:
  official: "..."
  internal: "docs/..."

last_verified: "YYYY-MM-DD"
```

## Status vocabulary

- `core`
- `first_class`
- `alternative`
- `reference`
- `legacy`
- `experimental`
- `planned`
- `blocked`
- `deprecated`
- `removed`

## Maturity vocabulary

- active
- maintenance
- historical
- uncertain

Codex must verify current project status before first integration or major upgrade.

## Ecosystem completeness

Each first-class ecosystem gets coverage entries for at least:

- runtime
- web
- ORM
- low-level data access
- migrations
- validation
- serialization
- authn
- authz
- API
- GraphQL
- gRPC
- WebSocket/realtime
- jobs
- queues
- cache
- scheduling
- CLI
- logging
- metrics
- tracing
- error reporting
- testing
- property/fuzz testing
- security
- linting
- formatting
- static analysis
- packaging
- build
- deployment
- profiling
- cloud/serverless
- file/object storage
- SDKs.

The registry should calculate coverage:

```text
Python             50/50
Node/TypeScript    50/50
Java               46/50
.NET               45/50
Go                 41/50
Rust               39/50
...
```

This is implementation inventory, not a learner score.

## Registry UI

Create an ATLAS developer/admin page showing:

- ecosystem
- category coverage
- technologies
- integration status
- version
- last verification
- owner/module
- dependencies
- alternatives
- deprecation
- missing categories.

Example:

```text
Python Ecosystem

Web
✓ Django       first_class
✓ FastAPI      first_class
✓ Flask        first_class
○ Litestar     alternative/planned
○ Sanic        reference
○ Tornado      reference

ORM/Data Access
✓ SQLAlchemy
✓ Django ORM
✓ SQLModel
✓ psycopg
✓ asyncpg
...
```

This is an engineering inventory, not a course page.

## Discovery and expansion

Periodically Codex should:

1. inspect official ecosystem sources,
2. identify significant missing technologies,
3. classify them,
4. verify maintenance/license/security,
5. decide status,
6. create a realistic integration ticket,
7. implement when prioritized.

## No dependency-hoarding

A registry entry does not require installation in the platform core.

A dependency belongs:
- in its service,
- optional adapter,
- isolated integration,
- or metadata/reference only.

## Legacy

ATLAS should include important legacy/enterprise systems where useful:
- SOAP
- old Java enterprise patterns
- older module systems
- traditional server-rendered stacks
- Hadoop MapReduce
- ZooKeeper coordination
- legacy broker/protocol patterns.

Label them.

## Emerging

Emerging technologies stay behind optional adapters until proven.

## Completeness target

The target is not literally every package in npm/PyPI/Maven Central.

The target is:
- every major engineering category,
- every major technology family,
- significant frameworks/tools within supported ecosystems,
- important legacy systems,
- important emerging systems,
- a registry that exposes omissions and can expand indefinitely.

## Progression fields

Each first-class technology must additionally record:

- maximum defined progression level,
- maximum implemented progression level,
- source paths for each level,
- concepts introduced at each level,
- relevant tests,
- architecture/evolution documentation,
- work items that advance the technology.

Use the canonical progression model from `20_PROGRESSIVE_COMPLEXITY_AND_COMMENTS.md`.

The registry UI must show both:
1. ecosystem-category completeness,
2. progressive-complexity completeness.


<!-- END 16_TECHNOLOGY_REGISTRY.md -->

---


<!-- BEGIN 17_REPOSITORY_WORK_MODEL.md -->

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


<!-- END 17_REPOSITORY_WORK_MODEL.md -->

---


<!-- BEGIN 18_OPEN_SOURCE_SOURCING_AND_PROVENANCE.md -->

# 18 — Open-Source Sourcing, Reuse and Provenance Policy

## Purpose

ATLAS should benefit aggressively from the existing open-source ecosystem without becoming a stitched-together Frankenstein repository.

Codex is encouraged to use the internet and public source repositories when available, but all reuse must preserve ATLAS architecture, licensing clarity, security and maintainability.

## Sourcing hierarchy

When implementing a technology or integration, prefer sources in this order:

1. official specification or standard,
2. official framework/project documentation,
3. official framework/project repository,
4. official examples/starters/generators,
5. well-maintained reference implementations,
6. reputable open-source projects,
7. community examples only when the above are insufficient.

## Default integration rule

Prefer, in order:

1. install/use the maintained library as a dependency,
2. generate from the framework's official scaffolding/tooling,
3. integrate an external system through an adapter/API/plugin boundary,
4. adapt a small auditable utility/component,
5. copy source only when there is a strong architectural reason and the license explicitly permits it.

Do not copy an entire repository into ATLAS merely because it already implements something similar.

## What Codex may reuse

Good candidates:
- shadcn source components,
- official framework starters,
- small utilities,
- protocol examples,
- Docker/Kubernetes reference configurations,
- official SDK examples,
- schema definitions,
- permissively licensed UI patterns,
- benchmark harness concepts,
- test patterns,
- generated clients,
- maintained libraries.

## What Codex should not do

Do not:
- blindly concatenate repositories,
- import unknown code without license review,
- copy random blog snippets into production paths,
- mix incompatible architecture styles without adapters,
- duplicate libraries already present,
- hide copied code provenance,
- add abandoned dependencies without an explicit legacy reason,
- import telemetry/tracking unexpectedly,
- bring secrets, credentials or environment-specific configuration from public examples,
- copy vulnerable demo code into production paths.

## Provenance records

Create:

```text
provenance/
├── external-components.yaml
├── imported-code.yaml
├── generated-clients.yaml
└── licenses/
```

For adapted/copied source, record:

```yaml
id: shadcn-data-table-adaptation
source:
  project: shadcn/ui
  url: https://...
  commit_or_version: ...
license: MIT
retrieved_at: YYYY-MM-DD

used_in:
  - packages/ui/src/data-grid/...

reuse_type: adapted_source

changes:
  - integrated ATLAS design tokens
  - added virtualization
  - added accessibility tests

review:
  security: passed
  dependencies: passed
  accessibility: passed
```

Dependencies installed normally through package managers do not each require a copied-source record, but the technology registry must still track significant dependencies.

## License policy

Before copying/adapting source:
- identify license,
- verify compatibility,
- preserve notices/attribution when required,
- do not copy code with unclear licensing.

Create an automated dependency/license inventory where practical.

## Security review for external code

Before adoption inspect:
- transitive dependencies,
- install scripts,
- network calls,
- telemetry,
- filesystem access,
- credential handling,
- unsafe deserialization,
- code execution,
- known vulnerabilities,
- package maintenance/activity.

## UI-specific rule

For online UI components:
- prefer shadcn/ui and owned source,
- inspect community registry source,
- normalize design tokens,
- remove unwanted tracking,
- verify keyboard/screen-reader behavior,
- add interaction tests.

## Architecture preservation

External code must conform to ATLAS boundaries.

Bad:

```text
ATLAS service
  directly depends on three unrelated vendor-specific APIs everywhere
```

Good:

```text
ATLAS interface
      |
      +-- Provider A adapter
      +-- Provider B adapter
      +-- Provider C adapter
```

## “Use existing code” strategy

Codex should absolutely study strong public implementations to accelerate work.

The desired behavior is:

```text
study existing engineering
        +
use official libraries
        +
reuse audited pieces
        +
generate ATLAS-owned integration
        +
test/security/telemetry
        =
cohesive ATLAS implementation
```

not:

```text
repo A + repo B + repo C copied together
```

## Version pinning

Pin meaningful runtime/dependency versions through:
- lockfiles,
- container tags,
- build manifests,
- technology registry.

Avoid unbounded `latest` tags for reproducible infrastructure.

## Dependency replacement

Provider interfaces should make it possible to replace important technologies later without rewriting the full product.

This is a deliberate ATLAS learning mechanism.


<!-- END 18_OPEN_SOURCE_SOURCING_AND_PROVENANCE.md -->

---


<!-- BEGIN 19_AUTONOMOUS_EXECUTION_AND_COMPLETION.md -->

# 19 — Autonomous Execution, Completion and Checkpoint Protocol

## Objective

When Codex is instructed to build ATLAS, it must perform implementation work rather than repeatedly stopping to propose more plans.

The scope is intentionally enormous. Completion therefore means continuous execution through the roadmap, with durable checkpoints whenever platform/session/tool limits prevent further work in the current run.

## Core execution rule

> **Do not voluntarily stop after planning, scaffolding, one page, one service, or one milestone. After completing and verifying the current coherent slice, immediately continue with the next highest-priority incomplete item.**

Continue until:
- the entire currently defined ATLAS scope is implemented and verified, or
- an external/tool/session/resource limitation makes further execution impossible.

## If blocked by an implementation decision

Do not ask the user for ordinary architecture choices that can reasonably be resolved from the context.

Use:
1. existing ATLAS architecture,
2. official best practices,
3. stable maintained defaults,
4. the simplest extensible choice.

Record non-trivial decisions in an ADR.

Ask only when there is genuinely missing information that cannot safely or correctly be inferred.

## If blocked by unavailable credentials/cloud resources

Implement:
- local equivalent,
- interface/provider,
- mock or emulator where appropriate,
- documented environment variables,
- integration tests that can run without production credentials.

Do not halt the rest of ATLAS because one external provider is unavailable.

## If a session/tool/runtime limit forces a stop

Before stopping, create/update:

```text
CHECKPOINT.md
.atlas/progress.json
```

`CHECKPOINT.md` must include:

```text
Current roadmap phase
Last completed task
Files created/changed
Architecture decisions
Database migrations
Commands run
Tests passing
Tests failing
Known issues
Services currently expected to run
Uncommitted/partial work
Exact next task
Exact next command
```

`.atlas/progress.json` should be machine-readable:

```json
{
  "current_phase": "...",
  "last_completed_task": "...",
  "next_task": "...",
  "quality_gates": {
    "lint": "pass",
    "typecheck": "pass",
    "unit": "pass",
    "integration": "pass",
    "e2e": "not_run"
  },
  "blocked": false,
  "blocker": null
}
```

The next Codex run must read these files first and continue.

## Continuous build loop

Repeat:

1. read authoritative context,
2. inspect current repo/progress,
3. select next coherent item,
4. implement actual files/code/config/migrations/tests,
5. run format/lint/typecheck,
6. run relevant tests,
7. run/build the real product,
8. verify visible/API/data behavior,
9. verify security/observability requirements,
10. fix discovered failures,
11. update technology registry/provenance,
12. update ADR/work item/progress,
13. continue to the next item.

## Definition of “implemented”

A feature is not implemented if it consists only of:
- empty files,
- comments,
- TODOs,
- mock cards,
- fake data with no path to real data,
- routes with placeholder text,
- uncalled service code,
- interfaces with no implementation.

Stubs are permitted only for dependencies that genuinely cannot be exercised locally, and must be clearly documented.

## Generate all necessary project files

Codex is explicitly authorized and instructed to create whatever repository files are needed, including:

- source files,
- package manifests,
- workspace files,
- environment templates,
- Dockerfiles,
- Compose manifests,
- database schemas,
- migrations,
- seed scripts,
- contracts,
- protobuf/schema files,
- API definitions,
- frontend components,
- styles,
- services,
- workers,
- CLI clients,
- mobile/desktop clients,
- SDKs,
- tests,
- fixtures,
- benchmarks,
- infrastructure code,
- CI workflows,
- observability configuration,
- security configuration,
- policies,
- documentation,
- ADRs,
- runbooks,
- registry metadata,
- provenance metadata,
- scripts,
- tooling.

Do not wait for the user to create boilerplate files manually.

## Quality recovery

If a quality command fails:
- inspect failure,
- fix it,
- rerun,
- repeat until passing or a genuine external blocker is identified.

Do not knowingly move to the next phase leaving ordinary compilation/type/lint/test errors behind.

## Resource-aware implementation

ATLAS may include components too heavy to run simultaneously on a normal laptop.

Support profiles such as:
- core
- web
- database
- data
- ai
- streaming
- observability
- security
- full

A developer editing React should not need the entire big-data stack running.

## Long-range completion

The roadmap is expected to take many implementation cycles.

Codex must treat `CHECKPOINT.md`, `.atlas/progress.json`, the registry and roadmap as persistent memory so each run continues the same build rather than restarting architecture design.

## Final completion criteria

Do not mark ATLAS complete until:
- required product surfaces exist,
- core flows are integrated,
- major ecosystems meet parity targets,
- tests/security/observability are operational,
- infrastructure is reproducible,
- technology registry shows defined scope coverage,
- no critical placeholder-only areas remain,
- documented quality gates pass.


<!-- END 19_AUTONOMOUS_EXECUTION_AND_COMPLETION.md -->

---


<!-- BEGIN 20_PROGRESSIVE_COMPLEXITY_AND_COMMENTS.md -->

# 20 — Progressive Complexity and Commented-Code Architecture

## Purpose

ATLAS must expose **progressive complexity for every major technology and engineering concept**.

The learner should not be dropped directly into the most abstract production implementation.

Instead, ATLAS should deliberately preserve a progression from:

```text
FOUNDATION
   ↓
SIMPLE
   ↓
REALISTIC
   ↓
ADVANCED
   ↓
COMPLEX
   ↓
DISTRIBUTED / SCALE
   ↓
PRODUCTION-HARDENED
   ↓
EXPERT / ALTERNATIVE ARCHITECTURE
```

The learner still works primarily from the IDE and modifies the real repository.

This progression is **not** a tutorial playground. It is implemented through increasingly sophisticated versions, modules, services, branches/configurations, adapters, work items and real product flows inside the ATLAS repository.

---

# 1. Progression model

Every substantial technology should be classified into one or more progression levels.

Recommended canonical levels:

## L0 — Foundation

Purpose:
- expose the smallest meaningful implementation,
- remove unnecessary abstraction,
- make execution flow obvious.

Examples:
- one HTTP endpoint,
- one SQL query,
- one React component,
- one queue producer/consumer,
- one simple model inference call,
- one Docker container.

L0 should still be correct and tested.

## L1 — Simple Product Integration

Purpose:
- connect the technology to an actual ATLAS feature.

Examples:
- CRUD API backed by PostgreSQL,
- React table fetching real API data,
- Redis caching a real endpoint,
- background job processing a real ATLAS task,
- simple ML model powering a real prediction feature.

## L2 — Realistic Engineering

Add:
- validation,
- errors,
- configuration,
- repository/service layers where useful,
- migrations,
- auth,
- tests,
- logging,
- retries,
- pagination,
- caching,
- typed contracts.

This should resemble normal professional application code.

## L3 — Advanced

Add:
- concurrency,
- async behavior,
- complex queries,
- event-driven processing,
- batching,
- rate limiting,
- multiple workers,
- background pipelines,
- advanced framework features,
- richer testing,
- performance considerations.

## L4 — Complex System

Add:
- multiple services,
- event contracts,
- distributed workflows,
- idempotency,
- partial failure,
- tracing,
- multi-tenancy,
- security boundaries,
- scaling decisions,
- alternate implementations.

## L5 — Scale / Distributed

Add:
- high data volume,
- partitioning,
- sharding concepts,
- replicas,
- distributed caches,
- streaming,
- cluster execution,
- autoscaling,
- backpressure,
- multi-region or fault-domain thinking,
- large-scale benchmarks.

## L6 — Production-Hardened

Add:
- SLOs,
- alerts,
- audit,
- disaster recovery,
- security hardening,
- dependency failure policies,
- rollout/rollback,
- migrations,
- compatibility,
- feature flags,
- capacity planning,
- performance budgets,
- operational runbooks.

## L7 — Expert / Alternate Architecture

Use for:
- migration to a competing framework,
- provider replacement,
- language rewrite,
- alternate architecture,
- deep optimization,
- low-level implementation,
- source/runtime internals,
- custom protocol/DSL,
- experimental systems.

Not every technology needs all eight levels immediately, but first-class technologies should progress as far as technically meaningful.

---

# 2. Progression must exist in the repository, not only the UI

The repository should make progression visible.

Possible structures include:

```text
services/examples/http/python-fastapi/
├── l0-foundation/
├── l1-simple-product/
├── l2-realistic/
├── l3-advanced/
└── README.md
```

However, do **not** duplicate large codebases unnecessarily.

For large real services, progression can instead be represented through:

- Git history/migration commits,
- versioned architecture modules,
- feature flags,
- provider implementations,
- archived/reference implementations,
- `evolution/` folders,
- engineering tickets,
- ADRs,
- before/after implementations,
- progressively more complex sibling services.

Recommended pattern:

```text
services/analytics-python/
├── src/
├── tests/
├── evolution/
│   ├── 01-naive-query/
│   ├── 02-indexed-query/
│   ├── 03-cache/
│   ├── 04-preaggregation/
│   └── 05-clickhouse/
└── docs/
    └── evolution.md
```

The active production-style implementation remains clean.

The `evolution/` directory preserves smaller historical/reference variants.

---

# 3. Website progression feature

ATLAS should have a real product/developer page for technology progression.

Suggested routes:

```text
/developer/technologies
/developer/technologies/[technology]
/developer/technologies/[technology]/progression
/developer/architecture/evolution
/developer/work
```

This is an engineering explorer, not a course portal.

Technology page example:

```text
FastAPI
────────────────────────────────────

Integration status: First Class
Used by: Analytics API, AI Gateway

Progression

L0  Minimal HTTP Endpoint                  ✓
L1  CRUD + PostgreSQL                      ✓
L2  Validation + SQLAlchemy + Alembic      ✓
L3  Async + Background Jobs + Cache        ✓
L4  Events + Auth + Rate Limits            ✓
L5  Horizontal Scaling + Kafka             ○
L6  SLO + DR + Security Hardening          ○
L7  Compare with Django / Go Rewrite       ○
```

Clicking a level should show:

- source locations,
- architecture diagram,
- relevant commits or evolution modules,
- tests,
- dependencies introduced at that level,
- work items,
- performance/security changes,
- comparison to previous level.

The UI must point the learner back to the **real repository paths**.

---

# 4. Progression metadata

Extend the technology registry.

Suggested schema:

```yaml
id: python-fastapi
name: FastAPI
status: first_class

progression:
  max_defined_level: 7
  max_implemented_level: 5

  levels:
    - level: 0
      name: foundation
      status: complete
      source:
        - examples/evolution/fastapi/l0-foundation
      concepts:
        - routing
        - request-response

    - level: 1
      name: simple-product
      status: complete
      source:
        - services/example-api
      concepts:
        - CRUD
        - postgres

    - level: 2
      name: realistic
      status: complete
      concepts:
        - pydantic
        - sqlalchemy
        - alembic
        - testing
        - validation

    - level: 3
      name: advanced
      status: complete
      concepts:
        - async
        - redis
        - background-jobs

    - level: 4
      status: complete
      concepts:
        - kafka
        - oauth
        - rate-limiting
        - tracing

    - level: 5
      status: planned
      concepts:
        - autoscaling
        - load-testing
```

The registry UI should show progression completeness separately from ecosystem-category completeness.

---

# 5. Every important technology gets progression

Examples:

## APIs

```text
L0 GET /health
L1 CRUD
L2 validation + DB + errors
L3 auth + pagination + cache
L4 async jobs + events
L5 gateway + multiple services
L6 rate limits + SLO + observability + DR
L7 protocol/provider migration
```

## PostgreSQL

```text
L0 table + SELECT
L1 CRUD + joins
L2 indexes + transactions
L3 EXPLAIN + locking + MVCC
L4 partitioning + replication
L5 high-volume workload
L6 backup/PITR/failover/audit
L7 internals / alternative architecture
```

## Redis

```text
L0 key/value
L1 cache
L2 TTL/invalidation
L3 distributed cache patterns
L4 streams/locks/rate limiting
L5 clustering/large workload
L6 failure/recovery/security
```

## Kafka

```text
L0 producer + consumer
L1 topic + partitions
L2 consumer groups
L3 schemas + retries + DLQ
L4 idempotency + event-driven services
L5 high-throughput/backpressure
L6 security/observability/DR
L7 replace with Pulsar/NATS/RabbitMQ
```

## React

```text
L0 component
L1 state + forms
L2 API integration
L3 composition + state architecture
L4 complex tables/charts/realtime
L5 performance/virtualization
L6 accessibility/error boundaries/production monitoring
L7 alternate state/rendering architecture
```

## Next.js

```text
L0 route/page
L1 layouts/components
L2 data fetching/server-client boundaries
L3 auth/forms/caching
L4 streaming/server actions/complex product flows
L5 performance/CDN/large application
L6 security/observability/reliability
L7 architecture migrations
```

## Django

```text
L0 view + URL
L1 model + template/API
L2 ORM + migrations + forms/DRF
L3 auth + permissions + Celery
L4 events/cache/search
L5 multi-service/high volume
L6 security/observability/DR
L7 migration/alternate implementation
```

## SQLAlchemy

```text
L0 engine + query
L1 ORM model/session
L2 relationships/transactions
L3 async/pooling
L4 repository/unit-of-work patterns
L5 performance/query optimization
L6 production connection/failure behavior
L7 compare Django ORM/SQLModel/raw SQL
```

## Node.js

```text
L0 native HTTP
L1 Express
L2 Fastify/Nest + validation
L3 ORM + queue + cache
L4 worker threads/events/realtime
L5 distributed services
L6 profiling/security/observability
L7 framework/runtime replacement
```

## Machine learning

```text
L0 baseline
L1 train/evaluate
L2 preprocessing/pipeline
L3 tuning/cross-validation
L4 registry/serving
L5 distributed/large-data training
L6 monitoring/drift/rollback
L7 alternate model/serving architecture
```

## RAG

```text
L0 document → embedding → retrieve → answer
L1 chunking/vector store
L2 metadata/filtering/citations
L3 hybrid search/reranking
L4 eval suite + tracing
L5 scale/multi-tenant
L6 security/governance/caching/reliability
L7 alternate retrieval architectures
```

## Agents

```text
L0 one tool
L1 multiple tools
L2 structured state
L3 workflow graph
L4 human approval + permissions
L5 multi-agent/distributed tools
L6 security/evals/observability/reliability
L7 alternative orchestration/framework-free rewrite
```

## Docker

```text
L0 Dockerfile
L1 multi-container Compose
L2 volumes/networks/healthchecks
L3 multi-stage builds
L4 security/scanning
L5 production images/build cache
L6 supply chain/signing/SBOM
L7 alternative runtime/WASM/containers internals
```

## Kubernetes

```text
L0 Pod
L1 Deployment + Service
L2 ConfigMap/Secret/Ingress
L3 probes/resources/HPA
L4 Helm/policies
L5 multi-service/observability
L6 security/HA/DR
L7 multi-cluster/service mesh/GitOps
```

Apply an equivalent ladder to every first-class technology.

---

# 6. "Simple spontaneous API" requirement

ATLAS should intentionally contain small APIs that appear naturally as product needs emerge.

Examples:

```text
GET /health
GET /version
GET /users/:id
POST /notes
GET /projects/:id/summary
POST /webhooks/test
```

These should coexist with increasingly complex APIs:

```text
POST /v1/datasets/:id/analysis
POST /v1/agents/:id/runs
GET  /v1/analytics/query
POST /v1/workflows/:id/execute
```

And advanced/distributed flows:

```text
API Gateway
  ↓
Auth
  ↓
Command Service
  ↓
Event Bus
  ↓
Multiple consumers
  ↓
Read model / analytics
```

This evolution should be documented and visible.

---

# 7. Code commenting philosophy

ATLAS source must be **extensively commented for comprehension**, but comments must be high-value.

Do not produce noise such as:

```python
# increment i
i += 1
```

Prefer comments that explain:

- why this abstraction exists,
- why this library/framework was chosen,
- assumptions,
- invariants,
- failure behavior,
- concurrency concerns,
- transaction boundaries,
- security boundaries,
- performance tradeoffs,
- protocol behavior,
- non-obvious framework behavior,
- compatibility concerns,
- why an apparently simpler solution is insufficient,
- links to ADRs/specifications.

Example:

```python
# We deliberately commit the database transaction before publishing the
# integration event. The outbox row is written in the same transaction as
# the domain change, so a process crash cannot persist one without the other.
# A separate relay publishes the outbox event to Kafka.
with session.begin():
    order.status = OrderStatus.CONFIRMED
    outbox.append(OrderConfirmed.from_order(order))
```

This teaches real engineering.

---

# 8. Comment density by progression level

## L0/L1

Comments can be more educational and explicit.

Explain:
- syntax that is unusual,
- execution flow,
- framework lifecycle,
- important types.

## L2/L3

Shift toward:
- design intent,
- framework behavior,
- error handling,
- transaction scope,
- async/concurrency concerns.

## L4+

Comments should resemble excellent production code:
- invariants,
- distributed-system assumptions,
- consistency guarantees,
- failure behavior,
- security boundaries,
- performance rationale,
- links to ADRs/runbooks.

Do not turn expert code into line-by-line prose.

---

# 9. Docstrings and API documentation

For significant public modules/classes/functions:

Use language-native documentation conventions.

Python:
- docstrings
- type hints

TypeScript:
- TSDoc/JSDoc for exported complex APIs

Java:
- Javadoc

C#:
- XML docs where useful

Go:
- Go doc comments

Rust:
- rustdoc

C/C++:
- Doxygen-style comments where appropriate

Documentation should include, where relevant:

- purpose,
- parameters,
- return value,
- exceptions/errors,
- side effects,
- concurrency,
- transaction behavior,
- security requirements,
- example usage.

---

# 10. Architecture comments

Every non-trivial service should contain:

```text
README.md
ARCHITECTURE.md
```

or link to central architecture documentation.

Explain:

- responsibility,
- public contracts,
- dependencies,
- data stores,
- events produced,
- events consumed,
- scaling model,
- security boundary,
- telemetry,
- common failure modes,
- local run instructions.

---

# 11. Evolution documentation

Each first-class technology/service should maintain an evolution record.

Example:

```text
docs/evolution/analytics-api.md
```

Possible content:

```text
V0 naive synchronous endpoint
V1 repository/database
V2 indexes
V3 Redis cache
V4 asynchronous refresh
V5 event-driven aggregation
V6 ClickHouse analytical backend
```

The learner should be able to see **why complexity was introduced**.

---

# 12. Complexity must be earned

Do not start with:

```text
API Gateway + Service Mesh + Kafka + CQRS + Event Sourcing + 14 services
```

for something that only requires one CRUD endpoint.

Progression should demonstrate:

```text
simple solution
        ↓
new requirement/problem
        ↓
specific complexity introduced
```

Example:

```text
direct DB query
     ↓
page becomes slow
     ↓
index
     ↓
read volume rises
     ↓
cache
     ↓
analytics workload grows
     ↓
preaggregation/ClickHouse
```

This is central to ATLAS.

---

# 13. Progression work items

Create tickets tied to levels.

Example:

```text
ATLAS-API-P01
Add a simple projects endpoint.

ATLAS-API-P02
Add validation and PostgreSQL persistence.

ATLAS-API-P03
Add authentication and pagination.

ATLAS-API-P04
Introduce Redis caching.

ATLAS-API-P05
Emit project events to Kafka.

ATLAS-API-P06
Scale the service under load.

ATLAS-API-P07
Add SLOs, tracing and disaster behavior.
```

The UI can display the sequence, but the code changes happen in the IDE.

---

# 14. Progression dashboard

Add a developer-focused page:

```text
Engineering Progression
─────────────────────────────────

Technology         Foundation  Simple  Realistic  Advanced  Complex  Scale  Prod  Expert
Python/FastAPI         ✓         ✓        ✓          ✓        ✓       ○     ○      ○
PostgreSQL             ✓         ✓        ✓          ✓        ✓       ✓     ○      ○
Kafka                  ✓         ✓        ✓          ✓        ○       ○     ○      ○
Kubernetes             ✓         ✓        ✓          ○        ○       ○     ○      ○
RAG                    ✓         ✓        ✓          ✓        ○       ○     ○      ○
```

Clicking a cell should navigate to source references, work items, architecture/evolution docs and test results.

---

# 15. Complexity comparisons

For important transitions, retain measurable comparisons.

Examples:

- naive query vs indexed query,
- synchronous vs async,
- single process vs workers,
- no cache vs Redis,
- pandas vs Polars,
- REST polling vs WebSocket,
- monolith implementation vs service extraction,
- single broker vs partitioned stream,
- one replica vs autoscaling,
- baseline ML model vs tuned model,
- simple retrieval vs hybrid+rereanking.

Show **why** the advanced design exists.

---

# 16. Acceptance criteria

A first-class technology is not considered well-covered unless:

- [ ] foundation implementation exists,
- [ ] real ATLAS integration exists,
- [ ] progression metadata exists,
- [ ] source paths are linked,
- [ ] code contains meaningful explanatory comments,
- [ ] tests exist at relevant levels,
- [ ] evolution rationale is documented,
- [ ] advanced levels introduce complexity only for a reason,
- [ ] registry reports current max level,
- [ ] website exposes progression status,
- [ ] realistic work items exist for advancing the implementation.

---

# 17. Codex rule

Whenever Codex adds a first-class technology:

1. create its simplest meaningful implementation,
2. integrate it into a real ATLAS product feature,
3. define its progression ladder,
4. implement successive useful complexity levels,
5. add high-value comments/docstrings,
6. preserve evolution examples without duplicating the whole application,
7. create tests,
8. record source paths in the registry,
9. update the progression dashboard,
10. continue advancing until the defined progression is complete or blocked by real constraints.


<!-- END 20_PROGRESSIVE_COMPLEXITY_AND_COMMENTS.md -->

---
