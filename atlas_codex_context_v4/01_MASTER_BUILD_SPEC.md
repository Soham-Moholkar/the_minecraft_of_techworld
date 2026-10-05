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
