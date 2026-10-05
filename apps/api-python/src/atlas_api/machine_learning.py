"""Deterministic, bounded model training for operational cost classification.

The product compares two maintained scikit-learn estimators with an intentionally
small NumPy implementation. The handwritten model makes gradient descent visible;
the library pipelines demonstrate the validation and preprocessing expected in a
real service. All three evaluate the same untouched holdout rows.
"""

from __future__ import annotations

import math
import time
from datetime import datetime
from importlib.metadata import version
from typing import Literal
from uuid import UUID

import numpy as np
from pydantic import BaseModel, ConfigDict, Field

from atlas_api.data_science import Row

MIN_ROWS = 20
ModelName = Literal[
    "logistic_regression", "decision_tree", "numpy_logistic", "pytorch_mlp", "keras_mlp"
]
FeatureName = Literal["requests", "day", "service"]


class ExperimentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=2, max_length=120)
    dataset_id: UUID
    suite: Literal["classical", "neural", "frameworks"] = "classical"


class EvaluationMetrics(BaseModel):
    accuracy: float
    balanced_accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float
    confusion_matrix: list[list[int]]


class TrainingPoint(BaseModel):
    epoch: int = Field(ge=1, le=80)
    loss: float = Field(ge=0, allow_inf_nan=False)


class ModelEvidence(BaseModel):
    model: ModelName
    implementation: Literal["scikit-learn", "from-scratch", "pytorch", "tensorflow-keras"]
    fit_ms: float
    metrics: EvaluationMetrics
    training_curve: list[TrainingPoint] = Field(default_factory=list)


class FeatureEffect(BaseModel):
    feature: FeatureName
    importance_mean: float
    importance_stddev: float


class ExperimentReport(BaseModel):
    task: Literal["high_cost_classification"] = "high_cost_classification"
    target_definition: str
    training_rows: int
    test_rows: int
    positive_rate: float
    random_seed: int
    sklearn_version: str
    torch_version: str | None = None
    tensorflow_version: str | None = None
    keras_version: str | None = None
    models: list[ModelEvidence]
    feature_effects: list[FeatureEffect]
    caveats: list[str]


class ExperimentSummary(BaseModel):
    id: UUID
    dataset_id: UUID
    dataset_name: str
    name: str
    created_at: datetime
    best_model: str
    best_balanced_accuracy: float


class ExperimentRead(ExperimentSummary):
    report: ExperimentReport


def _metrics(
    y_true: np.ndarray, prediction: np.ndarray, probability: np.ndarray
) -> EvaluationMetrics:
    from sklearn.metrics import (  # type: ignore[import-untyped]
        accuracy_score,
        balanced_accuracy_score,
        confusion_matrix,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    return EvaluationMetrics(
        accuracy=float(accuracy_score(y_true, prediction)),
        balanced_accuracy=float(balanced_accuracy_score(y_true, prediction)),
        precision=float(precision_score(y_true, prediction, zero_division=0)),
        recall=float(recall_score(y_true, prediction, zero_division=0)),
        f1=float(f1_score(y_true, prediction, zero_division=0)),
        roc_auc=float(roc_auc_score(y_true, probability)),
        confusion_matrix=[
            [int(value) for value in row]
            for row in confusion_matrix(y_true, prediction, labels=[0, 1]).tolist()
        ],
    )


def _scratch_features(frame: object, services: list[str]) -> np.ndarray:
    """Build a transparent numeric matrix for the educational baseline."""
    import pandas as pd  # type: ignore[import-untyped]

    typed = frame if isinstance(frame, pd.DataFrame) else pd.DataFrame(frame)
    numeric = typed[["requests", "day"]].to_numpy(dtype=np.float64)
    service = typed["service"].astype(str).to_numpy()
    one_hot = np.column_stack([(service == name).astype(np.float64) for name in services])
    return np.column_stack([numeric, one_hot])


def _scratch_logistic(
    train_frame: object, test_frame: object, y_train: np.ndarray, services: list[str]
) -> tuple[np.ndarray, np.ndarray]:
    """Fit batch gradient descent with train-only scaling and fixed convergence bounds."""
    train = _scratch_features(train_frame, services)
    test = _scratch_features(test_frame, services)
    mean = train.mean(axis=0)
    scale = train.std(axis=0)
    scale[scale == 0] = 1
    train = (train - mean) / scale
    test = (test - mean) / scale
    train = np.column_stack([np.ones(len(train)), train])
    test = np.column_stack([np.ones(len(test)), test])
    weights = np.zeros(train.shape[1], dtype=np.float64)
    for _ in range(800):
        logits = np.clip(train @ weights, -30, 30)
        probability = 1 / (1 + np.exp(-logits))
        gradient = train.T @ (probability - y_train) / len(train)
        weights -= 0.08 * gradient
    test_probability = 1 / (1 + np.exp(-np.clip(test @ weights, -30, 30)))
    return (test_probability >= 0.5).astype(np.int64), test_probability


def train_experiment(rows: list[Row]) -> ExperimentReport:
    """Train comparable models without allowing caller-selected code or parameters."""
    import pandas as pd  # type: ignore[import-untyped]
    from sklearn.base import clone  # type: ignore[import-untyped]
    from sklearn.compose import ColumnTransformer  # type: ignore[import-untyped]
    from sklearn.impute import SimpleImputer  # type: ignore[import-untyped]
    from sklearn.inspection import permutation_importance  # type: ignore[import-untyped]
    from sklearn.linear_model import LogisticRegression  # type: ignore[import-untyped]
    from sklearn.model_selection import train_test_split  # type: ignore[import-untyped]
    from sklearn.pipeline import Pipeline  # type: ignore[import-untyped]
    from sklearn.preprocessing import OneHotEncoder, StandardScaler  # type: ignore[import-untyped]
    from sklearn.tree import DecisionTreeClassifier  # type: ignore[import-untyped]

    if len(rows) < MIN_ROWS:
        raise ValueError(f"dataset needs at least {MIN_ROWS} cleaned rows")
    frame = pd.DataFrame(rows)
    train_rows, test_rows = train_test_split(frame, test_size=0.25, random_state=42)
    # The threshold is learned from training rows. Holdout costs define only
    # holdout labels; they never influence preprocessing, fitting, or vocabulary.
    threshold = float(np.median(train_rows["cost"].to_numpy(dtype=np.float64)))
    y_train = (train_rows["cost"].to_numpy(dtype=np.float64) > threshold).astype(np.int64)
    y_test = (test_rows["cost"].to_numpy(dtype=np.float64) > threshold).astype(np.int64)
    if min(np.bincount(y_train, minlength=2)) < 5 or min(
        np.bincount(y_test, minlength=2)
    ) < 1:
        raise ValueError("split needs five training and one holdout example in each class")

    def features(source: object) -> object:
        typed = source if isinstance(source, pd.DataFrame) else pd.DataFrame(source)
        return pd.DataFrame(
            {
                "requests": typed["requests"].astype(float),
                "day": pd.to_datetime(typed["date"], format="%Y-%m-%d").dt.day.astype(float),
                "service": typed["service"].astype(str),
            }
        )

    x_train = features(train_rows)
    x_test = features(test_rows)
    preprocessing = ColumnTransformer(
        [
            (
                "numeric",
                Pipeline([("fill", SimpleImputer()), ("scale", StandardScaler())]),
                ["requests", "day"],
            ),
            ("service", OneHotEncoder(handle_unknown="ignore"), ["service"]),
        ]
    )
    estimators: list[tuple[ModelName, object]] = [
        ("logistic_regression", LogisticRegression(max_iter=500, random_state=42)),
        (
            "decision_tree",
            DecisionTreeClassifier(max_depth=4, min_samples_leaf=2, random_state=42),
        ),
    ]
    evidence: list[ModelEvidence] = []
    fitted_logistic: object | None = None
    for name, estimator in estimators:
        # Each estimator owns its fitted preprocessing state. Reusing one mutable
        # transformer would allow the second fit to alter the first pipeline.
        pipeline = Pipeline([("prepare", clone(preprocessing)), ("model", estimator)])
        started = time.perf_counter_ns()
        pipeline.fit(x_train, y_train)
        fit_ms = (time.perf_counter_ns() - started) / 1_000_000
        prediction = np.asarray(pipeline.predict(x_test), dtype=np.int64)
        probability = np.asarray(pipeline.predict_proba(x_test)[:, 1], dtype=np.float64)
        evidence.append(
            ModelEvidence(
                model=name, implementation="scikit-learn", fit_ms=fit_ms,
                metrics=_metrics(y_test, prediction, probability),
            )
        )
        if name == "logistic_regression":
            fitted_logistic = pipeline
    services = sorted(str(value) for value in train_rows["service"].unique())
    started = time.perf_counter_ns()
    scratch_prediction, scratch_probability = _scratch_logistic(
        x_train, x_test, np.asarray(y_train, dtype=np.float64), services
    )
    evidence.append(
        ModelEvidence(
            model="numpy_logistic", implementation="from-scratch",
            fit_ms=(time.perf_counter_ns() - started) / 1_000_000,
            metrics=_metrics(y_test, scratch_prediction, scratch_probability),
        )
    )
    if fitted_logistic is None:  # Defensive invariant if the estimator map changes.
        raise RuntimeError("logistic comparison model was not trained")
    effects = permutation_importance(
        fitted_logistic, x_test, y_test, scoring="balanced_accuracy", n_repeats=8,
        random_state=42, n_jobs=1,
    )
    if not all(math.isfinite(float(value)) for value in effects.importances_mean):
        raise RuntimeError("model interpretation produced a non-finite result")
    feature_names: tuple[FeatureName, FeatureName, FeatureName] = (
        "requests",
        "day",
        "service",
    )
    return ExperimentReport(
        target_definition=f"cost greater than training-row median ({threshold:.2f})",
        training_rows=len(train_rows), test_rows=len(test_rows),
        positive_rate=float(np.concatenate([y_train, y_test]).mean()),
        random_seed=42, sklearn_version=version("scikit-learn"), models=evidence,
        feature_effects=[
            FeatureEffect(
                feature=name, importance_mean=float(mean), importance_stddev=float(stddev)
            )
            for name, mean, stddev in zip(
                feature_names, effects.importances_mean,
                effects.importances_std, strict=True
            )
        ],
        caveats=[
            "The derived target demonstrates workflow mechanics, not production validity.",
            "One deterministic 25% holdout can be unstable for small datasets.",
            "Correlated inputs can hide permutation importance on this holdout.",
            "Only metrics are retained; ATLAS does not deserialize executable model artifacts.",
        ],
    )
