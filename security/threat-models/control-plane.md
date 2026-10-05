# Control-plane threat model

## Assets and boundaries

Tenant projects, notes, credentials, and audit context cross Browser → Next.js BFF
→ FastAPI → PostgreSQL boundaries. The public browser never receives the service
credential. Database credentials exist only in process/container configuration.

## Initial STRIDE review

- Spoofing: bearer validation and constant-time comparison; OIDC is the next level.
- Tampering: typed schemas, bounded strings, ORM parameterization, server-side auth.
- Repudiation: correlation/structured logs and tenant-scoped immutable audit events exist;
  an event outbox for external delivery remains pending.
- Information disclosure: sanitized errors and restrictive headers; WebSocket URLs
  carry only opaque, short-lived, one-use tickets—not the durable bearer credential.
- Denial of service: pagination/body/message/connection caps, upstream timeouts, and
  per-socket rate limits exist; general HTTP rate limiting remains pending.
- Elevation: principal and repository-level organization boundaries exist and have
  cross-tenant regression coverage; fine-grained RBAC/ABAC remains pending.

## Verified controls

- Credentials stay in the Next.js server runtime and never enter browser props.
- WebSocket tickets expire, are atomically consumed once, and are issued only through
  a same-origin BFF route; the API validates Origin before ticket redemption.
- Every project, note, search, and audit query is scoped by the principal tenant.
- Project/note mutation and its audit evidence commit in the same transaction.
- Unknown or cross-tenant identifiers return 404 to avoid existence disclosure.
- Remaining priority: signed OIDC sessions, CSRF protection, role policies, key
  rotation, rate limiting, device/session management, and external audit delivery.
# Phase 10 local streaming/lakehouse boundary

- Asset: tenant synthetic counters, consumer offsets, accepted effects, immutable snapshots.
- API selects tenant from Principal, fixes topic/group/table names, and rejects
  caller tenant/broker/path fields. Owner role, development environment and independent
  opt-ins gate operations. This dev identity/BFF is not suitable for shared deployment.
- Admission caps raw POST bytes before JSON parsing and validates strict event/batch
  schemas. Broker payloads are size bounded and inert; no tools/SQL/file inputs run.
- Sink commits precede acknowledgements. Duplicate IDs deduplicate effects; conflicting
  IDs and malformed/negative counters cannot overwrite accepted units. Retention gaps
  block consumption rather than silently losing history. Failed broker publish can be
  partial and must be retried with stable identities.
- Quarantine/logs/metrics omit rejected payloads and credentials. Tenant-scoped exports
  include accepted IDs/counters only and embed lineage. Fixed filenames, no-store,
  nosniff and redacted BFF/API failures limit accidental exposure.
- Standalone SQLite source/effect storage and local Iceberg history have quotas. Catalog
  optimistic conflicts fail; orphan files from failed writes and explicit snapshot expiry
  need future maintenance. Paths/catalog are trusted operator configuration. Windows
  compatibility uses the local FileIO URI parser; remote catalogs are not exposed.
- Kafka host port binds loopback and disables automatic topics. PLAINTEXT is local only;
  TLS/SASL/ACLs, distributed group coordination, persistent container storage, retention
  recovery, production identity and end-to-end traces remain acceptance gaps.

# Cross-phase BFF and orchestration corrections

Project/note writes now share same-origin admission, streamed 16KB body limits,
strict input schemas, UUID path validation and provider response/error redaction.
Health/project/audit reads validate contracts and prohibit caching. Client views
validate responses independently and cancel unmounted requests. General session
CSRF/OIDC remains a production requirement beyond this local origin guard.

The usage Airflow status adapter requires owner/development/independent opt-in,
server-owned tenant/DAG/URL/JWT, disables redirects and environment proxies, caps
provider bytes and record counts, and projects only fixed run/task observations.
Conf, logs, notes, rendered fields and XCom never cross the status boundary.
Its API is read-only. Manual tasks ignore dag_run.conf and use a server-held API
credential; source defines HTTP operations, 100-event batch, timeouts/retries and
DAG concurrency. XCom retains bounded aggregates/digest only. Consume has no
automatic retries because an uncertain response can hide a committed batch.
Live scheduler and runtime authority acceptance remain pending; this is trusted
single-tenant development, not shared remote worker isolation.

Named usage/Kafka volumes now preserve state through recreation. Paths are owned
by runtime images; no destructive cleanup endpoint or automatic offset reset was
added. Volume permissions/startup/retention still require real runtime verification.

Development Compose publishers are now loopback-only, including existing database,
API/web and Node protocol ports. The consistency gate rejects profiles that widen
host exposure while retaining known development credentials. Source-owned BFF
requests reject redirects and cap streamed provider output before projection.

Spark observations require an independent opt-in, owner/development identity and
the server-selected tenant/provider directory. The HTTP surface cannot submit jobs
or select SQL, paths or master endpoints. A receipt is trusted local operator state,
not remote attestation: namespace/type/bytes/time/aggregate bounds, current content
digest and current source aggregates are checked. The worker has a bounded source,
exclusive input lock, atomic receipt replace and a four-minute job deadline. API
containers mount shared compute state read-only. No Spark RPC ports are published.

Flink observations require the configured tenant, owner/development opt-in and a
fixed 32-hex job ID. Provider reads disable redirects/proxies, cap response bytes,
bound vertices and project no plans/configuration/checkpoint paths. Deprecated
pressure is unavailable. The unauthenticated local Flink REST listener remains
loopback-only; the BFF exposes none of its submit/cancel/savepoint controls. Only
the jobmanager/client receives the usage API credential, not the taskmanager.
Live Linux job/recovery/container acceptance is pending. PyFlink's older constrained
Beam/Arrow decoder is isolated, receives only the authenticated fixed-schema bounded
export, and needs runtime/dependency review before broader deployment.

BI receives only a separately stored accepted-usage aggregate and lineage digest.
Native read-only SQLite enforcement is tested; the Superset container additionally
mounts the projection read-only and has separate metadata storage. Login/CSRF stay
enabled, secrets and accounts are operator-supplied, and template/guest execution
is disabled. Live container, observer role, chart and refresh acceptance remain
pending. ATLAS only reads bounded publication metadata for the configured ID and
tenant-specific title with a server token. Publication does not attest freshness;
no SQL, CSS, provider owners, raw event identities or application data cross that
observation boundary. The fixed projection command has no HTTP execution endpoint.

Canvas stage selection and refresh use only the existing bounded streaming and
compute GET contracts. No graph editing, job submission or artifact publication
authority is added. Failed contracts clear old observations, independent requests
retain partial evidence, and unmounted reads are cancelled. Source-defined edges
and separately checked receipts never imply an atomic cross-provider snapshot.
