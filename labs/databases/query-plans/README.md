# Tenant query-plan and composite-index lab

This resettable, standard-library SQLite lab reproduces the ATLAS project-list
access pattern: find one tenant, filter its projects by status, order newest
first, and return a bounded page. It compares the query before and after this
index:

```sql
CREATE INDEX idx_projects_tenant_status_created_at
ON projects (organization_id, status, created_at DESC);
```

The index places equality predicates first and the sort column last. After the
index is added, SQLite can seek directly to the tenant/status slice and return
rows in the requested order instead of scanning projects and building a
temporary sorting B-tree.

## Run the lab

From the repository root, use the same Python 3.12 interpreter as ATLAS:

```powershell
python labs/databases/query-plans/run.py start
python labs/databases/query-plans/run.py test
python labs/databases/query-plans/run.py benchmark
python labs/databases/query-plans/run.py reset
```

`start` generates 20,000 deterministic, non-sensitive projects and leaves an
indexed SQLite database plus `plan-evidence.json` under `.lab-state/`. Open the
JSON file in the IDE and compare `before.plan` with `after.plan`.

`test` asserts the important invariants: both schemas return identical rows,
the baseline does not use the named composite index, the indexed plan does, and
reset removes only known generated artifacts.

`benchmark` creates `benchmark.json` with warmup count, repetitions, median,
p95, environment details, configuration, and caveats. Timing is intentionally
not a test assertion: synthetic data, cache warmth, CPU frequency, filesystem,
and OS scheduling make small local timings variable. The normalized
`EXPLAIN QUERY PLAN` output and identical results are the stable evidence.

Run the complete lifecycle, including guaranteed cleanup, with:

```powershell
python labs/databases/query-plans/run.py verify
```

## Experiment safely

Useful IDE exercises are to change the query or index order, run `verify`, and
inspect how the plan changes. For example, move `created_at` ahead of `status`
in the index and observe whether both equality filtering and ordering remain
fully covered. The lab never connects to the ATLAS development database, makes
no network requests, and uses no credentials.

