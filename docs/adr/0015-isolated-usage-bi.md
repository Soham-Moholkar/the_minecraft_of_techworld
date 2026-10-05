# ADR 0015 — Isolated aggregate usage BI

Status: accepted for trusted local development; Superset runtime acceptance pending.

BI receives one aggregate row per configured tenant/provider, derived from the
existing bounded and lineage-validated accepted-event Parquet contract. A fixed
operator command writes a separate SQLite projection transactionally. It excludes
raw event identities, rejected payloads, notes, credentials and application tables.
The command is not exposed as a browser-triggered export or SQL endpoint.

Superset 6.1.0 uses separate metadata storage and a read-only projection mount.
Its configured SQLite connection includes `mode=ro&uri=true`; a native SQLAlchemy
regression verifies that writes fail. Login and CSRF remain enabled, the operator
supplies a strong secret and creates accounts explicitly, and the observer role is
limited to the owned dataset/dashboard. The optional profile binds loopback and
caps resources. Actual container mount, role and chart enforcement need Linux
acceptance, independently of the native SQLite test.

The ATLAS API reads only publication metadata for one configured dashboard ID and
tenant-specific title using a server-held token, fixed URL and bounded response.
It excludes provider configuration, CSS, SQL, owner records and secrets. Owner,
development, feature and tenant checks apply before any provider request. Logs
and counters use fixed labels. Published metadata does not certify dataset currency;
the dataset includes its own digest and refresh timestamp for explicit inspection.

Official upstream 6.1.0 release/image and Apache-2.0/subcomponent licensing were
reviewed on 2026-10-04. The dependency stays isolated from the API and Spark graph.
See `docs/runbooks/usage-bi.md` for reproducible setup and remaining acceptance.
