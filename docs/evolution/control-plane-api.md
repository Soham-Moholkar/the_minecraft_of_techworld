# Control-plane API evolution

- L0: `/health` and `/version`, correct and tested.
- L1: organization/project/note product flow through the repository adapter.
- L2: validation, auth boundary, pagination, migrations, security headers, logs,
  metrics, PostgreSQL/SQLite providers, tenant-scoped authorization, atomic audit
  evidence, integration and security regression tests.
- L3 next: OIDC sessions, fine-grained RBAC, audit outbox, Redis cache/rate limiting,
  background jobs.
- L4+: event contracts, idempotent consumers, trace propagation,
  scale tests, SLOs, DR, and alternate Go/Django implementations.
