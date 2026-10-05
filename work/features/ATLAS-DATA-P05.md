# ATLAS-DATA-P05 — Operational dataset catalog and profiling

Status: complete; packaged browser, migrations and 19/19 quality gates verified 2026-09-15

Outcome: authenticated CSV import, tenant catalog, persistent cleaned rows and
profiles, quality accounting, NumPy distributions, SciPy confidence intervals,
and matching pandas/Polars/DuckDB aggregations. The UI exposes imports, saved
datasets, histogram/table summaries, measured engine evidence and limitations.

Acceptance: real engine correctness, tenant isolation, owner permission, bounded
inputs, finite measurements, duplicate handling, atomic audit persistence, loading/
error/empty states, responsive browser import and reload, clean-reset scaling lab,
strict typing/lint, production build, and updated registry/progression.

Tests: `apps/api-python/tests/test_datasets.py`,
`apps/web/src/components/dataset-workspace.test.tsx`, and
`labs/data/science-quality/run.py verify`.

Scope: one real operational schema and interactive laptop-sized workloads.
Architecture: ADR 0005. Next roadmap phase: Phase 6, ML experiments and evaluation.

Final evidence: 65 API tests (87.84% coverage), 28 web tests, strict lint/types,
production API/web images, SQLite round-trip and PostgreSQL schema checks, and
100/1000/5000-row lab. Browser imported 62 rows, excluded one invalid and one
duplicate, reloaded 60 saved rows after an API restart, recovered from invalid
input, and displayed three matching engine results at desktop and 390px mobile.
