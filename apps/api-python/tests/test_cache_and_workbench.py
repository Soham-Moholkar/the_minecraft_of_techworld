"""Redis fallback, cache isolation, and safe workbench contract tests."""

import json
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient
from redis.exceptions import ConnectionError as RedisConnectionError
from sqlalchemy import select

from atlas_api.cache_profile import RedisProjectCacheRepository, tenant_cache_key
from atlas_api.database import get_session
from atlas_api.models import Organization, Project


def _session(client: TestClient) -> Any:
    return next(client.app.dependency_overrides[get_session]())


def _seed_projects(client: TestClient) -> None:
    session = _session(client)
    northstar = session.scalar(select(Organization).where(Organization.slug == "northstar"))
    other = session.scalar(select(Organization).where(Organization.slug == "other-tenant"))
    assert northstar is not None and other is not None
    session.add_all(
        [
            Project(organization_id=northstar.id, slug="active-one", name="Active One"),
            Project(
                organization_id=northstar.id,
                slug="paused-one",
                name="Paused One",
                status="paused",
            ),
            Project(organization_id=other.id, slug="hidden-one", name="Hidden One"),
        ]
    )
    session.commit()


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.ttls: dict[str, int] = {}

    def ping(self) -> bool:
        return True

    def get(self, key: str) -> str | None:
        return self.values.get(key)

    def set(self, key: str, value: str, *, ex: int) -> bool:
        self.values[key] = value
        self.ttls[key] = ex
        return True

    def ttl(self, key: str) -> int:
        return self.ttls.get(key, -2)

    def close(self) -> None:
        return None


def test_cache_profile_requires_auth_and_degrades_to_relational_data(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    _seed_projects(client)
    assert client.get("/v1/database/cache-profile").status_code == 401

    response = client.get("/v1/database/cache-profile", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["status"] == "unavailable"
    assert response.json()["cache_state"] == "bypass"
    assert response.json()["project_total"] == 2
    assert response.json()["status_counts"] == [
        {"status": "active", "count": 1},
        {"status": "paused", "count": 1},
    ]


def test_cache_repository_misses_then_hits_a_non_enumerable_tenant_key(
    client: TestClient,
) -> None:
    _seed_projects(client)
    fake = FakeRedis()
    repository = RedisProjectCacheRepository(
        _session(client),
        "redis://redacted",
        client_factory=lambda _: cast(Any, fake),
    )

    first = repository.read(organization_slug="northstar")
    second = repository.read(organization_slug="northstar")

    assert first.cache_state == "miss"
    assert second.cache_state == "hit"
    assert second.project_total == 2
    assert list(fake.values) == [tenant_cache_key("northstar")]
    assert "northstar" not in next(iter(fake.values))


def test_workbench_is_tenant_scoped_bounded_and_rejects_sql_fields(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    _seed_projects(client)
    assert client.post("/v1/database/workbench", json={}).status_code == 401

    response = client.post(
        "/v1/database/workbench",
        headers=auth_headers,
        json={
            "query_name": "tenant_projects_by_status",
            "status": "active",
            "limit": 1,
        },
    )

    assert response.status_code == 200
    assert response.json()["returned_count"] == 1
    assert response.json()["items"][0]["project_slug"] == "active-one"
    assert "hidden-one" not in response.text
    assert (
        client.post(
            "/v1/database/workbench",
            headers=auth_headers,
            json={"sql": "SELECT * FROM projects"},
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/v1/database/workbench",
            headers=auth_headers,
            json={"limit": 10_000},
        ).status_code
        == 422
    )


def test_cache_and_workbench_metrics_are_bounded(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    client.get("/v1/database/cache-profile", headers=auth_headers)
    client.post("/v1/database/workbench", headers=auth_headers, json={})

    metrics = client.get("/metrics").text
    assert "atlas_database_cache_profile_operations_total" in metrics
    assert "atlas_database_workbench_queries_total" in metrics


@pytest.mark.parametrize("stage", ["factory", "get", "set"])
def test_cache_errors_preserve_authoritative_tenant_result(client: TestClient, stage: str) -> None:
    _seed_projects(client)

    class BrokenRedis(FakeRedis):
        def get(self, key: str) -> str | None:
            if stage == "get":
                raise RedisConnectionError("private endpoint")
            return None

        def set(self, key: str, value: str, *, ex: int) -> bool:
            raise RedisConnectionError("private credentials")

    def factory(_: str) -> Any:
        if stage == "factory":
            raise ValueError("private URL")
        return BrokenRedis()

    result = RedisProjectCacheRepository(
        _session(client), "redis://redacted", client_factory=factory
    ).read(organization_slug="northstar")
    assert result.cache_state == "bypass"
    assert result.project_total == 2
    assert "private" not in result.model_dump_json()


@pytest.mark.parametrize(
    "payload",
    [
        "bad json",
        '{"project_total": 999, "status_counts": []}',
        '{"project_total": 2, "status_counts": [{"status":"active","count":1},'
        '{"status":"active","count":1}]}',
    ],
)
def test_invalid_cache_is_replaced_from_sql(client: TestClient, payload: str) -> None:
    _seed_projects(client)
    fake = FakeRedis()
    fake.values[tenant_cache_key("northstar")] = payload
    fake.ttls[tenant_cache_key("northstar")] = 20
    result = RedisProjectCacheRepository(
        _session(client), "redis://redacted", client_factory=lambda _: cast(Any, fake)
    ).read(organization_slug="northstar")
    assert result.cache_state == "miss"
    assert json.loads(fake.values[tenant_cache_key("northstar")])["project_total"] == 2


def test_cached_tenants_never_share_data_and_expired_entries_are_refreshed(
    client: TestClient,
) -> None:
    _seed_projects(client)
    fake = FakeRedis()
    repository = RedisProjectCacheRepository(
        _session(client), "redis://redacted", client_factory=lambda _: cast(Any, fake)
    )
    assert repository.read(organization_slug="northstar").project_total == 2
    assert repository.read(organization_slug="other-tenant").project_total == 1
    fake.ttls[tenant_cache_key("northstar")] = -1  # Persistent entries violate the TTL contract.
    assert repository.read(organization_slug="northstar").cache_state == "miss"
