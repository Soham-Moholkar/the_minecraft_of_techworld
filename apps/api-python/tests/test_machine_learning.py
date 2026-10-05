"""Model correctness, experiment persistence, and tenant authorization tests."""

from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import select

from atlas_api.auth import Principal, require_principal
from atlas_api.data_science import generate_sample
from atlas_api.database import get_session
from atlas_api.machine_learning import train_experiment
from atlas_api.main import app
from atlas_api.models import AuditEvent, ModelExperiment, Organization


def _import_dataset(client: TestClient, headers: dict[str, str], rows: int = 60) -> str:
    response = client.post(
        "/v1/datasets",
        headers=headers,
        json={"name": "ML service usage", "csv_text": generate_sample(rows)},
    )
    assert response.status_code == 201, response.text
    return str(response.json()["id"])


def test_pipeline_and_scratch_models_share_bounded_holdout() -> None:
    from atlas_api.data_science import clean_csv

    rows, _, _, _ = clean_csv(generate_sample(80))
    report = train_experiment(rows)
    assert report.training_rows + report.test_rows == len(rows)
    assert [model.model for model in report.models] == [
        "logistic_regression",
        "decision_tree",
        "numpy_logistic",
    ]
    assert report.models[2].implementation == "from-scratch"
    assert all(0 <= model.metrics.balanced_accuracy <= 1 for model in report.models)
    assert all(
        sum(map(sum, model.metrics.confusion_matrix)) == report.test_rows
        for model in report.models
    )
    assert {effect.feature for effect in report.feature_effects} == {"requests", "day", "service"}
    assert "cost" not in {effect.feature for effect in report.feature_effects}
    # Reproduce only the deterministic row split: the reported threshold must
    # come from training costs, not from labels observed in the holdout.
    import numpy as np
    import pandas as pd  # type: ignore[import-untyped]
    from sklearn.model_selection import train_test_split  # type: ignore[import-untyped]

    train_rows, _ = train_test_split(pd.DataFrame(rows), test_size=0.25, random_state=42)
    expected_threshold = float(np.median(train_rows["cost"].to_numpy(dtype=np.float64)))
    assert report.target_definition.endswith(f"({expected_threshold:.2f})")


def test_experiment_catalog_persists_evidence_audit_and_tenant_boundary(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    assert client.get("/v1/ml/experiments").status_code == 401
    dataset_id = _import_dataset(client, auth_headers)
    created = client.post(
        "/v1/ml/experiments",
        headers=auth_headers,
        json={"name": "Cost risk baseline", "dataset_id": dataset_id},
    )
    assert created.status_code == 201, created.text
    experiment_id = created.json()["id"]
    assert created.json()["report"]["sklearn_version"] == "1.9.1"
    assert len(created.json()["report"]["models"]) == 3
    assert client.get("/v1/ml/experiments", headers=auth_headers).json()[0]["id"] == experiment_id
    assert client.get(
        f"/v1/ml/experiments/{experiment_id}", headers=auth_headers
    ).status_code == 200
    session = next(app.dependency_overrides[get_session]())
    stored = session.scalar(
        select(ModelExperiment).where(ModelExperiment.id == UUID(experiment_id))
    )
    audit = session.scalar(
        select(AuditEvent).where(AuditEvent.action == "model.experiment.created")
    )
    assert stored is not None and "pickle" not in str(stored.report).lower()
    assert audit is not None and audit.target_id == experiment_id
    other_tenant = session.scalar(select(Organization).where(Organization.slug == "other-tenant"))
    assert other_tenant is not None and stored is not None
    # SQLite test connections do not enforce foreign keys by default, so this
    # deliberately corrupt row proves the read query also checks both tenant IDs.
    session.add(
        ModelExperiment(
            organization_id=other_tenant.id,
            dataset_id=stored.dataset_id,
            name="Mismatched tenant evidence",
            report=stored.report,
        )
    )
    session.commit()
    northstar_catalog = client.get("/v1/ml/experiments", headers=auth_headers).json()
    assert [item["id"] for item in northstar_catalog] == [experiment_id]
    app.dependency_overrides[require_principal] = lambda: Principal(
        subject="other-viewer", organization_slug="other-tenant", roles=("viewer",)
    )
    assert client.get("/v1/ml/experiments", headers=auth_headers).json() == []
    assert (
        client.get(f"/v1/ml/experiments/{experiment_id}", headers=auth_headers).status_code
        == 404
    )
    assert (
        client.post(
            "/v1/ml/experiments",
            headers=auth_headers,
            json={"name": "Denied", "dataset_id": dataset_id},
        ).status_code
        == 403
    )


def test_training_rejects_small_dataset_without_partial_experiment(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    dataset_id = _import_dataset(client, auth_headers, rows=10)
    response = client.post(
        "/v1/ml/experiments",
        headers=auth_headers,
        json={"name": "Too small", "dataset_id": dataset_id},
    )
    assert response.status_code == 422
    assert client.get("/v1/ml/experiments", headers=auth_headers).json() == []
    assert "atlas_ml_training_total" in client.get("/metrics").text
