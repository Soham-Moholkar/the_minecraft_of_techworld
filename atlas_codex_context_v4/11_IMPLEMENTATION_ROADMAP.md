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