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
