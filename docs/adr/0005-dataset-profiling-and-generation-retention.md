# ADR 0005: Bounded dataset profiling and safe projection retention

Date: 2026-09-15. Status: accepted.

## Operational datasets

ATLAS accepts the owned `date,service,cost,requests` CSV schema, at most 256 KiB,
5,000 records, and 100 services per import. Invalid measurements are excluded and
counted; normalized exact duplicates are retained once. No arbitrary SQL, external
files, URLs, extensions, formula evaluation, or uploaded executable code is accepted.

PostgreSQL (SQLite for development) stores cleaned rows, source checksum, and an
immutable typed profile under an organization foreign key. Import and its audit
event commit together. Every read filters by the authenticated tenant; only an
owner can import. A catalog has at most 100 datasets. Raw CSV is not stored or logged.
The existing local development authentication boundary remains; public deployment
still depends on ATLAS-SEC-001's signed sessions and identity work.

NumPy computes descriptive statistics/histograms, pandas produces the frame,
SciPy computes a Student-t mean interval, and pandas/Polars/DuckDB independently
aggregate service costs and request counts. Engine results must agree on every
repetition. Dependencies live in the API `data` extra and load only for profiling.
DuckDB uses a private in-memory database with external access disabled.

This synchronous interactive workload is deliberately small. The 100/1,000/5,000
row lab documents scaling without claiming a production winner. Async ingestion,
arbitrary schemas, columnar object storage and larger workloads remain later work.

## MongoDB generation retention

Publication previously removed every generation except its own after switching
the tenant pointer. Concurrent publishers could delete each other's data; readers
holding the previous pointer could see an empty result. Publication now retains
immutable generations. The active pointer always selects a complete generation.
`removed_count` is zero; no immediate cleanup is claimed. A coordinated retention
job is deferred until it can account for active readers and publishers. Operators
must monitor storage growth and avoid repeated unattended publication meanwhile.

## Redis safety

ACL tests use `ACL DRYRUN`, never a real `FLUSHALL` or out-of-prefix mutation.
Optimistic retries have a three-attempt budget. Partial experiment failure still
cleans only fixed lab keys. Invalid, inconsistent or non-expiring portfolio cache
payloads refresh from authoritative SQL. Cache setup/read/write failures bypass it.

Reference: https://redis.io/docs/latest/commands/acl-dryrun/
