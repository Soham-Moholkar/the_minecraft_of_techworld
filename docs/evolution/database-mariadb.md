# MariaDB provider evolution

## Product integration

The fourth Phase 4 slice adds MariaDB as a reviewed SQLAlchemy dialect without
changing PostgreSQL's authoritative-store role. Query plans normalize MariaDB
JSON EXPLAIN into the same structural contract used by PostgreSQL and SQLite;
resolved predicates are discarded. Isolation introspection maps MariaDB's four
levels into ATLAS vocabulary and records its Repeatable Read default.

The Data Estate compares its primary provider with an optional MariaDB service.
The observer connection runs one fixed metadata statement and holds only `USAGE`.
Connection strings, host/user/database names, SQL, and raw driver errors never
cross the API or BFF. If the service is absent, the comparison reports
`unavailable` while primary product functions remain healthy.

## Executable evidence

The isolated lab owns two fixed tables inside the `atlas_lab` database. It proves
result-preserving composite-index selection, InnoDB Repeatable Read snapshot
stability, and error-code-based lock-wait recovery across separate connections.
Reset refuses root and any database other than `atlas_lab`, then removes only
the fixed tables and allowlisted evidence files.

This completes the first MySQL/MariaDB vertical slice. MongoDB is the next Phase
4 provider slice; Redis and cross-provider benchmark/security exercises follow.
