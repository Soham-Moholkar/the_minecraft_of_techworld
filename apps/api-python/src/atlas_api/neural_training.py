"""Bounded CPU training behind a JSON-only process boundary.

Only owned code runs in the child. This isolates tensor RNG/thread settings and
lets the parent kill timed-out work; it is not a sandbox for user-supplied code.
The fixed topology and input limits bound tensor memory without artifact loading.
"""

from __future__ import annotations

import json
import os
import subprocess  # noqa: S404 -- fixed executable/module, never caller-selected
import sys
import threading
import time
from importlib.util import find_spec

import numpy as np

from atlas_api.data_science import Row
from atlas_api.machine_learning import (
    ExperimentReport,
    ModelEvidence,
    TrainingPoint,
    _metrics,
    _scratch_features,
    train_experiment,
)

MAX_ROWS = 2000
MAX_SERVICES = 32
TIMEOUT_SECONDS = 90
NEURAL_SLOT = threading.BoundedSemaphore(1)


class TrainingBusyError(RuntimeError):
    """One child is already using this API worker's CPU allocation."""


class TrainingFailedError(RuntimeError):
    """A child failed; raw stderr can contain tenant data and must not be exposed."""


def validate_neural_rows(rows: list[Row]) -> None:
    if not 20 <= len(rows) <= MAX_ROWS:
        raise ValueError("neural comparison requires 20 to 2000 cleaned rows")
    if len({str(row["service"]) for row in rows}) > MAX_SERVICES:
        raise ValueError("neural comparison supports at most 32 distinct services")


def train_neural_isolated(rows: list[Row], *, include_keras: bool = False) -> ExperimentReport:
    """Return only validated evidence, or fail without persisting a partial run."""
    validate_neural_rows(rows)
    if find_spec("torch") is None:
        raise ImportError("optional CPU PyTorch runtime is not installed")
    if include_keras and (find_spec("tensorflow") is None or find_spec("keras") is None):
        raise ImportError("optional TensorFlow/Keras comparison runtime is not installed")
    if not NEURAL_SLOT.acquire(blocking=False):
        raise TrainingBusyError("neural training is busy; retry after the active run")
    try:
        # Limit BLAS before import in the child. Do not forward API credentials.
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
                # Keras otherwise interprets a missing home directory as the
                # literal relative path `~/.keras`, polluting the repository.
                "KERAS_HOME": os.path.join(
                    environment.get("TEMP", environment.get("TMP", ".")), "atlas-keras"
                ),
            }
        )
        result = subprocess.run(  # noqa: S603 -- constant module and JSON stdin
            [sys.executable, "-m", "atlas_api.neural_training"],
            input=json.dumps({"rows": rows, "include_keras": include_keras}),
            text=True,
            capture_output=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
            env=environment,
        )
        if result.returncode != 0:
            if result.returncode == 2:
                raise ValueError("split needs five training and one holdout example in each class")
            raise TrainingFailedError("neural training worker failed")
        return ExperimentReport.model_validate_json(result.stdout)
    except subprocess.TimeoutExpired as error:
        # subprocess.run kills and reaps the direct child on timeout.
        raise TrainingFailedError("neural training exceeded its 90 second limit") from error
    finally:
        NEURAL_SLOT.release()


def train_neural(rows: list[Row], *, include_keras: bool = False) -> ExperimentReport:
    """Owned worker: fixed 80-epoch MLP compared on Phase 6's identical holdout.

    Holdout loss never chooses the epoch, learning rate or architecture. Training
    curves contain training loss only; evaluation occurs once after the final epoch.
    """
    import pandas as pd  # type: ignore[import-untyped]
    import torch
    from sklearn.model_selection import train_test_split  # type: ignore[import-untyped]
    from torch import nn

    validate_neural_rows(rows)
    torch.set_num_threads(1)
    torch.manual_seed(42)
    torch.use_deterministic_algorithms(True)
    report = train_experiment(rows)
    train_rows, test_rows = train_test_split(pd.DataFrame(rows), test_size=0.25, random_state=42)
    threshold = float(np.median(train_rows["cost"].to_numpy(dtype=np.float64)))
    services = sorted(str(value) for value in train_rows["service"].unique())
    matrices = []
    for frame in (train_rows, test_rows):
        frame = frame.copy()
        frame["day"] = pd.to_datetime(frame["date"], format="%Y-%m-%d").dt.day
        matrices.append(_scratch_features(frame, services))
    train, test = matrices
    # Learn normalization and category vocabulary from training rows only.
    # Unknown holdout services become an all-zero one-hot vector.
    mean, scale = train.mean(axis=0), train.std(axis=0)
    scale[scale == 0] = 1
    x_train = torch.tensor((train - mean) / scale, dtype=torch.float32)
    x_test = torch.tensor((test - mean) / scale, dtype=torch.float32)
    y_train = torch.tensor(
        (train_rows["cost"].to_numpy(dtype=np.float64) > threshold).astype(np.float32)
    ).reshape(-1, 1)
    y_test = (test_rows["cost"].to_numpy(dtype=np.float64) > threshold).astype(np.int64)
    network = nn.Sequential(nn.Linear(train.shape[1], 16), nn.ReLU(), nn.Linear(16, 1))
    # Both backends start with identical weights, inputs, full batches and epochs.
    # Adam numerical details can still differ, so this is not a speed ranking.
    initial_weights = [parameter.detach().numpy().copy() for parameter in network.parameters()]
    optimizer = torch.optim.Adam(network.parameters(), lr=0.02)
    loss_function = nn.BCEWithLogitsLoss()
    curve: list[TrainingPoint] = []
    started = time.perf_counter_ns()
    network.train()
    for epoch in range(1, 81):
        optimizer.zero_grad(set_to_none=True)
        loss = loss_function(network(x_train), y_train)
        if not torch.isfinite(loss):
            raise TrainingFailedError("non-finite neural training loss")
        loss.backward()
        nn.utils.clip_grad_norm_(network.parameters(), max_norm=5.0)
        optimizer.step()
        curve.append(TrainingPoint(epoch=epoch, loss=float(loss.detach())))
    fit_ms = (time.perf_counter_ns() - started) / 1_000_000
    network.eval()
    with torch.inference_mode():
        probability = torch.sigmoid(network(x_test)).numpy().reshape(-1)
    report.models.append(
        ModelEvidence(
            model="pytorch_mlp",
            implementation="pytorch",
            fit_ms=fit_ms,
            metrics=_metrics(y_test, (probability >= 0.5).astype(np.int64), probability),
            training_curve=curve,
        )
    )
    report.torch_version = str(torch.__version__)
    if include_keras:
        from atlas_api.tensorflow_training import train_keras

        evidence, tensorflow_version, keras_version = train_keras(
            x_train.numpy(), x_test.numpy(), y_train.numpy(), y_test, initial_weights
        )
        report.models.append(evidence)
        report.tensorflow_version = tensorflow_version
        report.keras_version = keras_version
        report.caveats.append(
            "Keras shares PyTorch initialization and inputs; optimizer numerics can differ."
        )
    report.caveats.extend(
        [
            "PyTorch MLP: CPU, 16 hidden units, Adam 0.02, 80 fixed epochs; training loss only.",
            "Timings exclude startup; seeds do not guarantee equality across runtime versions.",
        ]
    )
    return report


if __name__ == "__main__":
    try:
        request = json.loads(sys.stdin.read())
        print(
            train_neural(request["rows"], include_keras=request["include_keras"]).model_dump_json()
        )
    except ValueError:
        sys.exit(2)
