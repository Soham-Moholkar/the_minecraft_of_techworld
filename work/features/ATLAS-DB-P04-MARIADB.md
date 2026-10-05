# ATLAS-DB-P04-MARIADB — MariaDB provider and transaction evidence

Status: complete; live lifecycle verified 2026-09-14

## Outcome

- Optional pinned MariaDB Compose service with separate least-privileged observer
  and database-scoped lab accounts.
- MariaDB query-plan, isolation, and explicit lock-catalog capability adapters.
- Authenticated normalized provider comparison with bounded metrics and logs.
- Data Estate comparison UI with loading, ready, unavailable, refresh, and error states.
- Resettable InnoDB composite-index, Repeatable Read, and lock-wait/retry lab.
- API, web, lab, registry, runbook, and lifecycle implementation. The live
  MariaDB lifecycle passed all four index, isolation, retry, and reset checks.

## Security boundary

No caller SQL or setting names are accepted. The observer has no table grants;
the public response excludes connection/error details. Lab reset is restricted to
the non-root `atlas_lab` account and two fixed table names.
