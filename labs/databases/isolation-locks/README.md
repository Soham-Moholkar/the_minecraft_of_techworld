# SQLite reader-snapshot and writer-lock lab

This resettable, standard-library lab uses a real file-backed SQLite database
and two independent connections to expose two transaction behaviors:

1. A reader begins a transaction and reads `feature-mode=disabled`. In WAL
   mode, a second connection changes the value to `enabled` and commits. The
   original reader still sees `disabled` until it commits, then sees `enabled`.
2. One writer uses `BEGIN IMMEDIATE` and changes `deployment-slot` without
   committing. A second writer has a 75 ms busy timeout, sees only the committed
   value, and receives the machine-readable `SQLITE_BUSY` result. After the
   first writer rolls back, the contender retries and commits successfully.

The tests intentionally do **not** assert elapsed time or error-message wording.
Both vary across operating systems and SQLite builds. Stable gates are the
configured `PRAGMA busy_timeout`, the `SQLITE_BUSY` code, observed values, and
explicit transaction boundaries.

## Run it

From the repository root:

```powershell
python labs/databases/isolation-locks/run.py start
python labs/databases/isolation-locks/run.py test
python labs/databases/isolation-locks/run.py reset
```

`start` writes a disposable database, `state.json`, and
`isolation-evidence.json` under `.lab-state/`. Open the JSON in the IDE to trace
the exact observations. The database contains two deterministic synthetic rows,
no PII, no credentials, and makes no network requests.

To execute the full lifecycle with guaranteed cleanup:

```powershell
python labs/databases/isolation-locks/run.py verify
```

## What to change and observe

- Replace the reader's `BEGIN` with separate autocommit reads and observe that
  each statement sees the newest committed version instead of one snapshot.
- Change `BUSY_TIMEOUT_MS`; the result remains `SQLITE_BUSY` while the first
  writer deliberately retains its lock. Do not turn wall-clock duration into a
  regression assertion.
- Change the holder's rollback to a commit and observe which value the contender
  can read before its successful retry.

SQLite WAL is a compact way to inspect these boundaries, but it is not a full
model of PostgreSQL MVCC or row-level locking. The follow-on progression should
compare PostgreSQL isolation levels, row locks, deadlock detection, and lock
observability against the live ATLAS database.

All connections are explicitly closed before cleanup. This matters on Windows,
where an open SQLite handle prevents deterministic removal of the database and
its `-wal`/`-shm` sidecars.
