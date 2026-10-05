/** Run selected quality gates; unselected runtime gates remain explicitly not_run. */
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
const profile = process.argv[2] ?? "local";
if (!["local", "platform", "data-engineering", "full"].includes(profile)) throw new Error("Unknown quality profile");
const retryFailed = process.argv[3] === "--retry-failed";
const refreshWeb = process.argv[3] === "--refresh-web";
if (process.argv[3] && !retryFailed && !refreshWeb) throw new Error("Unknown quality option");
const webGateIds = new Set(["registry-consistency", "web-lint", "web-types", "web-unit", "web-build"]);
const snapshotPath = resolve("apps/web/src/data/quality-snapshot.json");
const prior = retryFailed || refreshWeb ? JSON.parse(readFileSync(snapshotPath, "utf8")) : null;
if (prior && (prior.schema_version !== 2 || prior.profile !== profile)) throw new Error("Retry requires a matching recorded profile");
const nativePython = process.platform === "win32" ? ".venv/Scripts/python.exe" : ".venv/bin/python";
const python = existsSync(nativePython) ? nativePython : "python";
const py = (args) => `"${python}" ${args}`;
const gates = [
  ["registry-consistency", "Registry and progression consistency", py("scripts/audit_consistency.py"), "local"],
  ["agent-security-boundaries", "Agent memory and approvals", py("labs/security/agent-boundaries/run.py verify"), "local"],
  ["deployment-native-render", "Native Helm deployment policy (cluster unverified)", py("scripts/verify_deployment.py"), "platform"],
  ["infrastructure-local-plan", "Native OpenTofu local metadata lifecycle", py("scripts/verify_infrastructure_plan.py"), "platform"],
  ["usage-streaming-lakehouse", "Usage streaming / Parquet / Iceberg", py("scripts/verify_streaming.py"), "data-engineering"],
  ["usage-spark-local", "Actual local Spark Parquet rollup", py("scripts/verify_usage_spark.py"), "data-engineering"],
  ["live-kafka", "Live Kafka replay acceptance", py("scripts/verify_kafka.py"), "full"],
  ["airflow-dag-parse", "Linux Airflow DAG parse (scheduler acceptance separate)", py("scripts/verify_airflow_dag.py"), "full"],
  ["durable-event-pipeline", "Durable usage pipeline recovery", py("labs/data-engineering/event-pipeline/run.py verify"), "local"],
  ["web-lint", "Frontend lint", "pnpm --filter @atlas/web lint --max-warnings=0", "local"],
  ["web-types", "TypeScript strict", "pnpm --filter @atlas/web typecheck", "local"],
  ["web-unit", "Frontend unit", "pnpm --filter @atlas/web test", "local"],
  ["web-build", "Production build", "pnpm --filter @atlas/web build", "local"],
  ["api-lint", "Python lint", py("-m ruff check apps/api-python"), "local"],
  ["api-types", "Python strict typing", py("-m mypy apps/api-python/src"), "local"],
  ["api-tests", "API integration/security", py("-m pytest apps/api-python --cov=atlas_api --cov-fail-under=80"), "local"],
  ["node-types", "Node protocol strict typing", "pnpm --filter @atlas/api-node typecheck", "local"],
  ["node-tests", "REST/GraphQL/gRPC contract", "pnpm --filter @atlas/api-node test", "local"],
  ...[
    ["python-mastery", "labs/python/python-mastery", "local"],
    ["database-query-plans", "labs/databases/query-plans", "local"],
    ["database-isolation-locks", "labs/databases/isolation-locks", "local"],
    ["database-postgresql-concurrency", "labs/databases/postgresql-concurrency", "full"],
    ["database-mariadb-provider", "labs/databases/mariadb-provider", "full"],
    ["database-mongodb-document-model", "labs/databases/mongodb-document-model", "full"],
    ["database-redis-cache-streams", "labs/databases/redis-cache-streams", "full"],
    ["database-provider-benchmarks", "labs/databases/provider-benchmarks", "local"],
    ["database-security-boundaries", "labs/security/database-boundaries", "local"],
    ["data-science-quality", "labs/data/science-quality", "local"],
    ["machine-learning-evaluation", "labs/ml/model-evaluation", "local"],
    ["deep-learning-frameworks", "labs/deep-learning/framework-comparison", "local"],
    ["deep-learning-applied-ai", "labs/deep-learning/applied-ai", "local"],
  ].map(([id, path, scope]) => [id, id.replaceAll("-", " "), py(`${path}/run.py verify`), scope]),
];
const results = gates.map(([id, name, command, scope]) => {
  const selected = scope === "local" || profile === "full" || scope === profile || (profile === "platform" && scope === "data-engineering");
  if (!selected) return { id, name, command, scope, status: "not_run", duration_ms: 0, exit_code: null };
  if (prior) {
    const recorded = prior.gates.find(g => g.id === id);
    if (!recorded || recorded.command !== command || recorded.scope !== scope) throw new Error(`Changed gate requires a fresh profile: ${id}`);
    // Explicit recovery preserves the original observation time of other gates.
    // It is for repairing an interrupted/failed run, not certifying later edits.
    if ((retryFailed && recorded.status === "passed") || (refreshWeb && !webGateIds.has(id))) return { ...recorded, executed_at: recorded.executed_at ?? prior.generated_at };
  }
  console.log(`Running ${name}...`);
  const started = performance.now();
  // The full API suite includes several independently bounded framework workers;
  // its aggregate budget must exceed one worker's 90s cold-start allowance.
  const timeout = id === "api-tests" ? 600000 : 300000;
  const result = spawnSync(command, { cwd: process.cwd(), encoding: "utf8", shell: true, timeout, maxBuffer: 4 * 1024 * 1024 });
  if (result.status !== 0) console.error(`${name}: failed${result.error ? ` (${result.error.code ?? "runner error"})` : ""}\n${(result.stdout ?? "").slice(-1500)}\n${(result.stderr ?? "").slice(-1500)}`);
  if (["web-unit", "api-tests"].includes(id)) {
    const counts = (result.stdout ?? "").match(/(?:Tests\s+\d+ passed|\d+ passed[^\n]*)/g);
    if (counts) console.log(counts.join("\n"));
  }
  // Keep raw provider failures, local paths and test payloads out of browser data.
  return { id, name, command, scope, status: result.status === 0 ? "passed" : "failed", duration_ms: Math.round(performance.now() - started), exit_code: result.status, executed_at: new Date().toISOString() };
});
const snapshot = { schema_version: 2, generated_at: new Date().toISOString(), revision: "working-tree", profile,
  summary: { total: results.length, passed: results.filter(g => g.status === "passed").length, failed: results.filter(g => g.status === "failed").length, not_run: results.filter(g => g.status === "not_run").length }, gates: results };
writeFileSync(snapshotPath, `${JSON.stringify(snapshot, null, 2)}\n`, "utf8");
console.log(`quality snapshot (${profile}): ${snapshot.summary.passed} passed, ${snapshot.summary.failed} failed, ${snapshot.summary.not_run} not run`);
process.exit(snapshot.summary.failed === 0 ? 0 : 1);
