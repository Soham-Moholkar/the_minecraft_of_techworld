# Labs, Datasets, Benchmarks and Experiment Infrastructure

> **Product identity override:** Interpret this file through `00_PRODUCT_IDENTITY.md`. ATLAS is the real application; the IDE is the primary place for source modification. Any older “lesson/playground” wording means engineering documentation, operational tooling, reference modules, or controlled test environments—not the central product model.


## 1. Lab principles

Labs must be:
- reproducible,
- resettable,
- isolated,
- observable,
- small enough to run locally where possible,
- scalable to larger profiles when useful.

## 2. Lab lifecycle

```text
discover
  ↓
read prerequisites
  ↓
start
  ↓
seed
  ↓
observe baseline
  ↓
modify
  ↓
run
  ↓
test
  ↓
benchmark
  ↓
inject fault
  ↓
diagnose
  ↓
fix
  ↓
reset
```

## 3. Dataset catalog

Do not commit giant datasets blindly.

Each dataset needs a manifest:
- id
- name
- description
- source/license
- schema
- row count
- size
- target/label if relevant
- data quality notes
- PII/sensitivity classification
- checksum
- generation/download instructions.

Prefer:
- small checked-in samples,
- deterministic synthetic generators,
- download scripts for openly licensed public datasets,
- clear attribution/license.

## 4. Dataset classes

Create examples for:
- tabular
- time series
- text
- images
- logs/events
- graph
- geospatial
- transactional
- clickstream
- sensor/IoT
- financial synthetic data
- e-commerce synthetic data
- security event synthetic data.

## 5. Dirty-data laboratory

Create controlled datasets containing:
- missing values
- duplicate records
- bad types
- mixed date formats
- impossible ranges
- outliers
- encoding issues
- inconsistent categories
- skew
- leakage columns
- class imbalance
- schema drift.

## 6. Scale profiles

Dataset generators should support:
- 1k
- 10k
- 100k
- 1M
- 10M
- optionally 100M/distributed profile

Use generated data and document resource expectations.

## 7. Benchmark harness

A benchmark definition should record:
- benchmark id
- implementation
- input size
- warmup
- repetitions
- runtime
- hardware info where available
- dependency versions
- configuration
- result metrics
- notes.

## 8. Benchmark visualization

Frontend needs:
- comparison table,
- distribution plot,
- latency percentiles,
- throughput,
- memory,
- CPU,
- data-size scaling,
- configuration diff,
- run history.

## 9. Benchmark caveats

Always explain:
- synthetic workload limitations,
- cache effects,
- warm/cold behavior,
- hardware differences,
- network effects,
- correctness vs performance tradeoffs.

## 10. Suggested benchmark labs

### Python
- list vs generator memory
- loops vs vectorization
- asyncio vs threads vs processes for appropriate workloads
- serialization options

### Dataframes
- pandas vs Polars vs DuckDB
- groupby
- join
- filter
- CSV/Parquet scans

### Databases
- index vs no index
- join strategies
- read cache
- connection pooling
- bulk insert
- partitioning
- analytical queries

### APIs
- JSON REST throughput
- sync vs async server patterns
- REST vs GraphQL/gRPC for carefully scoped workloads

### Streaming
- partitions
- consumer count
- batching
- backpressure

### ML
- algorithm training time
- CPU/GPU
- batch inference
- quantized vs non-quantized model where available

### Infrastructure
- container resource limits
- HPA behavior
- cache on/off
- queue buffering.

## 11. Artifact capture

Every run may produce:
- stdout/stderr
- logs
- metrics
- traces
- test report
- benchmark JSON
- screenshots where useful
- generated plots
- query plans.

Use a common artifact model.

## 12. Reset discipline

Each stateful lab needs:
- reset data,
- remove generated resources,
- stop containers/processes,
- clean temporary credentials,
- verify clean state.

Cloud labs require an explicit teardown path.