# ATLAS-DB-P04-ISOLATION — Live isolation profile and locking lab

Status: completed 2026-08-28

Context: query plans are visible, but provider isolation mappings and actual
two-connection lock behavior were not yet inspectable.

Acceptance criteria:

- [x] authenticated read-only introspection reports PostgreSQL and SQLite semantics,
- [x] the Data Estate renders current/default levels and the capability matrix,
- [x] a resettable lab proves reader snapshots, writer contention, rollback, and retry,
- [x] API, frontend, lab, live PostgreSQL, and browser checks pass.

Evidence: `apps/api-python/src/atlas_api/concurrency_profiles.py`,
`apps/web/src/components/isolation-visualizer.tsx`,
`labs/databases/isolation-locks`, and `output/playwright`.
