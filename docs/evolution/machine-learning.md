# Machine-learning engineering progression

- L0: `machine_learning.py` derives an explicit binary target, excludes its source
  from the feature matrix, and fits a readable NumPy logistic regression with
  train-only scaling and fixed gradient-descent bounds.
- L1: a deterministic split comes first; its training rows alone define the target
  threshold and categorical vocabulary. Scikit-learn pipelines own imputation, scaling, categorical encoding,
  logistic regression, and a shallow decision-tree comparison. All models share a
  deterministic stratified holdout and report classification metrics and confusion
  matrices.
- L2: `/v1/ml/experiments` and `/models` add tenant-scoped saved-dataset training,
  immutable JSON experiment evidence, audit events, input/catalog limits,
  structured logs, Prometheus metrics, response validation, accessible
  interpretation, and regression tests. Executable estimator artifacts are not
  deserialized or retained.
- L3: holdout permutation importance, explicit caveats, a resettable product-code
  lab, and comparable from-scratch/library implementations expose evaluation and
  interpretability tradeoffs.
- L4–L7: planned cross-validation jobs, model registry artifacts, drift monitoring,
  distributed tuning, deployment/canary providers, and governance approvals.

Run `python labs/ml/model-evaluation/run.py verify` for offline evidence and
`pytest apps/api-python/tests/test_machine_learning.py` for API/security coverage.

The pinned scikit-learn 1.9.1 release, its stable Pipeline and permutation
importance documentation, Python 3.12 wheel, BSD-3-Clause license, and maintained
project status were reviewed on 2026-09-15. No third-party source was copied.
