# 14 — Ecosystem Parity and Completeness Matrix

## Objective

When ATLAS says it supports a language or backend ecosystem, it must not mean “we used one framework once.”

Each first-class ecosystem should cover the equivalent engineering surface:

1. language/runtime
2. package/dependency management
3. project/build tooling
4. configuration
5. web framework(s)
6. API framework(s)
7. routing/middleware
8. validation/schema
9. serialization
10. ORM/data mapper
11. lower-level database driver/query builder
12. migrations
13. authentication
14. authorization
15. sessions/cookies/tokens
16. async/concurrency
17. background jobs
18. queues/messaging
19. scheduling
20. caching
21. WebSockets/realtime
22. GraphQL
23. gRPC/Protobuf
24. CLI
25. logging
26. metrics
27. tracing/OpenTelemetry
28. error reporting
29. testing
30. mocking
31. property/fuzz testing where mature
32. performance benchmarking/profiling
33. security scanning/linting
34. formatting/linting
35. type checking/static analysis
36. documentation/API generation
37. deployment/containerization
38. cloud/serverless integrations
39. SDK/client generation
40. file/object storage integrations
41. email/notifications integrations
42. payments/business integrations where relevant
43. feature flags/config distribution
44. resilience/retry/circuit-breaker patterns
45. dependency injection where idiomatic
46. templating/server-rendered UI where idiomatic
47. RPC/event contracts
48. database transaction patterns
49. Testcontainers/ephemeral integration environments
50. production hardening.

The list is extensible. New categories should be added to the technology registry.

# Python ecosystem — extremely deep coverage

Python must be one of the deepest ecosystems in ATLAS.

## Runtime/language
- CPython
- PyPy concepts
- syntax/runtime internals where useful
- asyncio
- threading
- multiprocessing
- concurrent.futures
- subprocess
- pathlib/files
- sockets/networking
- typing/generics/protocols
- dataclasses
- context managers
- decorators
- generators/iterators

## Package/environment/build
- pip
- venv
- uv
- Poetry concepts
- pip-tools concepts
- pyproject.toml
- setuptools concepts
- wheel/sdist
- locking
- private package indexes concepts

## Web frameworks
Deep:
- Django
- FastAPI
- Flask

Also cover/integrate where current and useful:
- Starlette
- Litestar
- Falcon concepts
- Sanic concepts
- Tornado concepts
- Bottle legacy/minimal concepts

## APIs/contracts
- Django REST Framework
- FastAPI
- Flask API patterns
- GraphQL via maintained Python ecosystem
- gRPC Python
- WebSockets
- SSE
- OpenAPI
- JSON Schema
- Protobuf
- AsyncAPI concepts

## Validation/schema
- Pydantic
- dataclasses
- attrs
- marshmallow concepts
- JSON Schema

## ORM/data access
Deep:
- SQLAlchemy ORM/Core
- Django ORM
- SQLModel concepts

Also:
- psycopg
- asyncpg
- query-builder concepts
- PyMongo
- redis-py
- search clients
- vector DB clients

## Migrations
- Alembic
- Django migrations

## Auth/security
- Django auth
- OAuth/OIDC
- JWT
- password hashing
- sessions
- CSRF/CORS
- security headers
- RBAC/ABAC
- secrets
- cryptography library safe usage

## Background jobs/workflows
- Celery
- RQ
- Dramatiq concepts
- APScheduler
- asyncio workers
- durable workflow clients
- Airflow for data jobs

## Messaging
- Kafka clients
- RabbitMQ/AMQP clients
- Redis Streams
- NATS clients
- Pulsar clients
- cloud pub/sub adapters

## Caching
- Redis
- in-process caching
- HTTP caching
- cachetools concepts

## Testing
- pytest
- unittest
- Hypothesis
- pytest-asyncio
- mocking/fixtures
- coverage.py
- tox/nox
- Testcontainers

## Quality
- Ruff
- Black concepts
- mypy
- Pyright concepts
- Bandit
- pip-audit concepts
- pre-commit

## Observability/performance
- logging
- structlog concepts
- OpenTelemetry
- Prometheus client
- error reporting concepts
- cProfile
- tracemalloc
- py-spy concepts

## Data/AI Python stack
- NumPy
- pandas
- Polars
- SciPy
- DuckDB
- PyArrow
- Dask
- statsmodels
- scikit-learn
- XGBoost
- LightGBM
- CatBoost
- imbalanced-learn
- Optuna
- SHAP
- PyTorch
- TensorFlow/Keras
- JAX
- ONNX/ONNX Runtime
- Transformers
- Datasets
- Tokenizers
- Sentence Transformers
- Accelerate
- PEFT
- MLflow
- LangChain
- LangGraph
- LlamaIndex
- DSPy
- agent-framework comparisons
- local-model clients
- vLLM-style serving clients
- Ray concepts
- PySpark
- Airflow
- Beam
- Flink Python APIs where useful

# Node.js / TypeScript ecosystem — parity with Python backend concerns

## Runtime/tooling
- Node.js
- npm
- pnpm
- Yarn concepts
- package.json
- workspaces
- ESM/CommonJS
- TypeScript
- tsconfig
- monorepo tooling

## Web frameworks
Deep:
- Express
- Fastify
- NestJS

Also:
- Hono
- Koa concepts
- AdonisJS concepts
- native Node HTTP
- serverless/edge handlers

## APIs/contracts
- REST
- OpenAPI
- GraphQL
- Apollo concepts
- GraphQL Yoga concepts
- tRPC
- gRPC
- Protobuf
- WebSockets
- Socket.IO
- SSE
- JSON Schema
- AsyncAPI concepts

## Validation
- Zod
- Valibot concepts
- Joi concepts
- class-validator
- Ajv/JSON Schema

## ORM/data access
Deep:
- Prisma
- Drizzle
- TypeORM

Also:
- Sequelize concepts
- MikroORM concepts
- Knex
- Kysely concepts
- node-postgres
- MySQL clients
- MongoDB driver
- Mongoose
- Redis clients
- search/vector clients

## Migrations
- Prisma migrations
- Drizzle migrations
- TypeORM migrations
- Knex migrations
- raw SQL migrations

## Auth/security
- Passport concepts
- Auth.js-style concepts
- sessions
- JWT
- OAuth/OIDC
- RBAC/ABAC
- CSRF/CORS
- Helmet/security headers
- rate limiting
- dependency/security scanning

## Jobs/queues
- BullMQ
- Agenda concepts
- cron
- worker_threads
- child_process
- broker clients
- durable workflow clients

## Testing
- Vitest
- Jest
- Node test runner
- Supertest
- Playwright
- Cypress
- Testcontainers
- mocking
- property/fuzz concepts

## Quality/observability
- ESLint
- Biome concepts
- Prettier
- strict TypeScript
- dependency audits
- Semgrep
- Pino
- Winston concepts
- OpenTelemetry
- Prometheus clients
- profiler/flamegraphs
- event-loop monitoring

# Java ecosystem

- JVM/JDK
- Maven
- Gradle
- Spring Boot
- Spring MVC
- Spring WebFlux
- Spring Security
- Spring Data
- Jakarta EE concepts
- Quarkus
- Micronaut
- Vert.x concepts
- JPA
- Hibernate
- JDBC
- jOOQ concepts
- MyBatis concepts
- Flyway
- Liquibase
- Spring Kafka
- JMS
- RabbitMQ
- scheduled jobs
- batch processing
- REST
- GraphQL
- gRPC
- WebSocket
- OpenAPI
- JUnit
- Mockito
- AssertJ concepts
- Testcontainers
- JMH
- Micrometer
- OpenTelemetry
- SLF4J/Logback
- OAuth/OIDC/JWT

# .NET / C# ecosystem

- .NET runtime
- C#
- NuGet
- dotnet CLI
- MSBuild concepts
- ASP.NET Core
- Minimal APIs
- MVC
- Razor Pages concepts
- Blazor concepts
- Entity Framework Core
- Dapper
- ADO.NET concepts
- EF migrations
- REST/OpenAPI
- GraphQL via maintained ecosystem
- gRPC
- SignalR
- WebSockets
- BackgroundService
- Hangfire concepts
- MassTransit concepts
- xUnit
- NUnit/MSTest concepts
- Moq/NSubstitute concepts
- Testcontainers
- BenchmarkDotNet
- ASP.NET Identity
- OAuth/OIDC/JWT
- policy authorization
- OpenTelemetry
- Serilog concepts

# Go ecosystem

- Go modules/toolchain
- net/http
- Chi
- Gin
- Fiber
- Echo concepts
- database/sql
- pgx
- GORM
- sqlc
- Ent concepts
- migrations
- REST/OpenAPI
- gRPC/Protobuf
- WebSockets
- GraphQL ecosystem
- goroutines/channels
- Kafka/NATS/RabbitMQ/Redis clients
- testing
- testify concepts
- fuzzing
- benchmarks
- race detector
- pprof
- staticcheck
- golangci-lint concepts
- Testcontainers
- OpenTelemetry
- slog/zap concepts
- OAuth/JWT

# Rust ecosystem

- Cargo
- Tokio
- Axum
- Actix Web
- Rocket/Warp concepts
- SQLx
- Diesel
- SeaORM concepts
- REST
- gRPC/Tonic
- WebSockets
- GraphQL ecosystem
- Protobuf
- Kafka/NATS/RabbitMQ/Redis clients
- cargo test
- property testing
- fuzzing
- Criterion
- Clippy
- rustfmt
- cargo audit concepts
- tracing
- OpenTelemetry
- OAuth/JWT integration

# Kotlin ecosystem

Server:
- Kotlin language
- coroutines
- Ktor
- Spring Boot Kotlin
- Exposed ORM concepts
- JPA/Hibernate
- serialization
- Gradle
- testing
- gRPC
- Kafka
- OpenTelemetry

Android:
- Jetpack Compose
- Room
- HTTP clients
- coroutines/Flow
- WorkManager
- secure storage
- notifications
- offline sync

# Scala ecosystem

- Scala
- sbt
- Cats/ZIO concepts
- Akka/Pekko actor concepts
- Play concepts
- Spark
- Kafka
- functional programming
- concurrency
- testing
- observability

# PHP ecosystem

- PHP
- Composer
- Laravel
- Symfony
- Eloquent
- Doctrine ORM
- queues/jobs
- events
- validation
- auth
- caching
- PHPUnit
- Pest concepts
- API development
- observability

# Ruby ecosystem

- Ruby
- Bundler
- Rails
- Active Record
- Rack
- Sidekiq
- background jobs
- Action Cable/WebSockets
- RSpec
- Minitest
- RuboCop
- auth/security
- observability

# Elixir ecosystem

- BEAM/OTP
- Mix
- Phoenix
- LiveView
- Ecto
- supervision trees
- GenServer
- channels
- Oban concepts
- ExUnit
- telemetry
- distributed Elixir

# Swift ecosystem

- Swift
- SwiftUI
- UIKit interoperability
- structured concurrency
- Combine concepts
- URLSession
- Codable
- Core Data/SwiftData concepts
- Keychain
- notifications
- background tasks
- deep links
- testing
- app architecture
- secure storage
- offline sync
- Vapor concepts if useful

# Dart/Flutter ecosystem

- Dart
- Flutter
- state management comparisons
- routing
- HTTP
- serialization
- local persistence
- background work
- secure storage
- notifications
- testing
- desktop/mobile/web deployment

# C/C++ systems ecosystem

- C/C++
- CMake
- Meson concepts
- memory
- threads
- sockets
- OpenSSL concepts
- gRPC C++
- Boost concepts
- database clients
- SIMD
- profiling
- sanitizers
- fuzzing
- GoogleTest/Catch2 concepts
- shared/static libraries
- FFI with Python/Rust/Node

# Cross-ecosystem equivalence

ATLAS documentation/registry should compare the same concern across ecosystems.

Example ORM/data access:

| Concern | Python | Node/TS | Java | .NET | Go | Rust | PHP | Ruby |
|---|---|---|---|---|---|---|---|---|
| High-level ORM | SQLAlchemy/Django ORM | Prisma/Drizzle/TypeORM | Hibernate/JPA | EF Core | GORM/Ent | Diesel/SeaORM | Eloquent/Doctrine | Active Record |
| Lower-level SQL | psycopg/asyncpg | node-postgres/Kysely/Knex | JDBC/jOOQ | ADO.NET/Dapper | database/sql/pgx/sqlc | SQLx | PDO/DBAL | adapters/raw SQL |
| Migration | Alembic/Django | Prisma/Drizzle/TypeORM | Flyway/Liquibase | EF migrations | migration tools | sqlx/diesel migration | Laravel/Doctrine | Rails migrations |

Create equivalent matrices for:
- web frameworks
- validation
- authentication
- authorization
- jobs
- messaging
- caching
- GraphQL
- gRPC
- testing
- observability
- configuration
- CLI
- security
- dependency management
- profiling
- migrations
- realtime
- cloud deployment.

## Rule

When Codex promotes a language to first-class status, it must populate all ecosystem-parity categories instead of adding only a hello-world service.
