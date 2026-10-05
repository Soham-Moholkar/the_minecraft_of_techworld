# ADR 0007: bounded neural comparison over immutable datasets

Accepted 2026-09-16. Phase 7 begins by comparing PyTorch and TensorFlow/Keras
against Phase 6 models in the existing `/models` workflow.

Use a fixed CPU MLP, 16 hidden units, full-batch Adam, 80 epochs and a 90-second
owned child process. The caller selects a suite, never code, model URLs, paths,
epochs or graph configuration. JSON enters and validated metric/curve JSON exits;
weights are never serialized. The child receives no ATLAS credentials. A
nonblocking semaphore admits one neural comparison per API worker; excess work
gets HTTP 429. This is process isolation for trusted code, not a hostile-code
sandbox or durable job queue. Worker count multiplies the concurrency allowance.

PyTorch and Keras share training-only normalization, category vocabulary, initial
weights, architecture and holdout. They use their native Adam implementations;
floating-point and optimizer details can differ. This comparison does not imply
identical convergence or a universal performance winner. Curves show pre-update
training loss, never holdout-guided stopping or hyperparameter selection.

The existing experiment JSON column and tenant/dataset composite foreign key
require no migration. Older reports retain defaults for new optional fields.
Owner authorization precedes computation; quota is checked before training and
again under the existing tenant lock before commit. Audit and metric outcomes
cover success, invalid data, unavailable runtime, busy worker and failed worker.

Limits: 20–2,000 rows, 32 service values, one CPU thread in each tensor runtime.
Timeout kills and reaps the child. There is no durable cancellation, queue or
automatic retry. HTTP disconnect may leave the bounded run finishing; an API
restart can interrupt it. An interrupted comparison stores no partial report.
Signed artifact storage, serving and distributed training are later progression.

Dependencies are optional. CPU PyTorch 2.14.0 uses its official CPU wheel index;
TensorFlow CPU 2.21.0 and Keras 3.15.1 use PyPI. PyTorch is BSD-style licensed,
TensorFlow/Keras Apache-2.0. Reviewed official installation, license and security
policies on 2026-09-16. No upstream source was copied. No model downloads, custom
ops, unsafe model deserialization or telemetry integrations are introduced.

References:
- https://pytorch.org/get-started/locally/
- https://github.com/pytorch/pytorch/blob/main/LICENSE
- https://github.com/pytorch/pytorch/security/policy
- https://www.tensorflow.org/install/pip
- https://github.com/tensorflow/tensorflow/security/policy
- https://keras.io/getting_started/
- https://github.com/keras-team/keras/blob/master/LICENSE
