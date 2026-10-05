# Framework and Library Coverage Matrix

> **Product identity override:** Interpret this file through `00_PRODUCT_IDENTITY.md`. ATLAS is the real application; the IDE is the primary place for source modification. Any older “lesson/playground” wording means engineering documentation, operational tooling, reference modules, or controlled test environments—not the central product model.


This file prevents “broad coverage” from being interpreted too narrowly.

ATLAS should cover the following ecosystems through a mixture of:
- deep first-class modules,
- comparison labs,
- reference pages,
- smaller examples.

Do not install every item into the platform core. Many belong in isolated labs.
Before adopting a dependency, verify current maintenance status, official docs, license and security posture.

# 1. Python ecosystem

## Core development
- CPython
- uv / pip / virtualenv concepts
- Poetry/pip-tools concepts
- Ruff
- Black concepts
- mypy / Pyright concepts
- pre-commit
- Pydantic
- dataclasses
- attrs concepts

## CLI / terminal / developer tools
- argparse
- Click
- Typer
- Rich
- Textual concepts

## HTTP/networking
- requests
- httpx
- aiohttp
- websockets
- urllib standard library

## Web/backend
- FastAPI
- Starlette
- Flask
- Django
- Django REST Framework
- Litestar concepts if current/relevant
- Uvicorn
- Gunicorn concepts

## Database/data access
- SQLAlchemy
- Alembic
- psycopg
- asyncpg
- Django ORM
- SQLModel concepts
- PyMongo
- redis-py

## Background work
- Celery
- RQ
- Dramatiq concepts
- APScheduler
- asyncio task patterns

## Serialization/config
- json
- csv
- pickle safety concepts
- PyYAML
- TOML
- python-dotenv concepts
- settings management

## Testing
- pytest
- unittest
- Hypothesis
- pytest-asyncio
- coverage.py
- tox/nox concepts
- Testcontainers Python

## Performance
- timeit
- cProfile
- profile
- tracemalloc
- py-spy concepts
- line/memory profiling concepts

# 2. Frontend / React ecosystem

## Foundation
- React
- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- Base UI
- Radix UI compatibility
- React Aria concepts

## State
Teach patterns before libraries.
Representative libraries:
- Zustand
- Redux Toolkit
- Jotai
- XState/state-machine concepts
- React Context/useReducer where appropriate

## Server state/data
- TanStack Query
- SWR comparison
- TanStack Table
- TanStack Virtual

## Forms/validation
- React Hook Form
- Zod
- Valibot concepts where useful

## Routing
- Next.js App Router
- React Router
- TanStack Router comparison where useful

## UI utilities
- Lucide icons
- Floating UI concepts
- cmdk/command-menu concepts
- date-fns
- drag-and-drop library selected from a maintained ecosystem
- resizable/split-pane utilities
- virtualization

## Motion
- Motion/Framer Motion ecosystem
- CSS transitions/animations
- reduced-motion accessibility
- Web Animations API concepts

## Editors/code
- Monaco Editor
- CodeMirror comparison
- Shiki syntax highlighting
- diff rendering
- terminal emulation such as xterm.js where suitable

## Graphs/diagrams
- React Flow / XYFlow
- Mermaid rendering
- D3 for custom visualization concepts
- Cytoscape.js concepts for graph/network views

## Charts
Use more than one when justified:
- shadcn Chart composition
- Recharts
- Plotly
- ECharts concepts
- D3 for lower-level teaching

## Rich content
- MDX
- Markdown
- math rendering
- syntax highlighting
- diagrams

## AI UI
- current shadcn chat primitives
- Vercel AI SDK/UI patterns where appropriate
- AI Elements where useful
- custom ATLAS agent/tool/eval components

# 3. Backend JavaScript / TypeScript

- Node.js
- Express
- Fastify
- NestJS
- Hono concepts where relevant
- tRPC concepts
- GraphQL server ecosystem
- Apollo concepts
- gRPC JS
- Socket.IO vs native WebSocket comparison
- Prisma concepts
- Drizzle ORM concepts
- TypeORM concepts
- Knex concepts
- BullMQ
- node-postgres
- Redis clients
- OpenTelemetry JS
- Pino/Winston logging concepts
- Vitest/Jest
- Supertest
- Playwright

# 4. Java ecosystem

- Java language/JDK
- Maven
- Gradle concepts
- Spring Boot
- Spring Web
- Spring Security
- Spring Data
- JPA
- Hibernate
- JUnit
- Mockito
- Testcontainers
- Micrometer
- OpenTelemetry Java concepts
- Kafka clients/Spring Kafka
- gRPC Java

# 5. Go ecosystem

Use the standard library heavily.
Also teach representative:
- net/http
- chi/gin/fiber comparison where useful
- sql/database drivers
- pgx
- Cobra concepts
- Zap/slog concepts
- testing/benchmarks
- OpenTelemetry Go

# 6. Rust ecosystem

- Cargo
- Tokio
- Axum/Actix comparison concepts
- Serde
- SQLx/Diesel concepts
- tracing
- Criterion benchmarks
- testing
- FFI/interoperability examples

# 7. Data science stack

## Core
- NumPy
- pandas
- Polars
- SciPy
- DuckDB
- PyArrow
- Dask

## Statistics
- statsmodels
- SciPy stats
- probabilistic programming concepts via a maintained library where useful

## Visualization
- Matplotlib
- Seaborn
- Plotly
- Altair
- Bokeh concepts where useful

## EDA/profiling
- custom ATLAS profiler
- ydata-profiling concepts
- missingno concepts
- data quality libraries where maintained

# 8. Classical ML

- scikit-learn
- XGBoost
- LightGBM
- CatBoost
- imbalanced-learn
- Optuna
- SHAP
- model interpretation/evaluation libraries as appropriate

# 9. Deep learning

- PyTorch
- torchvision/torchaudio concepts
- TensorFlow
- Keras
- JAX
- Flax concepts
- Lightning concepts
- ONNX
- ONNX Runtime

# 10. NLP / LLM / GenAI

## Hugging Face ecosystem
- Transformers
- Datasets
- Tokenizers
- Accelerate
- PEFT
- Sentence Transformers
- Safetensors concepts

## Serving/local inference
Teach multiple approaches:
- Ollama
- llama.cpp concepts
- vLLM
- Hugging Face inference patterns
- OpenAI-compatible local endpoints

## Retrieval
- FAISS
- vector database clients
- BM25/search-engine retrieval
- hybrid search
- reranking models

## LLM application frameworks
Cover foundations first, then representative current frameworks:
- LangChain
- LangGraph
- LlamaIndex
- DSPy
- AutoGen-style ecosystem
- CrewAI-style ecosystem
- PydanticAI-style typed agent patterns where current/relevant

Do not let framework abstractions hide tool/state/retry/security fundamentals.

## Evaluation/observability
Representative concepts/tools:
- LangSmith-style tracing/evals
- MLflow GenAI/eval capabilities where appropriate
- OpenTelemetry-based tracing
- custom ATLAS eval runner
- RAG evaluation libraries if current and maintainable

# 11. MLOps / data lifecycle

- MLflow
- DVC
- Optuna
- ONNX
- model registries
- feature-store concepts
- Feast concepts
- BentoML concepts
- KServe concepts
- Seldon concepts if current/relevant
- Ray concepts
- distributed training/serving concepts

# 12. Data engineering ecosystem

## Apache priority
- Spark / PySpark
- Kafka
- Flink
- Airflow
- Beam
- Hadoop
- Hive
- HBase
- Cassandra
- Iceberg
- Arrow
- Parquet
- Avro
- ORC
- Superset
- NiFi
- Pulsar
- Pinot
- Druid
- Calcite
- Lucene
- Solr

## Other important open tools/concepts
- dbt
- Dagster
- Prefect
- Airbyte concepts
- Debezium
- Great Expectations
- OpenLineage
- Marquez concepts
- lakeFS concepts
- Delta Lake concepts
- Trino
- Presto concepts

# 13. Databases

## Relational
- PostgreSQL
- MySQL/MariaDB
- SQLite

## NoSQL/cache
- MongoDB
- Redis
- Cassandra

## Analytical
- DuckDB
- ClickHouse

## Search
- Elasticsearch
- OpenSearch
- Lucene/Solr concepts

## Graph
- Neo4j
- graph query/model concepts

## Vector
Compare representative maintained options, including:
- PostgreSQL vector-extension approach
- FAISS local indexing
- Qdrant-style vector service
- Milvus-style distributed vector database
- Weaviate-style system concepts

Verify current licenses/maintenance before integration.

## Time series
Teach:
- PostgreSQL-based approaches
- Prometheus time-series model
- representative specialized time-series DB concepts.

# 14. Messaging / queues / workflows

- Kafka
- RabbitMQ
- Redis Streams
- NATS concepts
- Apache Pulsar
- cloud queue/pub-sub equivalents
- Celery/BullMQ
- durable workflow concepts
- Temporal-style workflow concepts where appropriate

# 15. DevOps and platform engineering

## Containers/orchestration
- Docker
- Docker Compose
- Kubernetes
- Helm
- Kustomize concepts

## IaC/config
- Terraform
- OpenTofu
- Ansible
- Pulumi concepts

## CI/CD
- GitHub Actions
- Jenkins
- GitLab CI concepts
- Argo CD
- Flux
- Tekton concepts

## Proxies/network edge
- NGINX
- Envoy
- Traefik
- Caddy concepts
- HAProxy concepts

## Service mesh
- Istio
- Linkerd concepts

## Secrets/config/service discovery
- Vault
- Consul
- SOPS concepts
- Sealed Secrets concepts
- External Secrets concepts

# 16. Observability

- OpenTelemetry
- Prometheus
- Grafana
- Loki
- Tempo
- Jaeger
- Alertmanager
- structured logging
- eBPF observability concepts
- OpenSearch/ELK-style logging concepts

# 17. Security tooling

Representative open/free tooling:
- OWASP ZAP
- Semgrep
- Bandit
- Trivy
- Grype
- Syft
- Gitleaks
- dependency audit tools
- npm audit concepts
- pip audit concepts
- container/IaC policy scanners
- Falco concepts
- OPA
- Gatekeeper
- Kyverno
- security headers/CSP tooling
- TLS inspection tools for local labs
- Wireshark/tcpdump concepts for authorized local traffic

# 18. Testing ecosystem

- pytest
- unittest
- Hypothesis
- Vitest
- Jest
- React Testing Library
- Playwright
- Cypress
- JUnit
- Mockito
- Testcontainers
- Pact/contract-testing concepts
- k6
- Locust
- Apache JMeter
- mutation testing tools per language
- fuzzing tools per language

# 19. API / schema / contracts

- OpenAPI
- JSON Schema
- GraphQL
- Protocol Buffers
- gRPC
- AsyncAPI concepts for events
- Avro schemas
- schema evolution
- code generation
- contract testing.

# 20. Rules for “everything”

The target is broad mastery, not dependency hoarding.

For a large ecosystem:
1. create a domain index,
2. teach core concepts without framework dependence,
3. choose first-class libraries for deep labs,
4. add comparison labs for major alternatives,
5. create searchable reference coverage for public APIs/commands,
6. keep niche/legacy frameworks as concise reference modules unless they teach an important idea.

This is how ATLAS can approach “everything under the sky” while remaining maintainable.