"""Contract and redaction tests for normalized database providers."""

from typing import Any

from fastapi.testclient import TestClient

from atlas_api.provider_comparison import _mariadb_available
from atlas_api.query_plans import normalise_mariadb_plan


def test_provider_comparison_requires_authentication(client: TestClient) -> None:
    response = client.get("/v1/database/providers")
    assert response.status_code == 401
    assert response.json() == {"detail": "invalid credentials"}


def test_provider_comparison_reports_primary_and_optional_state(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.get("/v1/database/providers", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert [provider["engine"] for provider in payload["providers"]] == ["sqlite", "mariadb"]
    assert payload["providers"][0]["status"] == "available"
    assert payload["providers"][0]["query_plan_format"] == "query_plan"
    assert payload["providers"][1]["status"] == "unavailable"
    assert payload["providers"][1]["version"] is None
    assert payload["providers"][1]["current_isolation"] is None
    serialized = response.text.lower()
    assert all(secret not in serialized for secret in ("password", "localhost", "atlas_lab"))

    metrics = client.get("/metrics").text
    assert "atlas_database_provider_comparisons_total" in metrics
    assert 'engine="mariadb",status="unavailable"' in metrics


def test_mariadb_metadata_is_normalized_without_connection_details() -> None:
    provider = _mariadb_available(
        "12.3.2-MariaDB-log", "REPEATABLE-READ", "READ-COMMITTED"
    )
    assert provider.engine == "mariadb"
    assert provider.current_isolation == "repeatable_read"
    assert provider.default_isolation == "read_committed"
    assert provider.version == "12.3.2-MariaDB-log"


def test_mariadb_plan_is_structural_and_redacts_predicates() -> None:
    plan: dict[str, Any] = {
        "query_block": {
            "nested_loop": [
                {
                    "table": {
                        "table_name": "o",
                        "access_type": "const",
                        "key": "slug",
                        "rows": 1,
                        "attached_condition": "o.slug = 'northstar'",
                    }
                },
                {
                    "table": {
                        "table_name": "p",
                        "access_type": "ref",
                        "key": "ix_projects_status",
                        "rows": 4,
                        "attached_condition": "p.status = 'active'",
                    }
                },
            ]
        }
    }

    nodes = normalise_mariadb_plan(plan)
    assert [node.relation for node in nodes] == ["organizations", "projects"]
    assert nodes[1].operation == "Ref access"
    assert nodes[1].estimated_rows == 4.0
    serialized = " ".join(node.detail for node in nodes)
    assert "northstar" not in serialized
    assert "active" not in serialized
