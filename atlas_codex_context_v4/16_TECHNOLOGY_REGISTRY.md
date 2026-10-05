# 16 — Technology Registry Specification

## Purpose

ATLAS needs a machine-readable registry so the “everything under the sky” objective is measurable and omissions are visible.

Create:

```text
registry/
├── technologies.yaml
├── ecosystems/
│   ├── python.yaml
│   ├── node-typescript.yaml
│   ├── java.yaml
│   ├── dotnet.yaml
│   ├── go.yaml
│   ├── rust.yaml
│   ├── kotlin.yaml
│   ├── scala.yaml
│   ├── php.yaml
│   ├── ruby.yaml
│   ├── elixir.yaml
│   ├── swift.yaml
│   ├── dart-flutter.yaml
│   └── cpp.yaml
├── categories.yaml
├── products.yaml
├── protocols.yaml
├── databases.yaml
├── apache.yaml
├── cloud-native.yaml
└── generated/
```

## Technology record

```yaml
id: python-sqlalchemy
name: SQLAlchemy
ecosystem: python
domain:
  - backend
  - database
category:
  - orm
  - sql-toolkit

status: first_class
maturity: active

integration:
  kind: real_product
  locations:
    - services/analytics-python
  adapter: null

alternatives:
  - django-orm
  - sqlmodel
  - psycopg

capabilities:
  - orm
  - sql-expression
  - transactions
  - pooling
  - async

tests:
  - unit
  - integration
  - migration

docs:
  official: "..."
  internal: "docs/..."

last_verified: "YYYY-MM-DD"
```

## Status vocabulary

- `core`
- `first_class`
- `alternative`
- `reference`
- `legacy`
- `experimental`
- `planned`
- `blocked`
- `deprecated`
- `removed`

## Maturity vocabulary

- active
- maintenance
- historical
- uncertain

Codex must verify current project status before first integration or major upgrade.

## Ecosystem completeness

Each first-class ecosystem gets coverage entries for at least:

- runtime
- web
- ORM
- low-level data access
- migrations
- validation
- serialization
- authn
- authz
- API
- GraphQL
- gRPC
- WebSocket/realtime
- jobs
- queues
- cache
- scheduling
- CLI
- logging
- metrics
- tracing
- error reporting
- testing
- property/fuzz testing
- security
- linting
- formatting
- static analysis
- packaging
- build
- deployment
- profiling
- cloud/serverless
- file/object storage
- SDKs.

The registry should calculate coverage:

```text
Python             50/50
Node/TypeScript    50/50
Java               46/50
.NET               45/50
Go                 41/50
Rust               39/50
...
```

This is implementation inventory, not a learner score.

## Registry UI

Create an ATLAS developer/admin page showing:

- ecosystem
- category coverage
- technologies
- integration status
- version
- last verification
- owner/module
- dependencies
- alternatives
- deprecation
- missing categories.

Example:

```text
Python Ecosystem

Web
✓ Django       first_class
✓ FastAPI      first_class
✓ Flask        first_class
○ Litestar     alternative/planned
○ Sanic        reference
○ Tornado      reference

ORM/Data Access
✓ SQLAlchemy
✓ Django ORM
✓ SQLModel
✓ psycopg
✓ asyncpg
...
```

This is an engineering inventory, not a course page.

## Discovery and expansion

Periodically Codex should:

1. inspect official ecosystem sources,
2. identify significant missing technologies,
3. classify them,
4. verify maintenance/license/security,
5. decide status,
6. create a realistic integration ticket,
7. implement when prioritized.

## No dependency-hoarding

A registry entry does not require installation in the platform core.

A dependency belongs:
- in its service,
- optional adapter,
- isolated integration,
- or metadata/reference only.

## Legacy

ATLAS should include important legacy/enterprise systems where useful:
- SOAP
- old Java enterprise patterns
- older module systems
- traditional server-rendered stacks
- Hadoop MapReduce
- ZooKeeper coordination
- legacy broker/protocol patterns.

Label them.

## Emerging

Emerging technologies stay behind optional adapters until proven.

## Completeness target

The target is not literally every package in npm/PyPI/Maven Central.

The target is:
- every major engineering category,
- every major technology family,
- significant frameworks/tools within supported ecosystems,
- important legacy systems,
- important emerging systems,
- a registry that exposes omissions and can expand indefinitely.

## Progression fields

Each first-class technology must additionally record:

- maximum defined progression level,
- maximum implemented progression level,
- source paths for each level,
- concepts introduced at each level,
- relevant tests,
- architecture/evolution documentation,
- work items that advance the technology.

Use the canonical progression model from `20_PROGRESSIVE_COMPLEXITY_AND_COMMENTS.md`.

The registry UI must show both:
1. ecosystem-category completeness,
2. progressive-complexity completeness.
