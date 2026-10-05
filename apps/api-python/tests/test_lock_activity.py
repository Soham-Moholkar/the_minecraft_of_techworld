"""Security and normalization tests for the bounded lock-activity endpoint."""

import pytest
from fastapi.testclient import TestClient

from atlas_api.lock_activity import normalize_lock_rows


def test_lock_activity_requires_authentication(client: TestClient) -> None:
    response = client.get("/v1/database/lock-activity")
    assert response.status_code == 401
    assert response.json() == {"detail": "invalid credentials"}


def test_sqlite_reports_explicit_unavailable_state(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.get("/v1/database/lock-activity", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["engine"] == "sqlite"
    assert payload["available"] is False
    assert payload["total_locks"] == 0
    assert payload["waiting_locks"] == 0
    assert payload["buckets"] == []
    assert payload["generated_at"].endswith("Z")
    assert all(key not in payload for key in ("pid", "query", "relation", "transaction_id"))

    metrics = client.get("/metrics").text
    assert "atlas_database_lock_activity_snapshots_total" in metrics
    assert 'engine="sqlite"' in metrics


def test_lock_rows_are_normalized_and_totals_remain_composable() -> None:
    buckets = normalize_lock_rows(
        [
            {"mode": "RowExclusiveLock", "granted": True, "lock_count": 3},
            {"mode": "ShareLock", "granted": False, "lock_count": 1},
        ]
    )
    assert [(bucket.mode, bucket.granted, bucket.count) for bucket in buckets] == [
        ("RowExclusiveLock", True, 3),
        ("ShareLock", False, 1),
    ]
    assert sum(bucket.count for bucket in buckets if not bucket.granted) == 1


@pytest.mark.parametrize(
    "row",
    [
        {"mode": "", "granted": True, "lock_count": 1},
        {"mode": "ShareLock", "granted": "yes", "lock_count": 1},
        {"mode": "ShareLock", "granted": True, "lock_count": -1},
        {"mode": "ShareLock", "granted": True, "lock_count": True},
    ],
)
def test_invalid_database_lock_rows_fail_closed(row: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        normalize_lock_rows([row])
