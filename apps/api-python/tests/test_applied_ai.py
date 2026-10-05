"""Applied-AI model quality, persistence, telemetry and authorization tests."""

from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import select

from atlas_api.applied_training import run_applied_isolated
from atlas_api.auth import Principal, require_principal
from atlas_api.database import get_session
from atlas_api.main import app
from atlas_api.models import AppliedAIExperiment, AuditEvent


def test_real_applied_suite_is_complete_deterministic_and_beats_baselines() -> None:
    first = run_applied_isolated()
    second = run_applied_isolated()
    assert first == second
    assert {task.task for task in first.tasks} == {
        "computer_vision",
        "time_series",
        "nlp_attention",
        "recommendation",
    }
    for task in first.tasks:
        assert task.training_curve[-1].loss < task.training_curve[0].loss
        assert (
            task.model_score > task.baseline_score
            if task.higher_is_better
            else task.model_score < task.baseline_score
        )


def test_applied_api_persists_audit_and_tenant_scope(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    report = run_applied_isolated()
    with patch("atlas_api.applied_routes.run_applied_isolated", return_value=report):
        response = client.post(
            "/v1/ml/applied-experiments",
            headers=auth_headers,
            json={"name": "Applied compatibility"},
        )
    assert response.status_code == 201, response.text
    experiment = response.json()
    assert experiment["tasks"] == 4 and experiment["improved_tasks"] == 4
    assert (
        client.get(f"/v1/ml/applied-experiments/{experiment['id']}", headers=auth_headers).json()
        == experiment
    )
    session = next(app.dependency_overrides[get_session]())
    assert session.scalar(select(AppliedAIExperiment)) is not None
    audit = session.scalar(
        select(AuditEvent).where(AuditEvent.action == "model.applied_experiment.created")
    )
    assert audit is not None and audit.target_id == experiment["id"]
    app.dependency_overrides[require_principal] = lambda: Principal(
        subject="other", organization_slug="other-tenant", roles=("owner",)
    )
    assert client.get("/v1/ml/applied-experiments", headers=auth_headers).json() == []
    assert (
        client.get(
            f"/v1/ml/applied-experiments/{experiment['id']}", headers=auth_headers
        ).status_code
        == 404
    )


def test_applied_api_validates_and_authorizes_before_training(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    assert client.get("/v1/ml/applied-experiments").status_code == 401
    assert (
        client.post(
            "/v1/ml/applied-experiments", headers=auth_headers, json={"name": "x", "seed": 7}
        ).status_code
        == 422
    )
    app.dependency_overrides[require_principal] = lambda: Principal(
        subject="viewer", organization_slug="northstar", roles=("viewer",)
    )
    with patch("atlas_api.applied_routes.run_applied_isolated") as training:
        assert (
            client.post(
                "/v1/ml/applied-experiments", headers=auth_headers, json={"name": "Denied run"}
            ).status_code
            == 403
        )
        training.assert_not_called()
    assert "atlas_applied_ai_runs_total" in client.get("/metrics").text
