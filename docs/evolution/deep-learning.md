# Deep learning progression

- L0: tensor layers, autodiff, loss and fixed optimizer loop in `neural_training.py`.
- L1: tenant dataset selection and persisted comparison at `/models`.
- L2: training-only preprocessing, deterministic regression, process timeout,
  bounded admission, audit, metrics and accessible loss evidence.
- L3: TensorFlow/Keras adapter with identical initial weights and shared holdout.
- L4 planned: durable training jobs, cancellation, signed artifacts and serving.
- L5 planned: GPU batching, resource scheduling and distributed training.
- L6 planned: model approval, drift monitoring and recovery SLOs.
- L7 planned: compiler/export and alternative architecture comparisons.

Phase 7 is complete at the bounded product-integration scope. The applied suite
uses actual image tensors, chronological sequences, token sequences and explicit
user/item interactions rather than relabeling tabular vectors. Public datasets,
durable jobs and production serving remain later progression rather than Phase 7
acceptance blockers.

Inspect `docs/adr/0007-isolated-neural-comparison.md` for invariants and limitations.
Run `python labs/deep-learning/framework-comparison/run.py verify` with the data
and frameworks extras installed. Advance work item ATLAS-DL-P07 next.
