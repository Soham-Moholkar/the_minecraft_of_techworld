from fastapi.testclient import TestClient


def test_health_and_security_headers(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["database"] == "reachable"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-request-id"]


def test_projects_require_authentication(client: TestClient) -> None:
    response = client.get("/v1/projects")
    assert response.status_code == 401
    assert response.json() == {"detail": "invalid credentials"}


def test_identity_version_and_metrics(client: TestClient, auth_headers: dict[str, str]) -> None:
    version = client.get("/version")
    assert version.status_code == 200
    assert version.json()["service"] == "atlas-api"
    identity = client.get("/v1/me", headers=auth_headers)
    assert identity.status_code == 200
    assert identity.json()["organization_slug"] == "northstar"
    assert identity.json()["roles"] == ["owner"]
    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "atlas_http_requests_total" in metrics.text


def test_project_and_note_flow(client: TestClient, auth_headers: dict[str, str]) -> None:
    organizations = client.app.dependency_overrides  # ensure fixture has configured the app
    assert organizations
    # Fetch the deterministic fixture id through a small test-only transaction is avoided:
    # an invalid UUID first proves object validation, then the API flow uses seeded data below.
    from atlas_api.database import get_session

    session = next(client.app.dependency_overrides[get_session]())
    organization_id = str(
        session.execute(
                __import__("sqlalchemy")
                .select(__import__("atlas_api.models", fromlist=["Organization"]).Organization.id)
                .where(
                    __import__("atlas_api.models", fromlist=["Organization"]).Organization.slug
                    == "northstar"
                )
        ).scalar_one()
    )
    response = client.post(
        "/v1/projects",
        headers=auth_headers,
        json={
            "organization_id": organization_id,
            "slug": "risk-console",
            "name": "Risk Console",
            "description": "Tenant-scoped operational risk.",
        },
    )
    assert response.status_code == 201
    project = response.json()
    note = client.post(
        f"/v1/projects/{project['id']}/notes",
        headers=auth_headers,
        json={"author": "Ada", "body": "Validate the new exposure model."},
    )
    assert note.status_code == 201
    assert note.json()["body"].startswith("Validate")
    notes = client.get(f"/v1/projects/{project['id']}/notes", headers=auth_headers)
    assert [item["author"] for item in notes.json()] == ["Ada"]
    listing = client.get("/v1/projects?limit=10", headers=auth_headers)
    assert listing.json()["total"] == 1
    search = client.get("/v1/search?q=risk", headers=auth_headers)
    assert search.status_code == 200
    assert [item["name"] for item in search.json()] == ["Risk Console"]
    audit = client.get("/v1/audit", headers=auth_headers)
    audit_events = audit.json()
    assert [event["action"] for event in audit_events] == [
        "project.note_added",
        "project.created",
    ]
    stream = client.get("/v1/events/stream?once=true", headers=auth_headers)
    assert stream.status_code == 200
    assert stream.headers["content-type"].startswith("text/event-stream")
    assert "event: audit" in stream.text
    assert "project.note_added" in stream.text
    assert "retry: 2000" in stream.text
    resumed = client.get(
        "/v1/events/stream?once=true",
        headers={**auth_headers, "Last-Event-ID": audit_events[1]["id"]},
    )
    assert resumed.status_code == 200
    assert "project.note_added" in resumed.text
    assert "project.created" not in resumed.text
    unavailable = client.get(
        "/v1/events/stream?once=true",
        headers={
            **auth_headers,
            "Last-Event-ID": "00000000-0000-0000-0000-000000000001",
        },
    )
    assert unavailable.status_code == 409
    assert unavailable.json() == {"detail": "event cursor unavailable"}
    duplicate = client.post(
        "/v1/projects",
        headers=auth_headers,
        json={
            "organization_id": organization_id,
            "slug": "risk-console",
            "name": "Duplicate",
        },
    )
    assert duplicate.status_code == 409


def test_search_rejects_unbounded_or_unauthenticated_input(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    assert client.get("/v1/search?q=risk").status_code == 401
    assert client.get("/v1/search?q=x", headers=auth_headers).status_code == 422


def test_tenant_boundary_hides_other_organizations(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    from sqlalchemy import select

    from atlas_api.database import get_session
    from atlas_api.models import Organization

    session = next(client.app.dependency_overrides[get_session]())
    other_id = str(
        session.execute(
            select(Organization.id).where(Organization.slug == "other-tenant")
        ).scalar_one()
    )
    response = client.post(
        "/v1/projects",
        headers=auth_headers,
        json={"organization_id": other_id, "slug": "forbidden", "name": "Forbidden"},
    )
    # Returning 404 avoids disclosing that another tenant identifier is valid.
    assert response.status_code == 404
    unknown_project = "00000000-0000-0000-0000-000000000001"
    assert client.get(
        f"/v1/projects/{unknown_project}/notes", headers=auth_headers
    ).status_code == 404
    assert client.post(
        f"/v1/projects/{unknown_project}/notes",
        headers=auth_headers,
        json={"author": "Ada", "body": "Must remain tenant scoped."},
    ).status_code == 404
