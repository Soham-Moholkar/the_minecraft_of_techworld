# ATLAS-SEC-001 — Replace local bearer provider with OIDC and tenant authorization

Implement signed HTTP-only sessions, OIDC discovery/key rotation, organization
claims, RBAC/ABAC checks, access audit events, login/logout/device management, CSRF
protection for mutation routes, and security regression tests. Preserve the
`Principal` dependency contract and a fully offline development identity emulator.

