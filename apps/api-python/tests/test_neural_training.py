"""Real CPU regression plus isolation, admission, and failure-path coverage."""

import subprocess
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from atlas_api.auth import Principal, require_principal
from atlas_api.data_science import Row, clean_csv, generate_sample
from atlas_api.main import app
from atlas_api.neural_training import (
    NEURAL_SLOT,
    TrainingBusyError,
    TrainingFailedError,
    train_neural_isolated,
    validate_neural_rows,
)


def sample() -> list[Row]:
    return clean_csv(generate_sample(80))[0]


def test_neural_reproducibility_and_shared_holdout() -> None:
    first = train_neural_isolated(sample())
    second = train_neural_isolated(sample())
    neural = first.models[-1]
    assert neural.model == "pytorch_mlp"
    assert len(neural.training_curve) == 80
    assert neural.training_curve[-1].loss < neural.training_curve[0].loss
    assert neural.training_curve == second.models[-1].training_curve
    assert neural.metrics == second.models[-1].metrics
    assert neural.metrics.balanced_accuracy >= 0.7
    assert all(
        sum(map(sum, item.metrics.confusion_matrix)) == first.test_rows for item in first.models
    )
    assert first.torch_version is not None


def test_holdout_changes_cannot_affect_training_curve() -> None:
    from sklearn.model_selection import train_test_split  # type: ignore[import-untyped]

    rows = sample()
    before = train_neural_isolated(rows)
    _, test_indices = train_test_split(list(range(len(rows))), test_size=0.25, random_state=42)
    for index in test_indices:
        rows[index] = {**rows[index], "requests": 99999, "service": "unseen-holdout"}
    after = train_neural_isolated(rows)
    assert before.models[-1].training_curve == after.models[-1].training_curve
    assert before.target_definition == after.target_definition


def test_limits_busy_timeout_failure_and_slot_release() -> None:
    with pytest.raises(ValueError, match="20 to 2000"):
        validate_neural_rows(sample() * 26)
    with pytest.raises(ValueError, match="32 distinct"):
        validate_neural_rows([{**row, "service": str(i)} for i, row in enumerate(sample())])
    with NEURAL_SLOT, pytest.raises(TrainingBusyError):
        train_neural_isolated(sample())
    with (
        patch(
            "atlas_api.neural_training.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="owned-worker", timeout=90),
        ),
        pytest.raises(TrainingFailedError, match="90 second"),
    ):
        train_neural_isolated(sample())
    assert NEURAL_SLOT.acquire(blocking=False)
    NEURAL_SLOT.release()
    with (
        patch(
            "atlas_api.neural_training.subprocess.run",
            return_value=subprocess.CompletedProcess(
                args=[], returncode=1, stdout="", stderr="private data"
            ),
        ),
        pytest.raises(TrainingFailedError, match="worker failed"),
    ):
        train_neural_isolated(sample())
    with (
        patch("atlas_api.neural_training.find_spec", return_value=None),
        pytest.raises(ImportError),
    ):
        train_neural_isolated(sample())


def test_neural_api_persistence_authorization_and_validation(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    dataset = client.post(
        "/v1/datasets",
        headers=auth_headers,
        json={
            "name": "Neural dataset",
            "csv_text": generate_sample(80),
        },
    ).json()
    body = {"name": "Neural evidence", "dataset_id": dataset["id"], "suite": "frameworks"}
    response = client.post("/v1/ml/experiments", headers=auth_headers, json=body)
    assert response.status_code == 201, response.text
    experiment = response.json()
    saved = client.get(f"/v1/ml/experiments/{experiment['id']}", headers=auth_headers)
    assert saved.json() == experiment
    assert len(experiment["report"]["models"][-1]["training_curve"]) == 80
    models = experiment["report"]["models"]
    assert len(models) == 5 and models[-1]["implementation"] == "tensorflow-keras"
    assert models[-1]["training_curve"][0]["loss"] == pytest.approx(
        models[-2]["training_curve"][0]["loss"], abs=1e-6
    )
    invalid = client.post("/v1/ml/experiments", headers=auth_headers, json={**body, "epochs": 999})
    assert invalid.status_code == 422
    with patch("atlas_api.ml_routes.train_neural_isolated", side_effect=TrainingBusyError("busy")):
        assert client.post("/v1/ml/experiments", headers=auth_headers, json=body).status_code == 429
    with patch(
        "atlas_api.ml_routes.train_neural_isolated", side_effect=TrainingFailedError("failed")
    ):
        assert client.post("/v1/ml/experiments", headers=auth_headers, json=body).status_code == 503
    assert len(client.get("/v1/ml/experiments", headers=auth_headers).json()) == 1
    app.dependency_overrides[require_principal] = lambda: Principal(
        subject="other-owner", organization_slug="other-tenant", roles=("owner",)
    )
    with patch("atlas_api.ml_routes.train_neural_isolated") as trainer:
        assert client.post("/v1/ml/experiments", headers=auth_headers, json=body).status_code == 404
        trainer.assert_not_called()
    assert (
        client.get(f"/v1/ml/experiments/{experiment['id']}", headers=auth_headers).status_code
        == 404
    )
