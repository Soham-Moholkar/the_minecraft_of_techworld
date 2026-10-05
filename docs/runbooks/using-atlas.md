# Using ATLAS

## Fastest start

From the repository root:

```powershell
Copy-Item .env.example .env
docker compose up -d --build
docker compose ps
```

Open `http://localhost:3000`. API documentation is at `http://localhost:8000/docs`;
health is at `/health`, metrics at `/metrics`, and the authenticated stream is
proxied to the browser through `/api/events`. The Node protocol facade exposes HTTP
and GraphQL on port `8100` and gRPC on port `8101`.

For source-level hot reload instead of containers, follow the root `README.md` and
run the API and web development commands in separate terminals.

## Product workflows

1. **Navigate:** use the sidebar, the mobile menu, or press `Ctrl+K`/`Cmd+K` to
   open the keyboard command palette.
2. **Search:** open Global search and enter at least two characters. Results come
   from tenant-scoped persisted project metadata.
3. **Projects:** open Projects, choose **New project**, supply a lowercase dashed
   slug, and submit. Select a project to add engineering notes. Optimistic UI state
   is removed automatically if the server rejects either mutation.
4. **Security:** open Security to inspect the immutable `project.created` and
   `project.note_added` evidence committed with those mutations.
5. **Observability:** open Observability to watch the authenticated SSE audit feed.
   EventSource reconnects automatically if the API restarts. Its last received event
   ID travels through the BFF, so already-rendered events are not replayed. Use
   **Measure round trip** to exercise the ticket-authenticated WebSocket path.
6. **Catalog:** open Domain catalog, then a domain, to see the owner, posture, and
   concrete source/evidence path for each registered capability.
7. **Topics:** open a topic, mark sections complete, bookmark it, and save a private
   note. This state currently stays in local browser storage.
8. **Labs:** the lab workspace displays the exact start/test/reset commands and
   records your lifecycle progress. Run commands explicitly in the IDE terminal;
   the browser does not execute local processes.
9. **Theme:** use **Toggle color mode** at the bottom of the sidebar. The choice
   persists in the current browser.
10. **Data:** open Data estate to compare PostgreSQL/SQLite with optional MariaDB,
    publish the tenant's optional MongoDB project read model, inspect the authenticated
    query plan and isolation matrix, and view privacy-bounded lock counts. Reload a
    panel for fresh evidence.
11. **Tests:** open Test center to inspect the latest checked-in quality run.

## Run the Python mastery lab

```powershell
.\.venv\Scripts\python labs\python\python-mastery\run.py start
.\.venv\Scripts\python labs\python\python-mastery\run.py test
.\.venv\Scripts\python labs\python\python-mastery\dist\atlas-python-mastery.pyz
.\.venv\Scripts\python labs\python\python-mastery\benchmark.py
.\.venv\Scripts\python labs\python\python-mastery\run.py reset
```

Use `run.py verify` to execute start, tests, benchmark, and guaranteed cleanup as
one quality operation. `start` also records generator peak memory, demonstrates that
one failed process item does not discard successful work, writes a CPU profile, and
builds the executable `.pyz`. Benchmark timings compare mechanisms on your current
machine; use them as local evidence, not universal performance guarantees.

## Inspect and benchmark database query plans

Open `http://localhost:3000/data` while the stack is running. The viewer calls the
same-origin BFF, which keeps the service credential on the server and requests only
the fixed `tenant_projects_by_status` query. The selected status is a bound parameter;
the UI cannot send arbitrary SQL. PostgreSQL plans come from the live core database,
while API integration tests exercise the equivalent SQLite adapter.

Run the resettable SQLite index lab without starting the product stack:

```powershell
.\.venv\Scripts\python labs\databases\query-plans\run.py start
.\.venv\Scripts\python labs\databases\query-plans\run.py test
.\.venv\Scripts\python labs\databases\query-plans\run.py benchmark
.\.venv\Scripts\python labs\databases\query-plans\run.py reset
```

`run.py verify` performs the full lifecycle and verifies cleanup. The before/after
timings are machine-local evidence; correctness and actual plan/index selection are
the stable assertions.

## Explore transaction isolation and locks

The lower panel at `http://localhost:3000/data` reports the live engine's current
and default isolation levels plus native, mapped, conditional, and unsupported
semantics. Use its lab link or run the two-connection SQLite experiment directly:

```powershell
.\.venv\Scripts\python labs\databases\isolation-locks\run.py start
.\.venv\Scripts\python labs\databases\isolation-locks\run.py test
.\.venv\Scripts\python labs\databases\isolation-locks\run.py reset
```

`run.py verify` guarantees reset even if a check fails. Inspect
`labs/databases/isolation-locks/.lab-state/isolation-evidence.json` after `start`
to trace the original reader snapshot, the committed writer value, `SQLITE_BUSY`,
rollback, and retry. The evidence directory is intentionally removed by `reset`.

For PostgreSQL row locks, deadlocks, and Serializable recovery, use the lab link in
the lock-activity panel or run:

```powershell
.\.venv\Scripts\python labs\databases\postgresql-concurrency\run.py start
.\.venv\Scripts\python labs\databases\postgresql-concurrency\run.py test
.\.venv\Scripts\python labs\databases\postgresql-concurrency\run.py reset
```

`run.py verify` performs the full lifecycle with guaranteed cleanup. After `start`,
inspect `.lab-state/postgresql-concurrency-evidence.json` for SQLSTATE `55P03`,
`40P01`, and `40001`, the successful row-lock retry, and the final on-call invariant.
The lab starts the repository PostgreSQL service when necessary, owns only the fixed
`atlas_concurrency_lab` schema, and never records a URL, credential, SQL statement,
process identifier, or product row. ATLAS uses host port `55432` by default to avoid
collisions with native PostgreSQL installations.

## Compare and exercise MariaDB

Start the optional provider, API, and web surface:

```powershell
docker compose --profile database up -d --build mariadb api web
```

Open `http://localhost:3000/data`. The provider panel reports MariaDB's live version,
current/default isolation, JSON plan support, and InnoDB transaction model. The API
uses a `USAGE`-only observer and never exposes its connection details. Run the
isolated index/transaction exercise with:

```powershell
.\.venv\Scripts\python labs\databases\mariadb-provider\run.py start
.\.venv\Scripts\python labs\databases\mariadb-provider\run.py test
.\.venv\Scripts\python labs\databases\mariadb-provider\run.py reset
```

`run.py verify` guarantees reset. It checks composite-index selection without
changing results, a stable Repeatable Read snapshot, numeric lock-wait code `1205`,
and a successful whole-transaction retry. Reset refuses root and drops only the two
fixed lab tables.

## Publish and exercise the MongoDB document model

Start the optional document provider, API, and web surface:

```powershell
docker compose --profile database up -d --build mongodb api web
```

Open `http://localhost:3000/data`. In **MongoDB project projection**, choose
**Publish projection**. The server derives the tenant from the authenticated
principal and requires the owner role; the browser cannot provide a tenant, filter,
query, or MongoDB credential. The panel returns at most 25 allowlisted documents.
PostgreSQL remains authoritative, so publish again after relational project changes.

Run the isolated document/index/atomicity exercise with:

```powershell
.\.venv\Scripts\python labs\databases\mongodb-document-model\run.py start
.\.venv\Scripts\python labs\databases\mongodb-document-model\run.py test
.\.venv\Scripts\python labs\databases\mongodb-document-model\run.py reset
```

`run.py verify` guarantees reset. It checks compound-index plan selection without
changing results, JSON Schema rejection code `121`, stale version detection, and a
successful fresh-read retry. Reset refuses the root/product users and removes only
the two fixed lab collections. MongoDB is an optional SSPL-licensed provider; review
that license before production adoption.

## Run quality gates

```powershell
pnpm quality:snapshot
```

This refreshes the JSON consumed by Test center. Individual development commands
are `pnpm lint`, `pnpm typecheck`, `pnpm test`, and `pnpm build`. API quality uses:

```powershell
.\.venv\Scripts\python -m ruff check apps\api-python
.\.venv\Scripts\python -m mypy apps\api-python\src
.\.venv\Scripts\python -m pytest apps\api-python --cov=atlas_api
```

## Compare REST, GraphQL, and gRPC

The three transports use the same Node `ProjectProvider`, which delegates to the
authoritative Python API. After `docker compose up -d --build`, run:

```powershell
$headers = @{ Authorization = "Bearer atlas-local-development-token" }
Invoke-RestMethod "http://localhost:8100/v1/projects?limit=10" -Headers $headers

$body = @{ query = "query { projects(limit: 10) { slug name status } }" } | ConvertTo-Json
Invoke-RestMethod -Method Post "http://localhost:8100/graphql" `
  -Headers $headers -ContentType "application/json" -Body $body

$env:ATLAS_NODE_GRPC_ADDRESS = "localhost:8101"
pnpm --filter @atlas/api-node smoke:grpc
```

Use REST for familiar HTTP semantics and broad tooling, GraphQL for client-selected
response shapes, and gRPC for protobuf-defined service contracts. These smoke results
prove equivalent data flow; they are not performance rankings.

## Local operator memory

Apply the migration chain with
`python -m alembic -c apps/api-python/alembic.ini upgrade head`, then open
`/ai/repository` while the API runs in development mode with a trusted owner principal.
The memory panel needs no patch/test flag and does not enable either capability.

Enter a short note and operator-supplied provenance, choose 1, 7 or 30 days (default 7),
review it for sensitive/approval material, check the attestation and save. The store is
bounded to 50 notes per tenant; recognized credentials and approval digests/phrases are
rejected, but detection is not comprehensive. Do not enter personal/confidential data.
Notes are plain untrusted text, not model context or commands. Drafts are not saved to
browser storage. To delete a note, choose its delete action and confirm permanent deletion.

Expiry hides a note immediately, including on an open page. Physical cleanup runs on
the next successful save or the explicit **Remove expired memory** action. There is no
background sweeper: idle tenants' expired rows remain in storage until cleanup. GET is
read-only and only reports the count of expired rows, not their contents. Cleanup is
tenant-scoped and does not remove active notes. Database deletion removes the row, but
does not erase backup copies, SQLite pages or transaction logs. Audit events keep only
lifecycle metadata, not note text/title/provenance. See ADR 0011 for future retention work.

## Code comments and extension points

Comments and docstrings are concentrated at boundaries where intent is not obvious:
tenant authorization, atomic audit commits, optimistic rollback, browser persistence,
lab execution safety, safe generated-artifact cleanup, SSE session lifetime, cursor
ordering, one-use socket tickets, origin/capacity/rate controls, and non-disclosing
tenant boundaries. When extending ATLAS, preserve these invariants and update the
registry, evolution note, tests, work item, and checkpoint with the same change.

The next major security upgrade is OIDC/signed sessions with fine-grained RBAC. The
next full-stack upgrades are trace propagation, protocol load/failure evidence,
GraphQL subscriptions, and shared-store WebSocket tickets for horizontal scaling;
do not expose the current local bearer provider to an internet-facing environment.
# Phase 5 dataset catalog

Open `/datasets`, choose **Load sample CSV**, then **Import dataset**. The sample
is deterministic synthetic operational data, not a live business feed. The API
persists cleaned rows, a SHA-256 source checksum, quality counts, NumPy statistics,
SciPy uncertainty, and verified pandas/Polars/DuckDB aggregates. Reload the page and
select the saved dataset to inspect durable evidence.

For native development install `python -m pip install -e "apps/api-python[data,dev]"`
and apply migration `20260914_0003` with
`python -m alembic -c apps/api-python/alembic.ini upgrade head`.
The API Docker image includes the data extra. Rebuild with
`docker compose --profile database up -d --build`.

The import accepts `date,service,cost,requests`, at most 256 KiB, 5,000 rows,
and 100 service groups. The catalog holds at most 100 datasets per organization.
Invalid rows are counted/excluded; exact normalized duplicates are kept once.
Uploads are not executed, and raw CSV is not stored or logged. Use
`python labs/data/science-quality/run.py verify` for the three-scale local exercise.

MongoDB publication retains immutable generations after switching the pointer;
it does not delete prior generations while concurrent readers/publishers may
still need them. See ADR 0005 for the deferred coordinated retention policy.
