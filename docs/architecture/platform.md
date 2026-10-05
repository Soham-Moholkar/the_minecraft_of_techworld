# ATLAS platform architecture

```text
Browser
  → Next.js shell + same-origin BFF
      → FastAPI control plane
          → SQLAlchemy provider
              ├─ PostgreSQL (core profile)
              └─ SQLite (zero-service/local tests)

REST / GraphQL / gRPC clients
  → Node protocol facade
      → shared ProjectProvider
          → authenticated FastAPI control-plane API
```

The frontend does not embed a development API token. Next.js route handlers own
the local service credential and enforce bounded upstream timeouts. The API owns
validation, authentication, transaction boundaries, correlation, logs, metrics,
and database health. Migrations, deterministic seed data, tests, containers, and
CI travel with the slice.

The Node facade deliberately owns no second project database. REST, GraphQL, and
gRPC execute one typed provider contract and delegate to the authoritative FastAPI
API. This makes protocol semantics comparable without creating divergent data models.

The database inspection path is similarly narrow. The browser requests a named,
validated query through the same-origin BFF; FastAPI maps that name to fixed SQL and
bound parameters, applies the authenticated tenant slug, and asks the active dialect
for a plan. PostgreSQL `EXPLAIN (FORMAT JSON)` and SQLite `EXPLAIN QUERY PLAN` are
normalized into one read-only contract. Clients never submit SQL, so the educational
inspection surface does not become an arbitrary-query execution endpoint.

The adjacent concurrency profile follows the same rule. It reads fixed engine
settings and describes provider semantics without changing transaction state. A
separate disposable SQLite lab owns the stateful two-connection experiments, so
lock acquisition, rollback, and retry evidence cannot interfere with product data.

Repository intelligence follows an equally narrow read path. The authenticated
API creates a bounded, request-local index from allowlisted source, ranks
overlapping line chunks through a lexical/embedding provider contract, and
returns exact content-hash citations. The same-origin BFF validates requests and
responses before the workspace renders snippets. Immutable tenant evaluation
records measure grounding, citation integrity and injection detection; models
still receive no repository write or execution capability.

Hosted inference is guarded by a durable tenant reservation ledger. A short
database transaction serializes budget admission, then commits before outbound
network I/O; success settles actual usage and failures release the reservation.
Automatic hosted-to-local failover is allowed only before output begins. A
content-hash LRU accelerates chunk construction without becoming authoritative,
and the operations contract exposes remaining budget plus rolling availability
and p95 latency targets to the same workspace.
