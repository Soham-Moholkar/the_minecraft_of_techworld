# Model workflow, evaluation, and interpretation

Install the API data extra with `python -m pip install -e "apps/api-python[data,dev]"`,
then run `python labs/ml/model-evaluation/run.py verify` from the repository root.

The lab uses the same bounded training function as `/models`. It creates a
deterministic operational dataset, derives a balanced high-cost target, holds out
25%, and compares logistic regression, a shallow decision tree, and a NumPy
logistic baseline. Cost creates the target and is deliberately absent from the
feature matrix. Every model uses the same split.

`start` writes environment and evaluation evidence, `test` verifies comparable
confusion matrices and feature effects, and `reset` removes only that generated
JSON. Fit times describe this machine and workload; the test never declares a
universal speed winner. The derived target demonstrates the workflow and is not a
claim that this model should make production decisions.
