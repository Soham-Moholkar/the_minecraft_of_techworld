# Page and Route Inventory

> **Product identity override:** Interpret this file through `00_PRODUCT_IDENTITY.md`. ATLAS is the real application; the IDE is the primary place for source modification. Any older “lesson/playground” wording means engineering documentation, operational tooling, reference modules, or controlled test environments—not the central product model.


This file defines the desired breadth. The exact routes may evolve, but the information architecture must support them.

## Core

```text
/
dashboard
search
activity
bookmarks
notes
progress
settings
services
labs
lab/[id]
benchmarks
benchmark/[id]
projects
project/[id]
datasets
dataset/[id]
glossary
references
```

## Programming

```text
learn/python
learn/python/fundamentals
learn/python/functions
learn/python/oop
learn/python/typing
learn/python/iterators-generators
learn/python/decorators
learn/python/context-managers
learn/python/asyncio
learn/python/threading
learn/python/multiprocessing
learn/python/networking
learn/python/files
learn/python/testing
learn/python/profiling
learn/python/packaging
learn/python/stdlib

learn/javascript
learn/typescript
learn/java
learn/go
learn/rust
learn/c
learn/cpp
```

Each language should fan out into dozens of topic pages driven by metadata.

## Web

```text
web/html
web/css
web/browser
web/javascript
web/typescript
web/react
web/nextjs
web/vue
web/angular
web/svelte
web/accessibility
web/performance
web/forms
web/state
web/server-state
web/websockets
web/security
web/testing
```

## Backend

```text
backend/http
backend/rest
backend/graphql
backend/grpc
backend/websockets
backend/sse
backend/fastapi
backend/flask
backend/django
backend/node
backend/express
backend/fastify
backend/nest
backend/spring
backend/auth
backend/caching
backend/queues
backend/background-jobs
backend/rate-limiting
backend/files
backend/resilience
```

## Databases

```text
databases/dbms
databases/sql
databases/postgresql
databases/mysql
databases/sqlite
databases/mongodb
databases/redis
databases/cassandra
databases/neo4j
databases/search
databases/clickhouse
databases/duckdb
databases/vector
databases/time-series

databases/transactions
databases/mvcc
databases/isolation
databases/indexes
databases/query-plans
databases/joins
databases/locking
databases/wal
databases/replication
databases/partitioning
databases/sharding
databases/backup-recovery
databases/security
databases/performance
```

## Data science

```text
data
data/numpy
data/pandas
data/polars
data/scipy
data/duckdb
data/pyarrow
data/eda
data/statistics
data/visualization
data/cleaning
data/feature-engineering
data/quality
data/large-scale
```

## Machine learning

```text
ml
ml/regression
ml/classification
ml/trees
ml/ensembles
ml/svm
ml/clustering
ml/dimensionality-reduction
ml/anomaly-detection
ml/model-selection
ml/metrics
ml/interpretability
ml/pipelines
```

## Deep learning and applied AI

```text
deep-learning
deep-learning/pytorch
deep-learning/tensorflow
deep-learning/jax
deep-learning/optimization
deep-learning/cnn
deep-learning/rnn
deep-learning/attention
deep-learning/transformers

ai/nlp
ai/computer-vision
ai/time-series
ai/recommendation
ai/reinforcement-learning
```

## LLM and agent engineering

```text
ai-engineering
ai-engineering/llm
ai-engineering/tokenization
ai-engineering/embeddings
ai-engineering/rag
ai-engineering/vector-search
ai-engineering/reranking
ai-engineering/structured-output
ai-engineering/tool-calling
ai-engineering/evals
ai-engineering/observability
ai-engineering/fine-tuning
ai-engineering/quantization
ai-engineering/local-models

agents
agents/fundamentals
agents/workflows
agents/langgraph
agents/multi-agent
agents/memory
agents/tools
agents/human-approval
agents/mcp
agents/security
agents/evaluation
```

## Data engineering and Apache

```text
data-engineering
data-engineering/etl
data-engineering/elt
data-engineering/cdc
data-engineering/batch
data-engineering/streaming
data-engineering/orchestration
data-engineering/lineage
data-engineering/lake
data-engineering/lakehouse
data-engineering/warehouse

apache
apache/spark
apache/kafka
apache/flink
apache/airflow
apache/beam
apache/hadoop
apache/hive
apache/hbase
apache/cassandra
apache/iceberg
apache/arrow
apache/parquet
apache/avro
apache/orc
apache/superset
apache/nifi
apache/pulsar
apache/pinot
apache/druid
apache/calcite
apache/lucene
apache/solr
apache/jmeter
```

## DevOps/cloud

```text
devops
devops/linux
devops/shell
devops/git
devops/github
devops/docker
devops/compose
devops/kubernetes
devops/helm
devops/terraform
devops/ansible
devops/cicd
devops/release
devops/config
devops/secrets

cloud
cloud/aws
cloud/azure
cloud/gcp
cloud/identity
cloud/network
cloud/compute
cloud/containers
cloud/serverless
cloud/storage
cloud/databases
cloud/events
cloud/observability
cloud/security
cloud/cost
```

## Networking

```text
networking
networking/ip
networking/subnetting
networking/tcp
networking/udp
networking/dns
networking/http
networking/tls
networking/sockets
networking/proxy
networking/load-balancing
networking/cdn
networking/firewalls
networking/vpn
networking/packet-analysis
```

## Security

```text
security
security/fundamentals
security/threat-modeling
security/cryptography
security/identity
security/web
security/api
security/database
security/network
security/cloud
security/container
security/kubernetes
security/supply-chain
security/devsecops
security/detection
security/incident-response
security/ai
security/labs
security/findings
```

## Testing

```text
testing
testing/unit
testing/integration
testing/component
testing/api
testing/database
testing/contract
testing/e2e
testing/accessibility
testing/property-based
testing/fuzz
testing/mutation
testing/performance
testing/load
testing/stress
testing/spike
testing/soak
testing/chaos
testing/security
```

## Observability/SRE

```text
observability
observability/logs
observability/metrics
observability/traces
observability/opentelemetry
observability/prometheus
observability/grafana

sre
sre/sli-slo
sre/error-budgets
sre/alerting
sre/incidents
sre/runbooks
sre/postmortems
sre/capacity
sre/chaos
```

## Distributed systems

```text
distributed-systems
distributed-systems/consistency
distributed-systems/cap
distributed-systems/time
distributed-systems/ordering
distributed-systems/replication
distributed-systems/partitioning
distributed-systems/consensus
distributed-systems/leader-election
distributed-systems/idempotency
distributed-systems/retries
distributed-systems/distributed-locks
distributed-systems/backpressure
```

## System design

```text
system-design
system-design/foundations
system-design/calculators
system-design/url-shortener
system-design/pastebin
system-design/rate-limiter
system-design/chat
system-design/social-feed
system-design/ride-hailing
system-design/file-sync
system-design/ecommerce
system-design/payments
system-design/video-streaming
system-design/video-platform
system-design/search
system-design/marketplace
system-design/realtime-collaboration
system-design/analytics
system-design/event-platform
system-design/multi-region-saas
system-design/observability-platform
system-design/llm-serving
system-design/rag-agent-platform
```

## Count philosophy

Do not manually create 700 empty routes.
Build reusable typed page templates and content schemas, then fill them with real content incrementally.