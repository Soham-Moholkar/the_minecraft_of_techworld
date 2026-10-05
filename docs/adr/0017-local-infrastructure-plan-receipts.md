# ADR 0017: Local IaC plans and source-bound receipts

Accepted 2026-10-04. OpenTofu 1.13.0 stable (2026-09-30, MPL-2.0) powers the first
Terraform-language infrastructure plan slice. Official release, maintenance/security
policy, standalone checksum and JSON/plan documentation were reviewed before use.
The ignored portable tool preserves upstream notices and changes no global PATH.

The owned `.tf.json` uses only builtin `terraform_data` to record the validated
development deployment's budget and manifest digest. Its complete independent
configuration contract rejects providers, modules, data reads, provisioners,
remote backends and arbitrary functions before native execution. Only that file
and generated validated inputs are copied into a unique local fixture. Other
checkout files cannot enter the run. The CLI adapter implements a PlanEngine
interface; the HTTP composition root never imports or runs the native adapter.

Child environment excludes cloud keys, ATLAS credentials, user CLI configuration,
TF_VAR/TF_CLI_ARGS and proxies; an owned CLI configuration disables checkpoint
requests. Fixed commands have time/output bounds. Native verification actually
initializes/validates, plans one metadata creation, applies only that checked local
plan, proves a no-op second plan, rejects a resource-budget breach, destroys the
owned metadata and removes the unique fixture. No cloud resources or plugins.

The plan parser accepts only one fixed builtin resource, known non-sensitive input
bound to the validated deployment, and create/no-op actions. Nested native masks
must contain only false/empty markers; numeric zero is not boolean false. Unknown
formats/tool versions, provider/resource scope, extra resources, modules,
provisioners, destructive/update/replacement actions and input drift fail closed.
This narrow policy is not a generic arbitrary-provider plan evaluator.

Only after successful lifecycle/cleanup and unchanged source checks can --publish
atomically persist a small receipt. It contains digests, version, local scope,
create/change/destroy counts, validated numeric budget and capture time. Raw binary
plans, state, outputs, variables and credentials are deleted with the fixture and
never served over HTTP. JSON plan output may contain cleartext secrets; this
contract has none and never echoes raw failures. The receipt's state baseline is
explicitly an empty disposable fixture, not live Kubernetes or cloud state.

The owner/development/northstar API reads only fixed paths behind an independent
opt-in. Source bytes and manifest/input are rechecked to distinguish current,
older and absent receipts. No receipt grants apply authority. Shared filesystem
operators can forge files, so lineage is a local observation, not a signed remote
attestation. A proper secret/state/identity/release boundary precedes cloud work.

References: [release](https://github.com/opentofu/opentofu/releases/tag/v1.13.0),
[builtin resource](https://opentofu.org/docs/language/resources/tf-data/),
[JSON format](https://opentofu.org/docs/internals/json-format/),
[plan](https://opentofu.org/docs/cli/commands/plan/),
[installation](https://opentofu.org/docs/intro/install/standalone/).
