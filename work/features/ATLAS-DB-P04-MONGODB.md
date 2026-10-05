# ATLAS-DB-P04-MONGODB — MongoDB projection and document evidence

Status: complete; live lifecycle verified 2026-09-14

## Outcome

- Optional pinned MongoDB service with separate database-scoped product and lab users.
- Authenticated tenant-scoped project projection with an owner-only explicit publish.
- Generation-switched consistency model with fixed collections and bounded responses.
- Data Estate loading, ready, empty, unavailable, publish, refresh, and error states.
- Resettable compound-index, JSON Schema validation, and atomic version-update lab.
- API, web, telemetry, tests, registry, documentation, and lifecycle integration.
- Live lifecycle passed all five document, validation, index, retry, and reset checks.

## Security and license boundary

The API accepts no caller query/filter or tenant identifier. Tenant scope comes from
the authenticated principal, publication requires the owner role, and the browser
contract excludes sensitive fields and raw errors. Lab reset is restricted to one
non-root user, one fixed database, and two fixed collections. MongoDB uses the SSPL;
production adoption requires an explicit organizational license review.
