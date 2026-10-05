# Control-plane API architecture

- **Responsibility:** tenant-aware project metadata and collaboration operations.
- **Contract:** versioned REST/OpenAPI plus tenant-scoped SSE; `/health` and `/metrics`
  are operational endpoints.
- **Storage:** SQLAlchemy supports local SQLite and PostgreSQL without changing domain code.
- **Security:** bearer auth is required for product routes. The local provider is deliberately
  replaceable by OIDC; credentials are never accepted in query strings.
- **Telemetry:** request correlation, structured logs, counters, and duration histograms.
- **Scaling:** stateless HTTP replicas; database is the current coordination boundary.
- **Failure:** database failure makes readiness fail and product requests return an error;
  no in-memory fallback can silently diverge from authoritative state.
- **Repository AI:** only an allowlisted read-only source snapshot is exposed. The
  model receives no tools; original code is reattached after strict output validation.
  Hosted Responses and operator-enabled local Chat Completions adapters normalize
  SSE deltas and expose redacted readiness behind one provider contract. Prompt
  revisions are append-only, tenant-scoped relational records.
# Usage streaming boundary

`streaming_routes.py` composes request-scoped `UsageStream` sinks and a stable
`Broker` provider contract. SQLite is a durable local source; optional
`KafkaBroker` performs real broker I/O with manual partition/group offsets and
explicit acknowledgements. The sink commits deduplicated event effects before
acknowledgement. `streaming_export.py` and `usage_lakehouse.py` expose bounded
accepted-sink Parquet and local Iceberg projections. Owner/development/independent
opt-in gates and server-owned tenant/path/topic configuration constrain authority.
See ADR 0012 and `docs/runbooks/usage-streaming.md` for contracts, delivery semantics,
quota, telemetry, Windows filesystem compatibility and deferred distributed work.
