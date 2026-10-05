# PostgreSQL locks, deadlocks, and Serializable retry lab

This disposable lab uses the repository's PostgreSQL service and separate real
connections to demonstrate three production behaviors:

1. One transaction holds a row lock. A contender receives PostgreSQL SQLSTATE
   `55P03` (`lock_not_available`), then succeeds after the holder rolls back.
2. Two transactions lock rows in opposite order. PostgreSQL detects the cycle,
   aborts exactly one transaction with `40P01` (`deadlock_detected`), and lets
   the other commit.
3. Two on-call doctors make a write-skew decision under `SERIALIZABLE`.
   PostgreSQL rejects one transaction with `40001` (`serialization_failure`).
   A fresh retry re-reads state and preserves at least one on-call doctor.

The lab never touches product tables. It owns the fixed
`atlas_concurrency_lab` schema, uses four synthetic rows, and drops only that
schema during reset. Tests assert SQLSTATEs, transaction outcomes, and final
data invariants—not elapsed time or error-message text.

## Run it

From the repository root with the project virtual environment active:

```powershell
python labs/databases/postgresql-concurrency/run.py start
python labs/databases/postgresql-concurrency/run.py test
python labs/databases/postgresql-concurrency/run.py reset
```

Or run the complete lifecycle with guaranteed cleanup:

```powershell
python labs/databases/postgresql-concurrency/run.py verify
```

`start` reuses the local PostgreSQL service or starts the repository's Compose
service. It writes sanitized JSON evidence under `.lab-state/`; no connection
URL, credentials, SQL text, process identifier, or product row is recorded.
ATLAS maps PostgreSQL to host port `55432` by default so it can coexist with a
native PostgreSQL installation; containers still use `postgres:5432`.

To use another disposable PostgreSQL instance, set `ATLAS_POSTGRES_LAB_URL` to
its standard psycopg URL. The target user must be allowed to create and drop the
fixed lab schema. Do not point the exercise at a database where that schema is
owned by someone else.

## What to inspect

- Compare the row-lock holder's rollback with a commit and observe how the final
  balance changes after retry.
- Reverse both deadlock workers to a consistent lock order and observe that the
  `40P01` victim disappears.
- Change the Serializable transactions to `READ COMMITTED` and observe why the
  application-level on-call invariant can be violated by write skew.
- Open `postgresql-concurrency-evidence.json` to compare a retryable lock wait,
  deadlock victim selection, and optimistic Serializable recovery.

In application code, retry the **entire** transaction for `40001` and usually
`40P01`, with a bounded retry policy and fresh reads. Never replay only the last
statement: its earlier decision may no longer be valid.
