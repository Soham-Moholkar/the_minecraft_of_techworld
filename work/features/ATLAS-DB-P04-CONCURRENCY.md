# ATLAS-DB-P04-CONCURRENCY — PostgreSQL lock activity and recovery lab

Status: completed 2026-08-28

Context: ATLAS exposed provider isolation semantics, but operators could not see a
privacy-bounded live lock signal and learners could not exercise PostgreSQL's row
locks, deadlock detector, or Serializable retry contract.

Acceptance criteria:

- [x] authenticated read-only lock activity exposes aggregate modes and counts only,
- [x] the Data Estate renders granted/waiting state and honest provider limitations,
- [x] a disposable lab proves `55P03`, `40P01`, `40001`, and fresh-decision retry,
- [x] reset drops only the fixed lab schema and preserves unrelated learner notes,
- [x] API, frontend, lab, live PostgreSQL, and browser checks pass.

Evidence: `apps/api-python/src/atlas_api/lock_activity.py`,
`apps/web/src/components/lock-activity-viewer.tsx`,
`labs/databases/postgresql-concurrency`, and `output/playwright`.
