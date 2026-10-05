# MongoDB document projection evolution

## Product integration

The fifth Phase 4 database slice adds an optional MongoDB project read model while
PostgreSQL stays authoritative. An authenticated owner explicitly publishes only
their tenant's projects. The publisher writes a complete generation, atomically
replaces a single tenant state document that points readers at that generation,
and retains immutable generations for concurrent readers (ADR 0005). This avoids cross-database two-phase commit and
prevents readers from selecting a partially written refresh; it is intentionally
eventually consistent until the next explicit publication.

The read contract is bounded to 25 documents and returns only project slug, status,
note count, and creation time. Tenant identifiers, project names/descriptions, note
bodies, actors, credentials, hosts, raw BSON, query documents, and driver errors do
not cross the API or server-side web proxy. Both fixed collections use JSON Schema
validation and compound tenant/generation indexes. The product account is restricted
to `atlas_document`; the separate lab account is restricted to `atlas_document_lab`.

## Executable evidence

The resettable lab embeds line items in order documents, compares sanitized plan
stages before and after a compound index, proves validator rejection code `121`,
and uses a version in an atomic update filter to detect a stale inventory write and
retry from fresh state. Reset refuses unexpected users/databases and removes only
two fixed collections and allowlisted evidence files.

The implementation, API and component contracts, static Compose configuration, and
isolated tests are complete. Live container verification passed on 2026-09-14, including validation, indexes,
atomic retries, and exact reset. MongoDB's SSPL license is recorded as an
explicit adoption consideration. The Redis slice is also complete.
