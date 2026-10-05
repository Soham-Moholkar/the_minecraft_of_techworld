"""Contract and security regression tests for the allowlisted plan endpoint."""

from collections.abc import Sequence
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.engine import Connection, Engine

from atlas_api.database import get_session
from atlas_api.query_plans import normalise_postgresql_plan


def test_query_plan_requires_authentication(client: TestClient) -> None:
    response = client.get("/v1/database/query-plan")
    assert response.status_code == 401
    assert response.json() == {"detail": "invalid credentials"}


def test_query_plan_rejects_unallowlisted_input(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    arbitrary_sql = client.get(
        "/v1/database/query-plan",
        headers=auth_headers,
        params={"query_name": "drop_everything"},
    )
    assert arbitrary_sql.status_code == 422
    invalid_status = client.get(
        "/v1/database/query-plan",
        headers=auth_headers,
        params={"status": "active' OR 1=1 --"},
    )
    assert invalid_status.status_code == 422


def test_sqlite_query_plan_is_normalized_and_tenant_bound(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    session = next(client.app.dependency_overrides[get_session]())
    bind = session.get_bind()
    assert isinstance(bind, Engine)
    observed: list[tuple[str, object]] = []

    def capture(
        connection: Connection,
        cursor: object,
        statement: str,
        parameters: object,
        context: object,
        executemany: bool,
    ) -> None:
        del connection, cursor, context, executemany
        if statement.startswith("EXPLAIN QUERY PLAN"):
            observed.append((statement, parameters))

    event.listen(bind, "before_cursor_execute", capture)
    try:
        response = client.get(
            "/v1/database/query-plan",
            headers=auth_headers,
            params={"status": "active"},
        )
    finally:
        event.remove(bind, "before_cursor_execute", capture)

    assert response.status_code == 200
    payload = response.json()
    assert payload["engine"] == "sqlite"
    assert payload["query_name"] == "tenant_projects_by_status"
    assert payload["parameters"] == {"status": "active"}
    assert payload["generated_at"].endswith("Z")
    assert payload["nodes"]
    assert {node["operation"] for node in payload["nodes"]} <= {"Scan", "Search", "Use"}
    assert all(node["estimated_rows"] is None for node in payload["nodes"])
    assert observed
    statement, parameters = observed[0]
    assert "o.slug = ?" in statement
    assert "p.status = ?" in statement
    # SQLAlchemy compiles named binds positionally for SQLite. Their values prove
    # the authenticated tenant, rather than an HTTP parameter, supplied the scope.
    assert isinstance(parameters, Sequence)
    assert tuple(parameters) == ("northstar", "active")


def test_postgresql_tree_normalization_is_structural_and_redacted() -> None:
    plan: dict[str, Any] = {
        "Node Type": "Nested Loop",
        "Join Type": "Inner",
        "Plan Rows": 4,
        "Total Cost": 19.25,
        "Plans": [
            {
                "Node Type": "Index Scan",
                "Relation Name": "organizations",
                "Index Name": "ix_organizations_slug",
                "Index Cond": "(slug = 'northstar'::text)",
                "Plan Rows": 1,
                "Total Cost": 8.1,
            },
            {
                "Node Type": "Bitmap Heap Scan",
                "Relation Name": "projects",
                "Filter": "(status = 'active'::text)",
                "Plan Rows": 4,
                "Total Cost": 11.15,
            },
        ],
    }

    nodes = normalise_postgresql_plan(plan)
    assert [node.operation for node in nodes] == [
        "Nested Loop",
        "Index Scan",
        "Bitmap Heap Scan",
    ]
    assert nodes[0].estimated_rows == 4.0
    assert nodes[0].estimated_cost == 19.25
    assert nodes[1].relation == "organizations"
    assert "ix_organizations_slug" in nodes[1].detail
    assert "northstar" not in nodes[1].detail
    assert "active" not in nodes[2].detail
