# Monorepo Architecture

> **Product identity override:** Interpret this file through `00_PRODUCT_IDENTITY.md`. ATLAS is the real application; the IDE is the primary place for source modification. Any older “lesson/playground” wording means engineering documentation, operational tooling, reference modules, or controlled test environments—not the central product model.


## Goals

The monorepo must:
- support many languages,
- support many independently runnable labs,
- keep the primary product coherent,
- allow optional heavy services,
- make local onboarding possible,
- separate platform infrastructure from educational examples,
- support CI that does not rerun every expensive suite for every change.

## Proposed top-level structure

```text
atlas/
├── apps/
│   ├── web/                         # Next.js ATLAS UI
│   ├── api-python/                  # Primary FastAPI platform API
│   ├── api-node/                    # Node/TS teaching + selected platform services
│   ├── worker/                      # background jobs
│   ├── docs-indexer/                # content/search indexing
│   └── lab-orchestrator/            # starts/stops/resets safe local labs
│
├── packages/
│   ├── ui/                          # shared ATLAS UI system
│   ├── design-tokens/
│   ├── types/
│   ├── schemas/
│   ├── config/
│   ├── auth/
│   ├── telemetry/
│   ├── logger/
│   ├── api-client/
│   ├── content-engine/
│   ├── lab-sdk/
│   ├── benchmark-sdk/
│   ├── test-reporters/
│   ├── security-reporters/
│   └── visualization/
│
├── content/
│   ├── programming/
│   ├── web/
│   ├── databases/
│   ├── data-science/
│   ├── ml/
│   ├── deep-learning/
│   ├── ai-engineering/
│   ├── data-engineering/
│   ├── apache/
│   ├── devops/
│   ├── cloud/
│   ├── networking/
│   ├── security/
│   ├── testing/
│   ├── sre/
│   ├── distributed-systems/
│   └── system-design/
│
├── labs/
│   ├── python/
│   ├── frontend/
│   ├── backend/
│   ├── databases/
│   ├── data-science/
│   ├── ml/
│   ├── ai/
│   ├── data-engineering/
│   ├── apache/
│   ├── devops/
│   ├── cloud/
│   ├── security/
│   ├── networking/
│   └── distributed-systems/
│
├── examples/
│   ├── python/
│   ├── typescript/
│   ├── javascript/
│   ├── java/
│   ├── go/
│   ├── rust/
│   ├── cpp/
│   └── sql/
│
├── datasets/
│   ├── manifests/
│   ├── generators/
│   ├── samples/
│   └── schemas/
│
├── benchmarks/
│   ├── database/
│   ├── dataframes/
│   ├── api/
│   ├── concurrency/
│   ├── messaging/
│   ├── ml/
│   └── infrastructure/
│
├── security/
│   ├── threat-models/
│   ├── policies/
│   ├── scanners/
│   ├── secure-examples/
│   ├── vulnerable-labs/
│   └── incident-scenarios/
│
├── system-design/
│   ├── cases/
│   ├── diagrams/
│   ├── calculators/
│   └── simulations/
│
├── projects/
│   ├── financial-analytics/
│   ├── commerce-platform/
│   ├── telemetry-platform/
│   ├── multi-tenant-saas/
│   ├── ai-knowledge-workbench/
│   └── media-platform/
│
├── infra/
│   ├── docker/
│   ├── compose/
│   ├── kubernetes/
│   ├── helm/
│   ├── terraform/
│   ├── ansible/
│   ├── observability/
│   └── local/
│
├── tests/
│   ├── e2e/
│   ├── contracts/
│   ├── performance/
│   ├── security/
│   └── smoke/
│
├── scripts/
├── tools/
├── docs/
│   ├── adr/
│   ├── architecture/
│   ├── contributing/
│   └── runbooks/
│
├── .github/
│   └── workflows/
├── AGENTS.md
└── README.md
```

## Lab manifest

Every lab should eventually be describable by a manifest.

Example shape:

```yaml
id: postgres-index-basics
title: PostgreSQL Index Lab
domain: databases
runtime: docker
difficulty: intermediate

services:
  - postgres

resources:
  cpu: "1"
  memory: "1Gi"

commands:
  start: "./scripts/start.sh"
  reset: "./scripts/reset.sh"
  test: "./scripts/test.sh"
  benchmark: "./scripts/benchmark.sh"

safety:
  internet_access_required: false
  vulnerable_target: false

artifacts:
  - type: sql
    path: ./queries
  - type: test
    path: ./tests

telemetry:
  logs: true
  metrics: true
  traces: false
```

Build a typed schema and validator for manifests.

## Content metadata

Each content page should expose typed frontmatter:
- id
- slug
- title
- description
- domain
- technology
- level
- prerequisites
- tags
- labs
- related topics
- official references

## Service contracts

Platform services should use explicit OpenAPI/typed contracts.
For educational examples, additionally teach:
- REST
- GraphQL
- gRPC
- WebSockets
- SSE
- event contracts

## Data stores for platform metadata

Start simple:
- PostgreSQL for user/progress/content metadata that needs relational querying.
- Object/filesystem storage for generated artifacts and lab outputs.
- Redis only for valid cache/queue/session use cases.
- Search can begin with a lightweight index and later evolve.

Avoid using a technology merely to “check a box” in the platform core. Extra databases belong in labs unless there is a real platform requirement.

## Optional service profiles

Developer commands should allow profiles such as:
- core
- data
- ai
- observability
- security
- streaming
- full

A contributor should not need to boot Spark, Kafka, multiple vector databases and Kubernetes just to edit a button.

## Heavy labs

Large-data and cluster labs need scaled modes:
- tiny/local
- laptop
- cluster/cloud

Datasets should often be generated deterministically rather than storing giant binaries in Git.

## Architectural decision records

Create ADRs for:
- monorepo tooling,
- content engine,
- auth,
- lab isolation,
- database choices,
- search,
- telemetry,
- AI provider abstraction,
- deployment topology,
- security boundary changes.