# Provider read-pattern benchmark

This offline suite measures the same deterministic tenant/status result through an indexed SQLite query, an in-process document projection, and a precomputed cache hit. It records the workload, environment, warmups, repetitions, p50/p95 latency, throughput, result counts, checksums, and caveats.

The numbers are illustrative—not a database ranking. The implementations serve different responsibilities, and the MongoDB and Redis labs provide the real-provider behavior evidence.

```powershell
.\.venv\Scripts\python labs\databases\provider-benchmarks\run.py verify
```

Use `start` instead of `verify` to retain `.lab-state/benchmark.json`; use `reset` to remove only generated evidence.
