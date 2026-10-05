"""Real engine parity, dirty-data semantics, persistence, and tenant security."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from atlas_api.auth import Principal, require_principal
from atlas_api.data_science import clean_csv, profile_csv
from atlas_api.database import get_session
from atlas_api.main import app
from atlas_api.models import AuditEvent

CSV = (
    "date,service,cost,requests\n2026-09-01, API ,10,100\n"
    "2026-09-01,api,10,100\n2026-09-02,worker,30,200\n"
    "bad-date,api,50,5\n2026-09-02,api,NaN,10\n"
)


def test_real_engines_agree_and_statistics_exclude_invalid_and_duplicate_rows() -> None:
    rows, profile, checksum = profile_csv(CSV)
    assert len(rows) == profile.valid_rows == 2
    assert (profile.input_rows, profile.invalid_rows, profile.duplicate_rows) == (5, 2, 1)
    assert profile.cost_total == 40 and profile.cost_mean == 20
    assert sum(bucket.count for bucket in profile.histogram) == 2
    assert profile.mean_ci95 is not None and profile.mean_ci95[0] < 20 < profile.mean_ci95[1]
    assert {engine.engine for engine in profile.engines} == {"pandas", "polars", "duckdb"}
    assert all(engine.matches_reference for engine in profile.engines)
    assert len(checksum) == 64


@pytest.mark.parametrize(
    "text",
    [
        "service,cost\napi,10",
        '"unterminated header',
        "date,service,cost,requests\n2026-09-01,=cmd(),10,1",
        "date,service,cost,requests\n2026-09-01,api,inf,1",
        "date,service,cost,requests\n2026-09-01,api,-1,1",
        "date,service,cost,requests\n2026-09-01,api,1,1,unexpected",
        "x" * 262145,
    ],
    ids=[
        "header",
        "malformed-header",
        "formula",
        "nonfinite",
        "negative",
        "extra-column",
        "oversized",
    ],
)
def test_invalid_schema_formula_nonfinite_range_and_size_rejected(text: str) -> None:
    with pytest.raises(ValueError):
        clean_csv(text)


def test_catalog_persists_evidence_and_enforces_tenant_and_role_boundaries(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    assert client.get("/v1/datasets").status_code == 401
    imported = client.post(
        "/v1/datasets", headers=auth_headers, json={"name": "Service usage", "csv_text": CSV}
    )
    assert imported.status_code == 201, imported.text
    dataset_id = imported.json()["id"]
    assert client.get("/v1/datasets", headers=auth_headers).json()[0]["id"] == dataset_id
    read = client.get(f"/v1/datasets/{dataset_id}", headers=auth_headers)
    assert read.json()["profile"]["cost_total"] == 40
    assert "csv_text" not in read.text and "rows" not in read.json()
    session = next(app.dependency_overrides[get_session]())
    audit = session.scalar(select(AuditEvent).where(AuditEvent.action == "dataset.imported"))
    assert audit is not None and audit.target_id == dataset_id
    assert "csv_text" not in str(audit.details)
    app.dependency_overrides[require_principal] = lambda: Principal(
        subject="other-viewer", organization_slug="other-tenant", roles=("viewer",)
    )
    assert client.get("/v1/datasets", headers=auth_headers).json() == []
    assert client.get(f"/v1/datasets/{dataset_id}", headers=auth_headers).status_code == 404
    assert (
        client.post(
            "/v1/datasets", headers=auth_headers, json={"name": "Denied", "csv_text": CSV}
        ).status_code
        == 403
    )


def test_bad_import_does_not_persist_and_records_failure_metric(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post(
        "/v1/datasets",
        headers=auth_headers,
        json={"name": "Bad import", "csv_text": "wrong,header"},
    )
    assert response.status_code == 422
    assert client.get("/v1/datasets", headers=auth_headers).json() == []
    assert "atlas_dataset_imports_total" in client.get("/metrics").text


def test_single_value_has_no_inferential_interval() -> None:
    _, profile, _ = profile_csv("date,service,cost,requests\n2026-09-01,api,0,1")
    assert profile.mean_ci95 is None
    assert profile.cost_stddev == 0
