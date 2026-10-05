# ATLAS-ML-P06 — Model experiment and evaluation vertical

Status: complete; 20/20 local quality gates and packaged workflow verified 2026-09-16

Outcome: tenant owners train three comparable classifiers from saved operational
datasets. The persisted report includes deterministic split evidence, accuracy,
balanced accuracy, precision, recall, F1, ROC AUC, confusion matrices, scikit-learn
version, fit duration, permutation effects, and limitations. `/models` exposes the
workflow, history, comparison, interpretation, loading/error/empty states, and a
responsive layout.

Security: fixed product-owned target/features and algorithms; no caller code or
hyperparameters; 5,000-row and 100-experiment bounds; tenant predicates; owner-only
training; atomic audit evidence; no executable estimator serialization.

Tests: `apps/api-python/tests/test_machine_learning.py`,
`apps/web/src/components/machine-learning-workspace.test.tsx`, and
`labs/ml/model-evaluation/run.py verify`.
