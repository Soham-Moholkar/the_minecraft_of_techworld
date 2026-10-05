param(
  [ValidateSet("validate", "start", "test", "reset")]
  [string]$Action = "validate",
  [string]$Lab = "api-foundation"
)
$ErrorActionPreference = "Stop"
$manifest = Join-Path $PSScriptRoot "..\labs\python\$Lab\lab.json"
python (Join-Path $PSScriptRoot "validate_lab.py") $manifest
if ($Action -ne "validate") {
  python (Join-Path $PSScriptRoot "..\labs\python\$Lab\run.py") $Action
}

