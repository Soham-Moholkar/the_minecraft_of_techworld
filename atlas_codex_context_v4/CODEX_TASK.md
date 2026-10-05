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
