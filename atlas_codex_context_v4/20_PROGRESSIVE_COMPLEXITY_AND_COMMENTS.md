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
