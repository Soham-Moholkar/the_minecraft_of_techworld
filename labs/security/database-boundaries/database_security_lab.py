"""Local defensive database exercise for injection and least privilege."""

from __future__ import annotations

import json
import pathlib
import sqlite3
from contextlib import closing
from typing import Final

ATTACK_INPUT: Final = "%' OR 1=1 --"
TARGET_TENANT: Final = "northstar"
GENERATED_FILES: Final = ("database-security.sqlite3", "evidence.json", "state.json")


def prepare_database(path: pathlib.Path) -> None:
    """Create disposable data containing an explicit cross-tenant canary."""

    with closing(sqlite3.connect(path)) as connection, connection:
        connection.executescript(
            """
            CREATE TABLE projects (
                id INTEGER PRIMARY KEY,
                tenant TEXT NOT NULL,
                name TEXT NOT NULL
            );
            INSERT INTO projects (tenant, name) VALUES
                ('northstar', 'Atlas API'),
                ('northstar', 'Atlas Web'),
                ('other-tenant', 'Cross Tenant Canary');
            """
        )


def intentionally_vulnerable_search(
    connection: sqlite3.Connection, tenant: str, search: str
) -> list[tuple[str, str]]:
    """Demonstrate string-concatenation injection inside this local lab only."""

    # SECURITY LAB ONLY: this anti-pattern is intentionally executable so the
    # learner can observe the tenant-boundary failure before applying the fix.
    sql = (
        "SELECT tenant, name FROM projects "
        f"WHERE tenant = '{tenant}' AND name LIKE '%{search}%'"
    )
    return [(str(row[0]), str(row[1])) for row in connection.execute(sql)]


def secure_search(
    connection: sqlite3.Connection, tenant: str, search: str
) -> list[tuple[str, str]]:
    """Bind values and keep tenant authorization in the database predicate."""

    return [
        (str(row[0]), str(row[1]))
        for row in connection.execute(
            "SELECT tenant, name FROM projects WHERE tenant = ? AND name LIKE ?",
            (tenant, f"%{search}%"),
        )
    ]


def install_read_only_authorizer(connection: sqlite3.Connection) -> None:
    """Deny mutations and attachment to emulate a least-privileged query role."""

    allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION}

    def authorize(
        action: int,
        _one: str | None,
        _two: str | None,
        _db: str | None,
        _trigger: str | None,
    ) -> int:
        return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY

    connection.set_authorizer(authorize)


def run_exercise(database_path: pathlib.Path) -> dict[str, object]:
    """Capture exploit, remediation, authorization, and redaction evidence."""

    database_path.unlink(missing_ok=True)
    prepare_database(database_path)
    with closing(sqlite3.connect(database_path)) as connection:
        vulnerable = intentionally_vulnerable_search(
            connection, TARGET_TENANT, ATTACK_INPUT
        )
        secure = secure_search(connection, TARGET_TENANT, ATTACK_INPUT)
    with closing(sqlite3.connect(database_path)) as read_only:
        install_read_only_authorizer(read_only)
        read_count = len(secure_search(read_only, TARGET_TENANT, "Atlas"))
        try:
            read_only.execute("DELETE FROM projects")
            mutation_denied = False
        except sqlite3.DatabaseError:
            mutation_denied = True

    cross_tenant_exposed = any(tenant != TARGET_TENANT for tenant, _ in vulnerable)
    if not cross_tenant_exposed or secure or not mutation_denied or read_count != 2:
        raise RuntimeError(
            "the defensive database exercise did not prove its invariants"
        )
    return {
        "exercise": "database-injection-and-least-privilege",
        "scope": "local disposable SQLite database; no listener and no internet access",
        "threat_model": {
            "asset": "tenant-isolated project metadata",
            "attacker_capability": "controls a search value but has no filesystem access",
            "trust_boundary": "request value entering a database predicate",
        },
        "vulnerable_baseline": {
            "cross_tenant_exposed": cross_tenant_exposed,
            "returned_count": len(vulnerable),
        },
        "remediation": {
            "bound_parameters": True,
            "tenant_predicate_preserved": True,
            "attack_result_count": len(secure),
        },
        "least_privilege": {
            "read_count": read_count,
            "mutation_denied": mutation_denied,
        },
        "audit_event": {
            "query_id": "tenant_project_search",
            "outcome": "rejected-by-literal-match",
            "input_recorded": False,
        },
        "lessons": [
            "Bind untrusted values; never assemble SQL with string concatenation.",
            "Keep tenant scope in every authoritative repository predicate.",
            "Give read tools a read-only database role and deny attachment or schema changes.",
            "Log bounded query identifiers and outcomes, not hostile or sensitive input.",
        ],
    }


def write_evidence(state_dir: pathlib.Path) -> pathlib.Path:
    state_dir.mkdir(parents=True, exist_ok=True)
    database_path = state_dir / GENERATED_FILES[0]
    evidence_path = state_dir / GENERATED_FILES[1]
    evidence_path.write_text(
        json.dumps(run_exercise(database_path), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (state_dir / GENERATED_FILES[2]).write_text(
        json.dumps({"status": "ready", "evidence": evidence_path.name}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    return evidence_path


def reset_generated_state(state_dir: pathlib.Path) -> None:
    """Delete only fixed lab artifacts and preserve learner additions."""

    for filename in GENERATED_FILES:
        (state_dir / filename).unlink(missing_ok=True)
    if state_dir.exists() and not any(state_dir.iterdir()):
        state_dir.rmdir()
