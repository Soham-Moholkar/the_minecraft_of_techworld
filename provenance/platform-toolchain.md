# Phase 11 toolchain provenance

Helm 4.3.0: official Helm project, stable release dated 2026-09-09, Apache-2.0.
Reviewed official release/install/template documentation on 2026-10-04.
Windows amd64 archive retrieved from https://get.helm.sh/helm-v4.3.0-windows-amd64.zip.
SHA-256 verified before extraction:
`304ea163cce4d9ad14e189c01846c6a34de9cfdfe48536ae54b2e8ba7884e67c`.
Portable executable and original LICENSE/README remain in ignored .tools; no
global install or PATH changes. CI verifies the official Linux archive independently.
Maintenance/security updates require an intentional registry/checksum/script review;
a pinned version is reproducible, not a security certification.

All chart, policy and application integration source is ATLAS-owned. Kubernetes
documentation informed the stable API, quota, pod security and network contracts;
no external chart/repository/component was copied wholesale. Helm rendering is
verified locally; Kubernetes runtime version and actual cluster operation are pending.

OpenTofu 1.13.0: official stable release dated 2026-09-30, MPL-2.0. Official release,
maintenance/security policy and standalone/plan/JSON docs reviewed on 2026-10-04.
Windows amd64 archive and checksums fetched through official GitHub release assets;
checksum verified before extraction: cc19de2b9461d62ccf73d422703d939c44d6ffcd94e95bacf43752c34125f5d6.
Original LICENSE/README/CHANGELOG remain in ignored .tools/opentofu-1.13.0.
No global install/PATH change, external providers or cloud configuration. Native
local metadata lifecycle and resource precondition are actually verified. CI
verifies the published Linux checksum independently; signature attestation and
remote CI execution are not claimed. All integration/configuration source is owned.
