# ADR-0001: pnpm monorepo with a Python control plane

- Status: accepted
- Date: 2026-08-27

ATLAS begins with a Next.js product shell and FastAPI control-plane API in one
pnpm-oriented monorepo. Python packaging remains service-local. SQLAlchemy is the
data-access boundary so SQLite can provide a zero-service L0/L1 experience while
PostgreSQL is authoritative in the core Compose profile.

This earns complexity gradually: no broker, cache, or cluster is required until
load, asynchronous work, or durability requirements justify it.

