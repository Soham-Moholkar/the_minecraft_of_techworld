# Redis cache-aside, streams, transactions, and ACL lab

This optional Redis 8 lab proves four production-facing behaviors against real
connections: bounded cache TTL/expiry, consumer-group recovery of an unacknowledged
stream event, `WATCH` conflict detection with a fresh retry, and least-privileged
ACL denial of `FLUSHALL` and foreign key prefixes.

```powershell
.\.venv\Scripts\python labs\databases\redis-cache-streams\run.py start
.\.venv\Scripts\python labs\databases\redis-cache-streams\run.py test
.\.venv\Scripts\python labs\databases\redis-cache-streams\run.py reset
```

Use `run.py verify` for start, tests, and guaranteed cleanup. Reset authenticates as
`atlas_lab` and deletes only three constant `atlas:lab:*` keys; it never enumerates,
flushes, or selects caller-provided keys. Evidence records only booleans, counts, and
delivery semantics—never a URL, password, endpoint, event payload, or raw error.

The product uses a separate `atlas_cache` identity limited to `PING`, `GET`, `SET`,
and `TTL` on `atlas:cache:*`. PostgreSQL/SQLite remains authoritative, and a Redis
failure automatically becomes an uncached relational read.
