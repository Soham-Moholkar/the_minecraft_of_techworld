# Development deployment review

This is an offline preflight. No cluster has been certified by the render gate.
Enable `ATLAS_DEPLOYMENT_REVIEW_ENABLED=true` on a trusted local API, with
`ATLAS_REPOSITORY_ROOT` pointing to this repository, and open `/infrastructure`.
The normal development owner token remains server-side in the BFF. Refresh rereads
the artifact; failure clears the old evidence. Disabled/unauthorized reads return
403, missing/invalid files return a redacted 503, policy drift returns a blocked
observation without resource totals or teardown commands. `/metrics` includes
fixed-label `atlas_deployment_reviews_total`; logs omit values and local paths.

## Native verification

Use official Helm 4.3.0. On Windows the ignored workspace executable is
`.tools/helm-4.3.0/windows-amd64/helm.exe`; the script also accepts Helm on PATH.
The official Windows amd64 ZIP SHA-256 is
`304ea163cce4d9ad14e189c01846c6a34de9cfdfe48536ae54b2e8ba7884e67c`.
Linux amd64 tar SHA-256 is
`86584a54def73570558f66f5111cc53dfed56689637ae32c1201205d494f54fb`.
Verify before extraction, retain upstream notices and avoid changing system PATH.

```powershell
.venv/Scripts/python.exe scripts/verify_deployment.py
.venv/Scripts/python.exe -m pytest apps/api-python/tests/test_deployment_review.py
```

After an intentional chart change, update/review the independent policy, regenerate
using `scripts/verify_deployment.py --write`, then run the normal gate. Verification
does not change source or request cluster credentials. CI repeats Linux Helm render
and policy validation; workflow source is not evidence that a remote CI run passed.
The chart rejects unsupported namespace and image overrides. Release names are
fixed by the verification/install commands; physical resource names are fixed.

## Live local acceptance (pending)

First obtain a working Linux container engine and an isolated, owned `kind-atlas`
cluster with a supported Kubernetes version and a NetworkPolicy-enforcing CNI.
Do not use a shared or paid cluster. Record server version, admission and CNI.
Build `atlas-api:local` and `atlas-web:local` from the repository Dockerfiles and
load them into the owned kind cluster. These images/builds remain unverified here.
Create the separately owned namespace from `infra/kubernetes/namespace.yaml`;
create `atlas-operator` with a strong `dev-token` using operator-controlled secret
input (never commit secret manifests or put tokens in command history).

Review the chart and context, then install only the fixed local release:
`helm --kube-context kind-atlas upgrade --install atlas infra/helm/atlas --namespace atlas-dev`.
This is a manual future acceptance command, not performed by the application.
Verify API migration/seed and actual health, web/BFF project reads, UID/filesystem
permissions, secret injection, pod quotas and startup probes. Use loopback-bound
port forwarding for web port 3000. Do not add public ingress. NetworkPolicies do
not certify isolation without a compatible CNI; test allowed web→API/DNS and
rejected cross-namespace/unrelated-pod/Internet flows in the actual cluster.
Restart API, confirm SQLite persistence and compare project state before/after.
ReadWriteOnce does not itself prohibit multiple writers; the contract separately
requires a single API replica and Recreate. This is a development baseline.

## Teardown and reset

Inspect the UI's plan. Before executing any command, verify the namespace tenant
and managed-by labels, each resource's ownership, and the actual kind-atlas context.
Delete the two deployments first, then services, network policies, quota and
service account. Explicit commands list only fixed names and namespace. No
`--all`, namespace deletion, PVC deletion, secret deletion, Helm uninstall or
cluster deletion belongs to this plan. Namespace/PVC/operator secret and release
metadata remain. Removing a quota does not free storage or imply zero cloud cost.
Helm metadata can still report an installed release after manual workload removal;
a reviewed `helm upgrade --install` reconciles owned workloads for the next run.
Do not reset retained data without separate explicit operator intent.

There are no disposable application fixtures for the offline gate; it reads source
and emits bounded evidence. The checked artifact is intended for operator review,
not confidential data. The repository root is an operator trust boundary.
