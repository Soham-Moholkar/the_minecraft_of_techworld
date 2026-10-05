# ADR 0016: Owned development deployment review

Accepted 2026-10-04. Phase 11 is in progress after explicit user authorization;
Phase 9 and Phase 10 acceptance remain unfinished.

Infrastructure now observes a real, source-owned Helm render through an owner-only
development API and typed BFF. The API reads a bounded, fixed JSON artifact; it
never executes Helm, kubectl, a shell, uploaded manifests or cluster operations.
Its independent Python contract requires the complete fixed topology, including
every field. Unknown resources, duplicate identities, missing fields, additional
containers, inline secrets, privileges, scope changes and budget changes fail
closed. This is an ATLAS development policy, not a general admission controller.
Canonical JSON comparison distinguishes numeric zero from boolean false.

Native verification uses official checksum-verified Helm 4.3.0 (Apache-2.0), actual
lint/template, override rejection and byte-for-byte artifact consistency. Helm
notices stay with the ignored portable tool. No new runtime YAML dependency:
PyYAML is an existing developer dependency used only by the rendering script.
The API uses the standard JSON library and existing typed application contracts.

The first topology has one API writer on retained SQLite PVC storage and one web
pod, Recreate rollout, private ClusterIP services, non-root users, read-only roots,
bounded temporary volumes, disabled service-account tokens, probes, requests,
limits, quota and default-deny networking. The credential is an operator-created
external secret. The namespace is separately owned and retained; it is not in the
Helm release, avoiding namespace creation/adoption and uninstall-data conflicts.
Numeric UID 10001 and fsGroup 10001 avoid relying on image account name lookup.
Actual image startup, filesystem permissions and storage/network behavior remain
subject to live acceptance. Local image tags are never remotely pulled.

UI budget totals derive from validated manifests. Cloud pricing is unobserved.
Passing offline policy does not certify cluster health, CNI enforcement, resource
availability, Docker builds, availability, HA or recovery. No cluster version is
invented; the contract uses stable v1/apps-v1/networking-v1 APIs. Operators must
verify a supported cluster and effective admission policy during live acceptance.

Teardown produces a review-only list scoped to kind-atlas and atlas-dev. It excludes
namespace, PVC, secrets and Helm metadata and is withheld if the policy fails.
Operator ownership/context verification is mandatory before manual execution.
No HTTP mutation, apply, uninstall or cloud spend is introduced.

Progression: native rendering and product observation are implemented foundations.
Cluster scheduling/CNI/PVC recovery, immutable image releases, Terraform/Ansible,
cloud comparison, paid-resource budgets and production identity are future slices.

Primary references: [Helm release](https://github.com/helm/helm/releases/tag/v4.3.0),
[Helm template](https://helm.sh/docs/helm/helm_template/),
[Kubernetes quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/),
[network policy](https://kubernetes.io/docs/concepts/services-networking/network-policies/).
