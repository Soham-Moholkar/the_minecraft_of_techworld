"""Security, failure, and contract tests for the MongoDB read model."""

from datetime import UTC, datetime
from typing import Any, cast
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from atlas_api.auth import Principal, require_principal
from atlas_api.document_projection import (
    MongoProjectProjectionRepository,
    normalize_projection_documents,
)
from atlas_api.main import app
from atlas_api.schemas import (
    DocumentProjectionItem,
    DocumentProjectionPublishRead,
    DocumentProjectionSnapshotRead,
)


def test_document_projection_requires_authentication(client: TestClient) -> None:
    assert client.get("/v1/database/document-projection").status_code == 401
    assert client.post("/v1/database/document-projection/publish").status_code == 401


def test_unconfigured_projection_fails_closed(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    snapshot = client.get("/v1/database/document-projection", headers=auth_headers)
    publish = client.post(
        "/v1/database/document-projection/publish", headers=auth_headers
    )

    assert snapshot.status_code == 200
    assert snapshot.json()["status"] == "unavailable"
    assert snapshot.json()["items"] == []
    assert publish.status_code == 503
    assert publish.json() == {"detail": "document projection unavailable"}
    serialized = snapshot.text.lower() + publish.text.lower()
    assert all(value not in serialized for value in ("localhost", "password", "atlas_document"))


def test_projection_publish_requires_owner_role(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    app.dependency_overrides[require_principal] = lambda: Principal(
        subject="readonly-user",
        organization_slug="northstar",
        roles=("viewer",),
    )

    response = client.post(
        "/v1/database/document-projection/publish", headers=auth_headers
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "owner role required"}


def test_projection_documents_are_allowlisted_and_validated() -> None:
    item = normalize_projection_documents(
        [
            {
                "project_slug": "control-plane",
                "status": "active",
                "note_count": 2,
                "created_at": datetime(2026, 9, 1, tzinfo=UTC),
                "organization_slug": "northstar",
                "description": "must not cross the response boundary",
            }
        ]
    )[0]

    assert item.model_dump() == {
        "project_slug": "control-plane",
        "status": "active",
        "note_count": 2,
        "created_at": datetime(2026, 9, 1, tzinfo=UTC),
    }


def test_live_contract_uses_authenticated_tenant_and_bounded_metrics(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch: MonkeyPatch,
) -> None:
    observed_tenants: list[str] = []

    class FakeProjectionRepository:
        def __init__(self, session: object, mongodb_url: str | None) -> None:
            del session, mongodb_url

        def read(self, *, organization_slug: str) -> DocumentProjectionSnapshotRead:
            observed_tenants.append(organization_slug)
            return DocumentProjectionSnapshotRead(
                status="available",
                document_count=1,
                published_at=datetime(2026, 9, 1, tzinfo=UTC),
                items=[
                    DocumentProjectionItem(
                        project_slug="control-plane",
                        status="active",
                        note_count=2,
                        created_at=datetime(2026, 8, 27, tzinfo=UTC),
                    )
                ],
                index_strategy="tenant compound index",
                consistency_model="generation pointer",
                notes=["bounded"],
                generated_at=datetime(2026, 9, 1, tzinfo=UTC),
            )

        def publish(self, *, organization_slug: str) -> DocumentProjectionPublishRead:
            observed_tenants.append(organization_slug)
            return DocumentProjectionPublishRead(
                published_count=1,
                removed_count=0,
                published_at=datetime(2026, 9, 1, tzinfo=UTC),
            )

    monkeypatch.setattr(
        "atlas_api.main.MongoProjectProjectionRepository", FakeProjectionRepository
    )
    snapshot = client.get("/v1/database/document-projection", headers=auth_headers)
    publish = client.post(
        "/v1/database/document-projection/publish", headers=auth_headers
    )

    assert snapshot.status_code == 200
    assert snapshot.json()["items"][0]["project_slug"] == "control-plane"
    assert publish.status_code == 200
    assert publish.json()["published_count"] == 1
    assert observed_tenants == ["northstar", "northstar"]
    metrics = client.get("/metrics").text
    assert "atlas_database_document_projection_operations_total" in metrics
    assert 'operation="publish",status="success"' in metrics


def test_invalid_mongodb_document_fails_closed() -> None:
    malformed: list[dict[str, object]] = [
        {"project_slug": "ok", "status": "active", "note_count": True, "created_at": "bad"}
    ]
    with pytest.raises(ValueError, match="invalid"):
        normalize_projection_documents(malformed)


def test_publish_preserves_generations_held_by_readers_or_other_publishers() -> None:
    """A pointer switch must never erase concurrent/unexpired generations."""
    session = MagicMock()
    session.execute.return_value.all.return_value = []
    mongo = MagicMock()
    database = mongo.__enter__.return_value.__getitem__.return_value
    state = database.__getitem__.return_value
    repository = MongoProjectProjectionRepository(
        session, "mongodb://redacted", client_factory=lambda _: cast(Any, mongo)
    )
    first = repository.publish(organization_slug="northstar")
    second = repository.publish(organization_slug="northstar")
    assert first.removed_count == second.removed_count == 0
    state.delete_many.assert_not_called()
    calls = state.replace_one.call_args_list
    assert len(calls) == 2
    assert calls[0].args[0] == {"organization_slug": "northstar"}
    assert calls[0].args[1]["generation"] != calls[1].args[1]["generation"]
