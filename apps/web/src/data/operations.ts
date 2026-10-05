export type OperationalItem = {
  name: string;
  kind: string;
  status: "implemented" | "reference";
  owner: string;
  evidence: string;
};

export type OperationalDomain = {
  id: string;
  title: string;
  summary: string;
  posture: string;
  items: OperationalItem[];
};

export const operationalDomains: Record<string, OperationalDomain> = {
  data: {
      id: "data", title: "Data estate", summary: "Authoritative stores, derived read models, migration history, ownership, and portable development adapters.", posture: "5 providers · safe queries + cache + benchmark + security",
    items: [
      { name: "ATLAS PostgreSQL", kind: "Authoritative relational store", status: "implemented", owner: "Data Platform", evidence: "compose.yaml" },
        { name: "SQLite adapter", kind: "Offline/test provider", status: "implemented", owner: "Control Plane", evidence: "apps/api-python/src/atlas_api/database.py" },
        { name: "MariaDB provider", kind: "Optional least-privileged comparison and InnoDB lab", status: "implemented", owner: "Data Platform", evidence: "apps/api-python/src/atlas_api/provider_comparison.py" },
        { name: "MongoDB projection", kind: "Optional tenant-scoped document read model and atomic-update lab", status: "implemented", owner: "Data Platform", evidence: "apps/api-python/src/atlas_api/document_projection.py" },
        { name: "Redis cache", kind: "Optional cache-aside aggregate with SQL fallback and ACL-scoped lab", status: "implemented", owner: "Data Platform", evidence: "apps/api-python/src/atlas_api/cache_profile.py" },
      { name: "Alembic history", kind: "Transactional schema evolution", status: "implemented", owner: "Control Plane", evidence: "apps/api-python/alembic/versions" },
      { name: "Query-plan provider", kind: "Tenant-safe PostgreSQL and SQLite EXPLAIN", status: "implemented", owner: "Data Platform", evidence: "apps/web/src/components/explain-plan-viewer.tsx" },
      { name: "Concurrency profile", kind: "Live isolation semantics and provider mapping", status: "implemented", owner: "Data Platform", evidence: "apps/web/src/components/isolation-visualizer.tsx" },
      { name: "Lock activity", kind: "Privacy-bounded aggregate PostgreSQL lock snapshot", status: "implemented", owner: "Data Platform", evidence: "apps/web/src/components/lock-activity-viewer.tsx" },
      { name: "Safe query workbench", kind: "Named, parameterized, tenant-scoped and bounded read template", status: "implemented", owner: "Data Platform", evidence: "apps/web/src/components/database-operations-workbench.tsx" },
      { name: "Provider benchmark suite", kind: "Workload, percentile, correctness, environment and caveat evidence", status: "implemented", owner: "Reliability", evidence: "labs/databases/provider-benchmarks" },
      { name: "Database security exercise", kind: "Injection remediation, tenant boundary, redaction and least privilege", status: "implemented", owner: "Security", evidence: "labs/security/database-boundaries" },
    ],
  },
  pipelines: {
    id: "pipelines", title: "Pipelines", summary: "Reproducible quality, migration, seed, and lab lifecycle jobs with visible evidence.", posture: "Recorded quality evidence · deterministic seed",
    items: [
      { name: "Quality snapshot", kind: "Lint, type, test, build pipeline", status: "implemented", owner: "Developer Platform", evidence: "scripts/quality-snapshot.mjs" },
      { name: "Database bootstrap", kind: "Upgrade and idempotent seed", status: "implemented", owner: "Data Platform", evidence: "apps/api-python/src/atlas_api/seed.py" },
      { name: "Lab lifecycle", kind: "Start, test, reset contract", status: "implemented", owner: "Learning Platform", evidence: "labs/python" },
    ],
  },
  ai: {
    id: "ai", title: "AI workbench", summary: "Governed repository inference, retrieval, evaluation, prompts, patches, and isolated candidate tests.", posture: "Phase 9 · separate mutation and execution approvals",
    items: [
      { name: "AI technology registry", kind: "Capability and progression source", status: "implemented", owner: "AI Platform", evidence: "registry/technologies.yaml" },
      { name: "Repository intelligence", kind: "Hosted/local structured streaming with immutable prompts", status: "implemented", owner: "AI Platform", evidence: "apps/api-python/src/atlas_api/repository_ai.py" },
      { name: "Hybrid retrieval evaluation", kind: "Exact citations, grounding and injection evidence", status: "implemented", owner: "AI Platform", evidence: "apps/api-python/src/atlas_api/repository_retrieval.py" },
      { name: "AI operational controls", kind: "Tenant budget, safe fallback, cache and rolling SLO", status: "implemented", owner: "AI Platform", evidence: "apps/api-python/src/atlas_api/ai_operations.py" },
      { name: "Permission boundary", kind: "Read-only models plus opt-in exact-diff local patch approval", status: "implemented", owner: "Security", evidence: "docs/adr/0009-local-human-approved-patch-workflow.md" },
      { name: "Patch gateway", kind: "Digest-bound approval, stale-source denial and hash-safe rollback", status: "implemented", owner: "AI Platform", evidence: "apps/api-python/src/atlas_api/agent_patches.py" },
      { name: "Agent workflow", kind: "Persisted deterministic validation and human-review state graph", status: "implemented", owner: "AI Platform", evidence: "apps/api-python/src/atlas_api/agent_workflows.py" },
      { name: "Candidate test worker", kind: "Networkless container, workflow evidence and fresh retry approvals", status: "implemented", owner: "AI Platform", evidence: "apps/api-python/src/atlas_api/agent_test_worker.py" },
    ],
  },
  infrastructure: {
    id: "infrastructure", title: "Infrastructure", summary: "Local production-style services, health checks, private networking, and durable storage.", posture: "Compose source inventory",
    items: [
      { name: "Web runtime", kind: "Next.js standalone container", status: "implemented", owner: "Web Platform", evidence: "apps/web/Dockerfile" },
      { name: "API runtime", kind: "Non-root FastAPI container", status: "implemented", owner: "Control Plane", evidence: "apps/api-python/Dockerfile" },
      { name: "Protocol facade", kind: "Node REST, GraphQL, and gRPC", status: "implemented", owner: "Developer Platform", evidence: "apps/api-node" },
      { name: "Core Compose profile", kind: "Network and volume orchestration", status: "implemented", owner: "Platform", evidence: "compose.yaml" },
    ],
  },
  observability: {
    id: "observability", title: "Observability", summary: "Health, version, request correlation, structured logs, metrics, realtime checks, and operator recovery paths.", posture: "HTTP + SSE + WebSocket",
    items: [
      { name: "Service health", kind: "Database-aware readiness", status: "implemented", owner: "Control Plane", evidence: "apps/api-python/src/atlas_api/main.py" },
      { name: "Prometheus exposition", kind: "Request count and duration", status: "implemented", owner: "Reliability", evidence: "/metrics" },
      { name: "Realtime presence", kind: "Authenticated round-trip and connection metrics", status: "implemented", owner: "Reliability", evidence: "apps/web/src/components/realtime-console.tsx" },
      { name: "Recovery runbook", kind: "Control-plane troubleshooting", status: "implemented", owner: "Reliability", evidence: "docs/runbooks/control-plane-unavailable.md" },
    ],
  },
  security: {
    id: "security", title: "Security", summary: "Tenant-scoped authorization, server-only credentials, hardened responses, regression tests, and durable audit evidence.", posture: "Tenant authorization implementation",
    items: [
      { name: "Principal boundary", kind: "Replaceable identity provider", status: "implemented", owner: "Security", evidence: "apps/api-python/src/atlas_api/auth.py" },
      { name: "Tenant authorization", kind: "Repository-level query scope", status: "implemented", owner: "Control Plane", evidence: "apps/api-python/tests/test_api.py" },
      { name: "Immutable audit trail", kind: "Atomic mutation evidence", status: "implemented", owner: "Security", evidence: "apps/api-python/src/atlas_api/repository.py" },
    ],
  },
};
