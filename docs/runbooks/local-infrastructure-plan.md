# Local infrastructure plan review

This verifies budget metadata against an empty disposable local state. It does
not deploy Kubernetes or query a cloud account. OpenTofu 1.13.0 is the current
native engine; Terraform is an unimplemented alternate engine. Source uses the
Terraform JSON language and builtin terraform_data, with no external providers.

Use the official portable tool at ignored `.tools/opentofu-1.13.0/tofu.exe` on
Windows or checksum-verified `tofu` on PATH for Linux. Do not change global PATH.
Keep LICENSE/README. Windows amd64 ZIP SHA-256:
`cc19de2b9461d62ccf73d422703d939c44d6ffcd94e95bacf43752c34125f5d6`.
Linux amd64 ZIP SHA-256:
`ad494034a03aaa66d93fc1c2c164d01bedf21b44cfb8b616182cb69424a67672`.
These are official published checksum checks, not an independent signature
attestation. Linux CI verifies its own archive; remote CI has not run here.

```powershell
.venv/Scripts/python.exe scripts/verify_infrastructure_plan.py
.venv/Scripts/python.exe scripts/verify_infrastructure_plan.py --publish
.venv/Scripts/python.exe -m pytest apps/api-python/tests/test_infrastructure_plan.py
```

Normal verification leaves no new receipt. `--publish` atomically writes only the
redacted observation at `artifacts/infrastructure/local-plan.json`; artifacts are
ignored. Enable `ATLAS_INFRASTRUCTURE_PLAN_ENABLED=true` on a trusted local API
with this repository root. Open `/infrastructure` and refresh Local infrastructure
plan. This is independent of the Helm review flag. Missing receipt is distinct
from disabled/unavailable; older source is distinct from matching current source.
Whitespace/configuration-byte changes also invalidate content-bound lineage.
Changing manifest bytes or inputs requires a new verified native plan.

The complete configuration is source-owned and allowlisted before any CLI command.
The operator verifier creates a unique child under artifacts/plan-fixtures, copies
only the checked configuration and generated numeric input, and removes it when
finished. No user tfvars, extra .tf/.tofu files, cloud keys or provider modules enter
this workflow. Source changes during verification prevent publication. The native
over-budget test proves a failing precondition. Apply/destroy exercise only the
checked builtin metadata inside that disposable directory. No other state is read
or removed. Checkpointed older evidence remains if a later verification fails.

Raw saved plans and JSON can contain secrets in general; never add real provider
credentials or publish arbitrary plans through this slice. The API contains no
tool execution, uploads, context selectors, apply or destroy endpoints. Tokens stay
in the BFF. Fixed-label metrics `atlas_infrastructure_plan_reads_total` and structured
current/older/missing/unavailable events omit provider content. Malformed receipt
and source failures return redacted 503 with no-store.

Reset the receipt only when intentionally discarding this local observation. For
test workflows use a separately owned root/artifact copy. Do not delete unrelated
state, credentials, deployment data or cloud resources. Cloud state/billing,
provider installation, pricing and destructive plan approval remain future scope.
