"""Small, real neural tasks covering Phase 7's applied model families.

The fixtures are deterministic product simulations, not claims about external
benchmarks. Their purpose is to catch broken training loops, tensor contracts,
evaluation leakage, and framework upgrades while keeping laptop execution bounded.
"""

from __future__ import annotations

import json
import math
import os
import subprocess  # noqa: S404 -- fixed executable/module; no caller command
import sys
import time
from importlib.util import find_spec
from typing import Any

import numpy as np

from atlas_api.applied_ai import AppliedReport, AppliedTaskEvidence
from atlas_api.machine_learning import TrainingPoint
from atlas_api.neural_training import (
    NEURAL_SLOT,
    TIMEOUT_SECONDS,
    TrainingBusyError,
    TrainingFailedError,
)


def run_applied_isolated() -> AppliedReport:
    """Run trusted ATLAS training in the shared single-CPU admission boundary."""
    if find_spec("torch") is None:
        raise ImportError("optional CPU PyTorch runtime is not installed")
    if not NEURAL_SLOT.acquire(blocking=False):
        raise TrainingBusyError("neural training is busy; retry after the active run")
    try:
        environment = {
            key: value
            for key, value in os.environ.items()
            if key in {"PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "VIRTUAL_ENV"}
        }
        environment.update(
            {
                "OMP_NUM_THREADS": "1",
                "MKL_NUM_THREADS": "1",
                "OPENBLAS_NUM_THREADS": "1",
                "PYTHONHASHSEED": "42",
            }
        )
        result = subprocess.run(  # noqa: S603 -- constant interpreter and owned module
            [sys.executable, "-m", "atlas_api.applied_training"],
            text=True,
            capture_output=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
            env=environment,
        )
        if result.returncode:
            raise TrainingFailedError("applied AI worker failed")
        return AppliedReport.model_validate_json(result.stdout)
    except subprocess.TimeoutExpired as error:
        raise TrainingFailedError("applied AI suite exceeded its 90 second limit") from error
    finally:
        NEURAL_SLOT.release()


def _curve(losses: list[float]) -> list[TrainingPoint]:
    if not losses or not all(math.isfinite(value) and value >= 0 for value in losses):
        raise TrainingFailedError("applied AI produced invalid loss evidence")
    return [TrainingPoint(epoch=index, loss=value) for index, value in enumerate(losses, 1)]


def _vision(torch: Any, nn: Any) -> AppliedTaskEvidence:
    # Bright horizontal/vertical bands model two visual alert signatures. Noise
    # is generated before the split, while no statistic is learned from holdout.
    generator = np.random.default_rng(42)
    images = generator.normal(0, 0.08, size=(160, 1, 8, 8)).astype(np.float32)
    labels = np.arange(160) % 2
    for index, label in enumerate(labels):
        if label:
            images[index, 0, 3:5, :] += 1
        else:
            images[index, 0, :, 3:5] += 1
    order = generator.permutation(len(images))
    train_index, test_index = order[:120], order[120:]
    x_train = torch.tensor(images[train_index])
    y_train = torch.tensor(labels[train_index], dtype=torch.long)
    x_test = torch.tensor(images[test_index])
    y_test = labels[test_index]
    model = nn.Sequential(
        nn.Conv2d(1, 4, 3, padding=1), nn.ReLU(), nn.Flatten(), nn.Linear(4 * 8 * 8, 2)
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=0.02)
    loss_function = nn.CrossEntropyLoss()
    losses: list[float] = []
    for _ in range(20):
        optimizer.zero_grad(set_to_none=True)
        loss = loss_function(model(x_train), y_train)
        loss.backward()
        optimizer.step()
        losses.append(float(loss.detach()))
    model.eval()
    with torch.inference_mode():
        prediction = model(x_test).argmax(dim=1).numpy()
    return AppliedTaskEvidence(
        task="computer_vision",
        architecture="two-layer CNN",
        baseline="majority class",
        metric="accuracy",
        higher_is_better=True,
        model_score=float((prediction == y_test).mean()),
        baseline_score=float(max(np.bincount(y_test)) / len(y_test)),
        training_curve=_curve(losses),
        train_examples=120,
        test_examples=40,
    )


def _time_series(torch: Any, nn: Any) -> AppliedTaskEvidence:
    # Chronological split is an invariant: future request volume never trains the
    # scaler or GRU. A persistence forecast is the honest operational baseline.
    values = np.asarray(
        [100 + index * 0.25 + 14 * math.sin(index * 2 * math.pi / 12) for index in range(150)],
        dtype=np.float32,
    )
    mean, scale = float(values[:110].mean()), float(values[:110].std())
    normalized = (values - mean) / scale
    sequences = np.asarray([normalized[i : i + 12] for i in range(138)], dtype=np.float32)
    targets = normalized[12:]
    x_train = torch.tensor(sequences[:98, :, None])
    y_train = torch.tensor(targets[:98, None])
    x_test = torch.tensor(sequences[98:, :, None])
    y_test = values[110:]

    class ForecastGRU(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.gru = nn.GRU(1, 12, batch_first=True)
            self.output = nn.Linear(12, 1)

        def forward(self, values_in: Any) -> Any:
            encoded, _ = self.gru(values_in)
            return self.output(encoded[:, -1])

    model = ForecastGRU()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.03)
    loss_function = nn.MSELoss()
    losses: list[float] = []
    for _ in range(45):
        optimizer.zero_grad(set_to_none=True)
        loss = loss_function(model(x_train), y_train)
        loss.backward()
        optimizer.step()
        losses.append(float(loss.detach()))
    model.eval()
    with torch.inference_mode():
        prediction = model(x_test).numpy().reshape(-1) * scale + mean
    persistence = values[109:-1]
    return AppliedTaskEvidence(
        task="time_series",
        architecture="GRU forecaster",
        baseline="last-value persistence",
        metric="mae",
        higher_is_better=False,
        model_score=float(np.abs(prediction - y_test).mean()),
        baseline_score=float(np.abs(persistence - y_test).mean()),
        training_curve=_curve(losses),
        train_examples=98,
        test_examples=40,
    )


def _nlp(torch: Any, nn: Any) -> AppliedTaskEvidence:
    tokens = [
        "pad",
        "service",
        "api",
        "worker",
        "healthy",
        "stable",
        "outage",
        "failed",
        "latency",
        "normal",
    ]
    vocabulary = {token: index for index, token in enumerate(tokens)}
    generator = np.random.default_rng(43)
    sequences: list[list[int]] = []
    labels: list[int] = []
    for index in range(160):
        incident = index % 2
        status = "outage" if incident else "healthy"
        qualifier = "failed" if incident else "stable"
        service = "api" if generator.integers(0, 2) else "worker"
        tail = "latency" if generator.integers(0, 2) else "normal"
        sequences.append([vocabulary[x] for x in ["service", service, status, qualifier, tail]])
        labels.append(incident)
    order = generator.permutation(len(sequences))
    train_index, test_index = order[:120], order[120:]
    x_train = torch.tensor(np.asarray(sequences)[train_index], dtype=torch.long)
    y_train = torch.tensor(np.asarray(labels)[train_index], dtype=torch.long)
    x_test = torch.tensor(np.asarray(sequences)[test_index], dtype=torch.long)
    y_test = np.asarray(labels)[test_index]

    class IncidentTransformer(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.embedding = nn.Embedding(len(vocabulary), 12)
            self.position = nn.Parameter(torch.zeros(1, 5, 12))
            layer = nn.TransformerEncoderLayer(
                d_model=12, nhead=2, dim_feedforward=24, dropout=0, batch_first=True
            )
            self.encoder = nn.TransformerEncoder(layer, num_layers=1)
            self.output = nn.Linear(12, 2)

        def forward(self, input_tokens: Any) -> Any:
            encoded = self.encoder(self.embedding(input_tokens) + self.position)
            return self.output(encoded.mean(dim=1))

    model = IncidentTransformer()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.02)
    loss_function = nn.CrossEntropyLoss()
    losses: list[float] = []
    for _ in range(25):
        optimizer.zero_grad(set_to_none=True)
        loss = loss_function(model(x_train), y_train)
        loss.backward()
        optimizer.step()
        losses.append(float(loss.detach()))
    model.eval()
    with torch.inference_mode():
        prediction = model(x_test).argmax(dim=1).numpy()
    return AppliedTaskEvidence(
        task="nlp_attention",
        architecture="Transformer encoder",
        baseline="majority class",
        metric="accuracy",
        higher_is_better=True,
        model_score=float((prediction == y_test).mean()),
        baseline_score=float(max(np.bincount(y_test)) / len(y_test)),
        training_curve=_curve(losses),
        train_examples=120,
        test_examples=40,
    )


def _recommendation(torch: Any, nn: Any) -> AppliedTaskEvidence:
    users, items = 12, 12
    # Each user group prefers one item group. One positive is held out per user;
    # training negatives never include that held-out interaction.
    positives = {
        user: [item for item in range(items) if item % 3 == user % 3] for user in range(users)
    }
    heldout = {user: choices[-1] for user, choices in positives.items()}
    train_pairs: list[tuple[int, int, float]] = []
    for user, choices in positives.items():
        for item in choices[:-1]:
            train_pairs.append((user, item, 1.0))
        for item in range(items):
            if item % 3 != user % 3:
                train_pairs.append((user, item, 0.0))
    user_tensor = torch.tensor([pair[0] for pair in train_pairs])
    item_tensor = torch.tensor([pair[1] for pair in train_pairs])
    labels = torch.tensor([pair[2] for pair in train_pairs], dtype=torch.float32)
    user_embedding, item_embedding = nn.Embedding(users, 6), nn.Embedding(items, 6)
    optimizer = torch.optim.Adam(
        [*user_embedding.parameters(), *item_embedding.parameters()], lr=0.08
    )
    loss_function = nn.BCEWithLogitsLoss()
    losses: list[float] = []
    for _ in range(40):
        optimizer.zero_grad(set_to_none=True)
        score = (user_embedding(user_tensor) * item_embedding(item_tensor)).sum(dim=1)
        loss = loss_function(score, labels)
        loss.backward()
        optimizer.step()
        losses.append(float(loss.detach()))
    hits = 0
    with torch.inference_mode():
        for user in range(users):
            scores = (
                user_embedding(torch.tensor([user])).repeat(items, 1)
                * item_embedding(torch.arange(items))
            ).sum(dim=1)
            seen = set(positives[user][:-1])
            candidates = [
                item for item in scores.argsort(descending=True).tolist() if item not in seen
            ]
            hits += int(heldout[user] in candidates[:3])
    # Equal item popularity makes deterministic item IDs the baseline ranking.
    baseline_hits = sum(int(heldout[user] in [0, 1, 2]) for user in range(users))
    return AppliedTaskEvidence(
        task="recommendation",
        architecture="implicit matrix factorization",
        baseline="global popularity tie-break",
        metric="hit_rate_at_3",
        higher_is_better=True,
        model_score=hits / users,
        baseline_score=baseline_hits / users,
        training_curve=_curve(losses),
        train_examples=len(train_pairs),
        test_examples=users,
    )


def train_applied_suite() -> AppliedReport:
    import torch
    from torch import nn

    torch.set_num_threads(1)
    torch.manual_seed(42)
    torch.use_deterministic_algorithms(True)
    started = time.perf_counter()
    tasks = [
        _vision(torch, nn),
        _time_series(torch, nn),
        _nlp(torch, nn),
        _recommendation(torch, nn),
    ]
    if time.perf_counter() - started > TIMEOUT_SECONDS:
        raise TrainingFailedError("applied AI suite exceeded its internal budget")
    return AppliedReport(
        torch_version=str(torch.__version__),
        tasks=tasks,
        caveats=[
            "Deterministic synthetic fixtures are compatibility checks, not external benchmarks.",
            "Scores describe fixed workloads, not a universal architecture winner.",
            "The forecast split prevents future observations from training the model.",
            "Only JSON metrics and losses persist; executable checkpoints are discarded.",
        ],
    )


if __name__ == "__main__":
    print(json.dumps(train_applied_suite().model_dump(mode="json")))
