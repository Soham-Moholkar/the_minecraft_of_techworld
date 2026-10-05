# Database query-plan evolution

## Why this increment exists

ATLAS already used PostgreSQL as its authoritative store and SQLite as its
zero-service test adapter. Phase 4 makes database behavior inspectable without
adding an unsafe query console: one named tenant-scoped product query can be planned,
normalized, rendered, and reproduced in an isolated lab.

## Progression

- **L0 foundation:** migrations, constraints, seed data, and ordinary ORM access.
- **L1 product integration:** tenant-scoped project reads and transactional writes.
- **L2 realistic engineering:** indexes, audit atomicity, PostgreSQL health, and a
  SQLite compatibility adapter.
- **L3 advanced:** dialect-aware plan inspection, a shared normalized contract, a
  Data Estate explain viewer, and resettable composite-index evidence.

The next database increments should add explicit transaction/isolation and lock
evidence, followed by MVCC visibility, workload comparison, and recovery exercises.

## Security and interpretation

The API accepts an allowlisted query name and validated parameters, never SQL text.
The fixed statement includes the authenticated organization slug, preserving the
same non-disclosing tenant boundary as the ordinary project repository. Estimated
rows and costs are planner-specific signals rather than promises of runtime. The lab
therefore asserts result equality and index selection while recording timings only
as local comparative evidence.
