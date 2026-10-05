# System Design and Interactive Case Studies

> **Product identity override:** Interpret this file through `00_PRODUCT_IDENTITY.md`. ATLAS is the real application; the IDE is the primary place for source modification. Any older “lesson/playground” wording means engineering documentation, operational tooling, reference modules, or controlled test environments—not the central product model.


System design should be implemented as an interactive frontend laboratory, not as static diagrams.

## 1. Foundation modules

Teach:
- requirements
- functional vs non-functional requirements
- capacity estimation
- QPS
- bandwidth
- storage
- latency
- availability
- consistency
- caching
- CDN
- load balancing
- queues
- databases
- indexes
- partitioning
- replication
- search
- object storage
- rate limiting
- service discovery
- observability
- security.

## 2. Interactive architecture canvas

Users should be able to:
- drag components,
- connect data flow,
- change replicas,
- set region,
- set cache hit rate,
- change partition count,
- alter capacity,
- toggle failures,
- inspect tradeoffs.

Nodes:
- client
- DNS
- CDN
- WAF
- load balancer
- API gateway
- service
- worker
- queue
- stream
- cache
- relational DB
- NoSQL DB
- search
- object storage
- ML service
- agent service
- observability
- external dependency.

## 3. Calculators

Build:
- QPS
- concurrency
- storage
- bandwidth
- cache memory
- replication/storage overhead
- partition sizing
- rough availability composition.

These are educational calculators, not capacity guarantees.

## 4. Case-study ladder

### Foundation
- URL shortener
- Pastebin
- rate limiter
- file upload service
- notification service
- key-value service concepts

### Intermediate
- chat/WhatsApp-like system
- social feed/Instagram-like system
- Twitter/X-like timeline
- ride-hailing/Uber-like dispatch concepts
- Dropbox-like sync
- e-commerce checkout
- payment/ledger simulation
- collaborative editor concepts

### Advanced
- video streaming/Netflix-like architecture
- YouTube-like upload/transcode/delivery
- search engine concepts
- large marketplace/Amazon-like architecture
- Discord/Slack-like real-time system
- analytics platform
- event ingestion platform
- multi-region SaaS
- distributed database concepts
- feature flag platform
- observability platform
- LLM inference platform
- RAG/agent platform.

Use names as familiar analogies, not claims of exact proprietary implementation.

## 5. Every case study includes

1. Problem statement
2. Scope/non-goals
3. Requirements
4. Scale assumptions
5. API sketch
6. Data model
7. Baseline architecture
8. Request/data flow
9. Bottlenecks
10. Scaling evolution
11. Failure scenarios
12. Observability
13. Security/threat model
14. Cost tradeoffs
15. Alternatives
16. Interactive challenge
17. Architecture diff after learner changes.

## 6. Security architecture mode

Toggle from:
- normal architecture
to:
- security architecture

Overlay:
- trust boundaries
- sensitive assets
- auth boundaries
- public/private network boundaries
- encryption
- audit points
- rate-limit points
- secrets
- privileged components
- STRIDE findings.

## 7. Failure mode

Allow safe simulations:
- service down
- cache down
- replica lag
- queue backlog
- network delay
- regional outage model
- overloaded DB
- failed model service
- agent tool timeout.

Show expected user impact and signals.

## 8. Compare architectures

Support side-by-side:
- monolith vs microservices
- sync vs async
- SQL vs NoSQL choice for a specific requirement
- centralized vs partitioned
- single-region vs multi-region
- cache strategies
- queue/stream choices.

No universal “best architecture”.