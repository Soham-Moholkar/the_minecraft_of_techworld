# MariaDB provider, index, and transaction lab

This disposable lab starts ATLAS's optional MariaDB 12.3 service and proves
three behaviors against real InnoDB connections:

1. A tenant/status query returns identical rows before and after a composite
   index, while JSON EXPLAIN selects `ix_atlas_provider_lookup` afterward.
2. A `REPEATABLE READ` transaction retains its original snapshot after another
   connection commits, then sees the change from a fresh transaction.
3. A held row lock makes a contender return numeric error code `1205`; after the
   holder rolls back, the whole contender transaction retries and commits.

Correctness uses results, plan structure, transaction values, and the numeric
driver code—never elapsed time or localized error text. Evidence contains no SQL,
credentials, connection URL, host, user, or resolved predicate.

## Run it

From the repository root with `.venv` active:

```powershell
python labs/databases/mariadb-provider/run.py start
python labs/databases/mariadb-provider/run.py test
python labs/databases/mariadb-provider/run.py reset
```

Or run the complete lifecycle with guaranteed cleanup:

```powershell
python labs/databases/mariadb-provider/run.py verify
```

`start` reuses MariaDB on host port `53307` or starts only the optional
`database` Compose profile. The `atlas_lab` account can modify only the
`atlas_lab` database. Reset refuses a root connection and drops only
`atlas_provider_projects`, `atlas_provider_accounts`, and generated evidence.

To use a different disposable server, set the `ATLAS_MARIADB_LAB_HOST`,
`ATLAS_MARIADB_LAB_PORT`, `ATLAS_MARIADB_LAB_USER`,
`ATLAS_MARIADB_LAB_PASSWORD`, and `ATLAS_MARIADB_LAB_DATABASE` variables. The
database name must remain exactly `atlas_lab`; never point this lifecycle at a
shared or production database.

## Use it in ATLAS

Start the optional service and rebuild the API so its pinned PyMySQL driver and
observer URL are active:

```powershell
docker compose --profile database up -d --build mariadb api web
```

Open `http://localhost:3000/data`. The Relational provider comparison shows
MariaDB as `available`, its live server version, current/default isolation, JSON
plan format, and transaction model. The observer account has `USAGE` only and
cannot read lab or product tables. Stopping MariaDB changes the panel to an
honest `unavailable` state without breaking the primary ATLAS database.
