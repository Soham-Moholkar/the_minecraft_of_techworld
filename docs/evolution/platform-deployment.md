# Platform deployment progression

1. Owned stable Kubernetes API manifests, single-writer persistence, security and budget policy.
2. Actual native Helm lint/render, override rejection, artifact drift gate, owner-only product review.
3. Live owned local-cluster scheduling, image startup, CNI isolation, quota and PVC recovery.
4. Reproducible immutable image builds, scanning/SBOM, CI release promotion and rollback.
5. Terraform/OpenTofu local plans and cloud adapters with state/secret/cost safeguards.
6. Ansible configuration idempotence and AWS/Azure/GCP comparison labs with bounded teardown.
7. Production identity, admission policy, SLOs, disaster recovery and multi-environment releases.
8. Alternative runtimes/providers and measured operational tradeoffs.

Helm reaches level 2 through native local execution and real UI/API observation.
Kubernetes reaches level 1 through source policy; live cluster execution is pending.
Neither implies Phase 11 completion. See ADR 0016 and ATLAS-PLAT-P11.

OpenTofu now reaches level 2: independent builtin configuration, actual native
create/no-op/budget rejection/owned local teardown and product receipt lineage.
It does not implement Terraform's alternate CLI, cloud state or provider plans.
The next step is governed persistent state and provider-independent plan contracts,
followed by approved cloud/provider budgets and configuration automation. See ADR 0017.
