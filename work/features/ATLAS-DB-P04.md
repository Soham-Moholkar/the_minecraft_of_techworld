# ATLAS-DB-P04 — Safe cross-dialect query-plan inspection

Status: completed 2026-08-28

Context: PostgreSQL is authoritative and SQLite is the zero-service adapter, but
their planner evidence was not visible in the product or reproducible as a lab.

Acceptance criteria:

- [x] authenticated callers can request only an allowlisted, tenant-scoped query,
- [x] PostgreSQL and SQLite plans normalize into one typed response,
- [x] Data Estate renders loading, error, empty, and successful plan states,
- [x] a resettable lab proves equal results before/after a composite index,
- [x] API, frontend, lab, live PostgreSQL, and browser checks pass.

Evidence: `apps/api-python/src/atlas_api`, `apps/web/src/app/data`,
`labs/databases/query-plans`, and `output/playwright`.
