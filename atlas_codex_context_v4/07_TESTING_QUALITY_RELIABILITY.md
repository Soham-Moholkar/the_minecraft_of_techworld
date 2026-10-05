# Testing, Quality and Reliability Specification

Testing is a product feature, not only a CI concern.

# 1. Test taxonomy

ATLAS should demonstrate:

- unit testing
- component testing
- integration testing
- API testing
- database testing
- contract testing
- end-to-end testing
- smoke testing
- regression testing
- snapshot testing where appropriate
- accessibility testing
- visual regression concepts
- property-based testing
- fuzz testing
- mutation testing
- load testing
- stress testing
- spike testing
- soak/endurance testing
- resilience testing
- chaos/fault-injection testing
- security testing
- data quality tests
- ML evaluation/regression tests
- AI/agent evaluation tests

# 2. Tool coverage

## Python
- pytest
- unittest
- Hypothesis
- coverage tooling
- tox/nox concepts
- mocking/fixtures
- async tests

## JS/TS
- Vitest/Jest concepts
- React Testing Library
- Playwright
- Cypress
- mocking/service worker concepts

## API
- typed client tests
- Postman/Newman-style workflow
- pytest/http client
- Supertest
- REST Assured concepts for Java

## Java
- JUnit
- Spring testing patterns
- Testcontainers concepts

## Performance
- k6
- Locust
- Apache JMeter

## Security
Cross-reference security toolchain.

# 3. Test UI

Build a test center with:
- suite tree,
- live run status,
- pass/fail/skipped,
- duration,
- flaky marker,
- stack trace,
- logs,
- captured artifacts,
- snapshots,
- coverage,
- historical trends.

A learner should be able to intentionally break code and see exactly which tests catch it.

# 4. Coverage

Teach:
- statement,
- branch,
- function,
- line,
- why 100% coverage is not proof of correctness.

Visualize uncovered code.

# 5. Property-based testing

Labs:
- generate input ranges,
- discover edge cases,
- minimize failing case,
- compare example-based vs property-based tests.

# 6. Mutation testing

Show:
- mutation introduced,
- tests killed/survived mutation,
- mutation score,
- weak assertion examples.

# 7. Fuzzing

Only safe local code targets.
Teach:
- input generators,
- corpus,
- crash reproduction,
- shrinking/minimization concepts,
- invariants.

# 8. Performance tests

Standard metrics:
- latency p50/p95/p99
- requests/sec
- throughput
- error rate
- CPU
- memory
- saturation
- queue depth.

Benchmark metadata must include environment.

# 9. Reliability tests

Examples:
- dependency timeout
- dependency unavailable
- worker crash
- retry storm
- partial failure
- stale cache
- duplicate event
- out-of-order event
- database failover simulation
- network latency/loss
- resource exhaustion.

# 10. Testcontainers/local ephemeral services

Where appropriate, use isolated test services for:
- PostgreSQL
- Redis
- Kafka-compatible test flow
- object storage
- other databases.

Avoid shared mutable developer state in automated tests.

# 11. Contract testing

Teach:
- API contracts
- event contracts
- schema compatibility
- consumer/provider expectations
- backward compatibility.

# 12. Data testing

Teach tests for:
- schema
- nullability
- uniqueness
- ranges
- referential expectations
- distribution drift
- row counts
- freshness.

# 13. ML tests

- preprocessing invariants
- train/test leakage checks
- baseline comparison
- metric threshold
- reproducibility
- serialization
- inference schema
- latency
- drift checks.

# 14. AI/agent tests

- structured-output schema validation
- tool-call correctness
- no-tool cases
- tool timeout
- permission denial
- retrieval quality
- citation grounding
- prompt regression
- agent state transitions
- approval flow
- multi-step recovery.

# 15. CI strategy

Use change-aware jobs where practical.

Suggested stages:
1. lint/format
2. typecheck
3. unit/component
4. build
5. integration/contract
6. security
7. E2E
8. performance smoke
9. artifact/report publication

Heavy Spark/Kubernetes/cloud suites may be scheduled or opt-in rather than running on every UI edit.

# 16. Flaky-test discipline

Track:
- retries,
- quarantined tests,
- owner,
- reason,
- date,
- fix task.

Do not hide chronic failures behind unlimited retry logic.

# 17. Quality gates

At minimum:
- no lint errors,
- typecheck passes,
- relevant tests pass,
- build passes,
- critical security policy passes,
- migration checks pass when schemas change.
