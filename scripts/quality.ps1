param(
  [ValidateSet("local", "full", "data-engineering")]
  [string]$Profile = "full"
)

$ErrorActionPreference = "Stop"
$RepositoryPython = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $RepositoryPython)) {
  throw "Repository virtual environment not found at $RepositoryPython. Follow README.md setup first."
}

function Invoke-QualityStep {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Name,
    [Parameter(Mandatory = $true)]
    [scriptblock]$Command
  )

  Write-Host "`n==> $Name"
  & $Command

  # Windows PowerShell 5 does not make a failed native process honor
  # ErrorActionPreference. Inspecting LASTEXITCODE prevents a red test command
  # from being followed by later green output and a misleading process exit 0.
  if ($LASTEXITCODE -ne 0) {
    throw "$Name failed with exit code $LASTEXITCODE."
  }
}

Invoke-QualityStep "registry consistency" { & $RepositoryPython scripts/audit_consistency.py }
Invoke-QualityStep "agent security lab" { & $RepositoryPython labs/security/agent-boundaries/run.py verify }
Invoke-QualityStep "web lint" { pnpm lint }
Invoke-QualityStep "web types" { pnpm typecheck }
Invoke-QualityStep "web unit tests" { pnpm test }
Invoke-QualityStep "web production build" { pnpm build }
Invoke-QualityStep "API lint" { & $RepositoryPython -m ruff check apps/api-python }
Invoke-QualityStep "API strict types" { & $RepositoryPython -m mypy apps/api-python/src }
Invoke-QualityStep "API tests" { & $RepositoryPython -m pytest apps/api-python }
Invoke-QualityStep "Node protocol types" { pnpm --filter @atlas/api-node typecheck }
Invoke-QualityStep "Node protocol tests" { pnpm --filter @atlas/api-node test }
Invoke-QualityStep "Python mastery lab" { & $RepositoryPython labs/python/python-mastery/run.py verify }
Invoke-QualityStep "SQLite query-plan lab" { & $RepositoryPython labs/databases/query-plans/run.py verify }
Invoke-QualityStep "SQLite isolation lab" { & $RepositoryPython labs/databases/isolation-locks/run.py verify }
Invoke-QualityStep "provider benchmark lab" { & $RepositoryPython labs/databases/provider-benchmarks/run.py verify }
Invoke-QualityStep "database security lab" { & $RepositoryPython labs/security/database-boundaries/run.py verify }
Invoke-QualityStep "data-science lab" { & $RepositoryPython labs/data/science-quality/run.py verify }
Invoke-QualityStep "durable event pipeline lab" { & $RepositoryPython labs/data-engineering/event-pipeline/run.py verify }
Invoke-QualityStep "machine-learning lab" { & $RepositoryPython labs/ml/model-evaluation/run.py verify }
Invoke-QualityStep "deep-learning framework lab" { & $RepositoryPython labs/deep-learning/framework-comparison/run.py verify }
Invoke-QualityStep "applied-AI lab" { & $RepositoryPython labs/deep-learning/applied-ai/run.py verify }

if ($Profile -in @("full", "data-engineering")) {
  # Fails when extras are missing; skipped optional unit tests cannot certify
  # real Arrow/Iceberg behavior for the Phase 10 acceptance profile.
  Invoke-QualityStep "usage streaming/Parquet/Iceberg runtime" { & $RepositoryPython scripts/verify_streaming.py }
}

if ($Profile -eq "full") {
  # These provider checks intentionally remain full-profile gates because they
  # require Docker-backed services. A stopped Docker engine now fails loudly.
  Invoke-QualityStep "PostgreSQL concurrency lab" { & $RepositoryPython labs/databases/postgresql-concurrency/run.py verify }
  Invoke-QualityStep "MariaDB provider lab" { & $RepositoryPython labs/databases/mariadb-provider/run.py verify }
  Invoke-QualityStep "MongoDB document lab" { & $RepositoryPython labs/databases/mongodb-document-model/run.py verify }
  Invoke-QualityStep "Redis cache/stream lab" { & $RepositoryPython labs/databases/redis-cache-streams/run.py verify }
}

Write-Host "`nATLAS $Profile quality profile passed."
