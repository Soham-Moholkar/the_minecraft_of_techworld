# 15 — Expanded Product Surface and Technology Scope

This file adds broad multidisciplinary scope so technologies are exercised by real ATLAS product features.

## Native mobile
- iOS Swift/SwiftUI
- Android Kotlin/Jetpack Compose
- React Native comparison
- Flutter comparison
- auth
- push notifications
- deep links
- secure storage
- offline sync
- background work

## Desktop
- Tauri-style desktop client
- Electron comparison
- filesystem/process integration
- secure credentials
- auto-update concepts
- packaging

## CLI/TUI
Create a real `atlas` CLI:
- login
- organizations/projects
- services
- deploy
- logs
- datasets
- pipelines
- agents
- models
- migrations
- incidents
- security findings
- configuration

Add a TUI for operations where useful.

## Developer platform
- public REST
- GraphQL
- gRPC
- WebSockets/SSE
- webhooks
- API keys
- OAuth apps
- SDK generation
- Python SDK
- TypeScript SDK
- Java SDK
- Go SDK
- C# SDK
- API explorer
- versioning/deprecation

## Real-time collaboration
- presence
- cursors
- shared documents
- optimistic UI
- CRDT/OT concepts
- conflict resolution
- offline reconciliation

## Enterprise IAM
- organizations/tenants
- teams
- RBAC
- ABAC
- OAuth2/OIDC
- SSO
- MFA
- passkeys/WebAuthn
- service accounts
- API keys
- SCIM concepts
- temporary credentials
- session/device management
- access reviews

## Multi-tenancy
Compare:
- shared tables
- row-level security
- schema-per-tenant
- database-per-tenant
- quotas
- isolation
- encryption boundaries
- noisy-neighbor mitigation

## Billing/metering/FinOps
- plans
- subscriptions
- invoices
- payment simulation
- usage events
- AI token usage
- storage/network/compute usage
- quotas
- credits
- cost attribution
- budgets
- alerts

## Search platform
- PostgreSQL FTS
- OpenSearch/Elasticsearch
- Lucene/Solr concepts
- autocomplete
- fuzzy search
- facets
- filters
- ranking
- semantic/vector search
- hybrid search
- reranking

## File/document platform
- multipart uploads
- resumable uploads
- object storage
- metadata
- versioning
- previews/thumbnails
- malware scanning pipeline
- document parsing
- PDF/Office processing
- OCR
- deduplication
- retention
- signed URLs

## Media engineering
- image processing
- audio/video upload
- transcoding
- thumbnails
- metadata
- adaptive streaming
- codecs
- CDN
- queues
- GPU workers

## Geospatial
- PostGIS
- spatial indexes
- geofencing
- heatmaps
- routing concepts
- geospatial datasets
- maps/vector tiles
- fleet/resource tracking

## Time-series
- Prometheus model
- time-series DB patterns
- high-cardinality
- retention
- rollups
- downsampling
- alerting
- forecasting
- anomaly detection

## Event architecture
Support:
- Kafka
- Pulsar
- RabbitMQ
- NATS
- Redis Streams
- cloud pub/sub adapters
- event schemas
- replay
- DLQ
- ordering
- idempotency
- retries

## Durable workflows
- application workflows
- data workflows
- long-running jobs
- retries
- compensation/sagas
- checkpoints
- schedules
- human approval
- versioning

## Modern data platform
- batch
- streaming
- CDC
- ETL/ELT
- lake
- warehouse
- lakehouse
- federated query
- Iceberg
- Delta/Hudi concepts
- streaming-storage concepts
- catalogs
- lineage
- governance
- quality
- data contracts

## Data governance
- ownership
- catalog
- lineage
- sensitivity classification
- PII detection
- masking
- anonymization
- retention
- schema evolution
- access policies
- provenance
- quality

## Data formats/interchange
- JSON
- CSV
- XML
- YAML
- Avro
- Protobuf
- Parquet
- ORC
- Arrow
- Iceberg
- Delta/Hudi concepts
- compression/encoding
- zero-copy

## Multimodal AI
- text
- images
- audio
- video
- documents
- speech-to-text
- text-to-speech
- vision
- OCR
- multimodal embeddings
- multimodal retrieval
- multimodal agents

## AI infrastructure
- model gateway
- provider routing/failover
- local/hosted models
- GPU scheduling
- inference servers
- batching
- KV-cache concepts
- quantization
- LoRA/adapters
- distributed inference/training concepts
- model registry
- prompt registry
- AI observability
- eval gates

## AI governance/security
- model/prompt versions
- approvals
- evaluation gates
- audit
- data policies
- red-team scenarios
- prompt injection defense
- tool scopes
- tenant isolation
- provenance

## Internal developer platform
- service catalog
- ownership
- golden paths
- environment provisioning
- deployment status
- API catalog
- docs
- dependency health
- scorecards
- runbooks

## GitOps
- desired state
- PR-based changes
- Argo CD concepts
- Flux concepts
- drift/reconciliation
- progressive delivery
- rollback

## Advanced networking/service mesh
- NGINX
- Envoy
- HAProxy concepts
- Traefik/Caddy concepts
- service discovery
- retries
- circuit breaking
- traffic splitting
- mTLS
- Istio
- Linkerd concepts
- ingress/egress
- multi-cluster concepts

## Serverless/edge
- functions
- event triggers
- edge workers
- CDN compute
- cold starts
- edge caching
- geographic execution
- security/observability

## WebAssembly
- browser WASM
- WASI/server WASM concepts
- plugin sandboxing
- Rust/C++ to WASM
- performance comparisons

## Virtualization/container internals
- VMs
- hypervisor concepts
- microVMs
- namespaces
- cgroups
- OCI
- containerd/runc concepts
- filesystem layers
- networking
- sandboxing

## Storage engineering
- block
- file
- object
- distributed filesystem concepts
- S3 semantics
- MinIO
- Ceph concepts
- replication
- erasure coding
- lifecycle
- backup/restore
- caching

## Database internals
- WAL
- buffer pool
- page layout concepts
- B+ trees
- LSM
- compaction
- bloom filters
- query parsing/planning
- execution
- locks
- MVCC
- replication
- checkpoints/recovery

These are systems topics, not DSA practice.

## Distributed coordination
- etcd
- Consul
- ZooKeeper concepts
- leases
- distributed locks
- membership
- leader election
- health/configuration
- consensus
- split brain

## HPC/performance
- CPU profiling
- GPU compute
- CUDA concepts
- SIMD/vectorization
- multiprocessing
- mmap
- zero-copy
- Arrow memory
- distributed compute
- load/network profiling

## IoT/edge
- MQTT
- device registry
- provisioning
- certificates
- telemetry
- digital twins concepts
- OTA concepts
- edge processing
- streaming analytics

## Compiler/language tooling
Build an ATLAS DSL for policies/alerts/automation/workflows:
- lexer
- parser
- AST
- validation
- type checking concepts
- optimizer
- interpreter/executor
- syntax highlighting

## Policy/rules
- OPA/Rego concepts
- policy-as-code
- admission policies
- access rules
- automation rules
- alert expressions

## Feature flags/experimentation
- flags
- cohorts
- rollout percentages
- kill switches
- A/B tests
- assignment
- metrics
- statistics
- progressive delivery

## Recommendation/personalization
- retrieval
- ranking
- collaborative filtering
- content-based
- embeddings
- online signals
- evaluation

## Notifications
- email
- push
- SMS abstraction
- webhooks
- in-app
- templates
- preferences
- retries
- delivery tracking
- digests

## Enterprise connectors
Connector SDK for:
- databases
- object stores
- Git providers
- cloud providers
- project/ticket systems
- messaging
- identity
- warehouses
- SaaS APIs

Support:
- OAuth
- API keys
- webhooks
- polling
- rate limits
- pagination
- sync checkpoints
- backoff/retry

## Release engineering
- semantic versioning
- changelogs
- release candidates
- package/container registries
- signing
- provenance
- migrations
- canary
- blue/green
- rollback

## Build systems/monorepo engineering
- npm/pnpm
- Turborepo/Nx concepts
- Python builds/workspaces
- Maven
- Gradle
- Cargo
- Go modules
- CMake
- build cache
- dependency graphs
- affected builds

## Plugin architecture
Extensions:
- UI modules
- connectors
- agent tools
- MCP integrations
- models
- dashboards
- alert rules
- automation

Include:
- manifests
- permission scopes
- lifecycle
- compatibility
- versioning
- sandboxing

## Browser/web internals
- parsing/rendering
- event loop
- hydration
- Server Components concepts
- caching
- service workers
- Web Workers
- browser storage
- CSP
- profiling
- network waterfalls

## Offline-first
- local persistence
- sync queues
- optimistic writes
- conflict resolution
- retries
- background sync
- eventual consistency

## Disaster recovery
- backups
- PITR
- RPO/RTO
- failover
- restore drills
- region outage simulation
- multi-region data

## Chaos engineering
Controlled ATLAS infrastructure only:
- kill services
- delay networks
- fill disk
- exhaust memory
- expire credentials
- fail broker/cache/database replica/region
- corrupt configuration

## Compliance/privacy/governance
- data deletion/export
- retention
- consent concepts
- auditability
- residency
- access reviews
- control mapping

## GreenOps
- utilization
- idle resources
- cost/resource tradeoffs
- storage lifecycle
- energy/carbon concepts

## Production support
- ownership
- on-call
- escalation
- runbooks
- incidents
- status pages
- postmortems
- maintenance windows

## Product analytics
- events
- funnels
- cohorts
- retention
- attribution concepts
- experimentation metrics
- usage analytics

## Knowledge graph/graph analytics
- entity graph
- service graph
- lineage graph
- graph database
- traversal
- graph analytics
- graph-enhanced retrieval

## Rule

Every product surface must use technologies because the feature requires them. Avoid decorative inclusion.
