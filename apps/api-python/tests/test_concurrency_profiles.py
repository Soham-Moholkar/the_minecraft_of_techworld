"""Contract, portability, and security tests for isolation introspection."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.engine import Connection, Engine

from atlas_api.concurrency_profiles import (
    _sqlite_current_isolation,
    normalize_isolation_level,
)
from atlas_api.database import get_session


def test_concurrency_profile_requires_authentication(client: TestClient) -> None:
    response = client.get("/v1/database/concurrency-profile")
    assert response.status_code == 401
    assert response.json() == {"detail": "invalid credentials"}


def test_sqlite_concurrency_profile_is_normalized_and_read_only(
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
        observed.append((statement, parameters))

    event.listen(bind, "before_cursor_execute", capture)
    try:
        response = client.get("/v1/database/concurrency-profile", headers=auth_headers)
    finally:
        event.remove(bind, "before_cursor_execute", capture)

    assert response.status_code == 200
    payload = response.json()
    assert payload["engine"] == "sqlite"
    assert payload["current_isolation"] == "serializable"
    assert payload["default_isolation"] == "serializable"
    assert payload["generated_at"].endswith("Z")
    assert [item["level"] for item in payload["capabilities"]] == [
        "read_uncommitted",
        "read_committed",
        "repeatable_read",
        "serializable",
    ]
    assert [item["support"] for item in payload["capabilities"]] == [
        "conditional",
        "unsupported",
        "unsupported",
        "native",
    ]
    assert all("tenant" not in key for key in payload)
    assert observed == [("PRAGMA read_uncommitted", ())]

    metrics = client.get("/metrics").text
    assert "atlas_database_concurrency_profiles_total" in metrics
    assert 'engine="sqlite"' in metrics


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("READ COMMITTED", "read_committed"),
        ("repeatable-read", "repeatable_read"),
        ("  serializable  ", "serializable"),
        ("read   uncommitted", "read_uncommitted"),
    ],
)
def test_postgresql_isolation_spellings_are_normalized(raw: str, expected: str) -> None:
    assert normalize_isolation_level(raw) == expected


@pytest.mark.parametrize("raw", [None, 2, "snapshot", ""])
def test_unknown_isolation_values_fail_closed(raw: object) -> None:
    with pytest.raises(ValueError):
        normalize_isolation_level(raw)


def test_sqlite_pragma_values_are_strictly_normalized() -> None:
    assert _sqlite_current_isolation(0) == "serializable"
    assert _sqlite_current_isolation(1) == "read_uncommitted"
    with pytest.raises(ValueError):
        _sqlite_current_isolation(2)
