# Dataset engineering progression

- L0: `clean_csv` and `generate_sample` in `apps/api-python/src/atlas_api/data_science.py`
  expose explicit schema, bounds, finite values, normalized duplicates and deterministic data.
- L1: `dataset_routes.py`, `models.py`, migration `20260914_0003`, and `/datasets`
  connect import, analysis, storage, catalog browsing, and reloading saved profiles.
- L2: tenant predicates, owner-only imports, typed API/BFF validation, byte/row limits,
  durable audit, logs, metrics, generic provider errors, tests, and source checksums.
- L3: Polars lazy aggregation and in-memory DuckDB provide independently verified
  alternatives to pandas; NumPy/SciPy quantify distributions and uncertainty. A
  three-scale lab records measured timings with strict result parity.
- L4–L7: planned batch jobs, columnar/object storage, distributed scaling, retention,
  drift alerts, and alternate execution providers. These are not marked implemented.

NumPy and SciPy currently reach L2; pandas, Polars and DuckDB reach L3 for this
bounded workload. This is coverage of useful integrations, not ecosystem completion.

Run `python labs/data/science-quality/run.py verify` for the reproducible local
exercise, and `pytest apps/api-python/tests/test_datasets.py` for API/security tests.

Official documentation reviewed before adopting the pinned stable versions:

- https://numpy.org/doc/stable/ — NumPy 2.5.3; BSD-family and bundled permissive notices.
- https://pandas.pydata.org/docs/ — pandas 3.0.5; BSD-3-Clause.
- https://docs.pola.rs/ — Polars 1.44.2; MIT.
- https://docs.scipy.org/doc/scipy/ — SciPy 1.18.1; BSD-3-Clause.
- https://duckdb.org/docs/stable/clients/python/overview — DuckDB 1.5.5; MIT.

PyPI version metadata reported no advisories for those exact versions on 2026-09-14;
this is not a substitute for ongoing full dependency vulnerability scans. Packages
are installed normally; no third-party source was copied into ATLAS.
