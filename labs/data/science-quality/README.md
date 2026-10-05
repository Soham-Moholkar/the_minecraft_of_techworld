# Operational dataset quality and scaling

Install the API data extra: `python -m pip install -e "apps/api-python[data,dev]"`.
Run `python labs/data/science-quality/run.py verify` from the repository root.

`start` writes deterministic CSV and profiles at 100, 1,000, and 5,000 rows;
`test` checks the resulting evidence; `reset` removes only the two generated files.
Each fixture contains one invalid measurement and one normalized duplicate.
No cloud service, network listener, external dataset, or private data is used.

The product implementation lives in `apps/api-python/src/atlas_api/data_science.py`.
Modify cleaning or one aggregation adapter in the IDE and compare the evidence.
The product UI at `/datasets` imports the same schema and persists profiles.

Progression: explicit CSV validation → pandas data frame → NumPy distribution →
SciPy mean interval → independent Polars lazy and DuckDB SQL aggregations → bounded
scaling measurement. Timings exclude ingestion/I/O and use only three warm samples.
These laptop-sized measurements are not production capacity guarantees. Larger
datasets require a separately budgeted batch ingestion path, not a larger HTTP limit.
