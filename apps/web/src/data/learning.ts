export type TopicSection = {
  id: string;
  title: string;
  explanation: string;
  code?: string;
  language?: string;
};

export type Topic = {
  slug: string;
  title: string;
  domain: string;
  technology: string;
  level: string;
  summary: string;
  labId: string;
  sourcePath: string;
  sections: TopicSection[];
};

export const topics: Topic[] = [
  {
    slug: "control-plane-api-evolution",
    title: "Control-plane API evolution",
    domain: "Backend engineering",
    technology: "FastAPI + SQLAlchemy",
    level: "Realistic",
    summary: "Trace an authenticated request through validation, tenant authorization, a transaction boundary, persistence, and durable audit evidence.",
    labId: "api-foundation",
    sourcePath: "content/backend/control-plane-evolution.md",
    sections: [
      { id: "boundary", title: "Start at the boundary", explanation: "The route accepts a typed principal dependency. The provider can change from the offline bearer emulator to OIDC without changing every handler.", code: "principal: Annotated[Principal, Depends(require_principal)]", language: "python" },
      { id: "tenant", title: "Authorize every query", explanation: "Tenant scope belongs inside repository queries, not only in the UI. A cross-tenant identifier returns 404 so it cannot become an existence oracle.", code: "Project.organization_id == Organization.id\nOrganization.slug == principal.organization_slug", language: "python" },
      { id: "audit", title: "Commit evidence atomically", explanation: "The project or note and its audit event share one SQLAlchemy transaction. A rollback cannot leave an unaudited mutation behind.", code: "session.add(project)\nsession.add(audit_event)\nsession.commit()", language: "python" },
      { id: "realtime", title: "Upgrade to bidirectional realtime", explanation: "The browser exchanges server-side HTTP authentication for a short-lived one-use ticket. The socket then enforces origin, capacity, size, rate, and typed-envelope controls.", code: "POST /api/realtime/ticket\nWS /v1/realtime/ws?ticket=<opaque-one-use-grant>", language: "http" },
      { id: "protocols", title: "Compare contracts, not databases", explanation: "The Node facade exposes the same authoritative project provider through REST, GraphQL, and gRPC. This isolates protocol tradeoffs from data-model drift.", code: "GET :8100/v1/projects\nPOST :8100/graphql\ngRPC :8101 atlas.protocols.Projects/ListProjects", language: "text" },
      { id: "verify", title: "Verify the contract", explanation: "Integration and security tests exercise HTTP, authentication, tenant isolation, duplicate conflicts, notes, search, and the audit trail against an isolated database.", code: ".\\.venv\\Scripts\\python -m pytest apps/api-python --cov=atlas_api", language: "powershell" },
    ],
  },
  {
    slug: "python-mastery",
    title: "Python mastery vertical",
    domain: "Python",
    technology: "Python 3.12",
    level: "Foundation → advanced",
    summary: "A single executable vertical connecting typing, object design, generators, decorators, async work, concurrency, testing, and profiling.",
    labId: "python-mastery",
    sourcePath: "content/python/python-mastery.md",
    sections: [
      { id: "functions", title: "Functions and typing", explanation: "Small typed functions form the stable seam. Protocols describe capability without forcing inheritance.", code: "def normalize(values: list[float]) -> list[float]:\n    total = sum(values)\n    return [value / total for value in values]", language: "python" },
      { id: "oop", title: "Objects and protocols", explanation: "A frozen dataclass carries validated work while a protocol keeps providers replaceable.", code: "@dataclass(frozen=True)\nclass WorkItem:\n    id: str\n    value: float", language: "python" },
      { id: "lazy", title: "Generators and decorators", explanation: "Generators bound memory use; decorators add timing without obscuring the core algorithm.", code: "@profiled\ndef batches(items, size):\n    for index in range(0, len(items), size):\n        yield items[index:index + size]", language: "python" },
      { id: "concurrency", title: "Async and parallel work", explanation: "Async coordinates I/O. A process pool is reserved for CPU-bound work; threads fit blocking libraries that release the GIL.", code: "results = await asyncio.gather(*(fetch(item) for item in items))", language: "python" },
      { id: "failures", title: "Isolate process failures", explanation: "Process futures are collected independently so one invalid work item becomes explicit failure evidence without discarding successful results.", code: "result = parallel_squares_resilient([2, -1, 3])\nassert result.succeeded == {2: 4, 3: 9}\nassert -1 in result.failed", language: "python" },
      { id: "memory", title: "Measure memory and package execution", explanation: "tracemalloc measures the lazy workload, while zipapp produces a dependency-free executable archive that can be verified and removed by the lab lifecycle.", code: "python labs/python/python-mastery/run.py start\npython labs/python/python-mastery/dist/atlas-python-mastery.pyz", language: "powershell" },
      { id: "evidence", title: "Tests and profiling", explanation: "Correctness tests and a repeatable benchmark are separate artifacts. Optimize only after the profiler identifies a useful target.", code: "python labs/python/python-mastery/run.py test\npython labs/python/python-mastery/benchmark.py", language: "powershell" },
    ],
  },
];

export const labs = {
  "agent-security-boundaries": {
    id: "agent-security-boundaries", title: "Agent memory poisoning and separate approvals", domain: "Security", difficulty: "Advanced", runtime: "process", path: "labs/security/agent-boundaries",
    objective: "Verify actual memory isolation, expiry, content-free audit and separate digest-bound approvals without executing tools.",
    commands: { start: "python labs/security/agent-boundaries/run.py start", test: "python labs/security/agent-boundaries/run.py test", reset: "python labs/security/agent-boundaries/run.py reset" },
  },
  "durable-event-pipeline": {
    id: "durable-event-pipeline", title: "Durable usage pipeline and checkpoint recovery",
    domain: "Data engineering", difficulty: "Intermediate", runtime: "process",
    path: "labs/data-engineering/event-pipeline",
    objective: "Run an offline usage-event pipeline, inject a pre-commit crash, inspect tenant-scoped lag and quarantine counts, then verify safe replay. SQLite local provider; Kafka integration is pending.",
    commands: { start: "python labs/data-engineering/event-pipeline/run.py start", test: "python labs/data-engineering/event-pipeline/run.py test", reset: "python labs/data-engineering/event-pipeline/run.py reset" },
  },
  "framework-comparison": {
    id: "framework-comparison", title: "PyTorch and TensorFlow/Keras comparison",
    domain: "Deep learning", difficulty: "Advanced", runtime: "process",
    path: "labs/deep-learning/framework-comparison",
    objective: "Compare bounded neural training on identical inputs, initialization and holdout; inspect persisted losses and regression evidence.",
    commands: { start: "python labs/deep-learning/framework-comparison/run.py start", test: "python labs/deep-learning/framework-comparison/run.py test", reset: "python labs/deep-learning/framework-comparison/run.py reset" },
  },
  "model-evaluation": {
    id: "model-evaluation", title: "Model workflow, evaluation, and interpretation",
    domain: "Machine learning", difficulty: "Advanced", runtime: "process",
    path: "labs/ml/model-evaluation",
    objective: "Compare two scikit-learn pipelines with a from-scratch NumPy baseline on one deterministic holdout and inspect permutation effects.",
    commands: { start: "python labs/ml/model-evaluation/run.py start", test: "python labs/ml/model-evaluation/run.py test", reset: "python labs/ml/model-evaluation/run.py reset" },
  },
  "data-science-quality": {
    id: "data-science-quality", title: "Operational dataset quality and scaling",
    domain: "Data science", difficulty: "Advanced", runtime: "process",
    path: "labs/data/science-quality",
    objective: "Clean deterministic dirty data, profile distributions and uncertainty, and verify pandas, Polars, and DuckDB parity at three scales.",
    commands: { start: "python labs/data/science-quality/run.py start", test: "python labs/data/science-quality/run.py test", reset: "python labs/data/science-quality/run.py reset" },
  },
  "api-foundation": {
    id: "api-foundation",
    title: "Control-plane API foundation",
    domain: "Backend",
    difficulty: "Foundation",
    runtime: "process",
    path: "labs/python/api-foundation",
    objective: "Trace and verify the smallest resettable HTTP-flow lab without external network access.",
    commands: { start: "python labs/python/api-foundation/run.py start", test: "python labs/python/api-foundation/run.py test", reset: "python labs/python/api-foundation/run.py reset" },
  },
  "python-mastery": {
    id: "python-mastery",
    title: "Python mastery evidence lab",
    domain: "Python",
    difficulty: "Intermediate",
    runtime: "process",
    path: "labs/python/python-mastery",
    objective: "Run typed examples, concurrency paths, tests, and a deterministic profiling benchmark.",
    commands: { start: "python labs/python/python-mastery/run.py start", test: "python labs/python/python-mastery/run.py test", reset: "python labs/python/python-mastery/run.py reset" },
  },
  "database-query-plans": {
    id: "database-query-plans",
    title: "Tenant query-plan and composite-index lab",
    domain: "Databases",
    difficulty: "Intermediate",
    runtime: "process",
    path: "labs/databases/query-plans",
    objective: "Compare one tenant-scoped query before and after a composite index, then inspect stable plan and correctness evidence.",
    commands: { start: "python labs/databases/query-plans/run.py start", test: "python labs/databases/query-plans/run.py test", reset: "python labs/databases/query-plans/run.py reset" },
  },
  "database-isolation-locks": {
    id: "database-isolation-locks",
    title: "SQLite reader-snapshot and writer-lock lab",
    domain: "Databases",
    difficulty: "Advanced",
    runtime: "process",
    path: "labs/databases/isolation-locks",
    objective: "Observe a stable WAL reader snapshot, blocked writer, dirty-read prevention, rollback, and successful retry across real connections.",
    commands: { start: "python labs/databases/isolation-locks/run.py start", test: "python labs/databases/isolation-locks/run.py test", reset: "python labs/databases/isolation-locks/run.py reset" },
  },
  "database-postgresql-concurrency": {
    id: "database-postgresql-concurrency",
    title: "PostgreSQL locks, deadlocks, and Serializable retry lab",
    domain: "Databases",
    difficulty: "Advanced",
    runtime: "compose",
    path: "labs/databases/postgresql-concurrency",
    objective: "Classify a row-lock timeout and deadlock by SQLSTATE, then retry a Serializable transaction from fresh reads while preserving an application invariant.",
    commands: { start: "python labs/databases/postgresql-concurrency/run.py start", test: "python labs/databases/postgresql-concurrency/run.py test", reset: "python labs/databases/postgresql-concurrency/run.py reset" },
  },
  "database-mariadb-provider": {
    id: "database-mariadb-provider",
    title: "MariaDB provider, index, and transaction lab",
    domain: "Databases",
    difficulty: "Advanced",
    runtime: "compose",
    path: "labs/databases/mariadb-provider",
    objective: "Verify JSON plan/index selection, Repeatable Read snapshots, and numeric lock-wait recovery against real InnoDB connections.",
    commands: { start: "python labs/databases/mariadb-provider/run.py start", test: "python labs/databases/mariadb-provider/run.py test", reset: "python labs/databases/mariadb-provider/run.py reset" },
  },
  "database-mongodb-document-model": {
    id: "database-mongodb-document-model",
    title: "MongoDB document model, compound index, and atomic update lab",
    domain: "Databases",
    difficulty: "Advanced",
    runtime: "compose",
    path: "labs/databases/mongodb-document-model",
    objective: "Measure a compound tenant index, reject invalid documents, and prove optimistic atomic inventory updates against real MongoDB connections.",
    commands: { start: "python labs/databases/mongodb-document-model/run.py start", test: "python labs/databases/mongodb-document-model/run.py test", reset: "python labs/databases/mongodb-document-model/run.py reset" },
  },
  "database-redis-cache-streams": {
    id: "database-redis-cache-streams",
    title: "Redis cache, Streams, transaction, and ACL lab",
    domain: "Databases",
    difficulty: "Advanced",
    runtime: "compose",
    path: "labs/databases/redis-cache-streams",
    objective: "Verify cache expiry, consumer recovery, optimistic transaction retry, and least-privileged key access against real Redis.",
    commands: { start: "python labs/databases/redis-cache-streams/run.py start", test: "python labs/databases/redis-cache-streams/run.py test", reset: "python labs/databases/redis-cache-streams/run.py reset" },
  },
  "database-provider-benchmarks": {
    id: "database-provider-benchmarks",
    title: "Relational, document, and cache read-pattern benchmark",
    domain: "Databases",
    difficulty: "Advanced",
    runtime: "process",
    path: "labs/databases/provider-benchmarks",
    objective: "Compare repeatable read patterns with workload, environment, percentiles, correctness digests, and explicit caveats.",
    commands: { start: "python labs/databases/provider-benchmarks/run.py start", test: "python labs/databases/provider-benchmarks/run.py test", reset: "python labs/databases/provider-benchmarks/run.py reset" },
  },
  "database-security-boundaries": {
    id: "database-security-boundaries",
    title: "Database injection and least-privilege exercise",
    domain: "Security",
    difficulty: "Advanced",
    runtime: "process",
    path: "labs/security/database-boundaries",
    objective: "Observe an isolated tenant escape, then prove parameterization, tenant scoping, read-only authorization, and audit redaction.",
    commands: { start: "python labs/security/database-boundaries/run.py start", test: "python labs/security/database-boundaries/run.py test", reset: "python labs/security/database-boundaries/run.py reset" },
  },
} as const;

export function findTopic(slug: string) {
  return topics.find((topic) => topic.slug === slug);
}
