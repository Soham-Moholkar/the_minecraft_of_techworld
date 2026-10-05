"""Owner/tenant, privacy, retention and bounded-memory regression coverage."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from alembic import command
from atlas_api.agent_memory import MemoryCreate, create_memory, snapshot
from atlas_api.agent_memory_routes import ACTIONS
from atlas_api.auth import Principal, require_principal
from atlas_api.config import Settings, get_settings
from atlas_api.database import get_session
from atlas_api.main import app
from atlas_api.models import AgentMemory, AuditEvent, Organization

URL = "/v1/ai/repository/memory"
INPUT = {
    "title": "Reviewed local observation",
    "content": "The candidate worker requires Docker.",
    "provenance": "Operator observation in the local checkout",
    "retention_days": 7,
    "confirmation": "NO SECRETS OR APPROVALS",
}


def test_memory_lifecycle_and_content_free_audit(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    created = client.post(URL, headers=auth_headers, json=INPUT)
    assert created.status_code == 201, created.text
    assert created.headers["Cache-Control"] == "no-store"
    record = created.json()
    assert datetime.fromisoformat(record["expires_at"]) - datetime.fromisoformat(
        record["created_at"]
    ) == timedelta(days=7)
    read = client.get(URL, headers=auth_headers)
    assert read.json()["items"] == [record]
    assert read.json()["automatic_context"] is False
    assert read.json()["mode"] == "operator-managed"
    assert (
        client.request(
            "DELETE",
            f"{URL}/{record['id']}",
            headers=auth_headers,
            json={"confirmation": "DELETE MEMORY"},
        ).status_code
        == 200
    )
    assert client.get(URL, headers=auth_headers).json()["items"] == []
    session = next(app.dependency_overrides[get_session]())
    assert session.get(AgentMemory, UUID(record["id"])) is None
    evidence = session.scalars(
        select(AuditEvent).where(AuditEvent.target_type == "agent_memory")
    ).all()
    assert {item.action for item in evidence} == {"ai.memory.created", "ai.memory.deleted"}
    assert all(item.details == {} for item in evidence)
    assert INPUT["content"] not in json.dumps([item.details for item in evidence])
    session.close()


@pytest.mark.parametrize(
    "field,value",
    [
        ("content", "Authorization: Bearer sensitive-example-token"),
        ("title", "APPLY EXACT PATCH"),
        ("provenance", "password=not-for-memory"),
        ("content", "run_digest: " + "a" * 64),
        ("content", "-----BEGIN RSA PRIVATE KEY-----"),
        ("content", "postgresql://owner:credential@localhost/db"),
    ],
)
def test_sensitive_material_rejected_without_storage(
    client: TestClient,
    auth_headers: dict[str, str],
    field: str,
    value: str,
) -> None:
    result = client.post(URL, headers=auth_headers, json={**INPUT, field: value})
    assert result.status_code == 400
    assert value not in result.text
    assert client.get(URL, headers=auth_headers).json()["items"] == []
    session = next(app.dependency_overrides[get_session]())
    assert (
        session.scalars(select(AuditEvent).where(AuditEvent.target_type == "agent_memory")).all()
        == []
    )
    session.close()


@pytest.mark.parametrize(
    "changes",
    [
        {"retention_days": 365},
        {"confirmation": "approved"},
        {"content": "x" * 2_001},
        {"organization_id": "chosen-by-caller"},
        {"automatic_context": True},
    ],
)
def test_invalid_shape_and_authority_are_rejected(
    client: TestClient,
    auth_headers: dict[str, str],
    changes: dict[str, object],
) -> None:
    assert client.post(URL, headers=auth_headers, json={**INPUT, **changes}).status_code == 422


def test_memory_tenant_isolation_and_delete_confirmation(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    record = client.post(URL, headers=auth_headers, json=INPUT).json()
    assert (
        client.request(
            "DELETE", f"{URL}/{record['id']}", headers=auth_headers, json={"confirmation": "skip"}
        ).status_code
        == 422
    )
    app.dependency_overrides[require_principal] = lambda: Principal(
        "other-owner", "other-tenant", ("owner",)
    )
    assert client.get(URL).json()["items"] == []
    assert (
        client.request(
            "DELETE", f"{URL}/{record['id']}", json={"confirmation": "DELETE MEMORY"}
        ).status_code
        == 404
    )
    assert (
        client.post(f"{URL}/purge-expired", json={"confirmation": "REMOVE EXPIRED MEMORY"}).json()[
            "removed_count"
        ]
        == 0
    )
    app.dependency_overrides.pop(require_principal)
    assert len(client.get(URL, headers=auth_headers).json()["items"]) == 1


@pytest.mark.parametrize(
    "slug,roles,status",
    [
        ("northstar", ("reader",), 403),
        ("missing", ("owner",), 404),
    ],
)
def test_memory_requires_owner_and_existing_tenant(
    client: TestClient,
    slug: str,
    roles: tuple[str, ...],
    status: int,
) -> None:
    app.dependency_overrides[require_principal] = lambda: Principal("viewer", slug, roles)
    assert client.get(URL).status_code == status
    assert client.post(URL, json=INPUT).status_code == status


def test_memory_requires_auth_and_local_environment(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    assert client.get(URL).status_code == 401
    app.dependency_overrides[get_settings] = lambda: Settings(environment="production")
    assert client.get(URL, headers=auth_headers).status_code == 503
    assert client.post(URL, headers=auth_headers, json=INPUT).status_code == 503


def test_expiry_boundary_and_explicit_cleanup(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    session = next(app.dependency_overrides[get_session]())
    tenant = session.scalar(select(Organization).where(Organization.slug == "northstar"))
    other = session.scalar(select(Organization).where(Organization.slug == "other-tenant"))
    assert tenant is not None and other is not None
    now = datetime.now(UTC)
    expired = create_memory(
        session, tenant.id, MemoryCreate(**INPUT), "owner", now=now - timedelta(days=7)
    )
    other_expired = create_memory(
        session, other.id, MemoryCreate(**INPUT), "other", now=now - timedelta(days=7)
    )
    session.commit()
    expired_id, other_expired_id = expired.id, other_expired.id
    assert snapshot(session, tenant.id, now=now).items == []  # Equality is expired, not active.
    read = client.get(URL, headers=auth_headers).json()
    assert read["items"] == [] and read["expired_count"] == 1
    assert session.get(AgentMemory, expired.id) is not None  # GET does not mutate storage.
    result = client.post(
        f"{URL}/purge-expired", headers=auth_headers, json={"confirmation": "REMOVE EXPIRED MEMORY"}
    )
    assert result.json() == {"removed_count": 1}
    session.expire_all()
    assert session.get(AgentMemory, expired_id) is None
    assert session.get(AgentMemory, other_expired_id) is not None
    assert client.post(
        f"{URL}/purge-expired", headers=auth_headers, json={"confirmation": "REMOVE EXPIRED MEMORY"}
    ).json() == {"removed_count": 0}
    session.close()


def test_quota_database_invariant_and_save_cleanup(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    session = next(app.dependency_overrides[get_session]())
    tenant = session.scalar(select(Organization).where(Organization.slug == "northstar"))
    assert tenant is not None
    now = datetime.now(UTC)
    for _ in range(50):
        create_memory(session, tenant.id, MemoryCreate(**INPUT), "owner", now=now)
    session.commit()
    assert client.post(URL, headers=auth_headers, json=INPUT).status_code == 409
    record = session.scalar(select(AgentMemory).where(AgentMemory.organization_id == tenant.id))
    assert record is not None
    record.expires_at = now - timedelta(seconds=1)
    session.commit()
    assert client.post(URL, headers=auth_headers, json=INPUT).status_code == 201
    session.expire_all()
    assert len(session.scalars(select(AgentMemory)).all()) == 50
    invalid = AgentMemory(
        organization_id=tenant.id,
        slot=51,
        title="Invalid overflow slot",
        content=INPUT["content"],
        provenance=INPUT["provenance"],
        created_by="owner",
        created_at=now,
        expires_at=now + timedelta(days=7),
    )
    session.add(invalid)
    with pytest.raises(IntegrityError):
        session.flush()
    session.rollback()
    duplicate = AgentMemory(
        organization_id=tenant.id,
        slot=1,
        title="Duplicate slot",
        content=INPUT["content"],
        provenance=INPUT["provenance"],
        created_by="owner",
        created_at=now,
        expires_at=now + timedelta(days=7),
    )
    session.add(duplicate)
    with pytest.raises(IntegrityError):
        session.flush()
    session.rollback()
    session.close()


def test_memory_read_telemetry(client: TestClient, auth_headers: dict[str, str]) -> None:
    before = ACTIONS.labels("read")._value.get()
    assert client.get(URL).status_code == 401
    assert ACTIONS.labels("read")._value.get() == before
    assert client.get(URL, headers=auth_headers).status_code == 200
    assert ACTIONS.labels("read")._value.get() == before + 1


def test_memory_migration_round_trip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Only a disposable database is migrated/dropped; no developer data is touched.
    url = f"sqlite+pysqlite:///{(tmp_path / 'migration.db').as_posix()}"
    monkeypatch.setenv("ATLAS_DATABASE_URL", url)
    get_settings.cache_clear()
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.set_main_option("path_separator", "os")
    try:
        command.upgrade(config, "head")
        engine = create_engine(url)
        assert "agent_memories" in inspect(engine).get_table_names()
        with Session(engine) as session:
            tenant = Organization(slug="memory-migration", name="Migration fixture")
            session.add(tenant)
            session.flush()
            create_memory(session, tenant.id, MemoryCreate(**INPUT), "owner", now=datetime.now(UTC))
            session.commit()
        engine.dispose()
        command.downgrade(config, "20260923_0014")
        engine = create_engine(url)
        assert "agent_memories" not in inspect(engine).get_table_names()
        engine.dispose()
        command.upgrade(config, "head")
        engine = create_engine(url)
        assert "agent_memories" in inspect(engine).get_table_names()
        engine.dispose()
    finally:
        get_settings.cache_clear()
