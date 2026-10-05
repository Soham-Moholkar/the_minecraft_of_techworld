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
