"""Deterministic MariaDB index, snapshot, and lock-recovery experiments."""

from __future__ import annotations

import json
import os
import pathlib
from datetime import UTC, datetime
from typing import Any

import pymysql  # type: ignore[import-untyped]

PROJECTS_TABLE = "atlas_provider_projects"
ACCOUNTS_TABLE = "atlas_provider_accounts"
EVIDENCE_NAME = "mariadb-provider-evidence.json"


def connect(*, autocommit: bool = False) -> pymysql.connections.Connection:
    """Open the narrowly scoped lab database configured through explicit fields."""

    return pymysql.connect(
        host=os.getenv("ATLAS_MARIADB_LAB_HOST", "127.0.0.1"),
        port=int(os.getenv("ATLAS_MARIADB_LAB_PORT", "53307")),
        user=os.getenv("ATLAS_MARIADB_LAB_USER", "atlas_lab"),
        password=os.getenv("ATLAS_MARIADB_LAB_PASSWORD", "atlas_lab_dev_only"),
        database=os.getenv("ATLAS_MARIADB_LAB_DATABASE", "atlas_lab"),
        autocommit=autocommit,
        connect_timeout=2,
        read_timeout=5,
        write_timeout=5,
        charset="utf8mb4",
    )


def _assert_safe_target(connection: pymysql.connections.Connection) -> None:
    """Refuse destructive setup/reset unless the fixed disposable database is active."""

    with connection.cursor() as cursor:
        cursor.execute("SELECT DATABASE(), CURRENT_USER()")
        database, current_user = cursor.fetchone()
    if database != "atlas_lab" or str(current_user).lower().startswith("root@"):
        raise RuntimeError("MariaDB lab requires the non-root atlas_lab database account")


def reset_tables() -> None:
    """Drop only the two fixed tables owned by this exercise."""

    with connect() as connection:
        _assert_safe_target(connection)
        with connection.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {PROJECTS_TABLE}")
            cursor.execute(f"DROP TABLE IF EXISTS {ACCOUNTS_TABLE}")
        connection.commit()


def reset_generated_state(state_dir: pathlib.Path) -> None:
    """Remove allowlisted evidence while preserving learner-authored notes."""

    evidence = state_dir / EVIDENCE_NAME
    if evidence.exists():
        evidence.unlink()
    marker = state_dir / "state.json"
    if marker.exists():
        marker.unlink()
    if state_dir.exists() and not any(state_dir.iterdir()):
        state_dir.rmdir()


def _prepare_schema() -> None:
    with connect() as connection:
        _assert_safe_target(connection)
        with connection.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {PROJECTS_TABLE}")
            cursor.execute(f"DROP TABLE IF EXISTS {ACCOUNTS_TABLE}")
            cursor.execute(
                f"CREATE TABLE {PROJECTS_TABLE} ("
                "id INT PRIMARY KEY, tenant_slug VARCHAR(40) NOT NULL, "
                "status VARCHAR(20) NOT NULL, created_at INT NOT NULL"
                ") ENGINE=InnoDB"
            )
            cursor.execute(
                f"CREATE TABLE {ACCOUNTS_TABLE} ("
                "id INT PRIMARY KEY, balance INT NOT NULL"
                ") ENGINE=InnoDB"
            )
            rows = [
                (index, f"tenant-{index % 4}", ("active", "paused", "archived")[index % 3], index)
                for index in range(1, 241)
            ]
            cursor.executemany(
                f"INSERT INTO {PROJECTS_TABLE} (id, tenant_slug, status, created_at) "
                "VALUES (%s, %s, %s, %s)",
                rows,
            )
            cursor.execute(f"INSERT INTO {ACCOUNTS_TABLE} (id, balance) VALUES (1, 100)")
        connection.commit()


def _project_query(connection: pymysql.connections.Connection) -> list[int]:
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT id FROM {PROJECTS_TABLE} "
            "WHERE tenant_slug = %s AND status = %s "
            "ORDER BY created_at DESC LIMIT 25",
            ("tenant-1", "active"),
        )
        return [int(row[0]) for row in cursor.fetchall()]


def _explain(connection: pymysql.connections.Connection) -> dict[str, Any]:
    with connection.cursor() as cursor:
        cursor.execute(
            f"EXPLAIN FORMAT=JSON SELECT id FROM {PROJECTS_TABLE} "
            "WHERE tenant_slug = %s AND status = %s "
            "ORDER BY created_at DESC LIMIT 25",
            ("tenant-1", "active"),
        )
        raw = cursor.fetchone()[0]
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise RuntimeError("MariaDB returned a non-object JSON plan")
    return value


def _table_accesses(value: object) -> list[dict[str, object]]:
    """Reduce plan JSON to stable access fields and discard predicates/literals."""

    accesses: list[dict[str, object]] = []
    if isinstance(value, dict):
        table = value.get("table")
        if isinstance(table, dict):
            accesses.append(
                {
                    "table_name": table.get("table_name"),
                    "access_type": table.get("access_type"),
                    "key": table.get("key"),
                    "rows": table.get("rows"),
                }
            )
        for key, child in value.items():
            if key != "table":
                accesses.extend(_table_accesses(child))
    elif isinstance(value, list):
        for child in value:
            accesses.extend(_table_accesses(child))
    return accesses


def _index_experiment() -> dict[str, object]:
    with connect() as connection:
        before_result = _project_query(connection)
        before_access = _table_accesses(_explain(connection))
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE INDEX ix_atlas_provider_lookup ON {PROJECTS_TABLE} "
                "(tenant_slug, status, created_at)"
            )
        connection.commit()
        after_result = _project_query(connection)
        after_access = _table_accesses(_explain(connection))
    return {
        "result_ids_equal": before_result == after_result,
        "result_count": len(after_result),
        "before_access": before_access,
        "after_access": after_access,
        "selected_index": any(
            item.get("key") == "ix_atlas_provider_lookup" for item in after_access
        ),
    }


def _snapshot_experiment() -> dict[str, object]:
    with connect() as reader, connect() as writer:
        with reader.cursor() as cursor:
            cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
        reader.begin()
        with reader.cursor() as cursor:
            cursor.execute(f"SELECT balance FROM {ACCOUNTS_TABLE} WHERE id = 1")
            initial = int(cursor.fetchone()[0])
        writer.begin()
        with writer.cursor() as cursor:
            cursor.execute(f"UPDATE {ACCOUNTS_TABLE} SET balance = 125 WHERE id = 1")
        writer.commit()
        with reader.cursor() as cursor:
            cursor.execute(f"SELECT balance FROM {ACCOUNTS_TABLE} WHERE id = 1")
            repeated = int(cursor.fetchone()[0])
        reader.commit()
        reader.begin()
        with reader.cursor() as cursor:
            cursor.execute(f"SELECT balance FROM {ACCOUNTS_TABLE} WHERE id = 1")
            refreshed = int(cursor.fetchone()[0])
        reader.commit()
    return {
        "initial_balance": initial,
        "same_transaction_balance": repeated,
        "fresh_transaction_balance": refreshed,
        "snapshot_stable": initial == repeated,
        "fresh_transaction_visible": refreshed == 125,
    }


def _lock_recovery_experiment() -> dict[str, object]:
    error_code: int | None = None
    with connect() as holder, connect() as contender:
        holder.begin()
        with holder.cursor() as cursor:
            cursor.execute(f"UPDATE {ACCOUNTS_TABLE} SET balance = 130 WHERE id = 1")
        with contender.cursor() as cursor:
            cursor.execute("SET SESSION innodb_lock_wait_timeout = 1")
        contender.begin()
        try:
            with contender.cursor() as cursor:
                cursor.execute(f"UPDATE {ACCOUNTS_TABLE} SET balance = 140 WHERE id = 1")
        except pymysql.OperationalError as error:
            error_code = int(error.args[0])
            contender.rollback()
        else:
            contender.rollback()
        holder.rollback()

        contender.begin()
        with contender.cursor() as cursor:
            cursor.execute(f"UPDATE {ACCOUNTS_TABLE} SET balance = 150 WHERE id = 1")
        contender.commit()
        with contender.cursor() as cursor:
            cursor.execute(f"SELECT balance FROM {ACCOUNTS_TABLE} WHERE id = 1")
            final_balance = int(cursor.fetchone()[0])
    return {
        "first_attempt_error_code": error_code,
        "expected_lock_wait_code": 1205,
        "retry_committed": final_balance == 150,
        "final_balance": final_balance,
    }


def prepare_lab(state_dir: pathlib.Path) -> pathlib.Path:
    """Run all experiments and persist only sanitized, deterministic evidence."""

    _prepare_schema()
    evidence = {
        "engine": "mariadb",
        "generated_at": datetime.now(UTC).isoformat(),
        "index": _index_experiment(),
        "repeatable_read": _snapshot_experiment(),
        "lock_recovery": _lock_recovery_experiment(),
    }
    state_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = state_dir / EVIDENCE_NAME
    evidence_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    (state_dir / "state.json").write_text(
        json.dumps({"status": "ready", "evidence": EVIDENCE_NAME}, indent=2),
        encoding="utf-8",
    )
    return evidence_path
