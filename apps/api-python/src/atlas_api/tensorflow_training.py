"""TensorFlow/Keras alternative for the identical bounded cost classifier.

Called only in the isolated owned worker. No downloaded models, custom layers,
saved-model deserialization or tenant-controlled graph construction is allowed.
"""

import os
import time

import numpy as np

from atlas_api.machine_learning import ModelEvidence, TrainingPoint, _metrics


def train_keras(
    train: np.ndarray,
    test: np.ndarray,
    labels: np.ndarray,
    holdout: np.ndarray,
    weights: list[np.ndarray],
) -> tuple[ModelEvidence, str, str]:
    """Use GradientTape to expose autodiff without a background tf.data pool."""
    os.environ["KERAS_BACKEND"] = "tensorflow"
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
    import keras  # type: ignore[import-untyped]
    import tensorflow as tf  # type: ignore[import-untyped]

    tf.config.threading.set_intra_op_parallelism_threads(1)
    tf.config.threading.set_inter_op_parallelism_threads(1)
    keras.utils.set_random_seed(42)
    tf.config.experimental.enable_op_determinism()
    model = keras.Sequential(
        [
            keras.layers.Input(shape=(train.shape[1],)),
            keras.layers.Dense(16, activation="relu"),
            keras.layers.Dense(1),
        ]
    )
    # Dense stores [input, output]; PyTorch Linear stores [output, input].
    model.set_weights([weights[0].T, weights[1], weights[2].T, weights[3]])
    optimizer = keras.optimizers.Adam(learning_rate=0.02, epsilon=1e-8, global_clipnorm=5.0)
    loss_function = keras.losses.BinaryCrossentropy(from_logits=True)
    curve: list[TrainingPoint] = []
    started = time.perf_counter_ns()
    for epoch in range(1, 81):
        with tf.GradientTape() as tape:
            loss = loss_function(labels, model(train, training=True))
        gradients = tape.gradient(loss, model.trainable_weights)
        optimizer.apply_gradients(zip(gradients, model.trainable_weights, strict=True))
        curve.append(TrainingPoint(epoch=epoch, loss=float(loss.numpy())))
    elapsed = (time.perf_counter_ns() - started) / 1_000_000
    probability = np.asarray(tf.sigmoid(model(test, training=False)).numpy()).reshape(-1)
    return (
        ModelEvidence(
            model="keras_mlp",
            implementation="tensorflow-keras",
            fit_ms=elapsed,
            metrics=_metrics(holdout, (probability >= 0.5).astype(np.int64), probability),
            training_curve=curve,
        ),
        str(tf.__version__),
        str(keras.__version__),
    )
