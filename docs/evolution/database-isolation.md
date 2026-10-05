# Database isolation and lock evolution

## Product evidence

ATLAS exposes read-only concurrency metadata through one normalized API and the
Data Estate visualizer. PostgreSQL reports its current and default transaction
settings; SQLite reports its fixed `read_uncommitted` PRAGMA. The API accepts no
setting name or isolation level, so introspection cannot mutate connection state.

The matrix preserves important provider differences. PostgreSQL maps Read
Uncommitted to Read Committed, while SQLite offers serializable behavior by default
and makes dirty reads conditional on shared cache. Unsupported levels remain
explicit rather than being presented as equivalent guarantees.

## Executable lab evidence

The isolation lab uses a file-backed WAL database and independent connections to
show a reader retaining its original snapshot across a writer commit. A second
scenario holds `BEGIN IMMEDIATE`, records the contender's machine-readable
`SQLITE_BUSY`, proves the uncommitted value is invisible, rolls back, and retries.

Correctness gates use values, transaction boundaries, PRAGMA configuration, and
SQLite's error code. They deliberately avoid elapsed-time and message-text checks,
which vary by operating system.

## PostgreSQL lock and recovery progression

The next Phase 4 increment adds an authenticated, read-only snapshot over
`pg_catalog.pg_locks`. PostgreSQL aggregates by lock mode and granted state before
data leaves the server. The public contract omits relation names, process IDs,
transaction IDs, query text, and tenant rows. SQLite reports an explicit unavailable
state because it has no equivalent portable catalog; an empty response is never used
to imply that SQLite has no locks.

The disposable PostgreSQL lab owns only `atlas_concurrency_lab` and uses separate
connections to prove three machine-readable recovery boundaries: row contention
returns `55P03` before a successful retry, an actual wait cycle produces one `40P01`
victim and one commit, and Serializable write skew rejects one transaction with
`40001`. The rejected transaction retries from fresh reads and preserves the rule
that at least one doctor remains on call. Reset drops only the fixed schema and
allowlisted evidence files.

These are correctness exercises, not latency benchmarks. Tests gate on SQLSTATE,
commit/rollback outcomes, final values, and the application invariant; worker and
service timeouts only prevent a broken lab from hanging indefinitely.
